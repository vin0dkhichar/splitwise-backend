from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.group import Group
from app.models.expense import Expense, ExpenseType
from app.models.expense_share import ExpenseShare
from app.models.group_member import GroupMember


class SettlementRepository:
    def get_group_expenses(self, db: Session, group_id: int) -> List[Expense]:
        return db.query(Expense).filter(Expense.group_id == group_id).all()

    def get_user_group_memberships(
        self, db: Session, user_id: int
    ) -> List[GroupMember]:
        return db.query(GroupMember).filter(GroupMember.user_id == user_id).all()

    def get_group_by_id(self, db: Session, group_id: int) -> Optional[Group]:
        return db.query(Group).filter(Group.id == group_id).first()

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def get_users_by_ids(self, db: Session, user_ids: List[int]) -> List[User]:
        return db.query(User).filter(User.id.in_(user_ids)).all()

    def get_groups_by_ids(self, db: Session, group_ids: List[int]) -> List[Group]:
        return db.query(Group).filter(Group.id.in_(group_ids)).all()

    def is_user_group_member(self, db: Session, user_id: int, group_id: int) -> bool:
        membership = (
            db.query(GroupMember)
            .filter(GroupMember.user_id == user_id, GroupMember.group_id == group_id)
            .first()
        )
        return membership is not None

    def get_group_members(self, db: Session, group_id: int) -> List[int]:
        members = (
            db.query(GroupMember.user_id).filter(GroupMember.group_id == group_id).all()
        )
        return [member.user_id for member in members]

    def create_settlement_expense(
        self, db: Session, group_id: int, amount: float, paid_by: int, description: str
    ) -> Expense:
        settlement_expense = Expense(
            description=description,
            amount=amount,
            paid_by=paid_by,
            group_id=group_id,
            expense_type=ExpenseType.EXACT,
        )
        db.add(settlement_expense)
        db.flush()
        return settlement_expense

    def create_settlement_share(
        self, db: Session, expense_id: int, user_id: int, amount: float
    ) -> ExpenseShare:
        settlement_share = ExpenseShare(
            expense_id=expense_id, user_id=user_id, share_amount=amount, is_paid=True
        )
        db.add(settlement_share)
        return settlement_share

    def get_settlement_history(self, db: Session, group_id: int) -> List[Expense]:
        return (
            db.query(Expense)
            .filter(
                Expense.group_id == group_id,
                Expense.description.like("%Settlement payment%"),
            )
            .order_by(Expense.created_at.desc())
            .all()
        )

    def get_group_total_expenses(self, db: Session, group_id: int) -> float:
        result = (
            db.query(func.sum(Expense.amount))
            .filter(Expense.group_id == group_id)
            .scalar()
        )
        return float(result) if result else 0.0

    def commit(self, db: Session):
        db.commit()

    def rollback(self, db: Session):
        db.rollback()
