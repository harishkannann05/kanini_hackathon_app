"""Create database schema using DDL"""
import sqlite3

def create_schema():
    db_path = "backend_dev.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create all tables
    sql_statements = [
        """CREATE TABLE IF NOT EXISTS users (
            user_id BLOB PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            full_name TEXT,
            role TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS departments (
            department_id BLOB PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS doctors (
            doctor_id BLOB PRIMARY KEY,
            department_id BLOB,
            specialization TEXT,
            experience_years INTEGER,
            is_available BOOLEAN DEFAULT 1,
            user_id BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(department_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )""",
        
        """CREATE TABLE IF NOT EXISTS patients (
            patient_id BLOB PRIMARY KEY,
            full_name TEXT,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            email TEXT,
            symptoms TEXT,
            pre_existing_conditions TEXT,
            risk_level INTEGER,
            vital_signs TEXT,
            user_id BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )""",
        
        """CREATE TABLE IF NOT EXISTS visits (
            visit_id BLOB PRIMARY KEY,
            patient_id BLOB,
            status TEXT,
            triage_notes TEXT,
            risk_score INTEGER,
            assigned_doctor_id BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (assigned_doctor_id) REFERENCES doctors(doctor_id)
        )""",
        
        """CREATE TABLE IF NOT EXISTS queue (
            queue_id BLOB PRIMARY KEY,
            visit_id BLOB NOT NULL,
            doctor_id BLOB,
            priority_score INTEGER,
            queue_position INTEGER,
            waiting_time_minutes INTEGER DEFAULT 0,
            wait_time_boost INTEGER DEFAULT 0,
            is_emergency BOOLEAN DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (visit_id) REFERENCES visits(visit_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        )""",
        
        """CREATE TABLE IF NOT EXISTS medical_records (
            record_id BLOB PRIMARY KEY,
            visit_id BLOB,
            doctor_id BLOB,
            diagnosis TEXT,
            syndrome_identified TEXT,
            treatment_plan TEXT,
            follow_up_required BOOLEAN DEFAULT 0,
            follow_up_date TIMESTAMP,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (visit_id) REFERENCES visits(visit_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        )""",
        
        """CREATE TABLE IF NOT EXISTS symptom_severity (
            symptom_id BLOB PRIMARY KEY,
            name TEXT UNIQUE,
            severity INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS chronic_condition (
            condition_id BLOB PRIMARY KEY,
            chronic_condition TEXT UNIQUE,
            risk_modifier_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS doctor_assignment (
            assignment_id BLOB PRIMARY KEY,
            visit_id BLOB,
            doctor_id BLOB,
            assignment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (visit_id) REFERENCES visits(visit_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        )""",
        
        """CREATE TABLE IF NOT EXISTS audit_log (
            log_id BLOB PRIMARY KEY,
            action TEXT,
            table_name TEXT,
            record_id BLOB,
            user_id BLOB,
            changes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )""",
        
        """CREATE TABLE IF NOT EXISTS ai_assessment (
            assessment_id BLOB PRIMARY KEY,
            visit_id BLOB,
            risk_score INTEGER,
            risk_category TEXT,
            confidence FLOAT,
            model_version TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (visit_id) REFERENCES visits(visit_id)
        )""",
        
        """CREATE TABLE IF NOT EXISTS priority_rule (
            rule_id BLOB PRIMARY KEY,
            condition_name TEXT,
            base_priority_score INTEGER,
            multiplier FLOAT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS vital_sign_reference (
            vital_id BLOB PRIMARY KEY,
            vital_name TEXT UNIQUE,
            normal_min FLOAT,
            normal_max FLOAT,
            critical_min FLOAT,
            critical_max FLOAT,
            unit TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS document (
            document_id BLOB PRIMARY KEY,
            visit_id BLOB,
            file_path TEXT,
            extracted_text TEXT,
            file_type TEXT,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (visit_id) REFERENCES visits(visit_id)
        )""",
        
        """CREATE TABLE IF NOT EXISTS patient_preference (
            preference_id BLOB PRIMARY KEY,
            patient_id BLOB,
            preferred_doctor_id BLOB,
            preference_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (preferred_doctor_id) REFERENCES doctors(doctor_id)
        )""",
    ]
    
    for sql in sql_statements:
        try:
            cursor.execute(sql)
            print(f"✓ Created table: {sql.split('(')[0].replace('CREATE TABLE IF NOT EXISTS', '').strip()}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    count = cursor.fetchone()[0]
    print(f"\n✓ Total tables in database: {count}")
    
    conn.close()

if __name__ == "__main__":
    create_schema()
