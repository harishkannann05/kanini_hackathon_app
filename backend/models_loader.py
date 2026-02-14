"""
ML Model Loader — Loads trained models and metadata at startup.
All models are loaded once and reused across requests.
"""
import joblib
import json
import os

# Resolve paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")

# ── Load metadata ──────────────────────────────────────────────
with open(os.path.join(MODELS_DIR, "model_metadata.json"), "r") as f:
    metadata = json.load(f)

feature_cols: list[str] = metadata["feature_columns"]
threshold: float = metadata["stage1_threshold"]
model_version: str = metadata.get("model_version", "unknown")
hybrid_accuracy: float = metadata.get("hybrid_accuracy", 0.0)

# ── Load Stage 1 — XGBoost (High vs Not-High) ─────────────────
stage1_model = joblib.load(os.path.join(MODELS_DIR, "stage1_xgb.pkl"))

# ── Load Stage 2 — Logistic Regression (Medium vs Low) ────────
stage2_model = joblib.load(os.path.join(MODELS_DIR, "stage2_logistic.pkl"))

# ── Load Scaler ────────────────────────────────────────────────
scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))

print(f"[ModelLoader] Loaded models v{model_version} | "
      f"Threshold: {threshold:.4f} | "
      f"Accuracy: {hybrid_accuracy:.4f} | "
      f"Features: {len(feature_cols)}")
