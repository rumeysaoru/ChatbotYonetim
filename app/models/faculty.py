"""
Fakülte tablosu.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    users = relationship("User", back_populates="faculty")
    entries = relationship("Entry", back_populates="faculty")