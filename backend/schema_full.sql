-- DROP TABLES to ensure fresh schema
DROP TABLE IF EXISTS audit_logs, notifications, emergency_alerts, whatsapp_bookings, documents, prescriptions, medical_records, 
queue, patient_preferences, doctor_assignments, chronic_conditions, vital_signs_reference, symptom_severity, priority_rules, 
ai_assessments, visits, patients, doctor_availability, doctors, departments, users CASCADE;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

--------------------------------------------------
-- USERS (Authentication & Roles)
--------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('Admin','Recipient','Doctor','Patient')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- DEPARTMENTS
--------------------------------------------------
CREATE TABLE IF NOT EXISTS departments (
    department_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- DOCTORS
--------------------------------------------------
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    department_id UUID REFERENCES departments(department_id),
    specialization VARCHAR(100),
    experience_years INTEGER CHECK (experience_years >= 0),
    consultation_fee NUMERIC(10,2),
    is_available BOOLEAN DEFAULT TRUE,
    max_daily_patients INTEGER DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- DOCTOR AVAILABILITY SLOTS
--------------------------------------------------
CREATE TABLE IF NOT EXISTS doctor_availability (
    availability_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id UUID REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    available_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_booked BOOLEAN DEFAULT FALSE
);

--------------------------------------------------
-- PATIENTS (As per your required fields)
--------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    patient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    full_name VARCHAR(100),
    phone_number VARCHAR(20),
    age INTEGER NOT NULL CHECK (age BETWEEN 0 AND 120),
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('Male','Female','Other')),
    symptoms TEXT NOT NULL,
    blood_pressure VARCHAR(15) NOT NULL,
    heart_rate INTEGER NOT NULL CHECK (heart_rate > 0),
    temperature NUMERIC(4,2) NOT NULL CHECK (temperature BETWEEN 30 AND 45),
    pre_existing_conditions TEXT,
    risk_level VARCHAR(10) CHECK (risk_level IN ('Low','Medium','High')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- VISITS (Each hospital visit)
--------------------------------------------------
CREATE TABLE IF NOT EXISTS visits (
    visit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    visit_type VARCHAR(20) CHECK (visit_type IN ('Walk-In','Online')),
    arrival_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Waiting'
        CHECK (status IN ('Waiting','In Consultation','Completed','Cancelled')),
    emergency_flag BOOLEAN DEFAULT FALSE,
    waiting_time_minutes INTEGER DEFAULT 0,
    completed_at TIMESTAMP
);

--------------------------------------------------
-- AI RISK ASSESSMENTS
--------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_assessments (
    assessment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID REFERENCES visits(visit_id) ON DELETE CASCADE,
    risk_score INTEGER CHECK (risk_score BETWEEN 1 AND 10),
    risk_level VARCHAR(10) CHECK (risk_level IN ('Low','Medium','High')),
    recommended_department UUID REFERENCES departments(department_id),
    shap_explanation JSONB,
    model_version VARCHAR(50),
    confidence_score NUMERIC(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- PRIORITY RULES (Synced with 1_disease_priority_10k.csv)
--------------------------------------------------
CREATE TABLE IF NOT EXISTS priority_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    condition_name VARCHAR(200) NOT NULL,
    base_priority INTEGER CHECK (base_priority BETWEEN 1 AND 10),
    department_id UUID REFERENCES departments(department_id),
    emergency_override BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- SYMPTOM SEVERITY (Synced with 2_symptom_severity_10k.csv)
--------------------------------------------------
CREATE TABLE IF NOT EXISTS symptom_severity (
    symptom_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symptom_name VARCHAR(200),
    base_severity INTEGER,
    emergency_trigger BOOLEAN DEFAULT FALSE,
    associated_department VARCHAR(100),
    typical_duration_days INTEGER
);

--------------------------------------------------
-- VITAL SIGNS REFERENCE (Synced with 3_vital_signs_reference_10k.csv)
--------------------------------------------------
CREATE TABLE IF NOT EXISTS vital_signs_reference (
    vital_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vital_type VARCHAR(100),
    age_group VARCHAR(50),
    critical_low_threshold NUMERIC,
    critical_high_threshold NUMERIC,
    moderate_low_threshold NUMERIC,
    moderate_high_threshold NUMERIC,
    critical_instability_score INTEGER
);

--------------------------------------------------
-- CHRONIC CONDITIONS (Synced with 4_chronic_condition_modifiers_10k.csv)
--------------------------------------------------
CREATE TABLE IF NOT EXISTS chronic_conditions (
    chronic_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chronic_condition VARCHAR(200),
    risk_modifier_score INTEGER,
    high_risk_with_symptoms TEXT,
    associated_department VARCHAR(100),
    complication_risk_level VARCHAR(50)
);

--------------------------------------------------
-- DOCTOR ASSIGNMENTS
--------------------------------------------------
CREATE TABLE IF NOT EXISTS doctor_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID REFERENCES visits(visit_id) ON DELETE CASCADE,
    doctor_id UUID REFERENCES doctors(doctor_id),
    assigned_by UUID REFERENCES users(user_id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

--------------------------------------------------
-- PATIENT DOCTOR PREFERENCE
--------------------------------------------------
CREATE TABLE IF NOT EXISTS patient_preferences (
    preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    preferred_doctor UUID REFERENCES doctors(doctor_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- QUEUE SYSTEM
--------------------------------------------------
CREATE TABLE IF NOT EXISTS queue (
    queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID REFERENCES visits(visit_id) ON DELETE CASCADE,
    doctor_id UUID REFERENCES doctors(doctor_id),
    priority_score INTEGER NOT NULL,
    queue_position INTEGER,
    waiting_time_minutes INTEGER DEFAULT 0,
    wait_time_boost INTEGER DEFAULT 0,
    is_emergency BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- MEDICAL RECORDS
--------------------------------------------------
CREATE TABLE IF NOT EXISTS medical_records (
    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID REFERENCES visits(visit_id) ON DELETE CASCADE,
    doctor_id UUID REFERENCES doctors(doctor_id),
    diagnosis TEXT,
    syndrome_identified TEXT,
    treatment_plan TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- PRESCRIPTIONS
--------------------------------------------------
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_id UUID REFERENCES medical_records(record_id) ON DELETE CASCADE,
    medication_name VARCHAR(200),
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    duration VARCHAR(100),
    instructions TEXT
);

--------------------------------------------------
-- DOCUMENT UPLOADS (OCR)
--------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    visit_id UUID REFERENCES visits(visit_id),
    file_url TEXT NOT NULL,
    file_type VARCHAR(50),
    extracted_text TEXT,
    processed BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- WHATSAPP BOOKINGS
--------------------------------------------------
CREATE TABLE IF NOT EXISTS whatsapp_bookings (
    booking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) NOT NULL,
    patient_id UUID REFERENCES patients(patient_id),
    symptoms TEXT,
    triage_risk_score INTEGER,
    assigned_department UUID REFERENCES departments(department_id),
    assigned_doctor UUID REFERENCES doctors(doctor_id),
    booking_status VARCHAR(20)
        CHECK (booking_status IN ('Pending','Confirmed','Cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- EMERGENCY ALERTS
--------------------------------------------------
CREATE TABLE IF NOT EXISTS emergency_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visit_id UUID REFERENCES visits(visit_id) ON DELETE CASCADE,
    triggered_by VARCHAR(50) CHECK (triggered_by IN ('AI','Manual')),
    alert_message TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- NOTIFICATIONS
--------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

--------------------------------------------------
-- AUDIT LOGS
--------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    action TEXT NOT NULL,
    target_table VARCHAR(100),
    target_id UUID,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
