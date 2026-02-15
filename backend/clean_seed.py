"""Clean seed database with fresh data"""
import asyncio
import uuid
from db import AsyncSessionLocal
from models import SymptomSeverity, ChronicCondition, Department, Doctor
from sqlalchemy import delete, select, func

async def seed_data():
    print("Seeding database...")
    
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Delete existing data
            await session.execute(delete(SymptomSeverity))
            await session.execute(delete(ChronicCondition))
            print("✓ Cleared old data")
        
        # Seed Symptoms
        symptoms_data = [
            ("Fever", 7), ("Cough", 4), ("Chest Pain", 9), ("Headache", 5),
            ("Abdominal Pain", 7), ("Shortness of Breath", 9), ("Dizziness", 6),
            ("Nausea", 4), ("Fatigue", 3), ("Joint Pain", 5), ("Back Pain", 5),
            ("Sore Throat", 3), ("Runny Nose", 2), ("Vomiting", 6), ("Diarrhea", 5),
            ("Rash", 4), ("Swelling", 5), ("Blurred Vision", 7), ("Palpitations", 7),
            ("Confusion", 8), ("Muscle Pain", 4), ("Loss of Appetite", 3),
            ("Insomnia", 4), ("Anxiety", 4), ("Tremor", 5)
        ]
        
        async with session.begin():
            for name, severity in symptoms_data:
                symptom = SymptomSeverity(
                    symptom_id=uuid.uuid4(),
                    symptom_name=name,
                    base_severity=severity
                )
                session.add(symptom)
            await session.flush()
            print(f"✓ Seeded {len(symptoms_data)} symptoms")
        
        # Seed Chronic Conditions
        conditions_data = [
            ("Diabetes", 8), ("Hypertension", 7), ("Asthma", 6), ("Heart Disease", 9),
            ("COPD", 7), ("Kidney Disease", 8), ("Liver Disease", 8), ("Cancer", 10),
            ("HIV/AIDS", 9), ("Stroke History", 9), ("Epilepsy", 7), ("Arthritis", 4),
            ("Obesity", 5), ("Anemia", 5), ("Thyroid Disorder", 4)
        ]
        
        async with session.begin():
            for condition, risk_score in conditions_data:
                cond = ChronicCondition(
                    chronic_id=uuid.uuid4(),
                    chronic_condition=condition,
                    risk_modifier_score=risk_score
                )
                session.add(cond)
            await session.flush()
            print(f"✓ Seeded {len(conditions_data)} chronic conditions")
    
    # Verify
    async with AsyncSessionLocal() as session:
        sym_count = await session.execute(select(func.count()).select_from(SymptomSeverity))
        cond_count = await session.execute(select(func.count()).select_from(ChronicCondition))
        dept_count = await session.execute(select(func.count()).select_from(Department))
        doc_count = await session.execute(select(func.count()).select_from(Doctor))
        
        print(f"\n✓ Symptoms: {sym_count.scalar()}")
        print(f"✓ Conditions: {cond_count.scalar()}")
        print(f"✓ Departments: {dept_count.scalar()}")
        print(f"✓ Doctors: {doc_count.scalar()}")

if __name__ == "__main__":
    asyncio.run(seed_data())
