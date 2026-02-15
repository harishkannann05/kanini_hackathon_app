"""
Triage Service — Hybrid AI inference with SHAP explainability.
Stage 1: XGBoost → High vs Not-High
Stage 2: Logistic Regression → Medium vs Low (for Not-High)
SHAP: TreeExplainer for XGBoost feature contributions.
"""
import numpy as np
from models_loader import stage1_model, stage2_model, scaler, feature_cols, threshold, model_version
from utils import build_features

# ── Symptom → Department mapping ──────────────────────────────
SYMPTOM_DEPT_MAP = {
    "chest pain": "Cardiology",
    "palpitations": "Cardiology",
    "shortness of breath": "Pulmonology",
    "cough": "Pulmonology",
    "headache": "Neurology",
    "dizziness": "Neurology",
    "numbness": "Neurology",
    "abdominal pain": "Gastroenterology",
    "vomiting": "Gastroenterology",
    "diarrhea": "Gastroenterology",
    "fever": "General Medicine",
    "weakness": "General Medicine",
}

# Try to load dynamic mapping cache (created by scripts/import_datasets.py)
try:
    import json
    from pathlib import Path
    CACHE = Path(__file__).resolve().parents[1] / "data_cache.json"
    if CACHE.exists():
        with open(CACHE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            cached_map = data.get("symptom_to_department", {})
            # merge: prefer dataset mapping
            for k, v in cached_map.items():
                if k and v:
                    SYMPTOM_DEPT_MAP[k.lower().strip()] = v
except Exception:
    pass

# Priority order for department selection
DEPT_PRIORITY = ["Cardiology", "Neurology", "Pulmonology", "Gastroenterology", "General Medicine"]


def _determine_department(symptoms: list[str]) -> str:
    """Pick highest-priority department based on symptom list."""
    dept_hits: dict[str, int] = {}
    for s in symptoms:
        dept = SYMPTOM_DEPT_MAP.get(s.lower().strip())
        if dept:
            dept_hits[dept] = dept_hits.get(dept, 0) + 1

    if not dept_hits:
        return "General Medicine"

    for dept in DEPT_PRIORITY:
        if dept in dept_hits:
            return dept
    return "General Medicine"


def _compute_shap_explanation(features_df) -> dict:
    """Compute SHAP values for the XGBoost model to explain predictions."""
    try:
        import shap
        explainer = shap.TreeExplainer(stage1_model)
        shap_values = explainer.shap_values(features_df)

        # Get feature names and their SHAP contributions
        feature_names = features_df.columns.tolist()

        # For binary classification, shap_values may be a list
        if isinstance(shap_values, list):
            vals = shap_values[1][0]  # Class 1 (High risk)
        elif len(shap_values.shape) > 1:
            vals = shap_values[0]
        else:
            vals = shap_values[0] if len(shap_values.shape) == 1 else shap_values

        # Create feature contribution pairs
        contributions = []
        for name, val in zip(feature_names, vals):
            contributions.append({"feature": name, "contribution": round(float(val), 4)})

        # Sort by absolute contribution
        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)

        return {
            "top_factors": contributions[:8],
            "base_value": round(float(explainer.expected_value[1] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value), 4),
            "method": "SHAP_TreeExplainer"
        }
    except ImportError:
        # Fallback: use feature importance from XGBoost
        importances = stage1_model.feature_importances_
        feature_names = feature_cols
        contributions = []
        for name, imp in zip(feature_names, importances):
            contributions.append({"feature": name, "contribution": round(float(imp), 4)})
        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        return {
            "top_factors": contributions[:8],
            "base_value": 0.0,
            "method": "feature_importance_fallback"
        }
    except Exception as e:
        return {"top_factors": [], "error": str(e), "method": "error"}


def run_triage(payload: dict) -> dict:
    """
    Run the hybrid ML triage pipeline.
    Returns risk_level, risk_score, confidence, department, SHAP explanation.
    """
    # Build features
    features_df = build_features(payload)

    # Stage 1: XGBoost — High vs Not-High
    stage1_proba = stage1_model.predict_proba(features_df)[0]
    high_prob = float(stage1_proba[1])

    if high_prob >= threshold:
        risk_level = "High"
        risk_score = max(1, min(10, int(round(high_prob * 10))))  # Scale 1-10
        confidence = high_prob
    else:
        # Stage 2: Logistic Regression — Medium vs Low
        scaled = scaler.transform(features_df)
        stage2_proba = stage2_model.predict_proba(scaled)[0]
        # Class 0 = Low, Class 1 = Medium
        medium_prob = float(stage2_proba[1])

        if medium_prob >= 0.5:
            risk_level = "Medium"
            risk_score = max(1, min(10, int(round(medium_prob * 7))))  # Scale 1-7
            confidence = medium_prob
        else:
            risk_level = "Low"
            risk_score = max(1, min(10, int(round((1 - medium_prob) * 4))))  # Scale 1-4
            confidence = 1 - medium_prob

    # Determine department
    department_name = _determine_department(payload.get("symptoms", []))

    # SHAP explanation
    shap_explanation = _compute_shap_explanation(features_df)

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "confidence": round(confidence, 4),
        "department_name": department_name,
        "model_version": model_version,
        "shap_explanation": shap_explanation,
    }


def extract_symptoms_from_text(text: str) -> list[str]:
    """
    Parses natural language text to extract symptoms.
    Uses keyword matching against known symptoms.
    """
    text_lower = text.lower()
    found_symptoms = []
    
    # Simple keyword matching from SYMPTOM_DEPT_MAP
    for symptom in SYMPTOM_DEPT_MAP.keys():
        if symptom in text_lower:
            found_symptoms.append(symptom)
    return found_symptoms

def run_triage_text(text: str) -> dict:
    """
    1. Parse text for symptoms
    2. Run ML prediction
    """
    found_symptoms = extract_symptoms_from_text(text)
             
    # Default payload with extracted symptoms
    payload = {
        "age": 30, # Default
        "gender": "Male", # Default
        "systolic_bp": 120,
        "heart_rate": 72,
        "temperature": 37.0,
        "symptoms": found_symptoms,
        "chronic_conditions": []
    }
    
    return run_triage(payload)
