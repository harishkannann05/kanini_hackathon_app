"""
API Routes for ML-based patient insights
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from services.ml_insights import extract_key_insights, get_patient_insights_text

router = APIRouter(prefix="/patient", tags=["Patient Insights"])


@router.get("/{patient_id}/insights")
async def get_patient_insights(
    patient_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get ML-extracted insights for a patient's medical history.
    Returns: {chronic_conditions, recent_high_risk, medications, recurring_symptoms, summary}
    """
    try:
        insights = await extract_key_insights(db, patient_id)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{patient_id}/insights/text")
async def get_patient_insights_summary(
    patient_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a formatted text summary of patient insights for quick display.
    """
    try:
        text = await get_patient_insights_text(db, patient_id)
        return {"summary": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
