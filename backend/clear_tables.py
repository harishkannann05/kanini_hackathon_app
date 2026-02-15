import sqlite3

conn = sqlite3.connect('backend_dev.db')
cursor = conn.cursor()

tables = [
    'symptom_severity',
    'disease_priority', 
    'vital_signs_reference',
    'doctor_specialization',
    'focused_patient_dataset'
]

for table in tables:
    try:
        cursor.execute(f'DELETE FROM {table}')
        count = cursor.rowcount
        print(f'Deleted {count} rows from {table}')
    except Exception as e:
        print(f'Error deleting from {table}: {e}')

conn.commit()
print('\n✓ Tables cleared')
conn.close()
