from sqlalchemy import select
from fastapi import HTTPException
from app.models.user import User
from app.auth import hash_password


class UserService:

    @staticmethod
    async def get_by_id(db, user_id: int):
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update(db, user, data):
        update_data = data.dict(exclude_unset=True)

        if update_data.get("email"):
            result = await db.execute(
                select(User).where(User.email == update_data["email"])
            )
            existing_user = result.scalar_one_or_none()

            if existing_user and existing_user.id != user.id:
                raise HTTPException(
                    status_code=400,
                    detail="Email already exists"
                )

        if update_data.get("password"):
            update_data["password"] = hash_password(update_data["password"])

        for key, value in update_data.items():
            setattr(user, key, value)

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def delete(db, user):
        await db.delete(user)
        await db.commit()