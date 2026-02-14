import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def log(msg, success=True):
    icon = "✅" if success else "❌"
    print(f"{icon} {msg}")

try:
    # 1. Check Health (UI)
    print("\n--- 1. Checking UI Endpoints ---")
    try:
        r = requests.get(f"{BASE_URL}/")
        log(f"Root UI: {r.status_code}", r.status_code==200)
    except:
        log("Root UI unreachable", False)
    
    try:
        r = requests.get(f"{BASE_URL}/test-ui")
        log(f"Test UI: {r.status_code}", r.status_code==200)
    except:
        log("Test UI unreachable", False)

    # 2. Check Static Data
    print("\n--- 2. Checking Static Data ---")
    r = requests.get(f"{BASE_URL}/doctors")
    if r.status_code == 200:
        docs = r.json()
        log(f"Doctors endpoint: {len(docs)} doctors found", len(docs) > 0)
    else:
        log(f"Doctors endpoint failed: {r.status_code}", False)
    
    r = requests.get(f"{BASE_URL}/stats")
    log(f"Stats endpoint: {r.status_code}", r.status_code==200)

    # 3. Create Visit
    print("\n--- 3. Creating Visit (AI Triage) ---")
    payload = {
        "age": 45, "gender": "Male", "systolic_bp": 140, "heart_rate": 95, "temperature": 37.5,
        "symptoms": ["chest pain", "shortness of breath"],
        "chronic_conditions": ["hypertension"],
        "visit_type": "Walk-In",
        "uploaded_documents": []
    }
    r = requests.post(f"{BASE_URL}/visits", json=payload)
    if r.status_code == 200:
        data = r.json()
        log(f"Visit created! Risk: {data.get('risk_level')} (Score: {data.get('risk_score')})")
        log(f"Department: {data.get('department')} -> Doctor: {data.get('doctor_id')}")
        if 'shap_explanation' in data:
            log("SHAP explanation present")
    else:
        log(f"Visit creation failed: {r.status_code} {r.text}", False)

except Exception as e:
    log(f"Connection failed: {e}", False)
