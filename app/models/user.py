from sqlalchemy import Column, Integer, String
from app.core.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    group_memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Expense", back_populates="payer", foreign_keys="Expense.paid_by")
    shares = relationship("ExpenseShare", back_populates="user", foreign_keys="ExpenseShare.user_id")

    payments_made = relationship("Settlement", foreign_keys="Settlement.payer_id", back_populates="payer", cascade="all, delete-orphan")
    payments_received = relationship("Settlement", foreign_keys="Settlement.payee_id", back_populates="payee", cascade="all, delete-orphan")