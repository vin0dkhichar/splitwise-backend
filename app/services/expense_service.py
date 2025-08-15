from sqlalchemy.orm import Session
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.group_repository import GroupRepository
from app.models.expense import Expense, ExpenseType
from app.models.expense_share import ExpenseShare
from app.schemas.expense_schema import EqualExpenseCreate, ExactExpenseCreate, PercentageExpenseCreate
from typing import List, Optional

class ExpenseService:
    def __init__(self, expense_repo: ExpenseRepository, group_repo: GroupRepository):
        self.expense_repo = expense_repo
        self.group_repo = group_repo

    def _ensure_group_and_membership(
        self, db: Session, *, group_id: Optional[int], payer_id: int, participant_ids: List[int], requester_id: int
    ):
        if group_id is None:
            return
        group = self.group_repo.get_group(db, group_id)
        if not group:
            raise ValueError("Group not found")
        
        # requester (current_user) must be a member
        if not self.group_repo.is_user_in_group(db, group_id, requester_id):
            raise ValueError("Requester is not a member of this group")

        # payer must be a member
        if not self.group_repo.is_user_in_group(db, group_id, payer_id):
            raise ValueError("Payer is not a member of this group")

        # all participants must be members
        for uid in participant_ids:
            if not self.group_repo.is_user_in_group(db, group_id, uid):
                raise ValueError(f"User {uid} is not a member of this group")
    
    def create_expense_equal_split(self, db: Session, payload: EqualExpenseCreate, requester_id: int):
        if not payload.participant_ids:
            raise ValueError("participant_ids required for equal split")
        
        self._ensure_group_and_membership(
            db,
            group_id=payload.group_id,
            payer_id=payload.paid_by,
            participant_ids=payload.participant_ids,
            requester_id=requester_id,
        )

        expense = Expense(
            description=payload.description,
            amount=payload.amount,
            paid_by=payload.paid_by,
            group_id=payload.group_id,
            expense_type=ExpenseType.EQUAL,
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
    
    def create_expense_exact_split(self, db: Session, payload: ExactExpenseCreate, requester_id: int):
        if not payload.shares:
            raise ValueError("shares required for exact split")

        participant_ids = [s.user_id for s in payload.shares]
        self._ensure_group_and_membership(
            db,
            group_id=payload.group_id,
            payer_id=payload.paid_by,
            participant_ids=participant_ids,
            requester_id=requester_id,
        )

        total_share = sum(s.share_amount for s in payload.shares)
        if round(total_share, 2) != round(payload.amount, 2):
            raise ValueError("Sum of shares must equal total amount")

        expense = Expense(
            description=payload.description,
            amount=payload.amount,
            paid_by=payload.paid_by,
            group_id=payload.group_id,
            expense_type=ExpenseType.EXACT,
        )
        expense = self.expense_repo.create(db, expense)

        shares = []
        for s in payload.shares:
            es = ExpenseShare(expense_id=expense.id, user_id=s.user_id, share_amount=s.share_amount)
            shares.append(self.expense_repo.add_share(db, es))
        return {"expense": expense, "shares": shares}
    
    def create_expense_percentage_split(self, db: Session, payload: PercentageExpenseCreate, requester_id: int):
        if not payload.shares:
            raise ValueError("shares required for percentage split")

        participant_ids = [s.user_id for s in payload.shares]
        self._ensure_group_and_membership(
            db,
            group_id=payload.group_id,
            payer_id=payload.paid_by,
            participant_ids=participant_ids,
            requester_id=requester_id,
        )

        total_percentage = sum(s.percentage for s in payload.shares)
        if round(total_percentage, 2) != 100:
            raise ValueError("Total percentage must be 100")

        expense = Expense(
            description=payload.description,
            amount=payload.amount,
            paid_by=payload.paid_by,
            group_id=payload.group_id,
            expense_type=ExpenseType.PERCENTAGE,
        )
        expense = self.expense_repo.create(db, expense)

        shares = []
        for s in payload.shares:
            share_amount = round(payload.amount * (s.percentage / 100), 2)
            es = ExpenseShare(expense_id=expense.id, user_id=s.user_id, share_amount=share_amount)
            shares.append(self.expense_repo.add_share(db, es))
        return {"expense": expense, "shares": shares}

    def get_expense_with_shares(self, db: Session, expense_id: int, requester_id: int):
        result = self.expense_repo.get_expense_with_shares(db, expense_id)
        if not result:
            return None
        
        expense, shares_out = result

        if expense.group_id is not None:
            if not self.group_repo.is_user_in_group(db, expense.group_id, requester_id):
                raise ValueError("You do not have access to this expense")
        else:
            participant_ids = [s.user_id for s in shares_out]
            if requester_id != expense.paid_by and requester_id not in participant_ids:
                raise ValueError("You do not have access to this expense")

        return {"expense": expense, "shares": shares_out}
