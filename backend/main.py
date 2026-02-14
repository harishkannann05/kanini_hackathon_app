"""
Main FastAPI Application — Full orchestration with SHAP explainability.
Aligned with actual Supabase schema.
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from datetime import datetime, timezone
import uuid
import os
import shutil
import traceback
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from db import get_db
from db import init_db, USE_SQLITE
from models import (
    Patient, Visit, AIAssessment, DoctorAssignment,
    Queue, AuditLog, EmergencyAlert, Doctor, Department, Document
)
from schemas import VisitRequest, VisitResponse, OverrideRequest, ServeRequest
from services.triage_service import run_triage
from services.doctor_service import assign_doctor
from services.queue_service import (
    insert_into_queue, estimate_wait_time, get_doctor_queue
)
from services.ocr_service import extract_text_from_file, detect_conditions, merge_ocr_with_payload
from services.ws_manager import manager as ws_manager
from services.auth_service import create_user, authenticate_user
from pydantic import BaseModel
from fastapi import Depends
import jwt
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGO = "HS256"


class AuthRegister(BaseModel):
    full_name: str
    email: str
    password: str
    role: str = "Recipient"


class AuthLogin(BaseModel):
    email: str
    password: str

app = FastAPI(title="AI Smart Patient Triage", version="2.0.0")


@app.on_event("startup")
async def startup_event():
    # Tables already created by migration script
    # Skip init_db for now to avoid potential issues
    logger.info("Application started successfully")

# ── CORS ───────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve static UI ───────────────────────────────────────────
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)


@app.get("/")
async def serve_ui():
    return FileResponse(os.path.join(TEMPLATES_DIR, "index.html"))


@app.get("/test-ui")
async def serve_test_ui():
    return FileResponse(os.path.join(TEMPLATES_DIR, "simple_test.html"))


# ══════════════════════════════════════════════════════════════
#  POST /visits — Full Orchestration Endpoint
# ══════════════════════════════════════════════════════════════
@app.post("/visits", response_model=VisitResponse)
async def create_visit(payload: VisitRequest, db: AsyncSession = Depends(get_db)):
    """
    Atomic orchestration:
    1. OCR extraction (if files)
    2. Merge extracted data
    3. Create patient
    4. Create visit
    5. AI inference + SHAP
    6. Save AI assessment
    7. Emergency alert (if High)
    8. Assign doctor
    9. Insert into queue
    10. Calculate wait time
    11. Audit log
    """
    try:
      async with db.begin():
        payload_dict = payload.model_dump()

        # ── 1. OCR Processing ──
        ocr_detected = {"chronic_conditions": [], "symptoms": []}
        for doc_path in payload_dict.get("uploaded_documents", []):
            text = extract_text_from_file(doc_path)
            if text:
                detected = detect_conditions(text)
                ocr_detected["chronic_conditions"].extend(detected.get("chronic_conditions", []))
                ocr_detected["symptoms"].extend(detected.get("symptoms", []))

        # ── 2. Merge OCR results ──
        if ocr_detected["chronic_conditions"] or ocr_detected["symptoms"]:
            payload_dict = merge_ocr_with_payload(payload_dict, ocr_detected)

        # ── 3. Create Patient ──
        patient_id = str(uuid.uuid4())
        new_patient = Patient(
            patient_id=patient_id,
            age=payload_dict["age"],
            gender=payload_dict["gender"],
            symptoms=", ".join(payload_dict["symptoms"]),
            blood_pressure=f"{payload_dict['systolic_bp']}/0",
            heart_rate=payload_dict["heart_rate"],
            temperature=payload_dict["temperature"],
            pre_existing_conditions=", ".join(payload_dict["chronic_conditions"]),
        )
        db.add(new_patient)

        # ── 4. Create Visit ──
        visit_id = str(uuid.uuid4())
        new_visit = Visit(
            visit_id=visit_id,
            patient_id=patient_id,
            visit_type=payload_dict["visit_type"],
        )
        db.add(new_visit)
        await db.flush()

        # ── 5. Run AI Triage (with SHAP) ──
        triage_result = run_triage(payload_dict)

        # Update patient risk level
        new_patient.risk_level = triage_result["risk_level"]

        # Update visit emergency flag
        if triage_result["risk_level"] == "High":
            new_visit.emergency_flag = True

        # ── 6. Look up department UUID ──
        dept_name = triage_result["department_name"]
        dept_stmt = select(Department.department_id).where(
            func.lower(Department.name) == dept_name.lower()
        )
        dept_result = await db.execute(dept_stmt)
        dept_uuid = dept_result.scalar_one_or_none()

        # ── 7. Save AI Assessment ──
        new_assessment = AIAssessment(
            assessment_id=str(uuid.uuid4()),
            visit_id=visit_id,
            risk_score=triage_result["risk_score"],
            risk_level=triage_result["risk_level"],
            recommended_department=str(dept_uuid) if dept_uuid else None,
            confidence_score=triage_result["confidence"],
            model_version=triage_result["model_version"],
            shap_explanation=triage_result["shap_explanation"],
        )
        db.add(new_assessment)

        # ── 8. Emergency Alert (if High) ──
        if triage_result["risk_level"] == "High":
            alert = EmergencyAlert(
                alert_id=str(uuid.uuid4()),
                visit_id=visit_id,
                triggered_by="AI",
                alert_message=f"High-risk patient detected. Score: {triage_result['risk_score']}. Department: {dept_name}",
            )
            db.add(alert)

        # ── 9. Assign Doctor ──
        doctor_id, _ = await assign_doctor(db, dept_name, triage_result["risk_level"])

        if doctor_id:
            new_assignment = DoctorAssignment(
                assignment_id=str(uuid.uuid4()),
                visit_id=visit_id,
                doctor_id=doctor_id,
            )
            db.add(new_assignment)

        # ── 10. Insert into Queue ──
        queue_position = 0
        wait_minutes = 0
        if doctor_id:
            queue_position = await insert_into_queue(db, visit_id, doctor_id, triage_result)
            wait_minutes = await estimate_wait_time(db, visit_id, doctor_id)

        # ── 11. Audit Log ──
        audit = AuditLog(
            log_id=str(uuid.uuid4()),
            action="visit_created",
            target_table="visits",
            target_id=visit_id,
        )
        db.add(audit)

      return VisitResponse(
          visit_id=visit_id,
          patient_id=patient_id,
          risk_level=triage_result["risk_level"],
          risk_score=triage_result["risk_score"],
          confidence=triage_result["confidence"],
          department=dept_name,
          doctor_id=doctor_id,
          queue_position=queue_position,
          estimated_wait_minutes=wait_minutes,
          shap_explanation=triage_result["shap_explanation"],
      )
    except Exception as e:
      logger.error(f"POST /visits failed: {traceback.format_exc()}")
      raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════
#  POST /documents/upload — Upload EHR/EMR document
# ══════════════════════════════════════════════════════════════
@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for OCR processing. Returns extracted text and detected conditions."""
    # Save file
    file_path = os.path.join(UPLOADS_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract text
    text = extract_text_from_file(file_path)
    detected = detect_conditions(text) if text else {"chronic_conditions": [], "symptoms": []}

    return {
        "filename": file.filename,
        "extracted_text": text or "",
        "detected_conditions": detected,
        "file_path": file_path,
    }


# ══════════════════════════════════════════════════════════════
#  GET /queue/{doctor_id} — Doctor's active queue
# ══════════════════════════════════════════════════════════════
@app.get("/queue/{doctor_id}")
async def get_queue(doctor_id: str, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        queue = await get_doctor_queue(db, doctor_id)
        return {"doctor_id": doctor_id, "queue": queue}


# ══════════════════════════════════════════════════════════════
#  POST /queue/{queue_id}/serve — Mark consultation start/complete
# ══════════════════════════════════════════════════════════════
@app.post("/queue/{queue_id}/serve")
async def serve_queue_entry(queue_id: str, req: ServeRequest, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        stmt = select(Queue).where(Queue.queue_id == queue_id)
        result = await db.execute(stmt)
        entry = result.scalars().first()
        if not entry:
            raise HTTPException(status_code=404, detail="Queue entry not found")

        if req.action == "start":
            # Update visit status
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
            # Deactivate doctor assignment
            await db.execute(
                update(DoctorAssignment)
                .where(DoctorAssignment.visit_id == entry.visit_id)
                .values(is_active=False)
            )

        audit = AuditLog(
            log_id=str(uuid.uuid4()),
            action=f"queue_{req.action}",
            target_table="queue",
            target_id=queue_id,
        )
        db.add(audit)
        # notify websocket clients if this queue entry belonged to a doctor
        try:
            # load queue entry to find doctor_id
            q_stmt = select(Queue).where(Queue.queue_id == queue_id)
            qres = await db.execute(q_stmt)
            qentry = qres.scalars().first()
            if qentry and qentry.doctor_id:
                await ws_manager.broadcast_to_doctor(str(qentry.doctor_id), {
                    "event": f"queue_{req.action}",
                    "queue_id": queue_id,
                    "visit_id": str(qentry.visit_id),
                    "action": req.action,
                })
        except Exception:
            pass
    return {"status": "ok", "queue_id": queue_id, "action": req.action}


# ══════════════════════════════════════════════════════════════
#  POST /visits/{visit_id}/override — Manual risk override
# ══════════════════════════════════════════════════════════════
@app.post("/visits/{visit_id}/override")
async def override_risk(visit_id: str, req: OverrideRequest, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        stmt = select(AIAssessment).where(AIAssessment.visit_id == visit_id)
        result = await db.execute(stmt)
        assessment = result.scalars().first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        old_risk = assessment.risk_level
        assessment.risk_level = req.new_risk_level

        # Update queue priority
        queue_stmt = select(Queue).where(Queue.visit_id == visit_id)
        queue_result = await db.execute(queue_stmt)
        queue_entry = queue_result.scalars().first()
        if queue_entry:
            score_map = {"High": 100, "Medium": 60, "Low": 30}
            queue_entry.priority_score = score_map.get(req.new_risk_level, 30)
            queue_entry.is_emergency = req.new_risk_level == "High"

        audit = AuditLog(
            log_id=str(uuid.uuid4()),
            action="risk_override",
            target_table="ai_assessments",
            target_id=visit_id,
        )
        db.add(audit)

    return {"status": "ok", "visit_id": visit_id, "old_risk": old_risk, "new_risk": req.new_risk_level}


# ══════════════════════════════════════════════════════════════
#  GET /doctors — List all doctors
# ══════════════════════════════════════════════════════════════
@app.get("/doctors")
async def list_doctors(db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(
            select(Doctor, Department.name.label("dept_name"))
            .outerjoin(Department, Doctor.department_id == Department.department_id)
        )
        rows = result.all()
        return [
            {
                "doctor_id": str(row.Doctor.doctor_id),
                "specialization": row.Doctor.specialization,
                "department_id": str(row.Doctor.department_id) if row.Doctor.department_id else None,
                "department_name": row.dept_name,
                "experience_years": row.Doctor.experience_years,
                "is_available": row.Doctor.is_available,
            }
            for row in rows
        ]


@app.websocket("/ws/doctor/{doctor_id}")
async def websocket_doctor_queue(websocket, doctor_id: str):
    """WebSocket endpoint for doctor-specific live queue updates."""
    try:
        await ws_manager.connect(doctor_id, websocket)
        # upon connection, send a simple hello message
        await websocket.send_json({"event": "connected", "doctor_id": doctor_id})
        # keep the connection open and receive pings
        while True:
            data = await websocket.receive_text()
            # ignore incoming messages; it's a keep-alive channel
            await websocket.send_text('{"event":"ack"}')
    except Exception:
        pass
    finally:
        try:
            await ws_manager.disconnect(doctor_id, websocket)
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
#  GET /stats — Dashboard statistics
# ══════════════════════════════════════════════════════════════
@app.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Dashboard statistics for visualizations."""
    async with db.begin():
        # Risk distribution
        risk_stmt = select(
            AIAssessment.risk_level, func.count().label("count")
        ).group_by(AIAssessment.risk_level)
        risk_result = await db.execute(risk_stmt)
        risk_dist = {row.risk_level: row.count for row in risk_result}

        # Department load
        dept_stmt = select(
            Department.name, func.count(Queue.queue_id).label("count")
        ).outerjoin(Doctor, Department.department_id == Doctor.department_id
        ).outerjoin(Queue, Doctor.doctor_id == Queue.doctor_id
        ).group_by(Department.name)
        dept_result = await db.execute(dept_stmt)
        dept_load = {row.name: row.count for row in dept_result}

        # Total visits
        total_stmt = select(func.count()).select_from(Visit)
        total_result = await db.execute(total_stmt)
        total_visits = total_result.scalar() or 0

        # Recent visits
        recent_stmt = (
            select(Visit.visit_id, Visit.status, Visit.arrival_time, Patient.age, Patient.gender)
            .join(Patient, Visit.patient_id == Patient.patient_id)
            .order_by(Visit.arrival_time.desc())
            .limit(10)
        )
        recent_result = await db.execute(recent_stmt)
        recent = [
            {
                "visit_id": str(r.visit_id),
                "status": r.status,
                "arrival_time": r.arrival_time.isoformat() if r.arrival_time else None,
                "age": r.age,
                "gender": r.gender,
            }
            for r in recent_result
        ]

    return {
        "risk_distribution": risk_dist,
        "department_load": dept_load,
        "total_visits": total_visits,
        "recent_visits": recent,
    }


# ── AUTH ENDPOINTS (simple JWT) ─────────────────────────────────
@app.post("/auth/register")
async def register_user(req: AuthRegister, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        user = await create_user(db, req.full_name, req.email, req.password, req.role)
    return {"status": "ok", **user}


@app.post("/auth/login")
async def login_user(req: AuthLogin, db: AsyncSession = Depends(get_db)):
    auth = await authenticate_user(db, req.email, req.password)
    if not auth:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return auth


def get_current_user(token: str = Depends(lambda: None)):
    # placeholder for dependency wiring in future; keep simple for now
    return None
