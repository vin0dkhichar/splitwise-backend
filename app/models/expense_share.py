from sqlalchemy import Column, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class ExpenseShare(Base):
    __tablename__ = "expense_shares"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    share_amount = Column(Float, nullable=False)
    is_paid = Column(Boolean, nullable=False, default=False)

    expense = relationship("Expense", back_populates="shares")
    user = relationship("User", back_populates="shares")
