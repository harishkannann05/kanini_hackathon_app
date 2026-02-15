from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from models import Patient, Visit, AIAssessment, Department, EmergencyAlert, DoctorAssignment, Doctor
from services.ocr_service import extract_text_from_file, detect_conditions, merge_ocr_with_payload
from services.triage_service import run_triage
from services.doctor_service import assign_doctor
from services.queue_service import insert_into_queue, estimate_wait_time
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

async def create_visit_orchestration(db: AsyncSession, payload_dict: dict):
    """
    Orchestrates the entire visit creation process:
    OCR -> Merge -> Patient -> Visit -> Triage -> Assessment -> Alert -> Assign -> Queue
    """
    
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

    # ── 3. Create or Fetch Patient ──
    if payload_dict.get("patient_id"):
        patient_id = payload_dict["patient_id"]
        # Update mutable fields
        stmt = update(Patient).where(Patient.patient_id == patient_id).values(
            age=payload_dict["age"],
            full_name=payload_dict.get("full_name"),
            phone_number=payload_dict.get("phone_number"),
            symptoms=", ".join(payload_dict["symptoms"]),
            blood_pressure=f"{payload_dict['systolic_bp']}/0",
            heart_rate=payload_dict["heart_rate"],
            temperature=payload_dict["temperature"],
            pre_existing_conditions=", ".join(payload_dict["chronic_conditions"]),
            risk_level="Pending" 
        )
        await db.execute(stmt)
    else:
        patient_id = uuid.uuid4()
        new_patient = Patient(
            patient_id=patient_id,
            age=payload_dict["age"],
            gender=payload_dict["gender"],
            full_name=payload_dict.get("full_name"),
            phone_number=payload_dict.get("phone_number"),
            symptoms=", ".join(payload_dict["symptoms"]),
            blood_pressure=f"{payload_dict['systolic_bp']}/0",
            heart_rate=payload_dict["heart_rate"],
            temperature=payload_dict["temperature"],
            pre_existing_conditions=", ".join(payload_dict["chronic_conditions"]),
        )
        db.add(new_patient)

    # ── 4. Create Visit ──
    visit_id = uuid.uuid4()
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
    if payload_dict.get("patient_id"):
        await db.execute(update(Patient).where(Patient.patient_id == patient_id).values(risk_level=triage_result["risk_level"]))
    else:
        # new_patient is in session but check if it was added
        # It's better to update it via object if available, but for consistency lets query or update object
        # simpler: just execute update to be safe or set on object if we have reference
        # We didn't keep reference if we didn't use locals logic.
        # But we added to db.
        # Just update via stmt is safest or set attribute if we have variable.
        pass 
        # Actually my previous main.py logic used `new_patient.risk_level = ...`
        # Here `new_patient` variable exists in `else` block above.
        # If I use `stmt` it works for both.
        await db.execute(update(Patient).where(Patient.patient_id == patient_id).values(risk_level=triage_result["risk_level"]))
        

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
        assessment_id=uuid.uuid4(),
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
            alert_id=uuid.uuid4(),
            visit_id=visit_id,
            triggered_by="AI",
            alert_message=f"High-risk patient detected. Score: {triage_result['risk_score']}. Department: {dept_name}",
        )
        db.add(alert)

    # ── 9. Assign Doctor ──
    doctor_id = None
    if payload_dict.get("manual_doctor_id"):
        doctor_id = payload_dict["manual_doctor_id"]
        # Verify doctor exists?
    else:
        use_preferred = payload_dict.get("use_preferred_doctor", True)
        doctor_id, _ = await assign_doctor(
            db,
            dept_name,
            triage_result["risk_level"],
            patient_id if use_preferred else None,
        )

    if doctor_id:
        new_assignment = DoctorAssignment(
            assignment_id=uuid.uuid4(),
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

    # Return result
    return {
        "visit_id": str(visit_id),
        "patient_id": str(patient_id),
        "risk_level": triage_result["risk_level"],
        "risk_score": triage_result["risk_score"],
        "confidence": triage_result["confidence"],
        "department": dept_name,
        "doctor_id": str(doctor_id) if doctor_id else None,
        "queue_position": queue_position,
        "estimated_wait_minutes": wait_minutes,
        "shap_explanation": triage_result["shap_explanation"]
    }
