from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import get_db
from app.models.expense import Expense
from app.schema.expense import ExpenseCreate, ExpenseUpdate, ExpenseRead
from app.auth import get_current_user

router = APIRouter(prefix="/expense", tags=["expense"])


# GET ALL EXPENSES
@router.get("/", response_model=List[ExpenseRead])
async def get_expenses(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    result = await db.execute(
        select(Expense).where(Expense.user_id == user["user_id"])
    )
    return result.scalars().all()


# ADD EXPENSE
@router.post("/", response_model=ExpenseRead)
async def create_expense(
    expense: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    new_expense = Expense(
        title=expense.title,
        amount=expense.amount,
        user_id=user["user_id"]
    )

    db.add(new_expense)
    await db.commit()
    await db.refresh(new_expense)

    return new_expense


# GET ONE EXPENSE
@router.get("/{expense_id}", response_model=ExpenseRead)
async def get_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == user["user_id"]
        )
    )
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    return expense


# UPDATE EXPENSE
@router.put("/{expense_id}", response_model=ExpenseRead)
async def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == user["user_id"]
        )
    )
    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(expense, key, value)

    await db.commit()
    await db.refresh(expense)

    return expense


# DELETE EXPENSE
@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == user["user_id"]
        )
    )

    expense = result.scalar_one_or_none()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    await db.delete(expense)
    await db.commit()

    return {"msg": "deleted"}