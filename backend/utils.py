"""
Feature Engineering — Transforms raw patient intake into the 24-feature
DataFrame expected by the trained models.

Feature columns from model_metadata.json:
  Age, Systolic_BP, Heart_Rate, Temperature,
  Vital_Score, Chronic_Score, Age_Group,
  chest_pain, shortness_of_breath, fever, cough, headache,
  dizziness, vomiting, diarrhea, abdominal_pain, palpitations,
  weakness, numbness,
  chronic_hypertension, chronic_diabetes, chronic_heart,
  chronic_asthma, chronic_ckd
"""
import pandas as pd
from models_loader import feature_cols

# ── Known symptom columns (one-hot) ───────────────────────────
SYMPTOM_COLUMNS = [
    "chest_pain", "shortness_of_breath", "fever", "cough", "headache",
    "dizziness", "vomiting", "diarrhea", "abdominal_pain", "palpitations",
    "weakness", "numbness"
]

# ── Known chronic condition columns (one-hot) ─────────────────
CHRONIC_COLUMNS = [
    "chronic_hypertension", "chronic_diabetes", "chronic_heart",
    "chronic_asthma", "chronic_ckd"
]

# ── Symptom name → column name mapping ────────────────────────
SYMPTOM_MAP = {
    "chest pain": "chest_pain",
    "shortness of breath": "shortness_of_breath",
    "fever": "fever",
    "cough": "cough",
    "headache": "headache",
    "dizziness": "dizziness",
    "vomiting": "vomiting",
    "diarrhea": "diarrhea",
    "abdominal pain": "abdominal_pain",
    "palpitations": "palpitations",
    "weakness": "weakness",
    "numbness": "numbness",
}

# ── Chronic condition name → column name mapping ──────────────
CHRONIC_MAP = {
    "hypertension": "chronic_hypertension",
    "diabetes": "chronic_diabetes",
    "heart disease": "chronic_heart",
    "asthma": "chronic_asthma",
    "chronic kidney disease": "chronic_ckd",
    "ckd": "chronic_ckd",
}


def compute_vital_score(systolic_bp: float, heart_rate: float, temperature: float) -> float:
    """
    Computes a composite vital score.
    Higher score = more abnormal vitals.
    """
    score = 0.0

    # Blood pressure deviation from normal (120)
    bp_deviation = abs(systolic_bp - 120)
    if bp_deviation > 40:
        score += 3
    elif bp_deviation > 20:
        score += 2
    elif bp_deviation > 10:
        score += 1

    # Heart rate deviation from normal (72)
    hr_deviation = abs(heart_rate - 72)
    if hr_deviation > 40:
        score += 3
    elif hr_deviation > 20:
        score += 2
    elif hr_deviation > 10:
        score += 1

    # Temperature deviation from normal (37.0°C / 98.6°F)
    temp_deviation = abs(temperature - 37.0)
    if temp_deviation > 2.0:
        score += 3
    elif temp_deviation > 1.0:
        score += 2
    elif temp_deviation > 0.5:
        score += 1

    return score


def compute_chronic_score(chronic_flags: dict[str, int]) -> float:
    """
    Computes a chronic condition severity multiplier.
    More chronic conditions = higher score.
    """
    active = sum(chronic_flags.values())
    if active >= 3:
        return 3.0
    elif active == 2:
        return 2.0
    elif active == 1:
        return 1.0
    return 0.0


def compute_age_group(age: int) -> int:
    """
    Maps age to a group index.
    0: 0-17 (child), 1: 18-39 (young adult), 2: 40-59 (middle), 3: 60+ (senior)
    """
    if age < 18:
        return 0
    elif age < 40:
        return 1
    elif age < 60:
        return 2
    else:
        return 3


def build_features(payload: dict) -> pd.DataFrame:
    """
    Transforms a raw patient intake payload into a DataFrame
    with the exact 24 feature columns expected by the ML models.
    """
    # ── Extract raw values ──
    age = payload.get("age", 30)
    systolic_bp = payload.get("systolic_bp", 120)
    heart_rate = payload.get("heart_rate", 72)
    temperature = payload.get("temperature", 37.0)
    symptoms = [s.strip().lower() for s in payload.get("symptoms", [])]
    chronic_conditions = [c.strip().lower() for c in payload.get("chronic_conditions", [])]

    # ── Symptom one-hot encoding ──
    symptom_flags = {col: 0 for col in SYMPTOM_COLUMNS}
    for symptom in symptoms:
        col = SYMPTOM_MAP.get(symptom)
        if col:
            symptom_flags[col] = 1

    # ── Chronic condition one-hot encoding ──
    chronic_flags = {col: 0 for col in CHRONIC_COLUMNS}
    for condition in chronic_conditions:
        col = CHRONIC_MAP.get(condition)
        if col:
            chronic_flags[col] = 1

    # ── Engineered features ──
    vital_score = compute_vital_score(systolic_bp, heart_rate, temperature)
    chronic_score = compute_chronic_score(chronic_flags)
    age_group = compute_age_group(age)

    # ── Build row ──
    row = {
        "Age": age,
        "Systolic_BP": systolic_bp,
        "Heart_Rate": heart_rate,
        "Temperature": temperature,
        "Vital_Score": vital_score,
        "Chronic_Score": chronic_score,
        "Age_Group": age_group,
        **symptom_flags,
        **chronic_flags,
    }

    df = pd.DataFrame([row])
    # Ensure column order matches model expectations
    df = df[feature_cols]
    return df
