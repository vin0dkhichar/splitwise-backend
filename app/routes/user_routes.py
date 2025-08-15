from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.routes.auth_routes import get_current_user
from app.models.user import User


class UserRoutes:
    router = APIRouter(prefix="/users", tags=["Users"])
    user_service = UserService(UserRepository())

    @router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
    def create_user(payload: UserCreate, db: Session = Depends(get_db)):
        try:
            user = UserRoutes.user_service.create_user(db, payload)
        except ValueError as e:
            if str(e) == "email_exists":
                raise HTTPException(status_code=400, detail="Email already registered")
            if str(e) == "username_exists":
                raise HTTPException(status_code=400, detail="Username already taken")
            raise HTTPException(status_code=400, detail="Bad request")
        return user

    @router.get("/{user_id}", response_model=UserResponse)
    def get_user(user_id: int, db: Session = Depends(get_db)):
        user = UserRoutes.user_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @router.put("/{user_id}", response_model=UserResponse)
    def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
        if current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
        updated_user = UserRoutes.user_service.update_user(db, user_id, payload)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated_user

    @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
        if current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")
        success = UserRoutes.user_service.delete_user(db, user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return None
