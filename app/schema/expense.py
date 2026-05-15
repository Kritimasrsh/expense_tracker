from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ExpenseBase(BaseModel):
    title: str
    amount: float


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None


class ExpenseRead(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True