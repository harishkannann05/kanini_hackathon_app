"""
Helper function to record doctor preference after consultation
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from models import PatientPreference
import uuid


async def record_doctor_preference(
    db: AsyncSession,
    patient_id: str,
    doctor_id: str
):
    """
    Record that a patient has seen a doctor, creating a preference for future visits.
    Updates existing preference if it already exists.
    """
    from sqlalchemy import select, update
    
    # Coerce to UUID
    if isinstance(patient_id, str):
        patient_id = uuid.UUID(patient_id)
    if isinstance(doctor_id, str):
        doctor_id = uuid.UUID(doctor_id)
    
    # Check if preference already exists
    stmt = select(PatientPreference).where(
        PatientPreference.patient_id == patient_id,
        PatientPreference.preferred_doctor == doctor_id
    )
    result = await db.execute(stmt)
    existing = result.scalars().first()
    
    if existing:
        # Update timestamp to mark it as most recent
        await db.execute(
            update(PatientPreference)
            .where(PatientPreference.preference_id == existing.preference_id)
            .values(created_at=func.now())
        )
    else:
        # Create new preference
        new_pref = PatientPreference(
            preference_id=uuid.uuid4(),
            patient_id=patient_id,
            preferred_doctor=doctor_id
        )
        db.add(new_pref)
    
    await db.flush()
