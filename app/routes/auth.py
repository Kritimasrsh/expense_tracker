import os
from random import randint
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi_mail import MessageSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import get_db
from app.config.mail import fastmail
from app.models import User
from app.models.otp import OTP
from app.auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def generate_otp_code() -> str:
    return f"{randint(100000, 999999):06d}"


async def send_otp_email(email: str, code: str) -> bool:
    message = MessageSchema(
        subject="Fast Expense Tracker OTP",
        recipients=[email],
        body=f"Your login OTP is: {code}\nUse this code within 5 minutes.",
        subtype="plain",
    )

    try:
        await fastmail.send_message(message)
        return True
    except Exception as exc:
        print("OTP email send failed:", exc)
        return False


# SIGNUP
@router.post("/signup")
async def signup(
    email: str = Body(...),
    password: str = Body(...),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User).where(User.email == email)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=email,
        password=hash_password(password)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token({"user_id": user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# LOGIN (Step 1: credentials + OTP send)
@router.post("/login")
async def login(
    email: str = Body(...),
    password: str = Body(...),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Wrong password")

    code = generate_otp_code()
    otp = OTP(
        user_id=user.id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        used=False,
    )

    db.add(otp)
    await db.commit()
    await db.refresh(otp)

    sent = await send_otp_email(user.email, code)
    response = {
        "otp_sent": True,
        "message": "OTP sent to your email.",
    }

    if not sent or not os.getenv("EMAIL"):
        response["debug_otp"] = code
        response["message"] = "OTP generated. Email sending failed or email is not configured. Use debug_otp to complete login."

    return response


# VERIFY OTP (Step 2: issue token)
@router.post("/verify-otp")
async def verify_otp(
    email: str = Body(...),
    otp_code: str = Body(...),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.utcnow()
    otp_result = await db.execute(
        select(OTP).where(
            OTP.user_id == user.id,
            OTP.code == otp_code,
            OTP.used == False,
            OTP.expires_at >= now,
        ).order_by(OTP.created_at.desc())
    )
    otp = otp_result.scalar_one_or_none()

    if not otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    otp.used = True
    db.add(otp)
    await db.commit()

    token = create_token({"user_id": user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
async def me(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user["user_id"]))
    user_obj = result.scalar_one_or_none()

    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user_obj.id,
        "email": user_obj.email
    }
