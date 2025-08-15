from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    payer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    payee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)
    expense_share_id = Column(Integer, ForeignKey("expense_shares.id", ondelete="SET NULL"), nullable=True)
    settled_at = Column(DateTime(timezone=True), server_default=func.now())

    payer = relationship("User", foreign_keys=[payer_id], back_populates="payments_made")
    payee = relationship("User", foreign_keys=[payee_id], back_populates="payments_received")
    group = relationship("Group", back_populates="settlements")
    expense_share = relationship("ExpenseShare", back_populates="settlement")
