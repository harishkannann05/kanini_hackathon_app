from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User
from passlib.hash import bcrypt
import jwt
import os
import uuid
from datetime import datetime, timedelta

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGO = "HS256"

async def create_user(db: AsyncSession, full_name: str, email: str, password: str, role: str = "Recipient") -> dict:
    pw_hash = bcrypt.hash(password)
    user = User(
        user_id=str(uuid.uuid4()),
        full_name=full_name,
        email=email,
        password_hash=pw_hash,
        role=role,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return {"user_id": str(user.user_id), "email": user.email}


async def authenticate_user(db: AsyncSession, email: str, password: str) -> dict | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        return None
    if not bcrypt.verify(password, user.password_hash or ""):
        return None
    # create token
    payload = {
        "sub": str(user.user_id),
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return {"access_token": token, "token_type": "bearer", "user_id": str(user.user_id), "role": user.role}
