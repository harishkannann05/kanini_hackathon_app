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


async def run_import(force: bool = False):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Skip if already populated (unless force)
            existing = await session.execute("SELECT count(*) FROM disease_priority")
            count = existing.scalar() or 0
            if count > 0 and not force:
                print("Datasets already imported (use force=True to re-import). Skipping.")
                return

            print("Importing datasets from dataset2/ ...")

            # 1. disease_priority
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
            await import_table(df1, DiseasePriority, mapping1, session)

            # 2. symptom_severity
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
            await import_table(df2, SymptomSeverity, mapping2, session)

            # 3. vital_signs_reference
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
            await import_table(df3, VitalSignReference, mapping3, session)

            # 4. chronic_condition_modifiers
            df4 = pd.read_csv(DATA_DIR / "4_chronic_condition_modifiers_10k.csv")
            mapping4 = {
                "Chronic_ID": "chronic_id",
                "Chronic_Condition": "chronic_condition",
                "Risk_Modifier_Score": "risk_modifier_score",
                "High_Risk_With_Symptoms": "high_risk_with_symptoms",
                "Associated_Department": "associated_department",
                "Complication_Risk_Level": "complication_risk_level",
            }
            await import_table(df4, ChronicConditionModifier, mapping4, session)

            # 5. doctor_specialization
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
            await import_table(df5, DoctorSpecialization, mapping5, session)

            # 6. focused_patient_dataset (optional/large)
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
            await import_table(df6, FocusedPatientDataset, mapping6, session)

            print("Committing imported rows...")
        # commit happens on context exit

    # Build a small symptom->department cache to speed triage lookups
    try:
        import sqlalchemy
        from sqlalchemy import select
        from backend.db import AsyncSessionLocal as _ASL
        async with _ASL() as s:
            stmt = select(SymptomSeverity.symptom_name, SymptomSeverity.associated_department)
            res = await s.execute(stmt)
            mapping = {row[0].strip().lower(): row[1] for row in res if row[0]}
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"symptom_to_department": mapping}, f)
        print(f"Wrote mapping cache to {CACHE_FILE}")
    except Exception as e:
        print("Failed to write cache:", e)


if __name__ == "__main__":
    asyncio.run(run_import(force=False))
