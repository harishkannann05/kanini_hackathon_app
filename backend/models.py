"""
SQLAlchemy ORM Models — Mapped to the actual schema in schema_full.sql.
SQLite is the default runtime backend.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, ForeignKey,
    TIMESTAMP, Numeric, Uuid
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import JSON as JSON_TYPE
import uuid
from datetime import datetime


class Base(DeclarativeBase):
    pass


# ── Users ──────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Departments ────────────────────────────────────────────────
class Department(Base):
    __tablename__ = "departments"

    department_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Doctors ────────────────────────────────────────────────────
class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), unique=True)
    department_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("departments.department_id"), nullable=True)
    specialization: Mapped[str] = mapped_column(String, nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=True)
    consultation_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    max_daily_patients: Mapped[int] = mapped_column(Integer, default=50)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Patients ───────────────────────────────────────────────────
class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String, nullable=False)
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)
    blood_pressure: Mapped[str] = mapped_column(String, nullable=False)
    heart_rate: Mapped[int] = mapped_column(Integer, nullable=False)
    temperature: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    pre_existing_conditions: Mapped[str] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Visits ─────────────────────────────────────────────────────
class Visit(Base):
    __tablename__ = "visits"

    visit_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("patients.patient_id"), nullable=True)
    visit_type: Mapped[str] = mapped_column(String, nullable=True)
    arrival_time: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    status: Mapped[str] = mapped_column(String, default="Waiting")
    emergency_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    waiting_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)


# ── AI Assessments ─────────────────────────────────────────────
class AIAssessment(Base):
    __tablename__ = "ai_assessments"

    assessment_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    visit_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("visits.visit_id"))
    risk_score: Mapped[int] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[str] = mapped_column(String, nullable=True)
    recommended_department: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("departments.department_id"), nullable=True)
    shap_explanation: Mapped[dict] = mapped_column(JSON_TYPE, nullable=True)
    model_version: Mapped[str] = mapped_column(String, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Priority Rules ─────────────────────────────────────────────
class PriorityRule(Base):
    __tablename__ = "priority_rules"

    rule_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    condition_name: Mapped[str] = mapped_column(String(200), nullable=False)
    base_priority: Mapped[int] = mapped_column(Integer, nullable=True)
    department_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("departments.department_id"), nullable=True)
    emergency_override: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Symptom Severity ───────────────────────────────────────────
class SymptomSeverity(Base):
    __tablename__ = "symptom_severity"
    
    symptom_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    symptom_name: Mapped[str] = mapped_column(String(200))
    base_severity: Mapped[int] = mapped_column(Integer, nullable=True)
    emergency_trigger: Mapped[bool] = mapped_column(Boolean, default=False)
    associated_department: Mapped[str] = mapped_column(String(100), nullable=True)
    typical_duration_days: Mapped[int] = mapped_column(Integer, nullable=True)


# ── Vital Signs Reference ──────────────────────────────────────
class VitalSignReference(Base):
    __tablename__ = "vital_signs_reference"

    vital_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    vital_type: Mapped[str] = mapped_column(String(100))
    age_group: Mapped[str] = mapped_column(String(50), nullable=True)
    condition_modifier: Mapped[str] = mapped_column(String(100), nullable=True)
    critical_low_threshold: Mapped[float] = mapped_column(Numeric, nullable=True)
    critical_high_threshold: Mapped[float] = mapped_column(Numeric, nullable=True)
    moderate_low_threshold: Mapped[float] = mapped_column(Numeric, nullable=True)
    moderate_high_threshold: Mapped[float] = mapped_column(Numeric, nullable=True)
    critical_instability_score: Mapped[int] = mapped_column(Integer, nullable=True)
    moderate_instability_score: Mapped[int] = mapped_column(Integer, nullable=True)


# ── Chronic Conditions ─────────────────────────────────────────
class ChronicCondition(Base):
    __tablename__ = "chronic_conditions"

    chronic_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    chronic_condition: Mapped[str] = mapped_column(String(200))
    risk_modifier_score: Mapped[int] = mapped_column(Integer, nullable=True)
    high_risk_with_symptoms: Mapped[str] = mapped_column(Text, nullable=True)
    associated_department: Mapped[str] = mapped_column(String(100), nullable=True)
    complication_risk_level: Mapped[str] = mapped_column(String(50), nullable=True)


# ── Doctor Assignments ─────────────────────────────────────────
class DoctorAssignment(Base):
    __tablename__ = "doctor_assignments"

    assignment_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    visit_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("visits.visit_id"))
    doctor_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("doctors.doctor_id"))
    assigned_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


# ── Patient Doctor Preference ─────────────────────────────────
class PatientPreference(Base):
    __tablename__ = "patient_preferences"

    preference_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("patients.patient_id"))
    preferred_doctor: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("doctors.doctor_id"))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Queue ──────────────────────────────────────────────────────
class Queue(Base):
    __tablename__ = "queue"

    queue_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    visit_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("visits.visit_id"))
    doctor_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("doctors.doctor_id"), nullable=True)
    priority_score: Mapped[int] = mapped_column(Integer)
    queue_position: Mapped[int] = mapped_column(Integer, nullable=True)
    waiting_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    wait_time_boost: Mapped[int] = mapped_column(Integer, default=0)
    is_emergency: Mapped[bool] = mapped_column(Boolean, default=False)
    last_updated: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Medical Records ────────────────────────────────────────────
class MedicalRecord(Base):
    __tablename__ = "medical_records"

    record_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    visit_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("visits.visit_id"))
    doctor_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("doctors.doctor_id"), nullable=True)
    diagnosis: Mapped[str] = mapped_column(Text, nullable=True)
    syndrome_identified: Mapped[str] = mapped_column(Text, nullable=True)
    treatment_plan: Mapped[str] = mapped_column(Text, nullable=True)
    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False)
    follow_up_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True) 
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Prescriptions ──────────────────────────────────────────────
class Prescription(Base):
    __tablename__ = "prescriptions"

    prescription_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    record_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("medical_records.record_id"))
    medication_name: Mapped[str] = mapped_column(String(200), nullable=True)
    dosage: Mapped[str] = mapped_column(String(100), nullable=True)
    frequency: Mapped[str] = mapped_column(String(100), nullable=True)
    duration: Mapped[str] = mapped_column(String(100), nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=True)


# ── Disease Priority (Dataset) ─────────────────────────────────
class DiseasePriority(Base):
    __tablename__ = "disease_priority"

    condition_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    condition_name: Mapped[str] = mapped_column(String(200), nullable=True)
    condition_category: Mapped[str] = mapped_column(String(100), nullable=True)
    base_severity_score: Mapped[int] = mapped_column(Integer, nullable=True)
    default_department: Mapped[str] = mapped_column(String(100), nullable=True)
    emergency_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    contagious_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    max_recommended_wait_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    mortality_risk_level: Mapped[str] = mapped_column(String(50), nullable=True)
    progression_speed: Mapped[str] = mapped_column(String(50), nullable=True)


# ── Chronic Condition Modifiers (Dataset) ──────────────────────
class ChronicConditionModifier(Base):
    __tablename__ = "chronic_condition_modifiers"

    chronic_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    chronic_condition: Mapped[str] = mapped_column(String(200), nullable=True)
    risk_modifier_score: Mapped[int] = mapped_column(Integer, nullable=True)
    high_risk_with_symptoms: Mapped[str] = mapped_column(Text, nullable=True)
    associated_department: Mapped[str] = mapped_column(String(100), nullable=True)
    complication_risk_level: Mapped[str] = mapped_column(String(50), nullable=True)


# ── Doctor Specialization (Dataset) ────────────────────────────
class DoctorSpecialization(Base):
    __tablename__ = "doctor_specialization"

    doctor_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    specialization: Mapped[str] = mapped_column(String(100), nullable=True)
    subspecialty: Mapped[str] = mapped_column(String(100), nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=True)
    max_patients_per_hour: Mapped[int] = mapped_column(Integer, nullable=True)
    critical_case_certified: Mapped[bool] = mapped_column(Boolean, default=False)
    performance_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    preferred_case_types: Mapped[str] = mapped_column(Text, nullable=True)
    consultation_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    availability_hours_per_week: Mapped[int] = mapped_column(Integer, nullable=True)


# ── Focused Patient Dataset (Dataset) ──────────────────────────
class FocusedPatientDataset(Base):
    __tablename__ = "focused_patient_dataset"

    patient_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    symptoms: Mapped[str] = mapped_column(Text, nullable=True)
    blood_pressure: Mapped[str] = mapped_column(String(20), nullable=True)
    heart_rate: Mapped[int] = mapped_column(Integer, nullable=True)
    temperature: Mapped[float] = mapped_column(Numeric(4, 2), nullable=True)
    pre_existing_conditions: Mapped[str] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=True)


# Backwards-compatible alias
VitalSignsReference = VitalSignReference


# ── Documents ──────────────────────────────────────────────────
class Document(Base):
    __tablename__ = "documents"

    document_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("patients.patient_id"))
    visit_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("visits.visit_id"), nullable=True)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=True)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Whatsapp Bookings ──────────────────────────────────────────
class WhatsappBooking(Base):
    __tablename__ = "whatsapp_bookings"

    booking_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("patients.patient_id"), nullable=True)
    symptoms: Mapped[str] = mapped_column(Text, nullable=True)
    triage_risk_score: Mapped[int] = mapped_column(Integer, nullable=True)
    assigned_department: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("departments.department_id"), nullable=True)
    assigned_doctor: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("doctors.doctor_id"), nullable=True)
    booking_status: Mapped[str] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Emergency Alerts ───────────────────────────────────────────
class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"

    alert_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    visit_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("visits.visit_id"))
    triggered_by: Mapped[str] = mapped_column(String(50), nullable=True)
    alert_message: Mapped[str] = mapped_column(Text, nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Notifications ──────────────────────────────────────────────
class Notification(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


# ── Audit Logs ─────────────────────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=True)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    target_table: Mapped[str] = mapped_column(String(100), nullable=True)
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
