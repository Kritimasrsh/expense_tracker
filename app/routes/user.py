import os
import time

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import get_db
from app.models import User
from app.auth import get_current_user

router = APIRouter(prefix="/user", tags=["User"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# GET USER PROFILE
@router.get("/me")
async def get_me(
    current=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == current["user_id"])
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "name": user.name,
        "email": user.email,
        "profile_picture": user.profile_picture
    }


# UPLOAD PROFILE PICTURE
@router.post("/upload-profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == current["user_id"])
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file")

    file_ext = file.filename.split(".")[-1].lower()
    allowed_ext = ["jpg", "jpeg", "png", "webp"]

    if file_ext not in allowed_ext:
        raise HTTPException(
            status_code=400,
            detail="Only jpg, jpeg, png, webp allowed"
        )


    file_name = f"user_{user.id}_{int(time.time())}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    # save file
    contents = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    
    user.profile_picture = f"/uploads/{file_name}"

    await db.commit()
    await db.refresh(user)

    return {
        "success": True,
        "profile_picture": user.profile_picture
    }