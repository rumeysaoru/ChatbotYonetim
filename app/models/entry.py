"""
Veri girişi tablosu, projenin merkezi tablosu
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)

    content = Column(Text, nullable=False)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    working_unit_id = Column(
        Integer,
        ForeignKey("working_units.id"),
        nullable=False,
    )

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    ai_suggested_category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True,
    )

    status = Column(String(20), nullable=False, default="pending")

    version = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    created_by_user = relationship(
        "User",
        back_populates="entries",
        foreign_keys=[created_by],
    )

    working_unit = relationship(
        "WorkingUnit",
        back_populates="entries",
    )

    category = relationship(
        "Category",
        back_populates="entries",
        foreign_keys=[category_id],
    )

    ai_suggested_category = relationship(
        "Category",
        foreign_keys=[ai_suggested_category_id],
    )