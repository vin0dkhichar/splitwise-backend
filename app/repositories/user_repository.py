from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional


class UserRepository:
    def create_user(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def update_user(self, db: Session, user: User) -> User:
        db.commit()
        db.refresh(user)
        return user

    def get_all_users(self, db: Session):
        return db.query(User).all()

    def delete_user(self, db: Session, user: User):
        db.delete(user)
        db.commit()
