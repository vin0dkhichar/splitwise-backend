from pydantic import BaseModel
from typing import List
from datetime import datetime


class BalanceResponse(BaseModel):
    user_id: int
    username: str
    amount: float

    class Config:
        from_attributes = True


class SettlementResponse(BaseModel):
    from_user_id: int
    from_username: str
    to_user_id: int
    to_username: str
    amount: float

    class Config:
        from_attributes = True


class GroupSettlementResponse(BaseModel):
    group_id: int
    group_name: str
    balances: List[BalanceResponse]
    settlements: List[SettlementResponse]
    total_expenses: float
    total_settlements_needed: float

    class Config:
        from_attributes = True


class UserSettlementSummaryResponse(BaseModel):
    user_id: int
    username: str
    total_owed_to_user: float
    total_user_owes: float
    net_balance: float
    group_balances: List[dict]

    class Config:
        from_attributes = True


class MarkSettlementRequest(BaseModel):
    from_user_id: int
    to_user_id: int
    amount: float


class SettlementHistoryResponse(BaseModel):
    id: int
    description: str
    amount: float
    paid_by: str
    created_at: datetime
    shares: List[dict]

    class Config:
        from_attributes = True
