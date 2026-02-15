"""Direct seed symptoms - bypasses count check"""
import sqlite3
import uuid

conn = sqlite3.connect('backend_dev.db')
cursor = conn.cursor()

# Clear existing data
cursor.execute('DELETE FROM symptom_severity')

symptoms = [
    ("Fever", 7, 0, "General Medicine", 7),
    ("Cough", 4, 0, "Pulmonology", 14),
    ("Chest Pain", 9, 1, "Cardiology", 1),
    ("Headache", 5, 0, "Neurology", 7),
    ("Abdominal Pain", 7, 0, "Gastroenterology", 7),
    ("Shortness of Breath", 9, 1, "Pulmonology", 3),
    ("Dizziness", 6, 0, "Neurology", 5),
    ("Nausea", 4, 0, "Gastroenterology", 3),
    ("Fatigue", 3, 0, "General Medicine", 30),
    ("Joint Pain", 5, 0, "Orthopedics", 14),
    ("Back Pain", 5, 0, "Orthopedics", 14),
    ("Sore Throat", 3, 0, "General Medicine", 7),
    ("Runny Nose", 2, 0, "General Medicine", 7),
    ("Vomiting", 6, 0, "Gastroenterology", 3),
    ("Diarrhea", 5, 0, "Gastroenterology", 5),
    ("Rash", 4, 0, "General Medicine", 10),
    ("Swelling", 5, 0, "Emergency", 3),
    ("Blurred Vision", 7, 0, "Emergency", 1),
    ("Palpitations", 7, 0, "Cardiology", 1),
    ("Confusion", 8, 1, "Emergency", 1),
    ("Seizure", 10, 1, "Emergency", 1),
    ("Severe Bleeding", 10, 1, "Emergency", 1),
    ("Difficulty Breathing", 10, 1, "Emergency", 1),
    ("Loss of Consciousness", 10, 1, "Emergency", 1),
    ("Severe Chest Pain", 10, 1, "Emergency", 1),
]

print(f"Inserting {len(symptoms)} symptoms...")
for name, severity, emergency, dept, duration in symptoms:
    symptom_id = uuid.uuid4().bytes  # Convert UUID to bytes for SQLite
    cursor.execute('''
        INSERT INTO symptom_severity 
        (symptom_id, symptom_name, base_severity, emergency_trigger, associated_department, typical_duration_days)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (symptom_id, name, severity, emergency, dept, duration))

conn.commit()
print(f"✓ Inserted {len(symptoms)} symptoms")

# Ver ify
cursor.execute('SELECT COUNT(*) FROM symptom_severity')
count = cursor.fetchone()[0]
print(f"✓ Total symptoms in database: {count}")

conn.close()
