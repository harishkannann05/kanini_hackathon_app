"""
OCR Service — Extracts text from uploaded documents and maps to
chronic conditions / symptom flags to merge with intake data.
Uses pytesseract if available, otherwise graceful degradation.
"""
import os

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("[OCR] pytesseract or Pillow not installed. OCR disabled.")


# ── Keyword → condition/symptom mapping ───────────────────────
CHRONIC_KEYWORDS = {
    "hypertension": "hypertension",
    "high blood pressure": "hypertension",
    "diabetes": "diabetes",
    "diabetic": "diabetes",
    "type 2 diabetes": "diabetes",
    "type 1 diabetes": "diabetes",
    "heart disease": "heart disease",
    "cardiac": "heart disease",
    "coronary": "heart disease",
    "asthma": "asthma",
    "chronic kidney": "chronic kidney disease",
    "ckd": "chronic kidney disease",
    "renal failure": "chronic kidney disease",
}

SYMPTOM_KEYWORDS = {
    "chest pain": "chest pain",
    "shortness of breath": "shortness of breath",
    "dyspnea": "shortness of breath",
    "fever": "fever",
    "cough": "cough",
    "headache": "headache",
    "dizzy": "dizziness",
    "dizziness": "dizziness",
    "vomit": "vomiting",
    "nausea": "vomiting",
    "diarrhea": "diarrhea",
    "abdominal pain": "abdominal pain",
    "stomach pain": "abdominal pain",
    "palpitation": "palpitations",
    "weakness": "weakness",
    "fatigue": "weakness",
    "numbness": "numbness",
    "tingling": "numbness",
}


def extract_text_from_file(file_path: str) -> str:
    """Extracts text from an image file using pytesseract."""
    if not OCR_AVAILABLE:
        return ""
    
    if not os.path.exists(file_path):
        return ""

    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"[OCR] Error processing {file_path}: {e}")
        return ""


def detect_conditions(text: str) -> dict:
    """
    Scans extracted text for medical keywords.
    Returns detected chronic conditions and symptoms.
    """
    text_lower = text.lower()

    detected_chronic = set()
    for keyword, condition in CHRONIC_KEYWORDS.items():
        if keyword in text_lower:
            detected_chronic.add(condition)

    detected_symptoms = set()
    for keyword, symptom in SYMPTOM_KEYWORDS.items():
        if keyword in text_lower:
            detected_symptoms.add(symptom)

    return {
        "chronic_conditions": list(detected_chronic),
        "symptoms": list(detected_symptoms),
        "raw_text": text[:500]  # Store first 500 chars for audit
    }


def merge_ocr_with_payload(payload: dict, ocr_results: dict) -> dict:
    """
    Merges OCR-detected conditions/symptoms with the original intake payload.
    Does not duplicate existing entries.
    """
    merged = payload.copy()

    existing_symptoms = set(s.strip().lower() for s in merged.get("symptoms", []))
    for symptom in ocr_results.get("symptoms", []):
        if symptom.lower() not in existing_symptoms:
            merged["symptoms"].append(symptom)

    existing_chronic = set(c.strip().lower() for c in merged.get("chronic_conditions", []))
    for condition in ocr_results.get("chronic_conditions", []):
        if condition.lower() not in existing_chronic:
            merged["chronic_conditions"].append(condition)

    return merged
