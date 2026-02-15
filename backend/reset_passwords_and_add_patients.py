import sqlite3
import bcrypt
import requests
import random
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def reset_passwords():
    print("Resetting passwords to '1234'...")
    # Calculate path: backend/../backend_dev.db => project_root/backend_dev.db
    # This script is in backend/
    db_path = Path(__file__).resolve().parent.parent / "backend_dev.db"
    
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path}")
        # Fallback to backend/db.sqlite if exists or check current dir
        if (Path(__file__).parent / "backend_dev.db").exists():
            db_path = Path(__file__).parent / "backend_dev.db"
            print(f"Found at {db_path}")
        else:
            return

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Generate hash for '1234'
        hashed_pw = bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute("UPDATE users SET password_hash = ?", (hashed_pw,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        print(f"Success: Updated {count} users' passwords.")
    except Exception as e:
        print(f"Error updating passwords: {e}")

def add_patients():
    print("\nAdding 10 random patients...")
    symptom_groups = [
        {"symptoms": ["Joint pain", "Swollen knee"], "chronic": ["Arthritis"]},
        {"symptoms": ["Severe headache", "Vision loss"], "chronic": ["Migraine"]},
        {"symptoms": ["High fever", "Cough", "Throat pain"], "chronic": []},
        {"symptoms": ["Stomach pain", "Vomiting"], "chronic": ["Gastritis"], "age_max": 12},
        {"symptoms": ["Chest heavy", "Breathlessness"], "chronic": ["Hypertension"]},
        {"symptoms": ["Itchy skin", "Rash on back"], "chronic": ["Eczema"]},
        {"symptoms": ["Depressed mood", "Insomnia"], "chronic": []}
    ]

    names = ["Michael", "Emma", "Olivia", "Liam", "Noah", "James", "Sophia", "Lucas", "Ethan", "Mia", "Isabella", "Mason", "Logan", "Elijah"]

    for i in range(10):
        group = random.choice(symptom_groups)
        name = random.choice(names) + f" {random.randint(1,100)}"
        
        age = random.randint(1, group.get("age_max", 80))
        gender = random.choice(["Male", "Female"])
        
        payload = {
            "full_name": name,
            "age": age,
            "gender": gender,
            "phone_number": f"9876{random.randint(100000, 999999)}",
            "symptoms": group["symptoms"],
            "chronic_conditions": group.get("chronic", []),
            "systolic_bp": random.randint(110, 150),
            "heart_rate": random.randint(70, 110),
            "temperature": random.choice([36.5, 37.0, 38.5, 39.0]),
            "visit_type": "Walk-In",
            "use_preferred_doctor": True
        }

        try:
            r = requests.post(f"{BASE_URL}/visits", json=payload)
            if r.status_code == 200:
                data = r.json()
                print(f"Added {name} -> Risk: {data.get('risk_level')}, Dept: {data.get('department')} (AI Assigned)")
            else:
                print(f"Failed to add {name}: {r.text}")
        except Exception as e:
            print(f"Request failed: {e}")
        
        time.sleep(0.3)

if __name__ == "__main__":
    reset_passwords()
    add_patients()
