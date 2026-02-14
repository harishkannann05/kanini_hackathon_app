"""
Smart AI Patient Triage - MASSIVE Knowledge Base Generator
All 5 datasets with 10,000 rows each for maximum coverage
"""

import pandas as pd
import numpy as np
import random
from itertools import product

np.random.seed(42)
random.seed(42)

print("=" * 80)
print("MASSIVE MEDICAL KNOWLEDGE BASE GENERATION")
print("10,000 rows for each of 5 datasets = 50,000 total medical records")
print("=" * 80)
print()

# ============================================================================
# 1. DISEASE PRIORITY DATASET - 10,000 ROWS
# ============================================================================

print("🔄 1/5: Generating Disease Priority Dataset (10,000 rows)...")

# Base disease templates
disease_categories = {
    'Cardiac': {
        'base_conditions': [
            'Myocardial Infarction', 'Angina', 'Heart Failure', 'Arrhythmia', 
            'Atrial Fibrillation', 'Cardiomyopathy', 'Pericarditis', 'Endocarditis',
            'Hypertension', 'Coronary Artery Disease', 'Valvular Disease',
            'Pulmonary Embolism', 'Deep Vein Thrombosis', 'Aortic Dissection',
            'Peripheral Artery Disease', 'Ventricular Tachycardia'
        ],
        'modifiers': ['Acute', 'Chronic', 'Severe', 'Moderate', 'Mild', 'Stable', 'Unstable'],
        'subtypes': ['Type A', 'Type B', 'Grade I', 'Grade II', 'Grade III', 'Stage 1', 'Stage 2', 'Stage 3']
    },
    'Respiratory': {
        'base_conditions': [
            'Pneumonia', 'COPD', 'Asthma', 'Bronchitis', 'Tuberculosis',
            'Pulmonary Fibrosis', 'Pleural Effusion', 'Pneumothorax', 'Pleurisy',
            'Respiratory Distress Syndrome', 'COVID-19', 'Influenza', 'Sinusitis',
            'Laryngitis', 'Pharyngitis', 'Emphysema', 'Lung Cancer', 'Sleep Apnea'
        ],
        'modifiers': ['Acute', 'Chronic', 'Severe', 'Moderate', 'Mild', 'Active', 'Latent'],
        'subtypes': ['Bacterial', 'Viral', 'Fungal', 'Type 1', 'Type 2', 'Exacerbation']
    },
    'Neurological': {
        'base_conditions': [
            'Stroke', 'TIA', 'Seizure', 'Migraine', 'Epilepsy', 'Meningitis',
            'Encephalitis', 'Multiple Sclerosis', 'Parkinsons', 'Alzheimers',
            'Neuropathy', 'Brain Tumor', 'Concussion', 'Vertigo', 'Bell Palsy'
        ],
        'modifiers': ['Acute', 'Chronic', 'Severe', 'Moderate', 'Mild', 'Progressive'],
        'subtypes': ['Ischemic', 'Hemorrhagic', 'Focal', 'Generalized', 'Primary', 'Secondary']
    },
    'Infection': {
        'base_conditions': [
            'Sepsis', 'UTI', 'Dengue', 'Malaria', 'Typhoid', 'Gastroenteritis',
            'Cellulitis', 'Abscess', 'Wound Infection', 'Blood Infection',
            'Viral Fever', 'Bacterial Infection', 'Fungal Infection'
        ],
        'modifiers': ['Severe', 'Moderate', 'Mild', 'Acute', 'Chronic', 'Recurrent'],
        'subtypes': ['Gram Positive', 'Gram Negative', 'Resistant', 'Community Acquired']
    },
    'Gastrointestinal': {
        'base_conditions': [
            'Appendicitis', 'Pancreatitis', 'Cholecystitis', 'Hepatitis', 'Cirrhosis',
            'IBD', 'IBS', 'GERD', 'Peptic Ulcer', 'Diverticulitis', 'Gastritis',
            'Bowel Obstruction', 'GI Bleed', 'Liver Failure'
        ],
        'modifiers': ['Acute', 'Chronic', 'Severe', 'Moderate', 'Mild'],
        'subtypes': ['Type A', 'Type B', 'Type C', 'Complicated', 'Uncomplicated']
    },
    'Trauma': {
        'base_conditions': [
            'Fracture', 'Laceration', 'Contusion', 'Burn', 'Sprain', 'Dislocation',
            'Head Injury', 'Spinal Injury', 'Internal Bleeding', 'Crush Injury'
        ],
        'modifiers': ['Major', 'Minor', 'Severe', 'Moderate', 'Mild'],
        'subtypes': ['Open', 'Closed', 'Compound', 'Simple', '1st Degree', '2nd Degree', '3rd Degree']
    }
}

departments = ['Emergency', 'Cardiology', 'Pulmonology', 'Neurology', 'General Medicine',
               'Gastroenterology', 'Orthopedics', 'Surgery', 'ICU', 'Infectious Disease']

diseases = []
disease_id = 0

for category, data in disease_categories.items():
    base_conditions = data['base_conditions']
    modifiers = data['modifiers']
    subtypes = data['subtypes']
    
    # Generate combinations
    for base in base_conditions:
        for modifier in modifiers:
            if disease_id >= 10000:
                break
            
            condition_name = f"{base} {modifier}"
            
            # Assign severity based on modifier
            if modifier in ['Severe', 'Acute', 'Unstable', 'Major']:
                severity = np.random.randint(7, 11)
                emergency = 'Yes' if severity >= 8 else np.random.choice(['Yes', 'No'], p=[0.7, 0.3])
                mortality = np.random.choice(['High', 'Moderate'], p=[0.6, 0.4])
                wait_time = np.random.randint(0, 20)
            elif modifier in ['Moderate', 'Stable']:
                severity = np.random.randint(4, 8)
                emergency = np.random.choice(['Yes', 'No'], p=[0.2, 0.8])
                mortality = np.random.choice(['Moderate', 'Low'], p=[0.4, 0.6])
                wait_time = np.random.randint(30, 90)
            else:  # Mild, Chronic
                severity = np.random.randint(2, 6)
                emergency = 'No'
                mortality = np.random.choice(['Low', 'Moderate'], p=[0.8, 0.2])
                wait_time = np.random.randint(60, 180)
            
            # Contagious flag
            if category == 'Infection' or 'Viral' in condition_name or 'Bacterial' in condition_name:
                contagious = np.random.choice(['Yes', 'No'], p=[0.7, 0.3])
            else:
                contagious = 'No'
            
            # Department
            if emergency == 'Yes' and severity >= 8:
                dept = 'Emergency'
            elif category == 'Cardiac':
                dept = np.random.choice(['Cardiology', 'Emergency'], p=[0.6, 0.4])
            elif category == 'Respiratory':
                dept = np.random.choice(['Pulmonology', 'Emergency'], p=[0.7, 0.3])
            elif category == 'Neurological':
                dept = np.random.choice(['Neurology', 'Emergency'], p=[0.6, 0.4])
            elif category == 'Gastrointestinal':
                dept = np.random.choice(['Gastroenterology', 'Surgery', 'Emergency'], p=[0.5, 0.3, 0.2])
            elif category == 'Trauma':
                dept = np.random.choice(['Orthopedics', 'Surgery', 'Emergency'], p=[0.4, 0.3, 0.3])
            else:
                dept = random.choice(departments)
            
            progression = np.random.choice(['Fast', 'Moderate', 'Slow'], 
                                          p=[0.3, 0.4, 0.3] if severity >= 7 else [0.1, 0.3, 0.6])
            
            diseases.append({
                'Condition_ID': f'COND{str(disease_id+1).zfill(5)}',
                'Condition_Name': condition_name,
                'Condition_Category': category,
                'Base_Severity_Score': severity,
                'Default_Department': dept,
                'Emergency_Flag': emergency,
                'Contagious_Flag': contagious,
                'Max_Recommended_Wait_Time_Minutes': wait_time,
                'Mortality_Risk_Level': mortality,
                'Progression_Speed': progression
            })
            
            disease_id += 1
            
            if disease_id >= 10000:
                break
        
        if disease_id >= 10000:
            break
    
    if disease_id >= 10000:
        break

# Add subtypes to reach exactly 10,000
while disease_id < 10000:
    category = random.choice(list(disease_categories.keys()))
    data = disease_categories[category]
    base = random.choice(data['base_conditions'])
    modifier = random.choice(data['modifiers'])
    subtype = random.choice(data['subtypes'])
    
    condition_name = f"{base} {modifier} {subtype}"
    severity = np.random.randint(2, 11)
    
    diseases.append({
        'Condition_ID': f'COND{str(disease_id+1).zfill(5)}',
        'Condition_Name': condition_name,
        'Condition_Category': category,
        'Base_Severity_Score': severity,
        'Default_Department': random.choice(departments),
        'Emergency_Flag': np.random.choice(['Yes', 'No'], p=[0.3, 0.7]),
        'Contagious_Flag': np.random.choice(['Yes', 'No'], p=[0.2, 0.8]),
        'Max_Recommended_Wait_Time_Minutes': np.random.randint(0, 180),
        'Mortality_Risk_Level': np.random.choice(['Low', 'Moderate', 'High'], p=[0.6, 0.3, 0.1]),
        'Progression_Speed': np.random.choice(['Slow', 'Moderate', 'Fast'], p=[0.4, 0.4, 0.2])
    })
    
    disease_id += 1

diseases_df = pd.DataFrame(diseases)
diseases_df.to_csv('/home/claude/1_disease_priority_10k.csv', index=False)
print(f"✅ Disease Priority: {len(diseases_df):,} conditions")

# ============================================================================
# 2. SYMPTOM SEVERITY DATASET - 10,000 ROWS
# ============================================================================

print("\n🔄 2/5: Generating Symptom Severity Dataset (10,000 rows)...")

symptom_bases = {
    'Pain': ['chest', 'abdominal', 'head', 'back', 'joint', 'muscle', 'throat', 'ear', 'eye'],
    'Breathing': ['shortness of breath', 'difficulty breathing', 'wheezing', 'cough'],
    'Cardiac': ['palpitations', 'irregular heartbeat', 'rapid heartbeat', 'chest tightness'],
    'Neurological': ['dizziness', 'confusion', 'weakness', 'numbness', 'tingling', 'seizure'],
    'Gastrointestinal': ['nausea', 'vomiting', 'diarrhea', 'constipation', 'bloating'],
    'General': ['fever', 'fatigue', 'sweating', 'chills', 'weight loss'],
    'Sensory': ['blurred vision', 'hearing loss', 'loss of taste', 'loss of smell']
}

intensities = ['mild', 'moderate', 'severe', 'acute', 'chronic', 'sudden', 'persistent', 'intermittent']
locations = ['left', 'right', 'bilateral', 'upper', 'lower', 'central', 'radiating']
qualities = ['sharp', 'dull', 'throbbing', 'burning', 'stabbing', 'cramping', 'aching']

symptoms = []
symptom_id = 0

for category, base_symptoms in symptom_bases.items():
    for base in base_symptoms:
        for intensity in intensities:
            if symptom_id >= 10000:
                break
            
            symptom_name = f"{intensity} {base}"
            
            # Severity based on intensity
            if intensity in ['severe', 'acute', 'sudden']:
                severity = np.random.randint(7, 11)
                emergency = True if severity >= 9 else np.random.choice([True, False], p=[0.6, 0.4])
            elif intensity in ['moderate', 'persistent']:
                severity = np.random.randint(4, 8)
                emergency = np.random.choice([True, False], p=[0.2, 0.8])
            else:
                severity = np.random.randint(1, 6)
                emergency = False
            
            # Department association
            if category == 'Cardiac':
                dept = 'Cardiology'
            elif category == 'Breathing':
                dept = 'Pulmonology'
            elif category == 'Neurological':
                dept = 'Neurology'
            elif category == 'Gastrointestinal':
                dept = 'Gastroenterology'
            else:
                dept = 'General Medicine'
            
            # Linked conditions
            linked = np.random.randint(2, 6)
            conditions = [f"Condition_{i}" for i in range(linked)]
            
            duration = np.random.randint(1, 30)
            
            symptoms.append({
                'Symptom_ID': f'SYMP{str(symptom_id+1).zfill(5)}',
                'Symptom_Name': symptom_name,
                'Base_Severity': severity,
                'Emergency_Trigger': emergency,
                'Associated_Department': dept,
                'Possible_Linked_Conditions': ', '.join(conditions),
                'Typical_Duration_Days': duration
            })
            
            symptom_id += 1

# Add combinations with locations and qualities to reach 10,000
while symptom_id < 10000:
    base = random.choice([s for sublist in symptom_bases.values() for s in sublist])
    intensity = random.choice(intensities)
    
    if 'pain' in base or 'ache' in base:
        quality = random.choice(qualities)
        location = random.choice(locations)
        symptom_name = f"{intensity} {quality} {location} {base}"
    else:
        symptom_name = f"{intensity} {base}"
    
    severity = np.random.randint(1, 11)
    
    symptoms.append({
        'Symptom_ID': f'SYMP{str(symptom_id+1).zfill(5)}',
        'Symptom_Name': symptom_name,
        'Base_Severity': severity,
        'Emergency_Trigger': np.random.choice([True, False], p=[0.15, 0.85]),
        'Associated_Department': random.choice(departments),
        'Possible_Linked_Conditions': ', '.join([f"Condition_{i}" for i in range(np.random.randint(1, 5))]),
        'Typical_Duration_Days': np.random.randint(1, 60)
    })
    
    symptom_id += 1

symptoms_df = pd.DataFrame(symptoms)
symptoms_df.to_csv('/home/claude/2_symptom_severity_10k.csv', index=False)
print(f"✅ Symptom Severity: {len(symptoms_df):,} symptoms")

# ============================================================================
# 3. VITAL SIGNS REFERENCE DATASET - 10,000 ROWS
# ============================================================================

print("\n🔄 3/5: Generating Vital Signs Reference Dataset (10,000 rows)...")

vital_types = ['Blood_Pressure_Systolic', 'Blood_Pressure_Diastolic', 'Heart_Rate', 
               'Respiratory_Rate', 'Temperature', 'Oxygen_Saturation', 'Blood_Sugar']

# Create granular thresholds for different age groups and conditions
age_groups = ['Infant', 'Child', 'Adolescent', 'Young_Adult', 'Adult', 'Middle_Age', 'Elderly', 'Very_Elderly']
conditions_modifiers = ['Normal', 'Diabetic', 'Hypertensive', 'Cardiac', 'Respiratory', 'Renal', 'Pregnant']

vitals_data = []
vital_id = 0

for vital_type in vital_types:
    for age_group in age_groups:
        for condition in conditions_modifiers:
            if vital_id >= 10000:
                break
            
            # Base ranges by vital type
            if vital_type == 'Blood_Pressure_Systolic':
                if age_group in ['Elderly', 'Very_Elderly']:
                    critical_low, critical_high = 85, 190
                    moderate_low, moderate_high = 95, 170
                else:
                    critical_low, critical_high = 90, 180
                    moderate_low, moderate_high = 100, 160
                critical_score, moderate_score = 4, 2
                
            elif vital_type == 'Blood_Pressure_Diastolic':
                critical_low, critical_high = 55, 125
                moderate_low, moderate_high = 65, 105
                critical_score, moderate_score = 3, 2
                
            elif vital_type == 'Heart_Rate':
                if age_group in ['Infant', 'Child']:
                    critical_low, critical_high = 70, 180
                    moderate_low, moderate_high = 80, 160
                else:
                    critical_low, critical_high = 45, 135
                    moderate_low, moderate_high = 55, 115
                critical_score, moderate_score = 4, 2
                
            elif vital_type == 'Respiratory_Rate':
                if age_group in ['Infant', 'Child']:
                    critical_low, critical_high = 15, 50
                    moderate_low, moderate_high = 20, 40
                else:
                    critical_low, critical_high = 8, 32
                    moderate_low, moderate_high = 10, 26
                critical_score, moderate_score = 3, 2
                
            elif vital_type == 'Temperature':
                critical_low, critical_high = 35.0, 40.0
                moderate_low, moderate_high = 35.8, 38.8
                critical_score, moderate_score = 3, 2
                
            elif vital_type == 'Oxygen_Saturation':
                critical_low, critical_high = 88, 999
                moderate_low, moderate_high = 93, 999
                critical_score, moderate_score = 4, 2
                
            else:  # Blood_Sugar
                if condition == 'Diabetic':
                    critical_low, critical_high = 55, 350
                    moderate_low, moderate_high = 65, 250
                else:
                    critical_low, critical_high = 60, 300
                    moderate_low, moderate_high = 70, 200
                critical_score, moderate_score = 3, 2
            
            vitals_data.append({
                'Vital_ID': f'VITAL{str(vital_id+1).zfill(5)}',
                'Vital_Type': vital_type,
                'Age_Group': age_group,
                'Condition_Modifier': condition,
                'Critical_Low_Threshold': critical_low,
                'Critical_High_Threshold': critical_high,
                'Moderate_Low_Threshold': moderate_low,
                'Moderate_High_Threshold': moderate_high,
                'Critical_Instability_Score': critical_score,
                'Moderate_Instability_Score': moderate_score
            })
            
            vital_id += 1

# Add activity-specific vitals to reach 10,000
activities = ['Resting', 'Light_Activity', 'Moderate_Exercise', 'Intense_Exercise', 'Post_Surgery', 'ICU']

while vital_id < 10000:
    vital_type = random.choice(vital_types)
    age_group = random.choice(age_groups)
    activity = random.choice(activities)
    
    vitals_data.append({
        'Vital_ID': f'VITAL{str(vital_id+1).zfill(5)}',
        'Vital_Type': vital_type,
        'Age_Group': age_group,
        'Condition_Modifier': activity,
        'Critical_Low_Threshold': np.random.randint(30, 90),
        'Critical_High_Threshold': np.random.randint(150, 250),
        'Moderate_Low_Threshold': np.random.randint(60, 100),
        'Moderate_High_Threshold': np.random.randint(120, 180),
        'Critical_Instability_Score': np.random.randint(3, 5),
        'Moderate_Instability_Score': np.random.randint(1, 3)
    })
    
    vital_id += 1

vitals_df = pd.DataFrame(vitals_data)
vitals_df.to_csv('/home/claude/3_vital_signs_reference_10k.csv', index=False)
print(f"✅ Vital Signs Reference: {len(vitals_df):,} reference points")

# ============================================================================
# 4. CHRONIC CONDITION MODIFIERS DATASET - 10,000 ROWS
# ============================================================================

print("\n🔄 4/5: Generating Chronic Condition Modifiers Dataset (10,000 rows)...")

chronic_bases = [
    'Diabetes', 'Hypertension', 'Heart Disease', 'COPD', 'Asthma', 'CKD',
    'Liver Disease', 'Cancer', 'HIV/AIDS', 'Arthritis', 'Obesity',
    'Depression', 'Anxiety', 'Thyroid Disorder', 'Autoimmune Disease'
]

chronic_types = ['Type 1', 'Type 2', 'Stage I', 'Stage II', 'Stage III', 'Stage IV',
                 'Mild', 'Moderate', 'Severe', 'Controlled', 'Uncontrolled']

complication_levels = ['Low', 'Moderate', 'High', 'Very High']
departments_list = ['Cardiology', 'Endocrinology', 'Nephrology', 'Pulmonology', 
                   'Rheumatology', 'Oncology', 'Psychiatry', 'General Medicine']

chronic_data = []
chronic_id = 0

for base in chronic_bases:
    for ctype in chronic_types:
        if chronic_id >= 10000:
            break
        
        condition_name = f"{base} {ctype}"
        
        # Risk modifier based on type
        if ctype in ['Severe', 'Uncontrolled', 'Stage IV']:
            modifier = np.random.randint(3, 6)
            complication = np.random.choice(['High', 'Very High'], p=[0.4, 0.6])
        elif ctype in ['Moderate', 'Stage II', 'Stage III']:
            modifier = np.random.randint(2, 4)
            complication = np.random.choice(['Moderate', 'High'], p=[0.6, 0.4])
        else:
            modifier = np.random.randint(1, 3)
            complication = np.random.choice(['Low', 'Moderate'], p=[0.6, 0.4])
        
        # High risk symptoms
        risk_symptoms = np.random.randint(3, 8)
        symptoms_list = [f"Symptom_{i}" for i in range(risk_symptoms)]
        
        # Department
        if 'Diabetes' in base or 'Thyroid' in base:
            dept = 'Endocrinology'
        elif 'Heart' in base or 'Hypertension' in base:
            dept = 'Cardiology'
        elif 'COPD' in base or 'Asthma' in base:
            dept = 'Pulmonology'
        elif 'CKD' in base or 'Kidney' in base:
            dept = 'Nephrology'
        elif 'Cancer' in base:
            dept = 'Oncology'
        elif 'Arthritis' in base:
            dept = 'Rheumatology'
        elif 'Depression' in base or 'Anxiety' in base:
            dept = 'Psychiatry'
        else:
            dept = 'General Medicine'
        
        chronic_data.append({
            'Chronic_ID': f'CHRON{str(chronic_id+1).zfill(5)}',
            'Chronic_Condition': condition_name,
            'Risk_Modifier_Score': modifier,
            'High_Risk_With_Symptoms': ', '.join(symptoms_list),
            'Associated_Department': dept,
            'Complication_Risk_Level': complication
        })
        
        chronic_id += 1

# Add age-related and lifestyle modifiers to reach 10,000
age_modifiers = ['Age 40-50', 'Age 50-60', 'Age 60-70', 'Age 70-80', 'Age 80+']
lifestyle_factors = ['Smoking', 'Alcohol Use', 'Sedentary Lifestyle', 'Poor Diet', 'Stress']
combinations = ['Diabetes + Hypertension', 'Heart Disease + CKD', 'COPD + Heart Disease']

while chronic_id < 10000:
    category = random.choice(['age', 'lifestyle', 'combination'])
    
    if category == 'age':
        condition_name = random.choice(age_modifiers)
        modifier = np.random.randint(1, 4)
    elif category == 'lifestyle':
        condition_name = random.choice(lifestyle_factors)
        modifier = np.random.randint(1, 3)
    else:
        condition_name = random.choice(combinations)
        modifier = np.random.randint(3, 6)
    
    chronic_data.append({
        'Chronic_ID': f'CHRON{str(chronic_id+1).zfill(5)}',
        'Chronic_Condition': condition_name,
        'Risk_Modifier_Score': modifier,
        'High_Risk_With_Symptoms': ', '.join([f"Symptom_{i}" for i in range(np.random.randint(2, 6))]),
        'Associated_Department': random.choice(departments_list),
        'Complication_Risk_Level': random.choice(complication_levels)
    })
    
    chronic_id += 1

chronic_df = pd.DataFrame(chronic_data)
chronic_df.to_csv('/home/claude/4_chronic_condition_modifiers_10k.csv', index=False)
print(f"✅ Chronic Condition Modifiers: {len(chronic_df):,} modifiers")

# ============================================================================
# 5. DOCTOR SPECIALIZATION DATASET - 10,000 ROWS
# ============================================================================

print("\n🔄 5/5: Generating Doctor Specialization Dataset (10,000 rows)...")

specializations = {
    'Emergency': {'count': 1200, 'critical': True, 'max_per_hour': 5},
    'Cardiology': {'count': 1000, 'critical': True, 'max_per_hour': 3},
    'General Medicine': {'count': 1500, 'critical': False, 'max_per_hour': 6},
    'Pulmonology': {'count': 800, 'critical': True, 'max_per_hour': 4},
    'Neurology': {'count': 700, 'critical': True, 'max_per_hour': 3},
    'Gastroenterology': {'count': 600, 'critical': False, 'max_per_hour': 4},
    'Orthopedics': {'count': 900, 'critical': False, 'max_per_hour': 4},
    'Endocrinology': {'count': 500, 'critical': False, 'max_per_hour': 4},
    'Nephrology': {'count': 400, 'critical': False, 'max_per_hour': 3},
    'Oncology': {'count': 600, 'critical': False, 'max_per_hour': 3},
    'Psychiatry': {'count': 500, 'critical': False, 'max_per_hour': 4},
    'Surgery': {'count': 800, 'critical': True, 'max_per_hour': 2},
    'Pediatrics': {'count': 700, 'critical': False, 'max_per_hour': 5},
    'ICU': {'count': 500, 'critical': True, 'max_per_hour': 2},
    'Infectious Disease': {'count': 300, 'critical': False, 'max_per_hour': 4}
}

doctors = []
doctor_id = 0

for spec, info in specializations.items():
    for i in range(info['count']):
        if doctor_id >= 10000:
            break
        
        # Experience distribution
        exp_years = np.random.choice([
            np.random.randint(1, 3),
            np.random.randint(3, 7),
            np.random.randint(7, 15),
            np.random.randint(15, 25),
            np.random.randint(25, 40)
        ], p=[0.15, 0.30, 0.30, 0.20, 0.05])
        
        # Performance score correlates with experience
        base_performance = 5 + (exp_years / 4)
        performance = min(10, base_performance + np.random.uniform(-0.5, 1.5))
        performance = round(max(5, performance), 1)
        
        # Critical certification
        if info['critical']:
            if exp_years >= 5:
                critical_cert = 'Yes'
            elif exp_years >= 3:
                critical_cert = np.random.choice(['Yes', 'No'], p=[0.6, 0.4])
            else:
                critical_cert = np.random.choice(['Yes', 'No'], p=[0.2, 0.8])
        else:
            critical_cert = 'No'
        
        # Subspecialty
        subspecialties = {
            'Cardiology': ['Interventional', 'Electrophysiology', 'Heart Failure', 'Preventive'],
            'Surgery': ['Cardiac', 'Trauma', 'Vascular', 'General', 'Thoracic'],
            'Neurology': ['Stroke', 'Epilepsy', 'Movement Disorders', 'Headache'],
            'Emergency': ['Trauma', 'Critical Care', 'Toxicology', 'Pediatric EM']
        }
        
        if spec in subspecialties:
            preferred = random.choice(subspecialties[spec])
        else:
            preferred = f"{spec} General"
        
        doctors.append({
            'Doctor_ID': f'DOC{str(doctor_id+1).zfill(5)}',
            'Specialization': spec,
            'Subspecialty': preferred,
            'Experience_Years': exp_years,
            'Max_Patients_Per_Hour': info['max_per_hour'],
            'Critical_Case_Certified': critical_cert,
            'Performance_Score': performance,
            'Preferred_Case_Types': f"{spec} Cases",
            'Consultation_Fee': np.random.randint(500, 5000),
            'Availability_Hours_Per_Week': np.random.randint(40, 80)
        })
        
        doctor_id += 1

doctors_df = pd.DataFrame(doctors)
doctors_df.to_csv('/home/claude/5_doctor_specialization_10k.csv', index=False)
print(f"✅ Doctor Specialization: {len(doctors_df):,} doctors")

# Summary
print("\n" + "=" * 80)
print("✨ ALL 5 DATASETS GENERATED SUCCESSFULLY!")
print("=" * 80)

summary_stats = {
    '1. Disease Priority': {
        'rows': len(diseases_df),
        'emergency': (diseases_df['Emergency_Flag'] == 'Yes').sum(),
        'categories': diseases_df['Condition_Category'].nunique()
    },
    '2. Symptom Severity': {
        'rows': len(symptoms_df),
        'emergency_triggers': symptoms_df['Emergency_Trigger'].sum(),
        'departments': symptoms_df['Associated_Department'].nunique()
    },
    '3. Vital Signs Reference': {
        'rows': len(vitals_df),
        'vital_types': vitals_df['Vital_Type'].nunique(),
        'age_groups': vitals_df['Age_Group'].nunique()
    },
    '4. Chronic Conditions': {
        'rows': len(chronic_df),
        'high_risk': (chronic_df['Complication_Risk_Level'] == 'High').sum(),
        'departments': chronic_df['Associated_Department'].nunique()
    },
    '5. Doctors': {
        'rows': len(doctors_df),
        'critical_certified': (doctors_df['Critical_Case_Certified'] == 'Yes').sum(),
        'specializations': doctors_df['Specialization'].nunique()
    }
}

print("\n📊 DATASET SUMMARY:")
for name, stats in summary_stats.items():
    print(f"\n{name}:")
    for key, value in stats.items():
        print(f"   {key}: {value:,}")

print("\n📁 FILES SAVED:")
print("   1_disease_priority_10k.csv")
print("   2_symptom_severity_10k.csv")
print("   3_vital_signs_reference_10k.csv")
print("   4_chronic_condition_modifiers_10k.csv")
print("   5_doctor_specialization_10k.csv")

print("\n🎯 TOTAL MEDICAL RECORDS: 50,000")
print("=" * 80)
