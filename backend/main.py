"""
Main FastAPI Application — Full orchestration with SHAP explainability.
Aligned with the app schema (SQLite runtime).
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, WebSocket
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
from typing import Optional
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from db import get_db
from db import init_db, USE_SQLITE
from models import (
    Patient, Visit, AIAssessment, DoctorAssignment,
    Queue, AuditLog, EmergencyAlert, Doctor, Department, Document, ChronicCondition
)
from schemas import VisitRequest, VisitResponse, OverrideRequest, ServeRequest
from services.triage_service import run_triage
from services.doctor_service import assign_doctor
from services.queue_service import (
    insert_into_queue, estimate_wait_time, reorder_queue_for_doctor
)
from services.ocr_service import extract_text_from_file, detect_conditions, merge_ocr_with_payload
from services.ws_manager import manager as ws_manager
from services.auth_service import create_user, authenticate_user, get_current_user
from schemas import AuthRegister, AuthLogin
from pydantic import BaseModel
from fastapi import Depends
import jwt
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGO = "HS256"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    await init_db()
    try:
        from scripts.migrate_db import seed_departments_and_doctors
        await seed_departments_and_doctors()
    except Exception as e:
        logger.warning(f"Startup seed skipped: {e}")
    
    logger.info("Application started successfully")
    
    # ML models are auto-loaded when the triage_service module is imported
    
    yield
    
    # Shutdown (if needed)
    logger.info("Shutting down application...")


app = FastAPI(title="AI Smart Patient Triage", version="2.0.0", lifespan=lifespan)

# CORS Configuration - Allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:5175", "http://127.0.0.1:5175"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
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
from services.visit_service import create_visit_orchestration

# ...

@app.post("/visits", response_model=VisitResponse)
async def create_visit(payload: VisitRequest, db: AsyncSession = Depends(get_db)):
    """
    Atomic orchestration via visit_service.
    """
    try:
        async with db.begin():
            payload_dict = payload.model_dump()
            result = await create_visit_orchestration(db, payload_dict)
            
            # Audit Log
            audit = AuditLog(
                log_id=uuid.uuid4(),
                action=f"visit_created - Risk: {result['risk_level']}, Dept: {result['department']}",
                target_table="visits",
                target_id=uuid.UUID(result["visit_id"])
            )
            db.add(audit)
            return result
    except Exception as e:
        logger.error(f"Error creating visit: {e}")
        traceback.print_exc()
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
#  POST /visits/{visit_id}/override — Manual risk override
# ══════════════════════════════════════════════════════════════
@app.post("/visits/{visit_id}/override")
async def override_risk(visit_id: str, req: OverrideRequest, db: AsyncSession = Depends(get_db)):
    # Convert visit_id string to UUID
    try:
        visit_id_uuid = uuid.UUID(visit_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid visit_id format")
    
    async with db.begin():
        stmt = select(AIAssessment).where(AIAssessment.visit_id == visit_id_uuid)
        result = await db.execute(stmt)
        assessment = result.scalars().first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        old_risk = assessment.risk_level
        assessment.risk_level = req.new_risk_level

        # Update queue priority
        queue_stmt = select(Queue).where(Queue.visit_id == visit_id_uuid)
        queue_result = await db.execute(queue_stmt)
        queue_entry = queue_result.scalars().first()
        doctor_id = None
        if queue_entry:
            score_map = {"High": 100, "Medium": 60, "Low": 30}
            queue_entry.priority_score = score_map.get(req.new_risk_level, 30)
            queue_entry.is_emergency = req.new_risk_level == "High"
            doctor_id = str(queue_entry.doctor_id) if queue_entry.doctor_id else None

        audit = AuditLog(
            log_id=str(uuid.uuid4()),
            action="risk_override",
            target_table="ai_assessments",
            target_id=str(visit_id_uuid),
        )
        db.add(audit)

        if doctor_id:
            queue_list = await reorder_queue_for_doctor(db, doctor_id)
            await ws_manager.broadcast_to_doctor(doctor_id, {
                "event": "queue_reordered",
                "queue": queue_list
            })

    return {"status": "ok", "visit_id": str(visit_id_uuid), "old_risk": old_risk, "new_risk": req.new_risk_level}


# ══════════════════════════════════════════════════════════════
#  GET /doctors — List all doctors
# ══════════════════════════════════════════════════════════════
@app.get("/doctors")
async def list_doctors(db: AsyncSession = Depends(get_db)):
    from models import User  # Ensure User is available
    async with db.begin():
        result = await db.execute(
            select(Doctor, Department.name.label("dept_name"), User.full_name, User.email)
            .join(User, Doctor.user_id == User.user_id)
            .outerjoin(Department, Doctor.department_id == Department.department_id)
        )
        rows = result.all()
        return [
            {
                "doctor_id": str(row.Doctor.doctor_id),
                "full_name": row.full_name, # Doctor's real name
                "email": row.email,
                "specialization": row.Doctor.specialization,
                "department_id": str(row.Doctor.department_id) if row.Doctor.department_id else None,
                "department_name": row.dept_name,
                "experience_years": row.Doctor.experience_years,
                "is_available": row.Doctor.is_available,
            }
            for row in rows
        ]


@app.websocket("/ws/doctor/{doctor_id}")
async def websocket_doctor_queue(websocket: WebSocket, doctor_id: str):
    """WebSocket endpoint for doctor-specific live queue updates."""
    await websocket.accept()
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
            select(Visit.visit_id, Visit.status, Visit.arrival_time, Patient.age, Patient.gender, Patient.full_name)
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
                "patient_name": r.full_name,
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
# ── AUTH ENDPOINTS (simple JWT) ─────────────────────────────────
@app.post("/auth/register")
async def register_user_endpoint(req: AuthRegister, db: AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            user = await create_user(
                db,
                req.full_name,
                req.email,
                req.password,
                req.role,
                phone_number=req.phone_number,
                age=req.age,
                gender=req.gender,
                department_id=req.department_id,
                department_name=req.department_name,
                specialization=req.specialization,
                experience_years=req.experience_years,
            )
        return {"status": "ok", **user}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/auth/login")
async def login_user_endpoint(req: AuthLogin, db: AsyncSession = Depends(get_db)):
    auth = await authenticate_user(db, req.email, req.password)
    if not auth:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return auth


@app.get("/auth/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Return the currently authenticated user's profile from token."""
    return current_user


@app.get("/master/symptoms")
async def get_master_symptoms(q: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """Fetch symptom suggestions for autocomplete."""
    from models import SymptomSeverity
    async with db.begin():
        stmt = select(SymptomSeverity)
        if q:
            stmt = stmt.where(SymptomSeverity.symptom_name.ilike(f"%{q}%"))
        stmt = stmt.limit(20)
        result = await db.execute(stmt)
        symptoms = result.scalars().all()
        return [{"name": s.symptom_name, "severity": s.base_severity} for s in symptoms]


@app.get("/master/chronic-conditions")
async def get_master_chronic_conditions(q: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """Fetch chronic condition suggestions for autocomplete."""
    async with db.begin():
        stmt = select(ChronicCondition)
        if q:
            stmt = stmt.where(ChronicCondition.chronic_condition.ilike(f"%{q}%"))
        stmt = stmt.limit(20)
        result = await db.execute(stmt)
        conditions = result.scalars().all()
        return [{"name": c.chronic_condition, "risk_modifier": c.risk_modifier_score} for c in conditions]


@app.get("/departments")
async def list_departments(db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(Department))
        departments = result.scalars().all()
        return [
            {
                "department_id": str(d.department_id),
                "name": d.name,
                "description": d.description,
            }
            for d in departments
        ]


# ── DASHBOARD / STATS ──────────────────────────────────────────
from routes import recipient, doctor, whatsapp, patient, insights, queue_mgmt

app.include_router(recipient.router)
app.include_router(doctor.router)
app.include_router(whatsapp.router)
app.include_router(patient.router)
app.include_router(insights.router)
app.include_router(queue_mgmt.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

