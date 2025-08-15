from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.models.expense import Expense
from app.models.expense_share import ExpenseShare
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.group_repository import GroupRepository

class ExpenseSplitter(ABC):
    def __init__(self, expense_repo: ExpenseRepository, group_repo: GroupRepository):
        self.expense_repo = expense_repo
        self.group_repo = group_repo

    @abstractmethod
    def create_shares(self, db: Session, expense: Expense, payload, requester_id: int):
        pass

    @abstractmethod
    def update_shares(self, db: Session, expense: Expense, payload, requester_id: int):
        pass

    def ensure_membership(self, db: Session, group_id, payer_id, participant_ids, requester_id):
        if group_id is None:
            return
        group = self.group_repo.get_group(db, group_id)
        if not group:
            raise ValueError("Group not found")
        if not self.group_repo.is_user_in_group(db, group_id, requester_id):
            raise ValueError("Requester not in group")
        if not self.group_repo.is_user_in_group(db, group_id, payer_id):
            raise ValueError("Payer not in group")
        for uid in participant_ids:
            if not self.group_repo.is_user_in_group(db, group_id, uid):
                raise ValueError(f"User {uid} not in group")

class EqualExpenseSplitter(ExpenseSplitter):
    def create_shares(self, db: Session, expense: Expense, payload, requester_id: int):
        participant_ids = payload.participant_ids
        if not participant_ids:
            raise ValueError("No participants provided")
        
        self.ensure_membership(db, getattr(payload, "group_id", None), payload.paid_by, participant_ids, requester_id)

        n = len(participant_ids)
        share_amount = round(payload.amount / n, 2)
        
        shares = []
        for uid in participant_ids:
            es = ExpenseShare(expense_id=expense.id, user_id=uid, share_amount=share_amount)
            shares.append(self.expense_repo.add_share(db, es))
        return shares
    
    def update_shares(self, db: Session, expense: Expense, payload, requester_id: int):
        participant_ids = payload.participant_ids
        if not participant_ids:
            raise ValueError("No participants provided")
        
        self.ensure_membership(db, getattr(payload, "group_id", None), payload.paid_by, participant_ids, requester_id)

        self.expense_repo.delete_shares_for_expense(db, expense.id)
        
        n = len(participant_ids)
        share_amount = round(payload.amount / n, 2)
        
        shares = []
        for uid in participant_ids:
            es = ExpenseShare(expense_id=expense.id, user_id=uid, share_amount=share_amount)
            shares.append(self.expense_repo.add_share(db, es))
        return shares

class ExactExpenseSplitter(ExpenseSplitter):
    def create_shares(self, db: Session, expense: Expense, payload, requester_id: int):
        participant_ids = [s.user_id for s in payload.shares]
        if not participant_ids:
            raise ValueError("No participants provided")
        
        self.ensure_membership(db, getattr(payload, "group_id", None), payload.paid_by, participant_ids, requester_id)

        if round(sum(s.share_amount for s in payload.shares), 2) != round(payload.amount, 2):
            raise ValueError("Shares do not sum up to total amount")
        
        shares = []
        for s in payload.shares:
            es = ExpenseShare(expense_id=expense.id, user_id=s.user_id, share_amount=s.share_amount)
            shares.append(self.expense_repo.add_share(db, es))
        return shares
    
    def update_shares(self, db: Session, expense: Expense, payload, requester_id: int):
        participant_ids = [s.user_id for s in payload.shares]
        if not participant_ids:
            raise ValueError("No participants provided")
        
        self.ensure_membership(db, getattr(payload, "group_id", None), payload.paid_by, participant_ids, requester_id)

        if round(sum(s.share_amount for s in payload.shares), 2) != round(payload.amount, 2):
            raise ValueError("Shares do not sum up to total amount")
        
        self.expense_repo.delete_shares_for_expense(db, expense.id)
        
        shares = []
        for s in payload.shares:
            es = ExpenseShare(expense_id=expense.id, user_id=s.user_id, share_amount=s.share_amount)
            shares.append(self.expense_repo.add_share(db, es))
        return shares

class PercentageExpenseSplitter(ExpenseSplitter):
    def create_shares(self, db: Session, expense: Expense, payload, requester_id: int):
        participant_ids = [s.user_id for s in payload.shares]
        if not participant_ids:
            raise ValueError("No participants provided")
        
        self.ensure_membership(db, getattr(payload, "group_id", None), payload.paid_by, participant_ids, requester_id)

        if round(sum(s.percentage for s in payload.shares), 2) != 100:
            raise ValueError("Total percentage must be 100")
        
        shares = []
        for s in payload.shares:
            share_amount = round(payload.amount * (s.percentage / 100), 2)
            es = ExpenseShare(expense_id=expense.id, user_id=s.user_id, share_amount=share_amount)
            shares.append(self.expense_repo.add_share(db, es))
        return shares
    
    def update_shares(self, db: Session, expense: Expense, payload, requester_id: int):
        participant_ids = [s.user_id for s in payload.shares]
        if not participant_ids:
            raise ValueError("No participants provided")
        
        self.ensure_membership(db, getattr(payload, "group_id", None), payload.paid_by, participant_ids, requester_id)

        if round(sum(s.percentage for s in payload.shares), 2) != 100:
            raise ValueError("Total percentage must be 100")
        
        self.expense_repo.delete_shares_for_expense(db, expense.id)
        
        shares = []
        for s in payload.shares:
            share_amount = round(payload.amount * (s.percentage / 100), 2)
            es = ExpenseShare(expense_id=expense.id, user_id=s.user_id, share_amount=share_amount)
            shares.append(self.expense_repo.add_share(db, es))
        return shares
