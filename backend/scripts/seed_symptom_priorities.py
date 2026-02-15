"""
Script to seed symptom severity/priority weights into the database.
Run this after database setup to populate the symptom_severity table.
"""
import psycopg2
from dotenv import load_dotenv
import os
import uuid

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

SYMPTOM_WEIGHTS = [
    # Critical (10)
    ("Chest Pain", 10, "Critical condition requiring immediate attention"),
    ("Difficulty Breathing", 10, "Critical respiratory issue"),
    ("Unconsciousness", 10, "Medical emergency"),
    ("Severe Bleeding", 10, "Critical injury"),
    ("Stroke Symptoms", 10, "Time-sensitive emergency"),
    ("Heart Attack Symptoms", 10, "Critical cardiac event"),
    
    # High (7-9)
    ("High Fever (>103°F)", 9, "Potentially dangerous infection"),
    ("Severe Abdominal Pain", 8, "May indicate serious condition"),
    ("Head Injury", 8, "Potential concussion or trauma"),
    ("Seizure", 9, "Neurological emergency"),
    
    # Medium (4-6)
    ("Moderate Fever (100-103°F)", 5, "Common infection symptom"),
    ("Persistent Headache", 5, "May indicate underlying issue"),
    ("Vomiting", 5, "Dehydration risk"),
    ("Diarrhea", 4, "Dehydration and infection risk"),
    ("Body Aches", 4, "Flu-like symptoms"),
    
    # Low (1-3)
    ("Mild Fever (<100°F)", 3, "Minor infection"),
    ("Cough", 2, "Common cold symptom"),
    ("Runny Nose", 1, "Minor cold symptom"),
    ("Sore Throat", 2, "Minor infection"),
    ("Fatigue", 2, "General malaise"),
    ("Minor Cut", 1, "Minor injury"),
]


def seed_symptom_priorities():
    """Seed symptom priority weights into the database."""
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    try:
        cursor = conn.cursor()
        print("Seeding symptom priorities...")
        
        count = 0
        for symptom_name, severity, description in SYMPTOM_WEIGHTS:
            severity_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO symptom_severity (severity_id, symptom_name, base_severity, description)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (symptom_name) DO UPDATE SET base_severity = EXCLUDED.base_severity
                """,
                (severity_id, symptom_name, severity, description)
            )
            count += 1
        
        conn.commit()
        print(f"✅ Successfully seeded {count} symptom priority weights")
        print("\nSample entries:")
        print("  - Chest Pain: 10 (Critical)")
        print("  - Moderate Fever: 5 (Medium)")
        print("  - Cough: 2 (Low)")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    seed_symptom_priorities()
    print("\nDone! Symptom priorities are now available for triage scoring.")
