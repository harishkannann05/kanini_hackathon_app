"""
Queue Management API Routes - Reordering and Admin Controls
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import get_db
from models import Queue
from services.queue_service import reorder_queue_for_doctor
from datetime import datetime, timezone

router = APIRouter(prefix="/queue", tags=["Queue Management"])


@router.post("/recompute")
async def recompute_queue_priorities(
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger queue priority recomputation for all doctors.
    Applies wait-time boost to all queued patients and broadcasts updates.
    Admin-only endpoint.
    """
    try:
        async with db.begin():
            # Get all unique doctors with queue entries
            stmt = select(Queue.doctor_id).distinct()
            result = await db.execute(stmt)
            doctor_ids = [str(row[0]) for row in result.all()]
            
            recomputed_count = 0
            for doctor_id in doctor_ids:
                queue_list = await reorder_queue_for_doctor(db, doctor_id)
                recomputed_count += len(queue_list)
            
            return {
                "success": True,
                "recomputed_entries": recomputed_count,
                "doctors_affected": len(doctor_ids)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doctor_id}")
async def get_doctor_queue_endpoint(
    doctor_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the dynamically sorted queue for a specific doctor.
    Returns queue with wait-time boost applied.
    """
    try:
        queue_list = await reorder_queue_for_doctor(db, doctor_id)
        return {"queue": queue_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
