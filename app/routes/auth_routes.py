from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.core.database import get_db
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.core.security import create_access_token, decode_access_token
from app.core.config import settings
from app.schemas.auth_schema import Token
from app.schemas.user_schema import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
user_service = UserService(UserRepository())
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    email = form_data.username
    password = form_data.password
    user = user_service.authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    return {"access_token": token, "token_type": "bearer"}


# Dependency to get current user
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


@router.get("/me", response_model=UserResponse)
def read_me(current_user=Depends(get_current_user)):
    return current_user
