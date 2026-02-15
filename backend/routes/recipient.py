from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from db import get_db
from models import Patient, User
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter(prefix="/recipient", tags=["Recipient"])

class PatientCreate(BaseModel):
    full_name: str
    age: int
    gender: str
    phone_number: str
    symptoms: str
    blood_pressure: str
    heart_rate: int
    temperature: float
    pre_existing_conditions: Optional[str] = None

class CurrentVisitInfo(BaseModel):
    doctor_name: str
    department: str

class PatientResponse(BaseModel):
    patient_id: str
    full_name: Optional[str]
    age: int
    gender: str
    phone_number: Optional[str]
    risk_level: Optional[str]
    current_visit: Optional[CurrentVisitInfo] = None

@router.get("/patients/search", response_model=List[PatientResponse])
async def search_patients(q: str, db: AsyncSession = Depends(get_db)):
    """Search patients by name or phone and include current active visit info."""
    from models import Visit, DoctorAssignment, Doctor, User, Department
    
    async with db.begin():
        # Find matching patients
        stmt = select(Patient).where(
            or_(
                Patient.full_name.ilike(f"%{q}%"),
                Patient.phone_number.ilike(f"%{q}%")
            )
        )
        result = await db.execute(stmt)
        patients = result.scalars().all()
        
        response_list = []
        for p in patients:
            # Check for active visit
            # "Active" means not Completed and not Cancelled? Or just Assigned?
            # User says: "doctor input diagnosis and finish... should have current visits: except that doctor."
            # So if finished, show None.
            # Visit.status != 'Completed'
            visit_stmt = (
                select(User.full_name, Department.name)
                .select_from(Visit)
                .join(DoctorAssignment, Visit.visit_id == DoctorAssignment.visit_id)
                .join(Doctor, DoctorAssignment.doctor_id == Doctor.doctor_id)
                .join(User, Doctor.user_id == User.user_id)
                .join(Department, Doctor.department_id == Department.department_id)
                .where(
                    Visit.patient_id == p.patient_id,
                    Visit.status != 'Completed',
                    DoctorAssignment.is_active == True
                )
                .order_by(Visit.arrival_time.desc())
                .limit(1)
            )
            v_res = await db.execute(visit_stmt)
            active_visit = v_res.first()
            
            current_visit = None
            if active_visit:
                current_visit = CurrentVisitInfo(
                    doctor_name=f"Dr. {active_visit[0]}" if "Dr." not in active_visit[0] else active_visit[0],
                    department=active_visit[1]
                )

            response_list.append({
                "patient_id": str(p.patient_id),
                "full_name": p.full_name,
                "age": p.age,
                "gender": p.gender,
                "phone_number": p.phone_number,
                "risk_level": p.risk_level,
                "current_visit": current_visit
            })
            
        return response_list

@router.post("/patients", response_model=PatientResponse)
async def create_patient(payload: PatientCreate, db: AsyncSession = Depends(get_db)):
    """Register a new patient."""
    async with db.begin():
        # Check if phone exists? Optional but good practice.
        # For hackathon, just create.
        new_patient = Patient(
            patient_id=uuid.uuid4(),
            full_name=payload.full_name,
            phone_number=payload.phone_number,
            age=payload.age,
            gender=payload.gender,
            symptoms=payload.symptoms,
            blood_pressure=payload.blood_pressure,
            heart_rate=payload.heart_rate,
            temperature=payload.temperature,
            pre_existing_conditions=payload.pre_existing_conditions
        )
        db.add(new_patient)
        await db.flush()
        return {
            "patient_id": str(new_patient.patient_id),
            "full_name": new_patient.full_name,
            "age": new_patient.age,
            "gender": new_patient.gender,
            "phone_number": new_patient.phone_number,
            "risk_level": new_patient.risk_level # None initially
        }
@router.get("/visiting-patients", response_model=List[dict])
async def get_visiting_patients(db: AsyncSession = Depends(get_db)):
    """
    Get list of patients who have been assigned to a doctor.
    Shows Patient Name, Assigned Doctor, Department, and Syndrome/Risk.
    """
    from models import Visit, Patient, DoctorAssignment, Doctor, User, Department, AIAssessment
    from sqlalchemy import desc

    stmt = (
        select(
            Patient.full_name.label("patient_name"),
            Patient.age,
            Patient.gender,
            Patient.symptoms,
            Patient.risk_level,
            User.full_name.label("doctor_name"),
            Department.name.label("department_name"),
            Visit.visit_id,
            Visit.status,
            Visit.arrival_time
        )
        .join(Visit, Visit.patient_id == Patient.patient_id)
        .join(DoctorAssignment, DoctorAssignment.visit_id == Visit.visit_id)
        .join(Doctor, Doctor.doctor_id == DoctorAssignment.doctor_id)
        .join(User, User.user_id == Doctor.user_id)
        .outerjoin(Department, Doctor.department_id == Department.department_id)
        .where(
            DoctorAssignment.is_active == True,
            Visit.status != "Completed" # show active visits
        )
        .order_by(desc(Visit.arrival_time))
    )

    result = await db.execute(stmt)
    rows = result.all()
    
    return [
        {
            "patient_name": row.patient_name,
            "patient_details": f"{row.gender}, {row.age}y",
            "symptoms": row.symptoms, # acting as syndrome details
            "risk_level": row.risk_level,
            "doctor_name": f"Dr. {row.doctor_name}",
            "department": row.department_name,
            "status": row.status,
            "visit_time": row.arrival_time.strftime("%I:%M %p")
        }
        for row in rows
    ]
