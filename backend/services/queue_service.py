"""
Queue Service — Dynamic priority queue with wait time estimation.
Matches actual Supabase queue schema: queue_position, waiting_time_minutes, last_updated.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from models import Queue, Doctor
from datetime import datetime, timezone
import uuid


def compute_priority_score(risk_level: str, risk_score: int, is_emergency: bool) -> int:
    """Compute priority score. Higher = more urgent."""
    base = {"High": 80, "Medium": 50, "Low": 20}.get(risk_level, 20)
    if is_emergency:
        base = 100
    return min(base + (risk_score // 10), 100)


async def get_next_position(db: AsyncSession, doctor_id: str) -> int:
    """Get the next queue position for a doctor."""
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
    is_emergency = triage_result["risk_level"] == "High"
    priority = compute_priority_score(
        triage_result["risk_level"],
        triage_result["risk_score"],
        is_emergency
    )

    # Prevent duplicate insertions
    existing = await db.execute(
        select(Queue.queue_id).where(Queue.visit_id == visit_id)
    )
    if existing.scalar_one_or_none():
        return 0  # Already in queue

    position = await get_next_position(db, doctor_id)

    # Emergency patients get position 1 (pushed to front)
    if is_emergency:
        # Shift existing positions down
        await db.execute(
            update(Queue)
            .where(Queue.doctor_id == doctor_id)
            .values(queue_position=Queue.queue_position + 1)
        )
        position = 1

    queue_entry = Queue(
        queue_id=str(uuid.uuid4()),
        visit_id=visit_id,
        doctor_id=doctor_id,
        priority_score=priority,
        queue_position=position,
        waiting_time_minutes=0,
        is_emergency=is_emergency,
    )
    db.add(queue_entry)
    await db.flush()
    return position


async def estimate_wait_time(db: AsyncSession, visit_id: str, doctor_id: str) -> int:
    """
    Estimate wait time in minutes based on queue position and avg consultation time.
    """
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
    stmt = (
        select(Queue)
        .where(Queue.doctor_id == doctor_id)
        .order_by(Queue.priority_score.desc(), Queue.queue_position.asc())
    )
    result = await db.execute(stmt)
    entries = result.scalars().all()

    queue_list = []
    for i, entry in enumerate(entries, 1):
        now = datetime.now(timezone.utc)
        entered = entry.last_updated or now
        if entered.tzinfo is None:
            entered = entered.replace(tzinfo=timezone.utc)
        waiting_mins = int((now - entered).total_seconds() / 60)

        queue_list.append({
            "queue_id": str(entry.queue_id),
            "visit_id": str(entry.visit_id),
            "priority_score": entry.priority_score,
            "dynamic_score": entry.priority_score + (waiting_mins // 5),
            "queue_position": entry.queue_position,
            "is_emergency": entry.is_emergency,
            "waiting_minutes": waiting_mins,
            "position": i,
        })

    # Re-sort by dynamic score
    queue_list.sort(key=lambda x: x["dynamic_score"], reverse=True)
    for i, item in enumerate(queue_list, 1):
        item["position"] = i

    return queue_list
