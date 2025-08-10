from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.expense_service import ExpenseService
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.group_repository import GroupRepository

from app.schemas.expense_schema import EqualExpenseCreate, CustomExpenseCreate, ExpenseWithSharesOut
from app.routes.auth_routes import get_current_user

router = APIRouter(prefix="/expenses", tags=["expenses"])
service = ExpenseService(ExpenseRepository(), GroupRepository())

@router.post("/equal", response_model=ExpenseWithSharesOut, status_code=status.HTTP_201_CREATED)
def create_equal_expense(payload: EqualExpenseCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not payload.participant_ids:
        raise HTTPException(status_code=400, detail="participant_ids required for equal split")
    try:
        return service.create_expense_equal_split(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/custom", response_model=ExpenseWithSharesOut, status_code=status.HTTP_201_CREATED)
def create_custom_expense(payload: CustomExpenseCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not payload.shares:
        raise HTTPException(status_code=400, detail="shares required for custom split")
    try:
        return service.create_expense_custom_shares(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
