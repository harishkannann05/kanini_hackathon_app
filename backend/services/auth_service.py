
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User, Doctor, Patient, Department
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from db import get_db
import jwt
import os
import uuid
from datetime import datetime, timedelta

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGO = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480 # 8 hours

import bcrypt
from fastapi.security import OAuth2PasswordBearer

# pwd_context removed as we use bcrypt directly
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

VALID_ROLES = ["Admin", "Doctor", "Recipient", "Patient"]

def verify_password(plain_password: str, hashed_password: str):
    """Verify a plain password against a hashed password using bcrypt."""
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def get_password_hash(password: str):
    """Hash a password using bcrypt."""
    # Truncate to 72 bytes (bcrypt max length)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

async def create_user(
    db: AsyncSession,
    full_name: str,
    email: str,
    password: str,
    role: str = "Recipient",
    phone_number: str | None = None,
    age: int | None = None,
    gender: str | None = None,
    department_id: str | None = None,
    department_name: str | None = None,
    specialization: str | None = None,
    experience_years: int | None = None,
) -> dict:
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {VALID_ROLES}")

    # Check if user exists
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    pw_hash = get_password_hash(password)
    new_user_id = uuid.uuid4()
    user = User(
        user_id=new_user_id,
        full_name=full_name,
        email=email,
        password_hash=pw_hash,
        role=role,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    # Create role-specific profiles
    if role == "Doctor":
        if not department_id and department_name:
            dept_stmt = select(Department.department_id).where(
                Department.name.ilike(department_name)
            )
            dept_res = await db.execute(dept_stmt)
            department_id = dept_res.scalar_one_or_none()

        if not department_id:
            raise HTTPException(status_code=400, detail="Doctor must have a valid department")

        # Ensure UUID types for SQLite UUID emulation
        if isinstance(department_id, str):
            try:
                department_id = uuid.UUID(department_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid department_id")

        doctor = Doctor(
            doctor_id=uuid.uuid4(),
            user_id=new_user_id,
            department_id=department_id,
            specialization=specialization,
            experience_years=experience_years or 0,
            is_available=True,
        )
        db.add(doctor)

    if role == "Patient":
        if age is None or gender is None:
            raise HTTPException(status_code=400, detail="Patient registration requires age and gender")

        patient = Patient(
            patient_id=uuid.uuid4(),
            user_id=new_user_id,
            full_name=full_name,
            phone_number=phone_number,
            age=age,
            gender=gender,
            symptoms="Initial registration",
            blood_pressure="120/80",
            heart_rate=72,
            temperature=37.0,
            pre_existing_conditions=None,
            risk_level=None,
        )
        db.add(patient)

    return {"user_id": str(user.user_id), "email": user.email, "role": user.role}


async def authenticate_user(db: AsyncSession, email: str, password: str) -> dict | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        return None
    if not verify_password(password, user.password_hash or ""):
        return None
    
    # create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + access_token_expires
    payload = {
        "sub": str(user.user_id),
        "role": user.role,
        "exp": expire
    }
    encoded_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    
    response = {
        "access_token": encoded_token,
        "token_type": "bearer",
        "user_id": str(user.user_id),
        "role": user.role,
        "full_name": user.full_name
    }

    if user.role == 'Doctor':
        stmt = select(Doctor.doctor_id).where(Doctor.user_id == user.user_id)
        d_res = await db.execute(stmt)
        doctor_id = d_res.scalar_one_or_none()
        if doctor_id:
            response["doctor_id"] = str(doctor_id)
            
    return response


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> dict:
    # Note: db dependency is injected in main.py, but we define signature here.
    # In main.py we will override this or pass db explicitly if needed 
    # BUT FastAPI dependency injection requires db to be valid.
    # To avoid circular imports with get_db, we might need to define this in main or a separate dependencies file.
    # Let's keep the logic simple: parse token here, but we need DB to get full user object if we want.
    # For now, let's just return the payload claims or a partial User object.
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    if db is not None:
        stmt = select(User).where(User.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if user:
            return {
                "user_id": str(user.user_id),
                "role": user.role,
                "full_name": user.full_name,
                "email": user.email,
            }

    return {"user_id": user_id, "role": role}
