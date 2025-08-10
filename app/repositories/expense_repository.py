from sqlalchemy.orm import Session
from typing import Optional
from app.models.expense import Expense
from app.models.expense_share import ExpenseShare

class ExpenseRepository:
    def create(self, db: Session, expense: Expense) -> Expense:
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense

    def get_by_id(self, db: Session, expense_id: int) -> Optional[Expense]:
        return db.query(Expense).filter(Expense.id == expense_id).first()

    def list_for_group(self, db: Session, group_id: int):
        return db.query(Expense).filter(Expense.group_id == group_id).all()

    def add_share(self, db: Session, share: ExpenseShare) -> ExpenseShare:
        db.add(share)
        db.commit()
        db.refresh(share)
        return share

    def delete(self, db: Session, expense: Expense):
        db.delete(expense)
        db.commit()
