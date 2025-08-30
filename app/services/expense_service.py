from typing import Dict
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.group_repository import GroupRepository
from app.models.expense import Expense, ExpenseType
from app.services.expense_splitters import (
    EqualExpenseSplitter,
    ExactExpenseSplitter,
    PercentageExpenseSplitter,
)


class ExpenseService:
    def __init__(self, expense_repo: ExpenseRepository, group_repo: GroupRepository):
        self.expense_repo = expense_repo
        self.group_repo = group_repo
        self.splitters: Dict[ExpenseType, object] = {
            ExpenseType.EQUAL: EqualExpenseSplitter(expense_repo, group_repo),
            ExpenseType.EXACT: ExactExpenseSplitter(expense_repo, group_repo),
            ExpenseType.PERCENTAGE: PercentageExpenseSplitter(expense_repo, group_repo),
        }

    def create_expense(self, db, payload, expense_type: ExpenseType, requester_id: int):

        if getattr(payload, "group_id", None) is not None:
            if not self.group_repo.is_user_in_group(db, payload.group_id, requester_id):
                raise ValueError("You are not a member of this group")

        expense = Expense(
            description=payload.description,
            amount=payload.amount,
            paid_by=payload.paid_by,
            group_id=getattr(payload, "group_id", None),
            expense_type=expense_type,
        )
        expense = self.expense_repo.create(db, expense)

        splitter = self.splitters.get(expense_type)
        if not splitter:
            raise ValueError("Unsupported expense type")
        shares = splitter.create_shares(db, expense, payload, requester_id=requester_id)
        return {"expense": expense, "shares": shares}

    def get_expense_with_shares(self, db, expense_id: int, requester_id: int):
        result = self.expense_repo.get_expense_with_shares(db, expense_id)
        if not result:
            return None

        expense, shares_out = result
        if expense.group_id:
            if not self.group_repo.is_user_in_group(db, expense.group_id, requester_id):
                raise ValueError("You do not have access to this expense")
        else:
            participant_ids = [s.user_id for s in shares_out]
            if requester_id != expense.paid_by and requester_id not in participant_ids:
                raise ValueError("You do not have access to this expense")
        return {"expense": expense, "shares": shares_out}

    def list_expenses_for_group(self, db, group_id: int, requester_id: int):
        if not self.group_repo.is_user_in_group(db, group_id, requester_id):
            raise ValueError("You are not a member of this group")
        return self.expense_repo.list_for_group(db, group_id)

    def update_expense(
        self, db, expense_id: int, payload, expense_type: ExpenseType, requester_id: int
    ):
        existing_result = self.get_expense_with_shares(db, expense_id, requester_id)
        if not existing_result:
            raise ValueError("Expense not found or access denied")

        expense = existing_result["expense"]

        if getattr(payload, "group_id", None) is not None:
            if not self.group_repo.is_user_in_group(db, payload.group_id, requester_id):
                raise ValueError("You are not a member of this group")

        expense.description = payload.description
        expense.amount = payload.amount
        expense.paid_by = payload.paid_by
        expense.group_id = getattr(payload, "group_id", None)
        expense.expense_type = expense_type

        updated_expense = self.expense_repo.update(db, expense)

        splitter = self.splitters.get(expense_type)
        if not splitter:
            raise ValueError("Unsupported expense type")

        shares = splitter.update_shares(
            db, updated_expense, payload, requester_id=requester_id
        )
        return {"expense": updated_expense, "shares": shares}

    def delete_expense(self, db, expense_id: int, requester_id: int):
        existing_result = self.get_expense_with_shares(db, expense_id, requester_id)
        if not existing_result:
            return False

        expense = existing_result["expense"]

        self.expense_repo.delete_shares_for_expense(db, expense_id)

        self.expense_repo.delete(db, expense)

        return True
