from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.database import get_db
from app.models import Expense
from app.auth import get_current_user

router = APIRouter(prefix="/expense", tags=["Expense"])

# create expense
@router.post("/")
async def create_expense(title: str = Body(...), amount: float = Body(...), db: AsyncSession = Depends(get_db), current=Depends(get_current_user)):
    expense = Expense(title=title, amount=amount, user_id=current["user_id"])
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense

# get expenses
@router.get("/")
async def get_expenses(db: AsyncSession = Depends(get_db), current=Depends(get_current_user)):
    result = await db.execute(select(Expense).where(Expense.user_id == current["user_id"]))
    return result.scalars().all()

# update expense
@router.put("/{expense_id}")
async def update_expense(expense_id: int, title: str = Body(None), amount: float = Body(None), db: AsyncSession = Depends(get_db), current=Depends(get_current_user)):
    result = await db.execute(select(Expense).where(Expense.id == expense_id, Expense.user_id == current["user_id"]))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(404, "Expense not found")
    if title:
        expense.title = title
    if amount:
        expense.amount = amount
    db.add(expense)
    await db.commit()
    return {"message": "Expense updated"}

# delete expense
@router.delete("/{expense_id}")
async def delete_expense(expense_id: int, db: AsyncSession = Depends(get_db), current=Depends(get_current_user)):
    result = await db.execute(select(Expense).where(Expense.id == expense_id, Expense.user_id == current["user_id"]))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(404, "Expense not found")
    await db.delete(expense)
    await db.commit()
    return {"message": "Expense deleted"}