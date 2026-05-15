from sqlalchemy import select
from app.models.expense import Expense


class ExpenseService:

    # CREATE
    @staticmethod
    async def create(db, data, user_id):

        expense = Expense(
            title=data.title,
            amount=data.amount,
            user_id=user_id
        )

        db.add(expense)

        await db.commit()
        await db.refresh(expense)

        return expense

    # READ
    @staticmethod
    async def get_all(db, user_id):

        result = await db.execute(
            select(Expense).where(
                Expense.user_id == user_id
            )
        )

        return result.scalars().all()

    # UPDATE
    @staticmethod
    async def update(db, expense_id, data, user_id):

        result = await db.execute(
            select(Expense).where(
                Expense.id == expense_id,
                Expense.user_id == user_id
            )
        )

        expense = result.scalar_one_or_none()

        if not expense:
            return None

        expense.title = data.title
        expense.amount = data.amount

        await db.commit()
        await db.refresh(expense)

        return expense

    # DELETE
    @staticmethod
    async def delete(db, expense_id, user_id):

        result = await db.execute(
            select(Expense).where(
                Expense.id == expense_id,
                Expense.user_id == user_id
            )
        )

        expense = result.scalar_one_or_none()

        if not expense:
            return None

        await db.delete(expense)

        await db.commit()

        return True