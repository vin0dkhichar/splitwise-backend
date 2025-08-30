from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.repositories.settlement_repository import SettlementRepository
from app.services.settlement_service import SettlementService
from app.schemas.settlement_schema import (
    GroupSettlementResponse,
    UserSettlementSummaryResponse,
    MarkSettlementRequest,
    SettlementHistoryResponse,
)
from app.routes.auth_routes import get_current_user
from app.models.user import User


class SettlementRoutes:
    def __init__(self):
        self.router = APIRouter(prefix="/settlements", tags=["Settlements"])
        self.settlement_service = SettlementService(SettlementRepository())

        self.router.add_api_route(
            "/groups/{group_id}",
            self.get_group_settlements,
            response_model=GroupSettlementResponse,
            methods=["GET"],
            summary="Get group settlement summary",
            description="Get complete settlement summary for a group including balances and suggested settlements",
        )

        self.router.add_api_route(
            "/groups/{group_id}/balances",
            self.get_group_balances,
            methods=["GET"],
            summary="Get group balances only",
            description="Get only the balance information for a group (without settlement suggestions)",
        )

        self.router.add_api_route(
            "/groups/{group_id}/history",
            self.get_settlement_history,
            response_model=List[SettlementHistoryResponse],
            methods=["GET"],
            summary="Get settlement history",
            description="Get history of all settlements for a group",
        )

        self.router.add_api_route(
            "/groups/{group_id}/mark-paid",
            self.mark_settlement_paid,
            status_code=status.HTTP_200_OK,
            methods=["POST"],
            summary="Mark settlement as paid",
            description="Mark a settlement between two users as paid",
        )

        self.router.add_api_route(
            "/users/{user_id}",
            self.get_user_settlements,
            response_model=UserSettlementSummaryResponse,
            methods=["GET"],
            summary="Get user settlement summary",
            description="Get settlement summary for a user across all groups",
        )

        self.router.add_api_route(
            "/users/{user_id}/balances",
            self.get_user_balances,
            methods=["GET"],
            summary="Get user balances across groups",
            description="Get user's balance information across all groups",
        )

    def get_group_settlements(
        self,
        group_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        try:
            settlement_summary = self.settlement_service.get_group_settlement_summary(
                db, group_id, current_user.id
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get group settlements",
            )

        if not settlement_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
            )

        return settlement_summary

    def get_user_settlements(
        self,
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        try:
            user_summary = self.settlement_service.get_user_settlements_summary(
                db, user_id, current_user.id
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user settlements",
            )

        if not user_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user_summary

    def mark_settlement_paid(
        self,
        group_id: int,
        request: MarkSettlementRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        if request.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Settlement amount must be positive",
            )

        if request.from_user_id == request.to_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create settlement between same user",
            )

        try:
            success = self.settlement_service.mark_settlement_as_paid(
                db=db,
                group_id=group_id,
                from_user_id=request.from_user_id,
                to_user_id=request.to_user_id,
                amount=request.amount,
                requesting_user_id=current_user.id,
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to mark settlement as paid",
            )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to mark settlement as paid. Please check user IDs and group membership.",
            )

        return {"message": "Settlement marked as paid successfully"}

    def get_settlement_history(
        self,
        group_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        try:
            history = self.settlement_service.get_settlement_history(
                db, group_id, current_user.id
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get settlement history",
            )

        return history

    def get_group_balances(
        self,
        group_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        try:
            if not self.settlement_service.validate_group_access(
                db, current_user.id, group_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have access to this group",
                )

            balances = self.settlement_service.calculate_group_balances(db, group_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get group balances",
            )

        if not balances:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No balances found for this group",
            )

        return {
            "group_id": group_id,
            "balances": [
                {
                    "user_id": user_id,
                    "balance": round(balance, 2),
                    "status": (
                        "owed" if balance > 0 else "owes" if balance < 0 else "settled"
                    ),
                }
                for user_id, balance in balances.items()
                if abs(balance) > 0.01
            ],
        }

    def get_user_balances(
        self,
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        if user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users can only view their own balances",
            )

        try:
            balances = self.settlement_service.calculate_user_balances_across_groups(
                db, user_id
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user balances",
            )

        return {
            "user_id": user_id,
            "group_balances": [
                {
                    "group_id": group_id,
                    "balance": round(balance, 2),
                    "status": (
                        "owed" if balance > 0 else "owes" if balance < 0 else "settled"
                    ),
                }
                for group_id, balance in balances.items()
            ],
        }
