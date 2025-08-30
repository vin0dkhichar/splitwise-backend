from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from collections import defaultdict
from dataclasses import dataclass
from app.repositories.settlement_repository import SettlementRepository


@dataclass
class Balance:
    user_id: int
    username: str
    amount: float


@dataclass
class Settlement:
    from_user_id: int
    from_username: str
    to_user_id: int
    to_username: str
    amount: float


@dataclass
class GroupSettlement:
    group_id: int
    group_name: str
    balances: List[Balance]
    settlements: List[Settlement]
    total_expenses: float
    total_settlements_needed: float


class SettlementService:
    def __init__(self, settlement_repo: SettlementRepository):
        self.settlement_repo = settlement_repo

    def validate_group_access(self, db: Session, user_id: int, group_id: int) -> bool:
        return self.settlement_repo.is_user_group_member(db, user_id, group_id)

    def validate_users_in_group(
        self, db: Session, group_id: int, user_ids: List[int]
    ) -> bool:
        group_members = self.settlement_repo.get_group_members(db, group_id)
        return all(user_id in group_members for user_id in user_ids)

    def calculate_group_balances(self, db, group_id: int) -> Dict[int, float]:
        balances = defaultdict(float)

        expenses = self.settlement_repo.get_group_expenses(db, group_id)

        for expense in expenses:
            balances[expense.paid_by] += expense.amount

            for share in expense.shares:
                balances[share.user_id] -= share.share_amount

        return dict(balances)

    def calculate_user_balances_across_groups(
        self, db, user_id: int
    ) -> Dict[int, float]:
        group_balances = {}

        memberships = self.settlement_repo.get_user_group_memberships(db, user_id)

        for membership in memberships:
            group_balance = self.calculate_group_balances(db, membership.group_id)
            user_balance = group_balance.get(user_id, 0.0)
            if user_balance != 0:
                group_balances[membership.group_id] = user_balance

        return group_balances

    def get_group_settlement_summary(
        self, db, group_id: int, requesting_user_id: int
    ) -> Optional[GroupSettlement]:
        if not self.validate_group_access(db, requesting_user_id, group_id):
            raise ValueError("User does not have access to this group")

        group = self.settlement_repo.get_group_by_id(db, group_id)
        if not group:
            return None

        balance_dict = self.calculate_group_balances(db, group_id)

        user_ids = list(balance_dict.keys())
        if not user_ids:
            return GroupSettlement(
                group_id=group_id,
                group_name=group.name,
                balances=[],
                settlements=[],
                total_expenses=0.0,
                total_settlements_needed=0.0,
            )

        users = self.settlement_repo.get_users_by_ids(db, user_ids)
        user_map = {user.id: user.username for user in users}

        balances = [
            Balance(
                user_id=user_id,
                username=user_map.get(user_id, f"User {user_id}"),
                amount=round(amount, 2),
            )
            for user_id, amount in balance_dict.items()
            if abs(amount) > 0.01
        ]

        settlements = self._calculate_optimal_settlements(db, balance_dict, user_map)

        total_expenses = self.settlement_repo.get_group_total_expenses(db, group_id)
        total_settlements_needed = sum(
            abs(balance.amount) for balance in balances if balance.amount < 0
        )

        return GroupSettlement(
            group_id=group_id,
            group_name=group.name,
            balances=sorted(balances, key=lambda x: x.amount, reverse=True),
            settlements=settlements,
            total_expenses=round(total_expenses, 2),
            total_settlements_needed=round(total_settlements_needed, 2),
        )

    def _calculate_optimal_settlements(
        self, db, balances: Dict[int, float], user_map: Dict[int, str]
    ) -> List[Settlement]:
        settlements = []

        creditors = [
            (user_id, amount) for user_id, amount in balances.items() if amount > 0.01
        ]
        debtors = [
            (user_id, -amount) for user_id, amount in balances.items() if amount < -0.01
        ]

        creditors.sort(key=lambda x: x[1], reverse=True)
        debtors.sort(key=lambda x: x[1], reverse=True)

        creditor_list = [[user_id, amount] for user_id, amount in creditors]
        debtor_list = [[user_id, amount] for user_id, amount in debtors]

        while creditor_list and debtor_list:
            creditor_id, creditor_amount = creditor_list[0]
            debtor_id, debtor_amount = debtor_list[0]

            settlement_amount = min(creditor_amount, debtor_amount)

            if settlement_amount > 0.01:
                settlements.append(
                    Settlement(
                        from_user_id=debtor_id,
                        from_username=user_map.get(debtor_id, f"User {debtor_id}"),
                        to_user_id=creditor_id,
                        to_username=user_map.get(creditor_id, f"User {creditor_id}"),
                        amount=round(settlement_amount, 2),
                    )
                )

            creditor_list[0][1] -= settlement_amount
            debtor_list[0][1] -= settlement_amount

            if creditor_list[0][1] <= 0.01:
                creditor_list.pop(0)
            if debtor_list[0][1] <= 0.01:
                debtor_list.pop(0)

        return settlements

    def get_user_settlements_summary(
        self, db, user_id: int, requesting_user_id: int
    ) -> Optional[Dict]:
        if user_id != requesting_user_id:
            raise ValueError("Users can only view their own settlement summary")

        user = self.settlement_repo.get_user_by_id(db, user_id)
        if not user:
            return None

        group_balances = self.calculate_user_balances_across_groups(db, user_id)

        total_owed_to_user = sum(
            balance for balance in group_balances.values() if balance > 0
        )
        total_user_owes = sum(
            abs(balance) for balance in group_balances.values() if balance < 0
        )

        group_details = {}
        if group_balances:
            groups = self.settlement_repo.get_groups_by_ids(
                db, list(group_balances.keys())
            )
            group_details = {group.id: group.name for group in groups}

        return {
            "user_id": user_id,
            "username": user.username,
            "total_owed_to_user": round(total_owed_to_user, 2),
            "total_user_owes": round(total_user_owes, 2),
            "net_balance": round(total_owed_to_user - total_user_owes, 2),
            "group_balances": [
                {
                    "group_id": group_id,
                    "group_name": group_details.get(group_id, f"Group {group_id}"),
                    "balance": round(balance, 2),
                    "status": (
                        "owed" if balance > 0 else "owes" if balance < 0 else "settled"
                    ),
                }
                for group_id, balance in group_balances.items()
            ],
        }

    def mark_settlement_as_paid(
        self,
        db,
        group_id: int,
        from_user_id: int,
        to_user_id: int,
        amount: float,
        requesting_user_id: int,
    ) -> bool:
        if not self.validate_group_access(db, requesting_user_id, group_id):
            raise ValueError("User does not have access to this group")

        if not self.validate_users_in_group(db, group_id, [from_user_id, to_user_id]):
            raise ValueError("One or both users are not members of this group")

        try:
            from_user = self.settlement_repo.get_user_by_id(db, from_user_id)
            to_user = self.settlement_repo.get_user_by_id(db, to_user_id)

            if not from_user or not to_user:
                return False

            description = (
                f"Settlement payment from {from_user.username} to {to_user.username}"
            )

            settlement_expense = self.settlement_repo.create_settlement_expense(
                db,
                group_id=group_id,
                amount=amount,
                paid_by=from_user_id,
                description=description,
            )

            self.settlement_repo.create_settlement_share(
                db, expense_id=settlement_expense.id, user_id=to_user_id, amount=amount
            )

            self.settlement_repo.commit(db)
            return True

        except Exception:
            self.settlement_repo.rollback(db)
            return False

    def get_settlement_history(
        self, db, group_id: int, requesting_user_id: int
    ) -> List[Dict]:
        if not self.validate_group_access(db, requesting_user_id, group_id):
            raise ValueError("User does not have access to this group")

        settlements = self.settlement_repo.get_settlement_history(db, group_id)

        history = []
        for settlement in settlements:
            history.append(
                {
                    "id": settlement.id,
                    "description": settlement.description,
                    "amount": settlement.amount,
                    "paid_by": settlement.payer.username,
                    "created_at": settlement.created_at,
                    "shares": [
                        {
                            "user": share.user.username,
                            "amount": share.share_amount,
                            "is_paid": share.is_paid,
                        }
                        for share in settlement.shares
                    ],
                }
            )

        return history
