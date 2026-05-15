from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import get_db
from app.models.user import User
from app.schema.user import UserCreate, UserUpdate, UserRead
from app.services.user_service import UserService
from app.auth import get_current_user, hash_password

router = APIRouter(prefix="/users", tags=["Users"])


# CREATE (C)
@router.post("/", response_model=UserRead)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    existing = await db.execute(
        select(User).where(User.email == data.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        email=data.email,
        password=hash_password(data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


# READ ALL (R)
@router.get("/", response_model=List[UserRead])
async def get_users(db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User))
    users = result.scalars().all()

    return users


# READ ONE (R)
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# UPDATE (U)
@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Operation not permitted")

    db_user = await UserService.get_by_id(db, user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await UserService.update(db, db_user, data)

    return updated_user


# DELETE (D)
@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Operation not permitted")

    db_user = await UserService.get_by_id(db, user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await UserService.delete(db, db_user)

    return {"message": "User deleted successfully"}