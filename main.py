from fastapi import FastAPI
import joblib
import json
import pandas as pd
from schemas import PatientInput
from utils import age_group, compute_vital_score
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Load models
stage1_model = joblib.load("models/stage1_xgb.pkl")
stage2_model = joblib.load("models/stage2_logistic.pkl")
scaler = joblib.load("models/scaler.pkl")

with open("models/model_metadata.json") as f:
    metadata = json.load(f)

feature_cols = metadata["feature_columns"]
threshold = metadata["stage1_threshold"]

@app.post("/predict")
def predict_risk(patient: PatientInput):

    # Build feature dict
    data = {col: 0 for col in feature_cols}

    data["Age"] = patient.age
    data["Systolic_BP"] = patient.systolic_bp
    data["Heart_Rate"] = patient.heart_rate
    data["Temperature"] = patient.temperature
    data["Age_Group"] = age_group(patient.age)

    # Vital score
    data["Vital_Score"] = compute_vital_score(
        patient.systolic_bp,
        patient.heart_rate,
        patient.temperature
    )

    # Map symptoms
    for sym in patient.symptoms:
        key = sym.lower().replace(" ", "_")
        if key in data:
            data[key] = 1

    # Chronic mapping
    chronic_score = 0
    for cond in patient.chronic_conditions:
        key = f"chronic_{cond.lower().replace(' ', '_')}"
        if key in data:
            data[key] = 1
            chronic_score += 1

    data["Chronic_Score"] = chronic_score

    # Convert to DataFrame
    df_input = pd.DataFrame([data])[feature_cols]

    # Stage 1
    proba = stage1_model.predict_proba(df_input)[:,1][0]

    if proba >= threshold:
        risk = "High"
    else:
        df_scaled = scaler.transform(df_input)
        stage2_pred = stage2_model.predict(df_scaled)[0]
        risk = "Medium" if stage2_pred == 1 else "Low"

    return {
        "risk_level": risk,
        "stage1_probability": float(proba)
    }
