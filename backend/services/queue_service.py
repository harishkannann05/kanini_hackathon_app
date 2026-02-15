"""
Queue Service — Dynamic priority queue with wait time estimation.
Matches the queue schema: queue_position, waiting_time_minutes, last_updated.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from models import Queue, Doctor, Patient, Visit, ChronicCondition, SymptomSeverity, PriorityRule
from datetime import datetime, timezone
import uuid
from services.ws_manager import notify_doctor_queue_update


async def compute_priority_score(db: AsyncSession, visit_id: str, triage_result: dict, is_emergency: bool) -> int:
    """
    Compute priority score based on:
    Base Infection Priority + Vital Abnormality (risk_score) + Chronic Risk + Age Risk
    """
    # Convert visit_id to UUID
    try:
        visit_id_uuid = uuid.UUID(visit_id) if isinstance(visit_id, str) else visit_id
    except (ValueError, TypeError):
        return 50 if is_emergency else 0
    
    # 1. Base Score from AI Risk (1-10 scaled to 0-30)
    base_score = triage_result["risk_score"] * 3
    
    # 2. Fetch Patient Data
    stmt = select(Patient).join(Visit, Visit.patient_id == Patient.patient_id).where(Visit.visit_id == visit_id_uuid)
    result = await db.execute(stmt)
    patient = result.scalars().first()
    
    if not patient:
        return 50 if is_emergency else base_score

    # 3. Age Risk Multiplier
    age_score = 0
    if patient.age > 70 or patient.age < 2:
        age_score = 15
    elif patient.age > 50 or patient.age < 12:
        age_score = 10

    # 4. Chronic Risk Multiplier
    chronic_score = 0
    if patient.pre_existing_conditions:
        conditions = [c.strip() for c in patient.pre_existing_conditions.split(",") if c.strip()]
        for cond in conditions:
            # Try to match DB condition
            c_stmt = select(ChronicCondition.risk_modifier_score).where(func.lower(ChronicCondition.chronic_condition) == cond.lower())
            c_res = await db.execute(c_stmt)
            score = c_res.scalar_one_or_none() or 5  # Default 5 if not found but present
            chronic_score += score

    # 5. Symptom Severity / Infection Priority
    symptom_score = 0
    if patient.symptoms:
        symptoms = [s.strip() for s in patient.symptoms.split(",") if s.strip()]
        for sym in symptoms:
            s_stmt = select(SymptomSeverity.base_severity).where(func.lower(SymptomSeverity.symptom_name) == sym.lower())
            s_res = await db.execute(s_stmt)
            severity = s_res.scalar_one_or_none() or 3 # Default 3
            symptom_score += severity

    # 6. Priority Rules (disease/syndrome mapping)
    rule_score = 0
    rule_emergency = False
    rule_terms = []
    if patient.symptoms:
        rule_terms.extend([s.strip().lower() for s in patient.symptoms.split(",") if s.strip()])
    if patient.pre_existing_conditions:
        rule_terms.extend([c.strip().lower() for c in patient.pre_existing_conditions.split(",") if c.strip()])

    if rule_terms:
        rule_stmt = select(PriorityRule.base_priority, PriorityRule.emergency_override).where(
            func.lower(PriorityRule.condition_name).in_(rule_terms)
        )
        rule_res = await db.execute(rule_stmt)
        for base_priority, emergency_override in rule_res.all():
            if base_priority:
                rule_score += int(base_priority) * 5
            if emergency_override:
                rule_emergency = True

    # 7. Emergency Override
    emergency_boost = 50 if is_emergency or rule_emergency else 0

    total_score = base_score + age_score + chronic_score + symptom_score + rule_score + emergency_boost
    
    return min(total_score, 100)


async def get_next_position(db: AsyncSession, doctor_id: str) -> int:
    """Get the next queue position for a doctor."""
    # Coerce doctor_id to UUID if it's a string
    if isinstance(doctor_id, str):
        doctor_id = uuid.UUID(doctor_id)
    
    stmt = select(func.coalesce(func.max(Queue.queue_position), 0) + 1).where(
        Queue.doctor_id == doctor_id
    )
    result = await db.execute(stmt)
    return result.scalar() or 1


async def insert_into_queue(
    db: AsyncSession,
    visit_id: str,
    doctor_id: str,
    triage_result: dict,
) -> int:
    """
    Insert patient into the queue. Returns queue position.
    """
    # Coerce IDs to UUID early
    if isinstance(visit_id, str):
        visit_id_uuid = uuid.UUID(visit_id)
    else:
        visit_id_uuid = visit_id
        
    if isinstance(doctor_id, str):
        doctor_id_uuid = uuid.UUID(doctor_id)
        doctor_id_str = doctor_id
    else:
        doctor_id_uuid = doctor_id
        doctor_id_str = str(doctor_id)
    
    is_emergency = triage_result["risk_level"] == "High"
    
    # Compute detailed priority
    priority = await compute_priority_score(db, str(visit_id_uuid), triage_result, is_emergency)

    # Prevent duplicate insertions
    existing = await db.execute(
        select(Queue.queue_id).where(Queue.visit_id == visit_id_uuid)
    )
    if existing.scalar_one_or_none():
        return 0  # Already in queue

    position = await get_next_position(db, doctor_id_str)

    # Emergency patients get position 1 (pushed to front)
    if is_emergency:
        # Shift existing positions down
        await db.execute(
            update(Queue)
            .where(Queue.doctor_id == doctor_id_uuid)
            .values(queue_position=Queue.queue_position + 1)
        )
        position = 1

    queue_entry = Queue(
        queue_id=uuid.uuid4(),
        visit_id=visit_id_uuid,
        doctor_id=doctor_id_uuid,
        priority_score=priority,
        queue_position=position,
        waiting_time_minutes=0,
        is_emergency=is_emergency,
    )
    db.add(queue_entry)
    await db.flush()
    # Reorder and notify
    await reorder_queue_for_doctor(db, doctor_id_str)
    return position


async def estimate_wait_time(db: AsyncSession, visit_id: str, doctor_id: str) -> int:
    """
    Estimate wait time in minutes based on queue position and avg consultation time.
    """
    # Coerce IDs to UUID
    if isinstance(visit_id, str):
        visit_id = uuid.UUID(visit_id)
    if isinstance(doctor_id, str):
        doctor_id = uuid.UUID(doctor_id)
    
    # Get this patient's position
    stmt = select(Queue.queue_position).where(Queue.visit_id == visit_id)
    result = await db.execute(stmt)
    position = result.scalar() or 1

    # Get doctor's avg consultation time (default 15 min)
    doc_stmt = select(Doctor).where(Doctor.doctor_id == doctor_id)
    doc_result = await db.execute(doc_stmt)
    doctor = doc_result.scalars().first()

    avg_time = 15  # default
    if doctor and doctor.consultation_fee:
        # Use a simple heuristic: higher fee = more thorough = slightly longer
        avg_time = 15

    # patients_ahead * avg_time
    wait = max(0, (position - 1)) * avg_time
    return wait


async def get_doctor_queue(db: AsyncSession, doctor_id: str) -> list[dict]:
    """Get the dynamically sorted queue for a doctor."""
    # Coerce doctor_id to UUID if it's a string
    if isinstance(doctor_id, str):
        doctor_id = uuid.UUID(doctor_id)
    
    stmt = (
        select(
            Queue,
            Patient.patient_id,
            Patient.full_name,
            Patient.age,
            Patient.gender,
            Patient.symptoms,
            Patient.risk_level,
            Visit.status,
        )
        .join(Visit, Queue.visit_id == Visit.visit_id)
        .join(Patient, Visit.patient_id == Patient.patient_id)
        .where(Queue.doctor_id == doctor_id)
        .order_by(Queue.priority_score.desc(), Queue.queue_position.asc())
    )
    result = await db.execute(stmt)
    # result is rows of (Queue, full_name, age, gender, symptoms, risk_level)
    rows = result.all()

    queue_list = []
    for i, row in enumerate(rows, 1):
        queue_entry = row[0]
        patient_id = row[1]
        full_name = row[2]
        age = row[3]
        gender = row[4]
        symptoms = row[5]
        risk_level = row[6]
        visit_status = row[7]

        now = datetime.now(timezone.utc)
        entered = queue_entry.last_updated or now
        if entered.tzinfo is None:
            entered = entered.replace(tzinfo=timezone.utc)
        waiting_mins = int((now - entered).total_seconds() / 60)

        # Enhanced Wait-Time Priority Boost
        # After 30 min: +2 points per 15 min
        wait_boost = 0
        if waiting_mins > 30:
            excess_wait = waiting_mins - 30
            wait_boost = (excess_wait // 15) * 2
        
        dynamic_score = queue_entry.priority_score + wait_boost

        queue_list.append({
            "queue_id": str(queue_entry.queue_id),
            "visit_id": str(queue_entry.visit_id),
            "patient_id": str(patient_id) if patient_id else None,
            "patient_name": full_name or "Unknown",
            "age": age,
            "gender": gender,
            "symptoms": symptoms,
            "risk_level": risk_level,
            "priority_score": queue_entry.priority_score,
            "wait_time_boost": wait_boost,
            "dynamic_score": dynamic_score,
            "queue_position": queue_entry.queue_position,
            "is_emergency": queue_entry.is_emergency,
            "waiting_minutes": waiting_mins,
            "visit_status": visit_status,
            # Placeholder for position, to be re-calculated
            "position": 0
        })

    # Re-sort by dynamic score
    queue_list.sort(key=lambda x: x["dynamic_score"], reverse=True)
    
    # Update position based on dynamic sort
    for i, item in enumerate(queue_list, 1):
        item["position"] = i

    return queue_list


async def reorder_queue_for_doctor(db: AsyncSession, doctor_id: str) -> list[dict]:
    """Recompute dynamic queue ordering, persist positions, and broadcast updates."""
    queue_list = await get_doctor_queue(db, doctor_id)
    for item in queue_list:
        # Convert queue_id from string back to UUID for database query
        queue_id_uuid = uuid.UUID(item["queue_id"])
        await db.execute(
            update(Queue)
            .where(Queue.queue_id == queue_id_uuid)
            .values(
                queue_position=item["position"],
                wait_time_boost=item.get("wait_time_boost", 0),
            )
        )
    try:
        await notify_doctor_queue_update(doctor_id, {
            "event": "queue_reordered",
            "queue": queue_list,
        })
    except Exception:
        pass
    return queue_list
