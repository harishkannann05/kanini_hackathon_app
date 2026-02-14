-- Run this in your Supabase SQL Editor to create the necessary tables.

-- Users
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT,
    role TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Patients
CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    age INTEGER,
    gender TEXT,
    symptoms TEXT,
    blood_pressure TEXT,
    heart_rate INTEGER,
    temperature FLOAT,
    pre_existing_conditions TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Departments
CREATE TABLE IF NOT EXISTS departments (
    department_id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT,
    description TEXT
);

-- Visits
CREATE TABLE IF NOT EXISTS visits (
    visit_id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id TEXT REFERENCES patients(patient_id),
    visit_type TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- AI Assessments
CREATE TABLE IF NOT EXISTS ai_assessments (
    assessment_id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id TEXT REFERENCES visits(visit_id),
    risk_score INTEGER,
    risk_level TEXT,
    recommended_department TEXT,
    confidence_score FLOAT,
    model_version TEXT,
    shap_explanation JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Doctors
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id TEXT PRIMARY KEY,
    name TEXT,
    department_id TEXT,
    experience_years INTEGER,
    is_available BOOLEAN DEFAULT TRUE,
    avg_consultation_minutes FLOAT DEFAULT 15.0
);

-- Doctor Assignments
CREATE TABLE IF NOT EXISTS doctor_assignments (
    assignment_id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id TEXT REFERENCES visits(visit_id),
    doctor_id TEXT REFERENCES doctors(doctor_id),
    assigned_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Queue
CREATE TABLE IF NOT EXISTS queue (
    queue_id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id TEXT REFERENCES visits(visit_id),
    doctor_id TEXT REFERENCES doctors(doctor_id),
    priority_score INTEGER,
    is_emergency BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'waiting',
    entered_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    served_at TIMESTAMP WITHOUT TIME ZONE
);

-- Documents
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id TEXT REFERENCES visits(visit_id),
    file_path TEXT,
    extracted_text TEXT,
    detected_conditions JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Emergency Alerts
CREATE TABLE IF NOT EXISTS emergency_alerts (
    alert_id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id TEXT REFERENCES visits(visit_id),
    alert_type TEXT,
    message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    notification_id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id TEXT PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT,
    entity_id TEXT,
    details JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Seed some departments and doctors for testing
INSERT INTO departments (name, description) VALUES
('Cardiology', 'Heart and cardiovascular system'),
('Neurology', 'Brain and nervous system'),
('General Medicine', 'Standard primary care'),
('Pulmonology', 'Respiratory system'),
('Gastroenterology', 'Digestive system')
ON CONFLICT DO NOTHING;

INSERT INTO doctors (doctor_id, name, department_id, experience_years) VALUES
('DOC001', 'Dr. Smith', 'Cardiology', 15),
('DOC002', 'Dr. Jones', 'Cardiology', 5),
('DOC003', 'Dr. Doe', 'General Medicine', 10),
('DOC004', 'Dr. Ray', 'Neurology', 20),
('DOC005', 'Dr. Lee', 'Pulmonology', 8)
ON CONFLICT (doctor_id) DO NOTHING;
