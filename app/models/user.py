"""
Kullanıcı tablosu.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False)

    working_unit_id = Column(
        Integer,
        ForeignKey("working_units.id"),
        nullable=True,
    )

    created_at = Column(DateTime, server_default=func.now())

    name = Column(String(100), nullable=True)
    surname = Column(String(100), nullable=True)
    title = Column(String(150), nullable=True)
    title_english = Column(String(150), nullable=True)

    working_unit_name = Column(String(255), nullable=True)

    picture_source = Column(String(500), nullable=True)
    email = Column(String(150), nullable=True)
    office_phone = Column(String(30), nullable=True)
    status = Column(String(10), nullable=True)

    working_unit = relationship(
        "WorkingUnit",
        back_populates="users",
    )

    entries = relationship(
        "Entry",
        back_populates="created_by_user",
    )