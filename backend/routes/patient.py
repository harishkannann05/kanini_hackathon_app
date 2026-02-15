from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import get_db
from models import Patient, Visit, AIAssessment, User
from services.auth_service import get_current_user

router = APIRouter(prefix="/patient", tags=["Patient"])

@router.get("/my-records")
async def get_my_records(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get medical records for the logged-in patient."""
    if current_user["role"] != "Patient":
        raise HTTPException(status_code=403, detail="Not authorized")

    user_id = current_user["user_id"]
    user_full_name = current_user.get("full_name")
    
    async with db.begin():
        # Find patient record linked to user
        stmt = select(Patient).where(Patient.user_id == user_id)
        result = await db.execute(stmt)
        patient = result.scalars().first()
        
        if not patient and user_full_name:
            fallback_stmt = (
                select(Patient)
                .where(Patient.full_name == user_full_name)
                .order_by(Patient.created_at.desc())
                .limit(1)
            )
            fallback_res = await db.execute(fallback_stmt)
            patient = fallback_res.scalars().first()

            if patient:
                patient.user_id = user_id
                await db.flush()

        if not patient:
            return {"status": "no_record", "message": "No medical record linked to this account."}

        # Fetch visits
        v_stmt = select(Visit).where(Visit.patient_id == patient.patient_id).order_by(Visit.arrival_time.desc())
        v_res = await db.execute(v_stmt)
        visits = v_res.scalars().all()
        
        visit_history = []
        for v in visits:
            # Fetch assessment for risk score
            a_stmt = select(AIAssessment).where(AIAssessment.visit_id == v.visit_id)
            a_res = await db.execute(a_stmt)
            assess = a_res.scalars().first()
            
            visit_history.append({
                "visit_id": str(v.visit_id),
                "arrival_time": v.arrival_time,
                "status": v.status,
                "risk_level": assess.risk_level if assess else "N/A",
                "risk_score": assess.risk_score if assess else 0,
                "dept": assess.recommended_department if assess else "General"
            })

        return {
            "status": "found",
            "patient": {
                "full_name": patient.full_name,
                "age": patient.age,
                "gender": patient.gender,
                "blood_pressure": patient.blood_pressure,
                "symptoms": patient.symptoms,
                "pre_existing_conditions": patient.pre_existing_conditions
            },
            "visits": visit_history
        }
