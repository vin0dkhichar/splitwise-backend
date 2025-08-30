from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class ExpenseType(str, enum.Enum):
    EQUAL = "equal"
    EXACT = "exact"
    PERCENTAGE = "percentage"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    paid_by = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    group_id = Column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True
    )
    expense_type = Column(Enum(ExpenseType), nullable=False, default=ExpenseType.EQUAL)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("Group", back_populates="expenses")
    payer = relationship("User", back_populates="payments")
    shares = relationship(
        "ExpenseShare", back_populates="expense", cascade="all, delete-orphan"
    )
