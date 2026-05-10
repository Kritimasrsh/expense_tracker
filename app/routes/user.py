from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schema.user import UserCreate
from app.services.user_service import create_user, get_users

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)
    

@router.post("/list")
def add_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return create_user(db, user)


@router.get("/")
def all_users(
    db: Session = Depends(get_db)
):
    return get_users(db)