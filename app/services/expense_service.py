from sqlalchemy.orm import Session
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.group_repository import GroupRepository
from app.models.expense import Expense
from app.models.expense_share import ExpenseShare
from app.schemas.expense_schema import EqualExpenseCreate, CustomExpenseCreate
from typing import List

class ExpenseService:
    def __init__(self, expense_repo: ExpenseRepository, group_repo: GroupRepository):
        self.expense_repo = expense_repo
        self.group_repo = group_repo
    
    def create_expense_equal_split(self, db: Session, payload: EqualExpenseCreate):
        if payload.group_id:
            group = self.group_repo.get_group(db, payload.group_id)
            if not group:
                raise ValueError("Group not found")

            if not self.group_repo.is_user_in_group(db, payload.group_id, payload.paid_by):
                raise ValueError("Payer is not a member of the group")

            for user_id in payload.participant_ids:
                if not self.group_repo.is_user_in_group(db, payload.group_id, user_id):
                    raise ValueError(f"User {user_id} is not a member of the group")

        expense = Expense(
            description=payload.description,
            amount=payload.amount,
            paid_by=payload.paid_by,
            group_id=payload.group_id,
        )
        expense = self.expense_repo.create(db, expense)

        n = len(payload.participant_ids)
        if n == 0:
            raise ValueError("No participants provided")
        share = round(payload.amount / n, 2)
        shares = []
        for user_id in payload.participant_ids:
            es = ExpenseShare(expense_id=expense.id, user_id=user_id, share_amount=share)
            shares.append(self.expense_repo.add_share(db, es))
        return {"expense": expense, "shares": shares}

    def create_expense_custom_shares(self, db: Session, payload: CustomExpenseCreate):
        if payload.group_id:
            group = self.group_repo.get_group(db, payload.group_id)
            if not group:
                raise ValueError("Group not found")

            if not self.group_repo.is_user_in_group(db, payload.group_id, payload.paid_by):
                raise ValueError("Payer is not a member of the group")

            for share in payload.shares:
                if not self.group_repo.is_user_in_group(db, payload.group_id, share.user_id):
                    raise ValueError(f"User {share.user_id} is not a member of the group")

        expense = Expense(
            description=payload.description,
            amount=payload.amount,
            paid_by=payload.paid_by,
            group_id=payload.group_id,
        )
        expense = self.expense_repo.create(db, expense)

        total = 0
        shares_out = []
        for s in payload.shares:
            total += s.share_amount
            es = ExpenseShare(expense_id=expense.id, user_id=s.user_id, share_amount=s.share_amount)
            shares_out.append(self.expense_repo.add_share(db, es))

        if abs(total - payload.amount) > 0.01:
            self.expense_repo.delete(db, expense)
            raise ValueError("Sum of shares does not equal total amount")

        return {"expense": expense, "shares": shares_out}
