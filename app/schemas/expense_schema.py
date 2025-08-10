from pydantic import BaseModel
from typing import List, Optional

class ExpenseShareInput(BaseModel):
    user_id: int
    share_amount: float

class ExpenseOut(BaseModel):
    id: int
    description: Optional[str]
    amount: float
    paid_by: int
    group_id: Optional[int]

    class Config:
        from_attributes = True

class ExpenseShareOut(BaseModel):
    user_id: int
    share_amount: float

    class Config:
        from_attributes = True

class EqualExpenseCreate(BaseModel):
    description: Optional[str] = None
    amount: float
    paid_by: int
    group_id: Optional[int] = None
    participant_ids: List[int]

class CustomExpenseCreate(BaseModel):
    description: Optional[str] = None
    amount: float
    paid_by: int
    group_id: Optional[int] = None
    shares: List[ExpenseShareInput]

class ExpenseWithSharesOut(BaseModel):
    expense: ExpenseOut
    shares: List[ExpenseShareOut]
