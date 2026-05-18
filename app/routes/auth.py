from datetime import datetime, timedelta
from random import randint

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Path
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import get_db
from app.config.mail import fastmail
from fastapi_mail import MessageSchema

from app.models import User, OTP
from app.auth import hash_password, verify_password, create_token, verify_token


router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------- SCHEMAS ----------------
class SignupSchema(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class OTPVerifySchema(BaseModel):
    email: EmailStr
    otp_code: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    password: str


# ---------------- OTP ----------------
def generate_otp():
    return str(randint(100000, 999999))


# ---------------- EMAIL TEMPLATES ----------------
def build_otp_email(code: str):
    return f"""
    <div style="font-family:Arial;padding:20px">
        <h2>Expense Tracker App</h2>
        <p>Your OTP code is:</p>
        <h1>{code}</h1>
        <p>Valid for 5 minutes</p>
    </div>
    """


def build_reset_email(link: str):
    return f"""
    <div style="font-family:Arial;padding:20px">
        <h2>Password Reset</h2>
        <p>Click below:</p>
        <a href="{link}">Reset Password</a>
        <p>Expires in 15 minutes</p>
    </div>
    """


# ---------------- EMAIL SENDER ----------------
async def send_email(email: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype="html"
    )
    await fastmail.send_message(message)


# ---------------- SIGNUP ----------------
@router.post("/signup")
async def signup(data: SignupSchema, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password)
    )

    db.add(user)
    await db.commit()

    return {"success": True, "message": "Account created"}


# ---------------- LOGIN ----------------
@router.post("/login")
async def login(
    data: LoginSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Wrong password")

    otp_code = generate_otp()

    otp = OTP(
        user_id=user.id,
        code=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        used=False
    )

    db.add(otp)
    await db.commit()

    background_tasks.add_task(
        send_email,
        data.email,
        "OTP Code",
        build_otp_email(otp_code)
    )

    return {"success": True, "message": "OTP sent"}


# ---------------- VERIFY OTP ----------------
@router.post("/verify-otp")
async def verify_otp(data: OTPVerifySchema, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.utcnow()

    otp_result = await db.execute(
        select(OTP).where(
            OTP.user_id == user.id,
            OTP.code == data.otp_code,
            OTP.used == False,
            OTP.expires_at >= now
        )
    )

    otp = otp_result.scalar_one_or_none()

    if not otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    otp.used = True
    db.add(otp)
    await db.commit()

    token = create_token({"user_id": user.id})

    return {
        "success": True,
        "message": "Login success",
        "access_token": token,
        "token_type": "bearer"
    }


# ---------------- FORGOT PASSWORD ----------------
@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordSchema, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_token(
        {"user_id": user.id},
        expires_delta=timedelta(minutes=15)
    )

    reset_link = f"http://localhost:5173/reset-password/{token}"

    await send_email(
        data.email,
        "Reset Password",
        build_reset_email(reset_link)
    )

    return {"success": True, "message": "Reset link sent"}


# ---------------- RESET PASSWORD ----------------
@router.post("/reset-password/{token}")
async def reset_password(
    token: str = Path(...),
    data: ResetPasswordSchema = None,
    db: AsyncSession = Depends(get_db)
):

    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(data.password)

    db.add(user)
    await db.commit()

    return {"success": True, "message": "Password updated"}