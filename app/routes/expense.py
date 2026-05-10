from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import get_db
from app import models, schemas

router = APIRouter()


@router.post("/")
async def create_expense(
    expense: schemas.ExpenseCreate,
    db: AsyncSession = Depends(get_db)
):
    new_expense = models.Expense(**expense.model_dump())
    db.add(new_expense)
    await db.commit()
    await db.refresh(new_expense)
    return new_expense


@router.get("/")
async def get_expenses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Expense))
    return result.scalars().all()