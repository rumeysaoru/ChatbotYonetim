"""
Kullanıcı tablosu. İki rol var: admin (merkezi, tüm fakülteleri görür) ve data_entry (bir fakülteye bağlı).
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    
    role = Column(String(20), nullable=False)

    faculty_id = Column(Integer, ForeignKey("faculties.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    faculty = relationship("Faculty", back_populates="users")
    entries = relationship("Entry", back_populates="created_by_user")