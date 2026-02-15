from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from db import get_db
from models import Queue, Visit, DoctorAssignment, AuditLog, MedicalRecord
from services.ws_manager import manager as ws_manager
from schemas import ServeRequest, MedicalRecordCreate
from services.queue_service import reorder_queue_for_doctor
from services.preference_service import record_doctor_preference
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/doctor", tags=["Doctor"])

@router.get("/queue/{doctor_id}")
async def get_doctor_queue_endpoint(doctor_id: str, db: AsyncSession = Depends(get_db)):
    """Get active queue for a specific doctor."""
    from services.queue_service import get_doctor_queue # Late import to avoid circular if any
    async with db.begin():
        queue = await get_doctor_queue(db, doctor_id)
        return {"doctor_id": doctor_id, "queue": queue}

@router.post("/queue/{queue_id}/serve")
async def serve_queue_entry(queue_id: str, req: ServeRequest, db: AsyncSession = Depends(get_db)):
    """Start or complete a consultation."""
    async with db.begin():
        stmt = select(Queue).where(Queue.queue_id == queue_id)
        result = await db.execute(stmt)
        entry = result.scalars().first()
        if not entry:
            raise HTTPException(status_code=404, detail="Queue entry not found")

        if req.action == "start":
            await db.execute(
                update(Visit).where(Visit.visit_id == entry.visit_id).values(status="In Consultation")
            )
        elif req.action == "complete":
            await db.execute(
                update(Visit).where(Visit.visit_id == entry.visit_id).values(
                    status="Completed",
                    completed_at=datetime.now(timezone.utc)
                )
            )
            # Deactivate assignment
            await db.execute(
                update(DoctorAssignment)
                .where(DoctorAssignment.visit_id == entry.visit_id)
                .values(is_active=False)
            )
            # Remove from queue
            await db.execute(delete(Queue).where(Queue.queue_id == entry.queue_id))

            # Record patient preference for this doctor if possible
            visit_stmt = select(Visit.patient_id).where(Visit.visit_id == entry.visit_id)
            visit_res = await db.execute(visit_stmt)
            patient_id = visit_res.scalar_one_or_none()
            if patient_id and entry.doctor_id:
                await record_doctor_preference(db, str(patient_id), str(entry.doctor_id))
        
        # Audit Log
        audit = AuditLog(
            log_id=uuid.uuid4(),
            action=f"queue_{req.action}",
            target_table="queue",
            target_id=uuid.UUID(queue_id)
        )
        db.add(audit)

        if entry.doctor_id:
            queue_list = await reorder_queue_for_doctor(db, str(entry.doctor_id))
            await ws_manager.broadcast_to_doctor(str(entry.doctor_id), {
                "event": f"queue_{req.action}",
                "queue_id": queue_id,
                "visit_id": str(entry.visit_id),
                "action": req.action,
                "queue": queue_list,
            })
            
    return {"status": "ok", "queue_id": queue_id, "action": req.action}


@router.post("/visits/{visit_id}/record")
async def create_medical_record(
    visit_id: str,
    payload: MedicalRecordCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a consultation record for a visit."""
    follow_up_date = None
    if payload.follow_up_date:
        try:
            follow_up_date = datetime.fromisoformat(payload.follow_up_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid follow_up_date format")

    async with db.begin():
        record = MedicalRecord(
            record_id=uuid.uuid4(),
            visit_id=visit_id,
            doctor_id=payload.doctor_id,
            diagnosis=payload.diagnosis,
            syndrome_identified=payload.syndrome_identified,
            treatment_plan=payload.treatment_plan,
            follow_up_required=payload.follow_up_required,
            follow_up_date=follow_up_date,
            notes=payload.notes,
        )
        db.add(record)
        await db.flush()

        audit = AuditLog(
            log_id=uuid.uuid4(),
            action="medical_record_created",
            target_table="medical_records",
            target_id=record.record_id
        )
        db.add(audit)

    return {"status": "ok", "record_id": str(record.record_id)}
