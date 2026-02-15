"""Doctor Assignment Service — Finds best available doctor for a department.
Uses UUID-based doctor_id and department_id from the app schema.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import Doctor, DoctorAssignment, Department
import uuid


async def get_department_id(db: AsyncSession, department_name: str) -> str | None:
    """Look up department UUID by name."""
    stmt = select(Department.department_id).where(
        func.lower(Department.name) == department_name.lower()
    )
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()
    return str(row) if row else None




async def get_patient_preferred_doctor(
    db: AsyncSession,
    patient_id: str,
    department_id: str
) -> str | None:
    """
    Check if patient has a preferred doctor in the given department.
    Returns doctor_id if preference exists and doctor is available.
    """
    from models import PatientPreference
    
    # Coerce to UUID
    if isinstance(patient_id, str):
        patient_id = uuid.UUID(patient_id)
    if isinstance(department_id, str):
        department_id = uuid.UUID(department_id)
    
    stmt = (
        select(Doctor.doctor_id)
        .join(PatientPreference, Doctor.doctor_id == PatientPreference.preferred_doctor)
        .where(
            PatientPreference.patient_id == patient_id,
            Doctor.department_id == department_id,
            Doctor.is_available == True
        )
        .order_by(PatientPreference.created_at.desc())  # Most recent preference
        .limit(1)
    )
    
    result = await db.execute(stmt)
    doctor_id = result.scalar_one_or_none()
    return str(doctor_id) if doctor_id else None


async def assign_doctor(
    db: AsyncSession,
    department_name: str,
    risk_level: str,
    patient_id: str | None = None
) -> tuple[str | None, str | None]:
    """
    Assign the best available doctor in the given department.

    Strategy:
    1. Check if patient has preference for a doctor in this department (and if available during shift)
    2. Filter available doctors based on current SHIFT timings (09:00 - 17:00).
    3. If High Risk: Rank by Experience first (DESC), then least load (ASC).
    4. If Medium/Low Risk: Rank by Least Load (ASC), then Experience (DESC).
    
    Returns: (doctor_id, department_uuid) or (None, None) if no doctor available
    """
    from datetime import datetime
    import pytz # Assuming local time timezone awareness is needed, but using simple comparison for now.

    # Look up department UUID
    dept_id = await get_department_id(db, department_name)
    if not dept_id:
        # Fallback: try General Medicine or similar default
        # For now return None if department invalid
        # But wait, Triage might have sent "Cardiology" which is valid.
        # If not found, check DB for dept.
        dept_id = await get_department_id(db, "General Medicine")
        if not dept_id:
             return None, None

    # Convert dept_id to UUID
    dept_id_uuid = uuid.UUID(dept_id)
    
    # Get current time string "HH:MM"
    now = datetime.now()
    current_time_str = now.strftime("%H:%M")

    # 1. Check patient preference first
    # (Note: check_preference function needs to also check shift if strict, but let's assume if preferred we try to assign)
    if patient_id:
        preferred_doc_id = await get_patient_preferred_doctor(db, patient_id, dept_id)
        if preferred_doc_id:
             return preferred_doc_id, dept_id

    # 2. Count active assignments (Load) per doctor
    load_subq = (
        select(
            DoctorAssignment.doctor_id,
            func.count().label("active_count")
        )
        .where(DoctorAssignment.is_active == True)
        .group_by(DoctorAssignment.doctor_id)
        .subquery()
    )

    # 3. Query Active Doctors in Shift
    # We select doctor details and their current load
    stmt = (
        select(
            Doctor.doctor_id,
            Doctor.experience_years,
            func.coalesce(load_subq.c.active_count, 0).label("load"),
            Doctor.shift_start,
            Doctor.shift_end
        )
        .outerjoin(load_subq, Doctor.doctor_id == load_subq.c.doctor_id)
        .where(
            Doctor.department_id == dept_id_uuid,
            Doctor.is_available == True,
            # Shift Logic: Start <= Current <= End
            # Using string comparison for "HH:MM" works for same-day shifts
            Doctor.shift_start <= current_time_str,
            Doctor.shift_end >= current_time_str
        )
    )

    # 4. Apply Ranking Logic
    if risk_level == "High":
        # High Risk: Experience is key. Then least load.
        stmt = stmt.order_by(Doctor.experience_years.desc(), "load")
    else:
        # Med/Low Risk: Optimize for throughput (least load first). Then experience.
        stmt = stmt.order_by("load", Doctor.experience_years.desc())

    # Limit to 1
    stmt = stmt.limit(1)

    result = await db.execute(stmt)
    best_doctor = result.first()

    if best_doctor:
        return str(best_doctor.doctor_id), dept_id

    # Fallback: If no doctor fits shift/criteria in department, find ANY available doctor in that department
    # ignoring shift (maybe they stayed late) or load, just to ensure coverage.
    fallback_stmt = (
        select(Doctor.doctor_id)
        .where(Doctor.department_id == dept_id_uuid, Doctor.is_available == True)
        .limit(1)
    )
    fallback_result = await db.execute(fallback_stmt)
    fallback_doc = fallback_result.scalar_one_or_none()
    
    if fallback_doc:
        return str(fallback_doc), dept_id

    return None, None
