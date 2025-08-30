from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(String(500), nullable=True)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    members = relationship(
        "GroupMember", back_populates="group", cascade="all, delete-orphan"
    )
    expenses = relationship(
        "Expense", back_populates="group", cascade="all, delete-orphan"
    )
