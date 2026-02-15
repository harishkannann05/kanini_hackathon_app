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

class PatientResponse(BaseModel):
    patient_id: str
    full_name: Optional[str]
    age: int
    gender: str
    phone_number: Optional[str]
    risk_level: Optional[str]

@router.get("/patients/search", response_model=List[PatientResponse])
async def search_patients(q: str, db: AsyncSession = Depends(get_db)):
    """Search patients by name or phone."""
    async with db.begin():
        stmt = select(Patient).where(
            or_(
                Patient.full_name.ilike(f"%{q}%"),
                Patient.phone_number.ilike(f"%{q}%")
            )
        )
        result = await db.execute(stmt)
        patients = result.scalars().all()
        return [
            {
                "patient_id": str(p.patient_id),
                "full_name": p.full_name,
                "age": p.age,
                "gender": p.gender,
                "phone_number": p.phone_number,
                "risk_level": p.risk_level
            }
            for p in patients
        ]

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
