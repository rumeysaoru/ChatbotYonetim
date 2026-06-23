"""
Veri tabanı başlangıç test verisi
"""

import sys
import os

sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models.faculty import Faculty
from app.models.user import User
from app.models.category import Category
from app.models.entry import Entry
from app.services.auth_service import hash_password


def run():
    db = SessionLocal()
    try:
        faculty = db.query(Faculty).filter(Faculty.name == "Mühendislik Fakültesi").first()
        if not faculty:
            faculty = Faculty(name="Mühendislik Fakültesi")
            db.add(faculty)
            db.commit()
            db.refresh(faculty)
            print(f"Fakülte oluşturuldu: {faculty.name} (id={faculty.id})")
        else:
            print(f"Fakülte zaten var: {faculty.name} (id={faculty.id})")

        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin",
                faculty_id=None,
            )
            db.add(admin)
            db.commit()
            print("Admin oluşturuldu: admin / admin123")
        else:
            print("Admin zaten var.")

        entry_user = db.query(User).filter(User.username == "girisci1").first()
        if not entry_user:
            entry_user = User(
                username="girisci1",
                password_hash=hash_password("girisci123"),
                role="data_entry",
                faculty_id=faculty.id,
            )
            db.add(entry_user)
            db.commit()
            print("Veri girişçisi oluşturuldu: girisci1 / girisci123")
        else:
            print("Veri girişçisi zaten var.")

    finally:
        db.close()


if __name__ == "__main__":
    run()