from pydantic import BaseModel
from typing import List

class PatientInput(BaseModel):
    age: int
    gender: str
    systolic_bp: int
    heart_rate: int
    temperature: float
    symptoms: List[str]
    chronic_conditions: List[str]
