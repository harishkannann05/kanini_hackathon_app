import pytest
from services.triage_service import run_triage


def test_triage_high():
    payload = {
        "age": 60,
        "systolic_bp": 160,
        "heart_rate": 110,
        "temperature": 39.0,
        "symptoms": ["chest pain", "shortness of breath"],
        "chronic_conditions": ["hypertension"]
    }
    res = run_triage(payload)
    assert 'risk_level' in res
    assert 'risk_score' in res
    assert res['risk_level'] in ('High','Medium','Low')
