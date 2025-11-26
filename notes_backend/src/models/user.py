from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from src.core.database import Base


class User(Base):
    """
    User model for authentication.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(191), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notes = relationship("Note", back_populates="owner", cascade="all, delete-orphan")
