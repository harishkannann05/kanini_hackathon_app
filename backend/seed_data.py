"""SQLite seed wrapper - uses the migration seeding step."""
import asyncio
from backend.scripts.migrate_db import seed_departments_and_doctors

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


if __name__ == "__main__":
    asyncio.run(seed_departments_and_doctors())
