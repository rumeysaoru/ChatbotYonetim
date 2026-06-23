"""
Kategori tablosu
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("name", "faculty_id", name="uq_category_name_per_faculty"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    description = Column(String(500), nullable=True)

    faculty_id = Column(Integer, ForeignKey("faculties.id"), nullable=False)

    created_by_ai = Column(Integer, default=0, nullable=False)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    faculty = relationship("Faculty")
    creator = relationship("User")
    entries = relationship(
        "Entry",
        back_populates="category",
        foreign_keys="Entry.category_id",
    )

