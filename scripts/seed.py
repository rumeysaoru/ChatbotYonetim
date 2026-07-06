"""
Veri tabanı başlangıç test verisi
"""

import sys
import os

sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models.workingUnit import WorkingUnit
from app.models.user import User
from app.models.category import Category
from app.models.entry import Entry
from app.services.auth_service import hash_password


def run():
    db = SessionLocal()
    try:
        working_unit = (
            db.query(WorkingUnit)
            .filter(WorkingUnit.name == "Mühendislik Fakültesi")
            .first()
        )

        if not working_unit:
            working_unit = WorkingUnit(name="Mühendislik Fakültesi")
            db.add(working_unit)
            db.commit()
            db.refresh(working_unit)
            print(f"Çalışılan Birim oluşturuldu: {working_unit.name} (id={working_unit.id})")
        else:
            print(f"Çalışılan Birim zaten var: {working_unit.name} (id={working_unit.id})")

        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin",
                working_unit_id=None,
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
                working_unit_id=working_unit.id,
            )
            db.add(entry_user)
            db.commit()
            print("Veri girişçisi oluşturuldu: girisci1 / girisci123")
        else:
            print("Veri girişçisi zaten var.")

        working_unit2 = (
            db.query(WorkingUnit)
            .filter(WorkingUnit.name == "Tıp Fakültesi")
            .first()
        )

        if not working_unit2:
            working_unit2 = WorkingUnit(name="Tıp Fakültesi")
            db.add(working_unit2)
            db.commit()
            db.refresh(working_unit2)
            print(f"Çalışılan Birim oluşturuldu: {working_unit2.name} (id={working_unit2.id})")
        else:
            print(f"Çalışılan Birim zaten var: {working_unit2.name} (id={working_unit2.id})")

        entry_user2 = db.query(User).filter(User.username == "girisci2").first()
        if not entry_user2:
            entry_user2 = User(
                username="girisci2",
                password_hash=hash_password("girisci456"),
                role="data_entry",
                working_unit_id=working_unit2.id,
            )
            db.add(entry_user2)
            db.commit()
            print("Veri girişçisi oluşturuldu: girisci2 / girisci456")
        else:
            print("Veri girişçisi zaten var.")

    finally:
        db.close()


if __name__ == "__main__":
    run()