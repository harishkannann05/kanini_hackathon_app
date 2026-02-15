"""
Doctor Assignment Service — Finds best available doctor for a department.
Uses UUID-based doctor_id and department_id from the app schema.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import Doctor, DoctorAssignment, Department


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
    1. Check if patient has preference for a doctor in this department
    2. If not, High risk → most experienced available doctor
    3. Medium/Low → least loaded (fewest active assignments)

    Returns: (doctor_id, department_uuid) or (None, None) if no doctor available
    """
    # Look up department UUID
    dept_id = await get_department_id(db, department_name)
    if not dept_id:
        # Fallback: try General Medicine
        dept_id = await get_department_id(db, "General Medicine")
        if not dept_id:
            return None, None

    # 1. Check patient preference first
    if patient_id:
        preferred_doc = await get_patient_preferred_doctor(db, patient_id, dept_id)
        if preferred_doc:
            return preferred_doc, dept_id

    # Count active assignments per doctor in this department
    load_subq = (
        select(
            DoctorAssignment.doctor_id,
            func.count().label("active_count")
        )
        .where(DoctorAssignment.is_active == True)
        .group_by(DoctorAssignment.doctor_id)
        .subquery()
    )

    # Query available doctors in this department
    stmt = (
        select(
            Doctor.doctor_id,
            Doctor.experience_years,
            func.coalesce(load_subq.c.active_count, 0).label("load")
        )
        .outerjoin(load_subq, Doctor.doctor_id == load_subq.c.doctor_id)
        .where(
            Doctor.department_id == dept_id,
            Doctor.is_available == True
        )
    )

    if risk_level == "High":
        # Most experienced first
        stmt = stmt.order_by(Doctor.experience_years.desc(), "load")
    else:
        # Least loaded first
        stmt = stmt.order_by("load", Doctor.experience_years.desc())

    stmt = stmt.limit(1)

    result = await db.execute(stmt)
    row = result.first()

    if not row:
        # Fallback: any available doctor
        fallback = await db.execute(
            select(Doctor.doctor_id)
            .where(Doctor.is_available == True)
            .limit(1)
        )
        fb_row = fallback.scalar_one_or_none()
        return (str(fb_row), dept_id) if fb_row else (None, dept_id)

    return str(row.doctor_id), dept_id
