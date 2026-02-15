"""
Script to seed initial data: Admin, 10 Doctors, and 10 Patients.
"""
import asyncio
import os
import sys
import uuid
import random
from datetime import datetime

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import AsyncSessionLocal
from models import User, Doctor, Patient, Department
from services.auth_service import get_password_hash

async def seed_data():
    async with AsyncSessionLocal() as db:
        async with db.begin():
            # 1. Create Admin
            admin_email = "admin@gmail.com"
            # Check if exists
            import sqlalchemy as sa
            stmt = sa.select(User).where(User.email == admin_email)
            res = await db.execute(stmt)
            if not res.scalars().first():
                admin = User(
                    user_id=uuid.uuid4(),
                    full_name="admin",
                    email=admin_email,
                    password_hash=get_password_hash("admin123"),
                    role="Admin",
                    is_active=True
                )
                db.add(admin)
                print(f"Admin created: {admin_email}")

            # 2. Departments
            depts = ["General Medicine", "Cardiology", "Orthopedics", "Pediatrics", "Neurology"]
            dept_ids = []
            for d_name in depts:
                stmt = sa.select(Department).where(Department.name == d_name)
                res = await db.execute(stmt)
                dept = res.scalars().first()
                if not dept:
                    dept = Department(department_id=uuid.uuid4(), name=d_name, description=f"{d_name} Department")
                    db.add(dept)
                    print(f"Created Department: {d_name}")
                dept_ids.append(dept.department_id)

            # 3. Create 10 Doctors
            for i in range(1, 11):
                email = f"doctor{i}@hospital.com"
                stmt = sa.select(User).where(User.email == email)
                res = await db.execute(stmt)
                existing_user = res.scalars().first()
                if not existing_user:
                    u_id = uuid.uuid4()
                    user = User(
                        user_id=u_id,
                        full_name=f"Dr. Smith {i}",
                        email=email,
                        password_hash=get_password_hash("doctor123"),
                        role="Doctor",
                        is_active=True
                    )
                    db.add(user)
                    await db.flush() # Ensure u_id is available
                    
                    doctor = Doctor(
                        doctor_id=uuid.uuid4(),
                        user_id=u_id,
                        department_id=random.choice(dept_ids),
                        specialization="Generalist",
                        experience_years=random.randint(2, 20),
                        consultation_fee=500.0,
                        is_available=True,
                        max_daily_patients=50
                    )
                    db.add(doctor)
                    print(f"Created Doctor: {email}")
                else:
                    # Check if doctor entry exists for this user
                    stmt = sa.select(Doctor).where(Doctor.user_id == existing_user.user_id)
                    res = await db.execute(stmt)
                    if not res.scalars().first():
                        doctor = Doctor(
                            doctor_id=uuid.uuid4(),
                            user_id=existing_user.user_id,
                            department_id=random.choice(dept_ids),
                            specialization="Generalist",
                            experience_years=random.randint(2, 20),
                            consultation_fee=500.0,
                            is_available=True,
                            max_daily_patients=50
                        )
                        db.add(doctor)
                        print(f"Ensured Doctor entry for: {email}")

            # 4. Create 10 Patients
            genders = ["Male", "Female", "Other"]
            symptoms_list = ["Fever", "Cough", "Chest Pain", "Headache", "Abdominal Pain", "Fatigue"]
            risk_levels = ["Low", "Medium", "High"]
            
            for i in range(1, 11):
                phone = f"987654321{i-1}"
                stmt = sa.select(Patient).where(Patient.phone_number == phone)
                res = await db.execute(stmt)
                if not res.scalars().first():
                    patient = Patient(
                        patient_id=uuid.uuid4(),
                        full_name=f"Patient Name {i}",
                        phone_number=phone,
                        age=random.randint(5, 80),
                        gender=random.choice(genders),
                        symptoms=random.choice(symptoms_list),
                        blood_pressure=f"{random.randint(110, 160)}/{random.randint(70, 100)}",
                        heart_rate=random.randint(60, 110),
                        temperature=round(random.uniform(36.5, 39.5), 1),
                        risk_level=random.choice(risk_levels)
                    )
                    db.add(patient)
                    print(f"Created Patient: {patient.full_name}")
                else:
                    print(f"Patient with phone {phone} already exists")

            print("Seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
