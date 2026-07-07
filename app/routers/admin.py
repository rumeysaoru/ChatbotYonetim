from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.dependencies import require_admin
from datetime import datetime

from app.models.workingUnit import WorkingUnit
from app.models.user import User
from app.models.category import Category
from app.models.entry import Entry

from app.services.pdf_service import generate_category_pdf
from app.services.staff_lookup_service import lookup_staff_by_name, lookup_staff_by_email

router = APIRouter(prefix="/admin")
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from sqlalchemy import func

    total_entries = db.query(Entry).count()
    pending = db.query(Entry).filter(Entry.status.in_(["pending", "categorized"])).count()
    categorized = db.query(Entry).filter(Entry.status == "categorized").count()
    approved = db.query(Entry).filter(Entry.status == "approved").count()
    total_units = db.query(WorkingUnit).count()
    total_users = db.query(User).count()
    recent_entries = db.query(Entry).order_by(Entry.created_at.desc()).limit(5).all()
    total_categories = db.query(Category).count()
    
    return templates.TemplateResponse(
        request,
        "admin/dashboard.html",
        {
            "total_entries": total_entries,
            "pending": pending,
            "categorized": categorized,
            "approved": approved,
            "total_units": total_units,
            "total_categories": total_categories,
            "total_users": total_users,
            "recent_entries": recent_entries,
        },
    )
templates = Jinja2Templates(directory="app/templates")

@router.get("/kayitlar", response_class=HTMLResponse)
def list_all_entries(
    request: Request,
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
    page: int = 1,
    working_unit_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    per_page = 20
    offset = (page - 1) * per_page

    query = db.query(Entry)

    if working_unit_id:
        query = query.filter(Entry.working_unit_id == working_unit_id)
    if status:
        query = query.filter(Entry.status == status)
    if search:
        query = query.filter(Entry.content.ilike(f"%{search}%"))
    
    if date_from:
        try:
            dt_from = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Entry.created_at >= dt_from)
        except ValueError:
            pass

    if date_to:
        try:
            dt_to = datetime.strptime(date_to, "%Y-%m-%d")
            dt_to = dt_to.replace(hour=23, minute=59, second=59)
            query = query.filter(Entry.created_at <= dt_to)
        except ValueError:
            pass

    total = query.count()
    entries = (
        query.join(WorkingUnit, Entry.working_unit_id == WorkingUnit.id)
        .order_by(WorkingUnit.name.asc(), Entry.content.asc())
        .offset(offset)
        .limit(per_page)
        .all()
    )
    categories = db.query(Category).all()
    working_units = db.query(WorkingUnit).all()
    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse(
        request,
        "admin/entries.html",
        {
            "entries": entries,
            "categories": categories,
            "working_units": working_units,
            "page": page,
            "total_pages": total_pages,
            "selected_unit": working_unit_id,
            "selected_status": status,
            "search": search or "",
            "date_from": date_from or "",
            "date_to": date_to or "",
        },
    )


@router.post("/kayitlar/{entry_id}/kategori")
def assign_category(
    entry_id: int,
    category_id: int = Form(...),
    expected_version: int = Form(...),
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    entry = db.query(Entry).filter(Entry.id == entry_id).first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kayıt bulunamadı.")

    if entry.version != expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu kayıt başka bir yönetici tarafından güncellendi. Lütfen yenileyin.",
        )

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı.")

    entry.category_id = category_id
    entry.status = "approved"
    entry.version += 1
    db.commit()

    return RedirectResponse(url="/admin/kayitlar?success=1", status_code=303)


@router.get("/kategoriler", response_class=HTMLResponse)
def list_categories(
    request: Request,
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
    page: int = 1,
):
    per_page = 20
    offset = (page - 1) * per_page
    total = db.query(Category).count()
    categories = db.query(Category).order_by(Category.id).offset(offset).limit(per_page).all()
    working_units = db.query(WorkingUnit).all()
    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse(
        request,
        "admin/categories.html",
        {"categories": categories, "working_units": working_units, "page": page, "total_pages": total_pages},
    )

@router.post("/kayitlar/toplu-onayla")
def bulk_approve(
    entry_ids: str = Form(...),
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    ids = [int(i) for i in entry_ids.split(",") if i.strip()]

    for entry_id in ids:
        entry = db.query(Entry).filter(Entry.id == entry_id).first()
        if entry and entry.status != "approved":
            entry.status = "approved"
            entry.version += 1

    db.commit()
    return RedirectResponse(url="/admin/kayitlar?success=1", status_code=303)
@router.post("/kategoriler")
def create_category(
    request: Request,
    name: str = Form(...),
    working_unit_id: int = Form(...),
    description: str = Form(""),
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Category)
        .filter(Category.name == name, Category.working_unit_id == working_unit_id)
        .first()
    )
    if existing:
        return RedirectResponse(url="/admin/kategoriler?error=Bu+birimde+bu+isimde+bir+kategori+zaten+var.", status_code=303)

    new_category = Category(
        name=name,
        description=description or None,
        working_unit_id=working_unit_id,
        created_by=int(user["sub"]),
        created_by_ai=0,
    )
    db.add(new_category)
    db.commit()

    return RedirectResponse(url="/admin/kategoriler?success=1", status_code=303)


@router.get("/pdf/{category_id}")
def download_category_pdf(
    category_id: int,
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori bulunamadı.")

    entries = (
        db.query(Entry)
        .filter(Entry.category_id == category_id)
        .order_by(Entry.created_at.asc())
        .all()
    )

    pdf_bytes = generate_category_pdf(
        category_name=category.name,
        working_unit_name=category.working_unit.name,
        entries=entries,
    )

    safe_filename = f"kategori_{category.id}_raporu.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'},
    )


@router.get("/birimler", response_class=HTMLResponse)
def list_working_units(
    request: Request,
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
    page: int = 1,
):
    per_page = 20
    offset = (page - 1) * per_page
    total = db.query(WorkingUnit).count()
    working_units = db.query(WorkingUnit).order_by(WorkingUnit.id).offset(offset).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse(
        request,
        "admin/working_units.html",
        {"working_units": working_units, "page": page, "total_pages": total_pages},
    )


@router.post("/birimler")
def create_working_unit(
    name: str = Form(...),
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing = db.query(WorkingUnit).filter(WorkingUnit.name == name).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu isimde bir çalışılan birim zaten var",
        )

    new_working_unit = WorkingUnit(name=name)
    db.add(new_working_unit)
    db.commit()

    return RedirectResponse(url="/admin/birimler?success=1", status_code=303)


@router.get("/kullanicilar", response_class=HTMLResponse)
def list_users(
    request: Request,
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
    page: int = 1,
):
    per_page = 20
    offset = (page - 1) * per_page
    total = db.query(User).count()
    users = db.query(User).order_by(User.id).offset(offset).limit(per_page).all()
    working_units = db.query(WorkingUnit).all()
    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse(
        request,
        "admin/users.html",
        {"users": users, "working_units": working_units, "page": page, "total_pages": total_pages},
    )


@router.get("/kullanicilar/sorgula")
def lookup_user_info(
    email: str,
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    staff_info = lookup_staff_by_email(email)
    if not staff_info:
        return {"success": False, "message": "Bu e-posta için bilgi bulunamadı."}

    working_unit_name = staff_info.get("working_unit")
    working_unit_id = None

    if working_unit_name:
        existing_unit = db.query(WorkingUnit).filter(WorkingUnit.name == working_unit_name).first()
        if existing_unit:
            working_unit_id = existing_unit.id
        else:
            new_unit = WorkingUnit(name=working_unit_name)
            db.add(new_unit)
            db.commit()
            db.refresh(new_unit)
            working_unit_id = new_unit.id

    staff_info["working_unit_id"] = working_unit_id
    return {"success": True, "data": staff_info}


@router.post("/kullanicilar")
def create_user(
    username: str = Form(...),
    role: str = Form(...),
    working_unit_id: str = Form(""),
    name: str = Form(""),
    surname: str = Form(""),
    title: str = Form(""),
    working_unit_name: str = Form(""),
    email: str = Form(""),
    office_phone: str = Form(""),
    status_field: str = Form(""),
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı zaten kayıtlı",
        )

    if role not in ("admin", "data_entry"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz rol",
        )

    if role == "data_entry" and not working_unit_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veri girişçisi için çalışılan birim seçimi zorunludur.",
        )

    new_user = User(
        username=username,
        password_hash=None,
        role=role,
        working_unit_id=int(working_unit_id) if role == "data_entry" else None,
        name=name or None,
        surname=surname or None,
        title=title or None,
        email=email or None,
        office_phone=office_phone or None,
        status=status_field or None,
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse(url="/admin/kullanicilar?success=1", status_code=303)