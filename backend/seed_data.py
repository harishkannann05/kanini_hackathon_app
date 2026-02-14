"""
Seed script — Populates departments and doctors tables with reference data.
Run once: python seed_data.py
"""
import asyncio
import os
import uuid
from dotenv import load_dotenv
import urllib.parse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

load_dotenv()
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

encoded_user = urllib.parse.quote_plus(USER)
encoded_password = urllib.parse.quote_plus(PASSWORD)
DATABASE_URL = f"postgresql+asyncpg://{encoded_user}:{encoded_password}@{HOST}:{PORT}/{DBNAME}"

engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"statement_cache_size": 0})

DEPARTMENTS = [
    "Cardiology",
    "Neurology",
    "Pulmonology",
    "Gastroenterology",
    "General Medicine",
    "Emergency",
    "Orthopedics",
]

DOCTORS = [
    # (specialization, department, experience_years)
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
]


async def seed():
    async with engine.begin() as conn:
        # Check if departments already exist
        result = await conn.execute(text("SELECT COUNT(*) FROM departments"))
        count = result.scalar()
        if count > 0:
            print(f"Departments already seeded ({count} found). Skipping.")
        else:
            dept_map = {}
            for name in DEPARTMENTS:
                dept_id = str(uuid.uuid4())
                dept_map[name] = dept_id
                await conn.execute(text(
                    "INSERT INTO departments (department_id, name) VALUES (:id, :name)"
                ), {"id": dept_id, "name": name})
            print(f"Seeded {len(DEPARTMENTS)} departments.")

            # Seed doctors
            for spec, dept, exp in DOCTORS:
                doc_id = str(uuid.uuid4())
                dept_id = dept_map.get(dept)
                await conn.execute(text(
                    "INSERT INTO doctors (doctor_id, specialization, department_id, experience_years, is_available, consultation_fee, max_daily_patients) "
                    "VALUES (:id, :spec, :dept_id, :exp, true, 500, 20)"
                ), {"id": doc_id, "spec": spec, "dept_id": dept_id, "exp": exp})
            print(f"Seeded {len(DOCTORS)} doctors.")

        # Verify
        depts = await conn.execute(text("SELECT department_id, name FROM departments"))
        print("\n=== Departments ===")
        for row in depts:
            print(f"  {row[0]}: {row[1]}")

        docs = await conn.execute(text("SELECT doctor_id, specialization, department_id FROM doctors"))
        print("\n=== Doctors ===")
        for row in docs:
            print(f"  {row[0]}: {row[1]} (dept: {row[2]})")


asyncio.run(seed())
