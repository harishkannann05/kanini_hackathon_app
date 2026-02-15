"""Quick seed script for symptoms and chronic conditions"""
import asyncio
import sys
from pathlib import Path
import uuid

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.db import AsyncSessionLocal
from backend.models import SymptomSeverity, ChronicCondition

SYMPTOMS = [
    ("Fever", 7, False, "General Medicine", 7),
    ("Cough", 4, False, "Pulmonology", 14),
    ("Chest Pain", 9, True, "Cardiology", 1),
    ("Headache", 5, False, "Neurology", 7),
    ("Abdominal Pain", 7, False, "Gastroenterology", 7),
    ("Shortness of Breath", 9, True, "Pulmonology", 3),
    ("Dizziness", 6, False, "Neurology", 5),
    ("Nausea", 4, False, "Gastroenterology", 3),
    ("Fatigue", 3, False, "General Medicine", 30),
    ("Joint Pain", 5, False, "Orthopedics", 14),
    ("Back Pain", 5, False, "Orthopedics", 14),
    ("Sore Throat", 3, False, "General Medicine", 7),
    ("Runny Nose", 2, False, "General Medicine", 7),
    ("Vomiting", 6, False, "Gastroenterology", 3),
    ("Diarrhea", 5, False, "Gastroenterology", 5),
    ("Rash", 4, False, "General Medicine", 10),
    ("Swelling", 5, False, "Emergency", 3),
    ("Blurred Vision", 7, False, "Emergency", 1),
    ("Palpitations", 7, False, "Cardiology", 1),
    ("Confusion", 8, True, "Emergency", 1),
    ("Seizure", 10, True, "Emergency", 1),
    ("Severe Bleeding", 10, True, "Emergency", 1),
    ("Difficulty Breathing", 10, True, "Emergency", 1),
    ("Loss of Consciousness", 10, True, "Emergency", 1),
    ("Severe Chest Pain", 10, True, "Emergency", 1),
]

CONDITIONS = [
    ("Diabetes", 8),
    ("Hypertension", 7),
    ("Asthma", 6),
    ("Heart Disease", 9),
    ("COPD", 7),
    ("Kidney Disease", 8),
    ("Liver Disease", 8),
    ("Cancer", 10),
    ("HIV/AIDS", 9),
    ("Stroke History", 9),
    ("Epilepsy", 7),
    ("Arthritis", 4),
    ("Obesity", 5),
    ("Anemia", 5),
    ("Thyroid Disorder", 4),
]

async def seed_data():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Check if already seeded
            from sqlalchemy import select, func
            count = await session.scalar(select(func.count()).select_from(SymptomSeverity))
            if count > 0:
                print(f"Symptoms already seeded ({count} found). Skipping.")
            else:
                print(f"Seeding {len(SYMPTOMS)} symptoms...")
                for name, severity, emergency, dept, duration in SYMPTOMS:
                    symptom = SymptomSeverity(
                        symptom_id=uuid.uuid4(),
                        symptom_name=name,
                        base_severity=severity,
                        emergency_trigger=emergency,
                        associated_department=dept,
                        typical_duration_days=duration
                    )
                    session.add(symptom)
                print(f"✓ Seeded {len(SYMPTOMS)} symptoms")
            
            count2 = await session.scalar(select(func.count()).select_from(ChronicCondition))
            if count2 > 0:
                print(f"Conditions already seeded ({count2} found). Skipping.")
            else:
                print(f"Seeding {len(CONDITIONS)} chronic conditions...")
                for name, risk in CONDITIONS:
                    condition = ChronicCondition(
                        chronic_id=uuid.uuid4(),
                        chronic_condition=name,
                        risk_modifier_score=risk
                    )
                    session.add(condition)
                print(f"✓ Seeded {len(CONDITIONS)} chronic conditions")
            
        print("\n✓ Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
