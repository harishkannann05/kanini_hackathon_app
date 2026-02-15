"""Initialize database with all tables"""
import asyncio
import sqlite3
from db import engine

async def init_database():
    # Import all models to register them with Base
    from models import (
        Base, User, Doctor, Department, Patient, Visit, Queue, MedicalRecord,
        SymptomSeverity, ChronicCondition, DoctorAssignment, AuditLog, 
        AIAssessment, PriorityRule, VitalSignReference, Prescription, 
        DiseasePriority, ChronicConditionModifier, DoctorSpecialization,
        FocusedPatientDataset, Document, PatientPreference
    )
    
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✓ Database tables created successfully")
    
    # Verify with sqlite3
    db_path = "backend_dev.db"
    sqlite_conn = sqlite3.connect(db_path)
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    table_count = cursor.fetchone()[0]
    print(f"✓ Total tables in database: {table_count}")
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - {table[0]}")
    sqlite_conn.close()

if __name__ == "__main__":
    asyncio.run(init_database())
