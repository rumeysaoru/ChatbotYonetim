"""
Çalışılan birim tablosu.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class WorkingUnit(Base):
    __tablename__ = "working_units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    users = relationship("User", back_populates="working_unit")
    entries = relationship("Entry", back_populates="working_unit")