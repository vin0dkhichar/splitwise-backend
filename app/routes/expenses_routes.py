from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.expense_service import ExpenseService
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.group_repository import GroupRepository
from app.schemas.expense_schema import (
    EqualExpenseCreate,
    ExactExpenseCreate,
    PercentageExpenseCreate,
    ExpenseWithSharesOut,
)
from app.routes.auth_routes import get_current_user

class ExpenseRoutes:
    router = APIRouter(prefix="/expenses", tags=["expenses"])
    service = ExpenseService(ExpenseRepository(), GroupRepository())

    @router.post("/equal", response_model=ExpenseWithSharesOut, status_code=status.HTTP_201_CREATED)
    def create_equal_expense(payload: EqualExpenseCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        try:
            return ExpenseRoutes.service.create_expense_equal_split(db, payload, requester_id=current_user.id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/exact", response_model=ExpenseWithSharesOut, status_code=status.HTTP_201_CREATED)
    def create_exact_expense(payload: ExactExpenseCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        try:
            return ExpenseRoutes.service.create_expense_exact_split(db, payload, requester_id=current_user.id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/percentage", response_model=ExpenseWithSharesOut, status_code=status.HTTP_201_CREATED)
    def create_percentage_expense(payload: PercentageExpenseCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        try:
            return ExpenseRoutes.service.create_expense_percentage_split(db, payload, requester_id=current_user.id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{expense_id}", response_model=ExpenseWithSharesOut)
    def get_expense(expense_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        res = ExpenseRoutes.service.get_expense_with_shares(db, expense_id, requester_id=current_user.id)
        if not res:
            raise HTTPException(status_code=404, detail="Expense not found")
        return res
