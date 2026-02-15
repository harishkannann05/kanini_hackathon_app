"""
ML Insights Service - Extract key highlights from patient medical records
Uses NLP and pattern matching to identify important medical information
"""
from models import MedicalRecord, Patient, Visit, Prescription
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import re
from typing import List, Dict

# Critical keywords to highlight
CHRONIC_CONDITIONS = [
    "diabetes", "hypertension", "heart disease", "asthma", "copd", "cancer",
    "stroke", "kidney disease", "liver disease", "hiv", "hepatitis"
]

HIGH_RISK_SYMPTOMS = [
    "chest pain", "shortness of breath", "unconscious", "bleeding", "seizure",
    "stroke", "heart attack", "severe pain", "difficulty breathing"
]

MEDICATION_PATTERNS = [
    r"(insulin|metformin|aspirin|warfarin|statins?|beta.?blockers?)",
    r"(antibiotics?|steroids?|chemotherapy|immunosuppressants?)"
]


async def extract_key_insights(db: AsyncSession, patient_id: str) -> Dict:
    """
    Extract and highlight key medical insights for a patient.
    Returns: {
        "chronic_conditions": [...],
        "recent_high_risk": [...],
        "medications": [...],
        "recurring_symptoms": {...},
        "summary": "..."
    }
    """
    
    # Fetch patient data
    patient_stmt = select(Patient).where(Patient.patient_id == patient_id)
    patient_result = await db.execute(patient_stmt)
    patient = patient_result.scalars().first()
    
    if not patient:
        return {"error": "Patient not found"}
    
    # Fetch medical records (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    records_stmt = (
        select(MedicalRecord)
        .join(Visit, MedicalRecord.visit_id == Visit.visit_id)
        .where(Visit.patient_id == patient_id)
       .where(MedicalRecord.created_at >= six_months_ago)
        .order_by(MedicalRecord.created_at.desc())
    )
    records_result = await db.execute(records_stmt)
    records = records_result.scalars().all()
    
    # Initialize insights
    insights = {
        "chronic_conditions": [],
        "recent_high_risk": [],
        "medications": [],
        "recurring_symptoms": {},
        "visit_count_last_6_months": len(records),
        "summary": ""
    }
    
    # 1. Extract chronic conditions from patient record
    if patient.pre_existing_conditions:
        conditions_text = patient.pre_existing_conditions.lower()
        for condition in CHRONIC_CONDITIONS:
            if condition in conditions_text:
                insights["chronic_conditions"].append({
                    "condition": condition.title(),
                    "confidence": 0.9,
                    "source": "Patient Record"
                })
    
    # 2. Analyze medical records
    symptom_counts = {}
    
    for record in records:
        # Check for high-risk diagnoses
        if record.diagnosis:
            diagnosis_lower = record.diagnosis.lower()
            for risk_symptom in HIGH_RISK_SYMPTOMS:
                if risk_symptom in diagnosis_lower:
                    insights["recent_high_risk"].append({
                        "finding": risk_symptom.title(),
                        "date": record.created_at.strftime("%Y-%m-%d"),
                        "confidence": 0.85
                    })
        
        # Track recurring symptoms
        if record.syndrome_identified:
            syndrome = record.syndrome_identified.strip()
            if syndrome:
                symptom_counts[syndrome] = symptom_counts.get(syndrome, 0) + 1
    
    # 3. Find prescriptions
    for record in records[:5]:  # Last 5 visits
        presc_stmt = select(Prescription).where(Prescription.record_id == record.record_id)
        presc_result = await db.execute(presc_stmt)
        prescriptions = presc_result.scalars().all()
        
        for presc in prescriptions:
            if presc.medication_name and presc.medication_name not in [m["name"] for m in insights["medications"]]:
                insights["medications"].append({
                    "name": presc.medication_name,
                    "dosage": presc.dosage or "N/A",
                    "prescribed_date": record.created_at.strftime("%Y-%m-%d")
                })
    
    # 4. Identify recurring symptoms (>= 2 occurrences)
    insights["recurring_symptoms"] = {
        symptom: count for symptom, count in symptom_counts.items() if count >= 2
    }
    
    # 5. Generate summary
    summary_parts = []
    if insights["chronic_conditions"]:
        summary_parts.append(f"{len(insights['chronic_conditions'])} chronic condition(s) on record")
    if insights["recent_high_risk"]:
        summary_parts.append(f"{len(insights['recent_high_risk'])} recent high-risk finding(s)")
    if insights["visit_count_last_6_months"] > 3:
        summary_parts.append(f"Frequent visitor: {insights['visit_count_last_6_months']} visits in 6 months")
    if insights["recurring_symptoms"]:
        summary_parts.append(f"{len(insights['recurring_symptoms'])} recurring symptom(s)")
    
    insights["summary"] = "; ".join(summary_parts) if summary_parts else "No significant patterns detected"
    
    return insights


async def get_patient_insights_text(db: AsyncSession, patient_id: str) -> str:
    """Returns a formatted text summary for quick display."""
    insights = await extract_key_insights(db, patient_id)
    
    if "error" in insights:
        return insights["error"]
    
    lines = [f"**Patient Insights Summary**\n"]
    
    if insights["chronic_conditions"]:
        lines.append("🔴 **Chronic Conditions:**")
        for cond in insights["chronic_conditions"]:
            lines.append(f"  - {cond['condition']}")
    
    if insights["recent_high_risk"]:
        lines.append("\n⚠️ **Recent High-Risk Findings:**")
        for finding in insights["recent_high_risk"][:3]:  # Top 3
            lines.append(f"  - {finding['finding']} ({finding['date']})")
    
    if insights["medications"]:
        lines.append("\n💊 **Current Medications:**")
        for med in insights["medications"][:5]:  # Top 5
            lines.append(f"  - {med['name']} ({med['dosage']})")
    
    if insights["recurring_symptoms"]:
        lines.append("\n🔄 **Recurring Symptoms:**")
        for symptom, count in list(insights["recurring_symptoms"].items())[:3]:
            lines.append(f"  - {symptom}: {count} occurrences")
    
    lines.append(f"\n📊 {insights['summary']}")
    
    return "\n".join(lines)
