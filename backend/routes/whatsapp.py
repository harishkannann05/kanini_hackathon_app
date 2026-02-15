from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db
from models import WhatsappBooking, Patient
from services.triage_service import run_triage_text
import uuid

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

@router.post("/webhook")
async def whatsapp_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Stub for WhatsApp Webhook.
    Receives message, parses symptoms, runs triage, and replies.
    """
    form_data = await request.form()
    # Twilio/WhatsApp format usually
    sender = form_data.get("From")
    body = form_data.get("Body")
    
    if not body:
         return {"status": "ignored", "reason": "no body"}

    # Simple logic: If body contains "triage:", run triage
    # Else, welcome message
    
    reply_message = ""
    
    if "triage:" in body.lower() or "book:" in body.lower():
        text = body.lower().replace("triage:", "").replace("book:", "").strip()
        
        from services.triage_service import extract_symptoms_from_text
        from services.visit_service import create_visit_orchestration
        
        found_symptoms = extract_symptoms_from_text(text)
        
        # Defaults for WhatsApp user
        payload = {
            "age": 30, 
            "gender": "Male", 
            "systolic_bp": 120,
            "heart_rate": 72,
            "temperature": 37.0,
            "symptoms": found_symptoms if found_symptoms else [text], # Fallback to raw text if no keywords
            "chronic_conditions": [],
            "visit_type": "Online",
            "phone_number": sender.replace("whatsapp:", "")
        }
        
        try:
            async with db.begin():
                result = await create_visit_orchestration(db, payload)
                
                reply_message = (
                    f"✅ Appointment Booked!\n"
                    f"Risk: {result['risk_level']}\n"
                    f"Dept: {result['department']}\n"
                    f"Queue Position: #{result['queue_position']}\n"
                    f"Est. Wait: {result['estimated_wait_minutes']} mins"
                )
                
                # Also save to WhatsappBooking for specific logs if needed
                # But visit_service handles visit/patient/assignment/log creation.
                # Use WhatsappBooking table only if we want to track raw request?
                # For now, create_visit_orchestration creates the VISIT record which is the source of truth.
                
        except Exception as e:
            reply_message = f"Error: {str(e)}"
            
    else:
        reply_message = "Welcome! Send 'Triage: [symptoms]' to book an appointment."

    return Response(content=f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Message>{reply_message}</Message></Response>", media_type="application/xml")
