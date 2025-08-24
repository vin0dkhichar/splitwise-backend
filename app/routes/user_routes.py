from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.routes.auth_routes import get_current_user
from app.models.user import User


class UserRoutes:
    def __init__(self):
        self.router = APIRouter(prefix="/users", tags=["Users"])
        self.user_service = UserService(UserRepository())

        self.router.add_api_route(
            "/",
            self.create_user,
            response_model=UserResponse,
            status_code=status.HTTP_201_CREATED,
            methods=["POST"]
        )

        self.router.add_api_route(
            "/{user_id}",
            self.get_user,
            response_model=UserResponse,
            methods=["GET"]
        )

        self.router.add_api_route(
            "/{user_id}",
            self.update_user,
            response_model=UserResponse,
            methods=["PUT"]
        )

        # self.router.add_api_route(
        #     "/{user_id}",
        #     self.delete_user,
        #     status_code=status.HTTP_204_NO_CONTENT,
        #     methods=["DELETE"]
        # )

    def create_user(self, payload: UserCreate, db: Session = Depends(get_db)):
        try:
            user = self.user_service.create_user(db, payload)
        except ValueError as e:
            if str(e) == "email_exists":
                raise HTTPException(status_code=400, detail="Email already registered")
            if str(e) == "username_exists":
                raise HTTPException(status_code=400, detail="Username already taken")
            raise HTTPException(status_code=400, detail="Bad request")
        return user

    def get_user(self, user_id: int, db: Session = Depends(get_db)):
        user = self.user_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update_user(self, user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
        if current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
        updated_user = self.user_service.update_user(db, user_id, payload)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated_user

    def delete_user(self, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
        if current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")
        success = self.user_service.delete_user(db, user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return None