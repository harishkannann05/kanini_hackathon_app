"""
Complete initialization script (SQLite):
1. Create all tables
2. Import all datasets
3. Seed departments and doctors
4. Build cache mappings

Run from repository root: python -m backend.scripts.full_init
"""
import asyncio
import os
import sys
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

os.environ["USE_SQLITE"] = "1"

from dotenv import load_dotenv
load_dotenv(ROOT / "backend" / ".env")

from backend.db import engine, AsyncSessionLocal
from backend.models import Base, Department, Doctor
from sqlalchemy import func, select
from backend.scripts.import_datasets import run_import

# For backend (from backend/ as root)
sys.path.insert(0, str(ROOT / "backend"))


async def create_tables():
    """Create all ORM tables in SQLite."""
    print("\n" + "="*70)
    print("STEP 1: Creating all tables in SQLite...")
    print("="*70)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ All tables created successfully!")


async def seed_departments_and_doctors():
    """Seed basic departments and doctors."""
    print("\n" + "="*70)
    print("STEP 2: Seeding departments and doctors...")
    print("="*70)
    
    DEPARTMENTS = [
        "Cardiology",
        "Neurology",
        "Pulmonology",
        "Gastroenterology",
        "General Medicine",
        "Emergency",
        "Orthopedics",
        "Endocrinology",
    ]
    
    DOCTORS = [
        ("Cardiologist", "Cardiology", 15),
        ("Cardiac Surgeon", "Cardiology", 20),
        ("Neurologist", "Neurology", 12),
        ("Neuro Surgeon", "Neurology", 18),
        ("Pulmonologist", "Pulmonology", 10),
        ("Respiratory Specialist", "Pulmonology", 8),
        ("Gastroenterologist", "Gastroenterology", 14),
        ("General Physician", "General Medicine", 10),
        ("Family Medicine", "General Medicine", 7),
        ("Emergency Physician", "Emergency", 12),
        ("ER Specialist", "Emergency", 9),
        ("Orthopedic Surgeon", "Orthopedics", 16),
        ("Endocrinologist", "Endocrinology", 11),
    ]
    
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Check if already seeded
            result = await session.execute(select(func.count()).select_from(Department))
            count = result.scalar() or 0
            
            if count > 0:
                print(f"Departments already seeded ({count} found). Skipping.")
            else:
                dept_map = {}
                
                # Create departments
                for dept_name in DEPARTMENTS:
                    dept = Department(
                        department_id=str(uuid.uuid4()),
                        name=dept_name,
                    )
                    session.add(dept)
                    dept_map[dept_name] = dept
                
                await session.flush()
                print(f"✓ Created {len(DEPARTMENTS)} departments")
                
                # Create doctors
                for spec, dept_name, exp in DOCTORS:
                    dept = dept_map.get(dept_name)
                    if dept:
                        doctor = Doctor(
                            doctor_id=str(uuid.uuid4()),
                            specialization=spec,
                            department_id=dept.department_id,
                            experience_years=exp,
                            is_available=True,
                            consultation_fee=500.0,
                            max_daily_patients=20,
                        )
                        session.add(doctor)
                
                await session.flush()
                print(f"✓ Created {len(DOCTORS)} doctors")


async def import_datasets():
    """Import all CSV datasets."""
    print("\n" + "="*70)
    print("STEP 3: Importing datasets from dataset2/...")
    print("="*70)
    await run_import(force=True)


async def verify_data():
    """Verify data was imported."""
    print("\n" + "="*70)
    print("STEP 4: Verifying imported data...")
    print("="*70)
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy import func
        from backend.models import (
            Department, Doctor, DiseasePriority, SymptomSeverity,
            VitalSignReference, ChronicConditionModifier, DoctorSpecialization,
            FocusedPatientDataset
        )
        
        tables = [
            ("departments", Department),
            ("doctors", Doctor),
            ("disease_priority", DiseasePriority),
            ("symptom_severity", SymptomSeverity),
            ("vital_signs_reference", VitalSignReference),
            ("chronic_condition_modifiers", ChronicConditionModifier),
            ("doctor_specialization", DoctorSpecialization),
            ("focused_patient_dataset", FocusedPatientDataset),
        ]
        
        for table_name, model in tables:
            result = await session.execute(select(func.count()).select_from(model))
            count = result.scalar() or 0
            print(f"  {table_name}: {count} rows")


async def main():
    """Run all initialization steps."""
    try:
        print("\n" + "█"*70)
        print("█  KANINI HOSPITAL TRIAGE SYSTEM - FULL INITIALIZATION")
        print("█"*70)
        
        await create_tables()
        await seed_departments_and_doctors()
        await import_datasets()
        await verify_data()
        
        print("\n" + "█"*70)
        print("█  ✓ INITIALIZATION COMPLETE!")
        print("█"*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
