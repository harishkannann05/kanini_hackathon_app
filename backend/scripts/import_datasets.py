"""
Import dataset2 CSV files into the application's DB using SQLAlchemy async session.
Run: python -m backend.scripts.import_datasets (from repository root)
"""
import asyncio
import os
import json
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# allow running as script from repo root
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "dataset2"
CACHE_FILE = Path(__file__).resolve().parents[1] / "data_cache.json"

load_dotenv(ROOT / "backend" / ".env")

from backend.db import AsyncSessionLocal, engine, USE_SQLITE
from backend.models import (
    DiseasePriority, SymptomSeverity, VitalSignReference,
    ChronicConditionModifier, DoctorSpecialization, FocusedPatientDataset
)

async def import_table(df: pd.DataFrame, model_cls, mapping: dict, session):
    """Import dataframe rows into table via ORM."""
    rows = []
    for _, r in df.iterrows():
        kwargs = {}
        for col, attr in mapping.items():
            val = r.get(col)
            # normalize NaN
            if pd.isna(val):
                val = None
            # convert boolean-like strings
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


async def run_import(force: bool = False):
    """Import all CSV datasets into SQLite."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            print("Importing datasets from dataset2/ into SQLite...")

            # 1. disease_priority
            print("Importing disease_priority (1_disease_priority_10k.csv)...")
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
            print(f"  → Inserted {count1} rows into disease_priority")

            # 2. symptom_severity
            print("Importing symptom_severity (2_symptom_severity_10k.csv)...")
            df2 = pd.read_csv(DATA_DIR / "2_symptom_severity_10k.csv")
            mapping2 = {
                "Symptom_ID": "symptom_id",
                "Symptom_Name": "symptom_name",
                "Base_Severity": "base_severity",
                "Emergency_Trigger": "emergency_trigger",
                "Associated_Department": "associated_department",
                # "Possible_Linked_Conditions": "possible_linked_conditions",  # Not in model
                "Typical_Duration_Days": "typical_duration_days",
            }
            count2 = await import_table(df2, SymptomSeverity, mapping2, session)
            print(f"  → Inserted {count2} rows into symptom_severity")

            # 3. vital_signs_reference
            print("Importing vital_signs_reference (3_vital_signs_reference_10k.csv)...")
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
            print(f"  → Inserted {count3} rows into vital_signs_reference")

            # 4. chronic_condition_modifiers
            print("Importing chronic_condition_modifiers (4_chronic_condition_modifiers_10k.csv)...")
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
            print(f"  → Inserted {count4} rows into chronic_condition_modifiers")

            # 5. doctor_specialization
            print("Importing doctor_specialization (5_doctor_specialization_10k.csv)...")
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
            print(f"  → Inserted {count5} rows into doctor_specialization")

            # 6. focused_patient_dataset (optional/large)
            print("Importing focused_patient_dataset (focused_patient_dataset_15k.csv)...")
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
            print(f"  → Inserted {count6} rows into focused_patient_dataset")

            print(f"\nCommitting {count1+count2+count3+count4+count5+count6} total rows...")
        # commit happens on context exit

    print("✓ Dataset import complete!")

    # Build a small symptom->department cache to speed triage lookups
    try:
        from sqlalchemy import select
        async with AsyncSessionLocal() as s:
            stmt = select(SymptomSeverity.symptom_name, SymptomSeverity.associated_department)
            res = await s.execute(stmt)
            mapping = {row[0].strip().lower(): row[1] for row in res if row[0] and row[1]}
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"symptom_to_department": mapping}, f)
        print(f"✓ Wrote symptom→department cache to {CACHE_FILE}")
    except Exception as e:
        print(f"Warning: Failed to write cache: {e}")


if __name__ == "__main__":
    asyncio.run(run_import(force=False))
