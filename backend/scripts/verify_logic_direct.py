
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load env from backend/.env explicitly
load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))

# Add backend to path so we can import modules directly
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from db import AsyncSessionLocal
from schemas import VisitRequest
from main import create_visit
from models import Queue
from sqlalchemy import select
import logging

# Disable heavy logging
logging.basicConfig(level=logging.CRITICAL)

async def test():
    print("Testing create_visit logic...")
    async with AsyncSessionLocal() as session:
        payload = VisitRequest(
            age=55,
            gender='Male',
            systolic_bp=160,
            heart_rate=110,
            temperature=38.5,
            symptoms=['chest pain', 'shortness of breath'],
            chronic_conditions=['hypertension', 'diabetes'],
            visit_type='Walk-In'
        )
        try:
            # We need to simulate the background tasks or ensure they run?
            # create_visit is async, so awaiting it should run logic.
            response = await create_visit(payload, session)
            print("Success!")
            print(f"Visit ID: {response.visit_id}")
            print(f"Risk Level: {response.risk_level}") # Should be High/Medium
            print(f"Department: {response.department}")
            
            # Check Queue Priority
            stmt = select(Queue).where(Queue.visit_id == response.visit_id)
            q_res = await session.execute(stmt)
            q_entry = q_res.scalars().first()
            if q_entry:
                print(f"Queue Priority Score: {q_entry.priority_score}")
                print(f"Is Emergency: {q_entry.is_emergency}")
            else:
                print("No queue entry found (maybe doctor not assigned?)")

        except Exception as e:
            print(f"Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test())
