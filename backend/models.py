"""
SQLAlchemy ORM Models — Mapped to ACTUAL Supabase tables.
Schema inspected via information_schema on 2026-02-14.
Do NOT create/drop tables from code.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, ForeignKey,
    TIMESTAMP, SmallInteger, Numeric
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid
from datetime import datetime


class Base(DeclarativeBase):
    pass


# ── Patients ───────────────────────────────────────────────────
class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String)
    symptoms: Mapped[str] = mapped_column(Text)
    blood_pressure: Mapped[str] = mapped_column(String)
    heart_rate: Mapped[int] = mapped_column(Integer)
    temperature: Mapped[float] = mapped_column(Numeric)
    pre_existing_conditions: Mapped[str] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)


# ── Departments ────────────────────────────────────────────────
class Department(Base):
    __tablename__ = "departments"

    department_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)


# ── Visits ─────────────────────────────────────────────────────
class Visit(Base):
    __tablename__ = "visits"

    visit_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("patients.patient_id"), nullable=True)
    visit_type: Mapped[str] = mapped_column(String, nullable=True)
    arrival_time: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)
    status: Mapped[str] = mapped_column(String, default="Waiting", nullable=True)
    emergency_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    waiting_time_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)


# ── AI Assessments ─────────────────────────────────────────────
class AIAssessment(Base):
    __tablename__ = "ai_assessments"

    assessment_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    visit_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("visits.visit_id"), nullable=True)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[str] = mapped_column(String, nullable=True)
    recommended_department: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=True)
    shap_explanation: Mapped[dict] = mapped_column(JSONB, nullable=True)
    model_version: Mapped[str] = mapped_column(String, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Numeric, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)


# ── Doctors ────────────────────────────────────────────────────
class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=True)
    department_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=True)
    specialization: Mapped[str] = mapped_column(String, nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=True)
    consultation_fee: Mapped[float] = mapped_column(Numeric, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    max_daily_patients: Mapped[int] = mapped_column(Integer, default=50, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)


# ── Doctor Assignments ─────────────────────────────────────────
class DoctorAssignment(Base):
    __tablename__ = "doctor_assignments"

    assignment_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    visit_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("visits.visit_id"), nullable=True)
    doctor_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("doctors.doctor_id"), nullable=True)
    assigned_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)


# ── Queue ──────────────────────────────────────────────────────
class Queue(Base):
    __tablename__ = "queue"

    queue_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    visit_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("visits.visit_id"), nullable=True)
    doctor_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("doctors.doctor_id"), nullable=True)
    priority_score: Mapped[int] = mapped_column(Integer)
    queue_position: Mapped[int] = mapped_column(Integer, nullable=True)
    waiting_time_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    is_emergency: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)


# ── Documents (OCR uploads) ───────────────────────────────────
class Document(Base):
    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=True)
    visit_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("visits.visit_id"), nullable=True)
    file_url: Mapped[str] = mapped_column(Text)
    file_type: Mapped[str] = mapped_column(String, nullable=True)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)


# ── Emergency Alerts ──────────────────────────────────────────
class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"

    alert_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    visit_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("visits.visit_id"), nullable=True)
    triggered_by: Mapped[str] = mapped_column(String, nullable=True)
    alert_message: Mapped[str] = mapped_column(Text, nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)


# ── Notifications ─────────────────────────────────────────────
class Notification(Base):
    __tablename__ = "notifications"

    notification_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)


# ── Audit Logs ─────────────────────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=True)
    action: Mapped[str] = mapped_column(Text)
    target_table: Mapped[str] = mapped_column(String, nullable=True)
    target_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=True)
    ip_address: Mapped[str] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=True)
