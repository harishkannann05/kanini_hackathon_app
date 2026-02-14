import os
import sys

# Ensure project root is on sys.path so package imports work when executed from scripts/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from services.triage_service import run_triage

payload = {
    "age": 45,
    "systolic_bp": 140,
    "heart_rate": 95,
    "temperature": 38.2,
    "symptoms": ["chest pain", "shortness of breath"],
    "chronic_conditions": ["hypertension"]
}

print("Running triage...\n")
res = run_triage(payload)
print(res)
