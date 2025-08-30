from pydantic import BaseModel, Field
from typing import List, Optional


class ExpenseShareInput(BaseModel):
    user_id: int
    share_amount: float


class ExpensePercentageInput(BaseModel):
    user_id: int
    percentage: float = Field(..., gt=0, le=100)


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


class ExactExpenseCreate(BaseModel):
    description: Optional[str] = None
    amount: float
    paid_by: int
    group_id: Optional[int] = None
    shares: List[ExpenseShareInput]


class PercentageExpenseCreate(BaseModel):
    description: Optional[str] = None
    amount: float
    paid_by: int
    group_id: Optional[int] = None
    shares: List[ExpensePercentageInput]


class ExpenseWithSharesOut(BaseModel):
    expense: ExpenseOut
    shares: List[ExpenseShareOut]


class ExactShareUpdate(BaseModel):
    user_id: int
    share_amount: float


class PercentageShareUpdate(BaseModel):
    user_id: int
    percentage: float


class EqualExpenseUpdate(BaseModel):
    description: str
    amount: float
    paid_by: int
    participant_ids: List[int]
    group_id: Optional[int] = None


class ExactExpenseUpdate(BaseModel):
    description: str
    amount: float
    paid_by: int
    shares: List[ExactShareUpdate]
    group_id: Optional[int] = None


class PercentageExpenseUpdate(BaseModel):
    description: str
    amount: float
    paid_by: int
    shares: List[PercentageShareUpdate]
    group_id: Optional[int] = None
