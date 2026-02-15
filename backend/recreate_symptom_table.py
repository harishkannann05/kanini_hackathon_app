import sqlite3

conn = sqlite3.connect('backend_dev.db')
cursor = conn.cursor()

# Drop and recreate symptom_severity table
print("Dropping symptom_severity table...")
cursor.execute('DROP TABLE IF EXISTS symptom_severity')

print("Creating symptom_severity table...")
cursor.execute('''
CREATE TABLE symptom_severity (
    symptom_id BLOB PRIMARY KEY,
    symptom_name VARCHAR(200) NOT NULL,
    base_severity INTEGER,
    emergency_trigger BOOLEAN DEFAULT 0,
    associated_department VARCHAR(100),
    typical_duration_days INTEGER
)
''')

conn.commit()
print('✓ Table recreated')
conn.close()
