from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.expense_service import ExpenseService
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.group_repository import GroupRepository
from app.routes.auth_routes import get_current_user
from app.models.expense import ExpenseType
from app.schemas.expense_schema import (
    EqualExpenseCreate, ExactExpenseCreate, PercentageExpenseCreate, 
    ExpenseWithSharesOut, EqualExpenseUpdate, ExactExpenseUpdate, PercentageExpenseUpdate
)

class ExpenseRoutes:
    def __init__(self):
        self.router = APIRouter(prefix="/expenses", tags=["expenses"])
        self.service = ExpenseService(ExpenseRepository(), GroupRepository())

        self.payload_mapping = {
            ExpenseType.EQUAL: EqualExpenseCreate,
            ExpenseType.EXACT: ExactExpenseCreate,
            ExpenseType.PERCENTAGE: PercentageExpenseCreate,
        }

        self.update_payload_mapping = {
            ExpenseType.EQUAL: EqualExpenseUpdate,
            ExpenseType.EXACT: ExactExpenseUpdate,
            ExpenseType.PERCENTAGE: PercentageExpenseUpdate,
        }

        self.router.add_api_route(
            "/create/{expense_type}",
            self.create_expense,
            response_model=ExpenseWithSharesOut,
            status_code=status.HTTP_201_CREATED,
            methods=["POST"]
        )

        self.router.add_api_route(
            "/{expense_id}",
            self.get_expense,
            response_model=ExpenseWithSharesOut,
            methods=["GET"]
        )

        self.router.add_api_route(
            "/{expense_id}/update/{expense_type}",
            self.update_expense,
            response_model=ExpenseWithSharesOut,
            methods=["PUT"]
        )

        self.router.add_api_route(
            "/{expense_id}",
            self.delete_expense,
            status_code=status.HTTP_204_NO_CONTENT,
            methods=["DELETE"]
        )

    def create_expense(self, expense_type: ExpenseType, payload: dict = Body(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        Schema = self.payload_mapping.get(expense_type)
        if not Schema:
            raise HTTPException(status_code=400, detail="Invalid expense type")
        try:
            validated_payload = Schema(**payload)
            return self.service.create_expense(db, validated_payload, expense_type, requester_id=current_user.id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def get_expense(self, expense_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        try:
            res = self.service.get_expense_with_shares(db, expense_id, requester_id=current_user.id)
            if not res:
                raise HTTPException(status_code=404, detail="Expense not found")
            return res
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))
        
    def update_expense(self, expense_id: int, expense_type: ExpenseType, payload: dict = Body(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        try:
            existing_expense = self.service.get_expense_with_shares(db, expense_id, requester_id=current_user.id)
            if not existing_expense:
                raise HTTPException(status_code=404, detail="Expense not found")
            
            Schema = self.update_payload_mapping.get(expense_type)
            if not Schema:
                raise HTTPException(status_code=400, detail="Invalid expense type for update")
            
            validated_payload = Schema(**payload)
            return self.service.update_expense(db, expense_id, validated_payload, expense_type, requester_id=current_user.id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"Validation error: {e}")
            raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")

    def delete_expense(self, expense_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
        try:
            success = self.service.delete_expense(db, expense_id, requester_id=current_user.id)
            if not success:
                raise HTTPException(status_code=404, detail="Expense not found")
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))
