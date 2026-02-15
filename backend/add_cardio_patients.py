import requests
import random
import time

BASE_URL = "http://localhost:8000"

def add_patients():
    # 1. Fetch Doctors to find Cardiology dept
    print("Fetching doctors...")
    try:
        resp = requests.get(f"{BASE_URL}/doctors")
        if resp.status_code != 200:
            print(f"Failed to fetch doctors: {resp.text}")
            return
        doctors = resp.json()
    except Exception as e:
        print(f"Error connecting: {e}")
        return

    # Find Cardiology doctor
    cardio_docs = [d for d in doctors if d.get("department_name") and "Cardio" in d.get("department_name")]
    
    target_doc_id = None
    if not cardio_docs:
        print("No Cardiology doctors found! Will rely on AI routing based on symptoms.")
    else:
        target_doc = cardio_docs[0]
        target_doc_id = target_doc["doctor_id"]
        print(f"Targeting Dr. {target_doc['full_name']} ({target_doc['department_name']})")

    # 2. Add 5 Patients
    patients_data = [
        {"name": "Aravind", "age": 44, "gender": "Male", "symptoms": ["Chest pain", "Headache"]},
        {"name": "Manoj", "age": 58, "gender": "Male", "symptoms": ["Palpitations", "Dizziness", "Fever"]},
        {"name": "John", "age": 62, "gender": "Male", "symptoms": ["Severe chest tightness", "Sweating"]},
        {"name": "Sarah", "age": 50, "gender": "Female", "symptoms": ["Shortness of breath", "Fatigue"]},
        {"name": "Priya", "age": 41, "gender": "Female", "symptoms": ["Irregular heartbeat", "Anxiety"]}
    ]

    for p in patients_data:
        payload = {
            "full_name": p["name"],
            "age": p["age"],
            "gender": p["gender"],
            "phone_number": f"9876{random.randint(100000, 999999)}",
            "symptoms": p["symptoms"],
            "systolic_bp": random.randint(130, 180),
            "heart_rate": random.randint(85, 120),
            "temperature": 37.2,
            "visit_type": "Walk-In",
            "use_preferred_doctor": True
        }
        
        # If we found a doctor in Cardiology, try to assign manually to ensure they land there
        if target_doc_id:
            payload["manual_doctor_id"] = target_doc_id

        try:
            r = requests.post(f"{BASE_URL}/visits", json=payload)
            if r.status_code == 200:
                data = r.json()
                print(f"Added {p['name']} -> Risk: {data.get('risk_level')}, Dept: {data.get('department')}")
            else:
                print(f"Failed to add {p['name']}: {r.text}")
        except Exception as e:
            print(f"Request failed: {e}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    add_patients()
