from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserUpdate
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, db: Session, user_data: UserCreate):
        # unique checks
        if self.repository.get_user_by_email(db, user_data.email):
            raise ValueError("email_exists")
        if self.repository.get_user_by_username(db, user_data.username):
            raise ValueError("username_exists")

        hashed_password = hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password
        )
        return self.repository.create_user(db, new_user)

    def authenticate_user(self, db: Session, email: str, password: str):
        user = self.repository.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def get_user_by_id(self, db: Session, user_id: int):
        return self.repository.get_user_by_id(db, user_id)

    def update_user(self, db: Session, user_id: int, user_data: UserUpdate):
        user = self.repository.get_user_by_id(db, user_id)
        if not user:
            return None

        if user_data.username:
            existing = self.repository.get_user_by_username(db, user_data.username)
            if existing and existing.id != user.id:
                raise ValueError("username_exists")
            user.username = user_data.username
        if user_data.email:
            existing = self.repository.get_user_by_email(db, user_data.email)
            if existing and existing.id != user.id:
                raise ValueError("email_exists")
            user.email = user_data.email
        if user_data.password:
            user.password_hash = hash_password(user_data.password)

        return self.repository.update_user(db, user)

    def delete_user(self, db: Session, user_id: int):
        user = self.repository.get_user_by_id(db, user_id)
        if not user:
            return None
        self.repository.delete_user(db, user)
        return True
