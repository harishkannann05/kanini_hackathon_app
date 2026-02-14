"""
Hybrid Database Migration Script
- Works with both SQLite (local) and PostgreSQL (Supabase)
- Creates tables and imports datasets
- Can be run in both environments

Usage:
  For SQLite (local):   SET USE_SQLITE=1 && python -m backend.scripts.migrate_db
  For PostgreSQL (prod): SET USE_SQLITE=0 && python -m backend.scripts.migrate_db
"""
import asyncio
import os
import sys
from pathlib import Path
import uuid
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import func, select

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

# Load env
load_dotenv(ROOT / "backend" / ".env")

from backend.db import engine, AsyncSessionLocal, USE_SQLITE
from backend.models import Base, Department, Doctor
from backend.models import (
    DiseasePriority, SymptomSeverity, VitalSignReference,
    ChronicConditionModifier, DoctorSpecialization, FocusedPatientDataset
)

DATA_DIR = ROOT / "dataset2"
CACHE_FILE = ROOT / "backend" / "data_cache.json"


async def create_tables():
    """Create all ORM tables."""
    print("\n[1/5] Creating database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        db_type = "SQLite" if USE_SQLITE else "PostgreSQL"
        print(f"[OK] Tables created in {db_type}")
        return True
    except Exception as e:
        print(f"✗ Failed to create tables: {e}")
        return False


async def seed_departments_and_doctors():
    """Seed basic departments and doctors."""
    print("\n[2/5] Seeding departments and doctors...")
    
    DEPARTMENTS = [
        "Cardiology", "Neurology", "Pulmonology", "Gastroenterology",
        "General Medicine", "Emergency", "Orthopedics", "Endocrinology"
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
    
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Check if already seeded
                result = await session.execute(select(func.count()).select_from(Department))
                count = result.scalar() or 0
                
                if count > 0:
                    print(f"[OK] Departments already seeded ({count} found)")
                    return True
                
                # Create departments
                dept_map = {}
                for dept_name in DEPARTMENTS:
                    dept = Department(
                        department_id=str(uuid.uuid4()),
                        name=dept_name,
                    )
                    session.add(dept)
                    dept_map[dept_name] = dept
                
                await session.flush()
                print(f"  -> Created {len(DEPARTMENTS)} departments")
                
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
                print(f"  -> Created {len(DOCTORS)} doctors")
        
        print("[OK] Departments and doctors seeded")
        return True
    except Exception as e:
        print(f"✗ Failed to seed: {e}")
        return False


async def import_table(df: pd.DataFrame, model_cls, mapping: dict, session):
    """Import dataframe rows into table."""
    rows = []
    for _, r in df.iterrows():
        kwargs = {}
        for col, attr in mapping.items():
            val = r.get(col)
            if pd.isna(val):
                val = None
            if isinstance(val, str):
                vlow = val.strip().lower()
                if vlow in ("true", "yes", "y", "1"):
                    val = True
                elif vlow in ("false", "no", "n", "0"):
                    val = False
            kwargs[attr] = val
        rows.append(model_cls(**kwargs))
    if rows:
        session.add_all(rows)
    return len(rows)


async def import_datasets():
    """Import all CSV datasets."""
    print("\n[3/5] Importing dataset CSVs...")
    
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # 1. disease_priority
                print("  -> disease_priority...", end=" ")
                df1 = pd.read_csv(DATA_DIR / "1_disease_priority_10k.csv")
                mapping1 = {
                    "Condition_ID": "condition_id",
                    "Condition_Name": "condition_name",
                    "Condition_Category": "condition_category",
                    "Base_Severity_Score": "base_severity_score",
                    "Default_Department": "default_department",
                    "Emergency_Flag": "emergency_flag",
                    "Contagious_Flag": "contagious_flag",
                    "Max_Recommended_Wait_Time_Minutes": "max_recommended_wait_minutes",
                    "Mortality_Risk_Level": "mortality_risk_level",
                    "Progression_Speed": "progression_speed",
                }
                count1 = await import_table(df1, DiseasePriority, mapping1, session)
                print(f"{count1} rows")

                # 2. symptom_severity
                print("  -> symptom_severity...", end=" ")
                df2 = pd.read_csv(DATA_DIR / "2_symptom_severity_10k.csv")
                mapping2 = {
                    "Symptom_ID": "symptom_id",
                    "Symptom_Name": "symptom_name",
                    "Base_Severity": "base_severity",
                    "Emergency_Trigger": "emergency_trigger",
                    "Associated_Department": "associated_department",
                    "Possible_Linked_Conditions": "possible_linked_conditions",
                    "Typical_Duration_Days": "typical_duration_days",
                }
                count2 = await import_table(df2, SymptomSeverity, mapping2, session)
                print(f"{count2} rows")

                # 3. vital_signs_reference
                print("  -> vital_signs_reference...", end=" ")
                df3 = pd.read_csv(DATA_DIR / "3_vital_signs_reference_10k.csv")
                mapping3 = {
                    "Vital_ID": "vital_id",
                    "Vital_Type": "vital_type",
                    "Age_Group": "age_group",
                    "Condition_Modifier": "condition_modifier",
                    "Critical_Low_Threshold": "critical_low_threshold",
                    "Critical_High_Threshold": "critical_high_threshold",
                    "Moderate_Low_Threshold": "moderate_low_threshold",
                    "Moderate_High_Threshold": "moderate_high_threshold",
                    "Critical_Instability_Score": "critical_instability_score",
                    "Moderate_Instability_Score": "moderate_instability_score",
                }
                count3 = await import_table(df3, VitalSignReference, mapping3, session)
                print(f"{count3} rows")

                # 4. chronic_condition_modifiers
                print("  -> chronic_condition_modifiers...", end=" ")
                df4 = pd.read_csv(DATA_DIR / "4_chronic_condition_modifiers_10k.csv")
                mapping4 = {
                    "Chronic_ID": "chronic_id",
                    "Chronic_Condition": "chronic_condition",
                    "Risk_Modifier_Score": "risk_modifier_score",
                    "High_Risk_With_Symptoms": "high_risk_with_symptoms",
                    "Associated_Department": "associated_department",
                    "Complication_Risk_Level": "complication_risk_level",
                }
                count4 = await import_table(df4, ChronicConditionModifier, mapping4, session)
                print(f"{count4} rows")

                # 5. doctor_specialization
                print("  -> doctor_specialization...", end=" ")
                df5 = pd.read_csv(DATA_DIR / "5_doctor_specialization_10k.csv")
                mapping5 = {
                    "Doctor_ID": "doctor_id",
                    "Specialization": "specialization",
                    "Subspecialty": "subspecialty",
                    "Experience_Years": "experience_years",
                    "Max_Patients_Per_Hour": "max_patients_per_hour",
                    "Critical_Case_Certified": "critical_case_certified",
                    "Performance_Score": "performance_score",
                    "Preferred_Case_Types": "preferred_case_types",
                    "Consultation_Fee": "consultation_fee",
                    "Availability_Hours_Per_Week": "availability_hours_per_week",
                }
                count5 = await import_table(df5, DoctorSpecialization, mapping5, session)
                print(f"{count5} rows")

                # 6. focused_patient_dataset
                print("  → focused_patient_dataset...", end=" ")
                df6 = pd.read_csv(DATA_DIR / "focused_patient_dataset_15k.csv")
                mapping6 = {
                    "Patient_ID": "patient_id",
                    "Age": "age",
                    "Gender": "gender",
                    "Symptoms": "symptoms",
                    "Blood_Pressure": "blood_pressure",
                    "Heart_Rate": "heart_rate",
                    "Temperature": "temperature",
                    "Pre_Existing_Conditions": "pre_existing_conditions",
                    "Risk_Level": "risk_level",
                }
                count6 = await import_table(df6, FocusedPatientDataset, mapping6, session)
                print(f"{count6} rows")
        
        print("✓ All datasets imported successfully")
        return True
    except Exception as e:
        print(f"\n✗ Failed to import datasets: {e}")
        import traceback
        traceback.print_exc()
        return False


async def build_cache():
    """Build symptom->department cache."""
    print("\n[4/5] Building data cache...")
    
    try:
        import json
        async with AsyncSessionLocal() as session:
            stmt = select(SymptomSeverity.symptom_name, SymptomSeverity.associated_department)
            res = await session.execute(stmt)
            mapping = {row[0].strip().lower(): row[1] for row in res if row[0] and row[1]}
        
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"symptom_to_department": mapping}, f, indent=2)
        
        print(f"✓ Cache built with {len(mapping)} symptom mappings")
        return True
    except Exception as e:
        print(f"✗ Failed to build cache: {e}")
        return False


async def verify_data():
    """Verify data counts."""
    print("\n[5/5] Verifying imported data...")
    
    try:
        async with AsyncSessionLocal() as session:
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
            
            total = 0
            for table_name, model in tables:
                result = await session.execute(select(func.count()).select_from(model))
                count = result.scalar() or 0
                total += count
                status = "✓" if count > 0 else "✗"
                print(f"  {status} {table_name}: {count:,} rows")
            
            return total > 0
    except Exception as e:
        print(f"✗ Failed to verify: {e}")
        return False


async def main():
    """Run complete migration."""
    db_type = "SQLite (Local)" if USE_SQLITE else "PostgreSQL (Supabase)"
    print(f"\n{'='*70}")
    print(f"Database Migration - Using: {db_type}")
    print(f"{'='*70}")
    
    steps = [
        ("Creating tables", create_tables),
        ("Seeding departments/doctors", seed_departments_and_doctors),
        ("Importing datasets", import_datasets),
        ("Building cache", build_cache),
        ("Verifying data", verify_data),
    ]
    
    for i, (name, func) in enumerate(steps, 1):
        try:
            result = await func()
            if not result:
                print(f"\nMigration failed at step {i}: {name}")
                return False
        except Exception as e:
            print(f"\nError at step {i} ({name}): {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print(f"\n{'='*70}")
    print("MIGRATION COMPLETE!")
    print(f"{'='*70}\n")
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
