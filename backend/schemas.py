"""
Pydantic Schemas — Input validation and API response models.
Aligned with actual Supabase schema.
"""
from pydantic import BaseModel, Field
from typing import Optional


# ── Input ──────────────────────────────────────────────────────
class VisitRequest(BaseModel):
    """Patient intake payload."""
    age: int = Field(ge=0, le=120)
    gender: str
    systolic_bp: int = Field(ge=50, le=300)
    heart_rate: int = Field(ge=30, le=250)
    temperature: float = Field(ge=30.0, le=45.0)
    symptoms: list[str] = []
    chronic_conditions: list[str] = []
    visit_type: str = "Walk-In"
    uploaded_documents: list[str] = []  # file paths for OCR
    patient_id: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    manual_doctor_id: Optional[str] = None
    use_preferred_doctor: bool = True


# ── Output ─────────────────────────────────────────────────────
class VisitResponse(BaseModel):
    """Full response from the /visits endpoint."""
    visit_id: str
    patient_id: str
    risk_level: str
    risk_score: int
    confidence: float
    department: str  # department name for display
    doctor_id: Optional[str] = None
    queue_position: int
    estimated_wait_minutes: int
    shap_explanation: Optional[dict] = None


class OverrideRequest(BaseModel):
    """Manual risk override by a doctor."""
    new_risk_level: str = Field(pattern="^(High|Medium|Low)$")
    reason: str = Field(min_length=5)


class ServeRequest(BaseModel):
    """Start or complete serving a queue entry."""
    action: str = Field(pattern="^(start|complete)$")


class QueueEntry(BaseModel):
    """A single entry in a doctor's queue."""
    queue_id: str
    visit_id: str
    priority_score: int
    dynamic_score: int
    queue_position: int
    is_emergency: bool
    waiting_minutes: int
    position: int


class AuthRegister(BaseModel):
    full_name: str
    email: str
    password: str
    role: str = "Recipient"
    phone_number: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None


class AuthLogin(BaseModel):
    email: str
    password: str


class MedicalRecordCreate(BaseModel):
    doctor_id: Optional[str] = None
    diagnosis: Optional[str] = None
    syndrome_identified: Optional[str] = None
    treatment_plan: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[str] = None
    notes: Optional[str] = None
