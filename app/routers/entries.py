from fastapi import APIRouter, Request, Form, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.dependencies import require_data_entry

from app.models.workingUnit import WorkingUnit
from app.models.user import User
from app.models.category import Category
from app.models.entry import Entry

from app.services.categorization_service import categorize_entry

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/kayitlar", response_class=HTMLResponse)
def list_entries(
    request: Request,
    user: dict = Depends(require_data_entry),
    db: Session = Depends(get_db),
):
    entries = (
        db.query(Entry)
        .filter(Entry.created_by == int(user["sub"]))
        .order_by(Entry.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        request,
        "entries/list.html",
        {"entries": entries},
    )


@router.get("/kayitlar/yeni", response_class=HTMLResponse)
def new_entry_form(
    request: Request,
    user: dict = Depends(require_data_entry),
    db: Session = Depends(get_db),
):
    working_unit = (
        db.query(WorkingUnit)
        .filter(WorkingUnit.id == user["working_unit_id"])
        .first()
    )

    working_unit_name = working_unit.name if working_unit else "Çalışma Biriminiz"

    return templates.TemplateResponse(
        request,
        "entries/new.html",
        {"working_unit_name": working_unit_name},
    )


@router.post("/kayitlar/yeni")
def create_entry(
    request: Request,
    content: str = Form(...),
    background_tasks: BackgroundTasks = None,
    user: dict = Depends(require_data_entry),
    db: Session = Depends(get_db),
):
    if not content or not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Metin boş olamaz.",
        )

    new_entry = Entry(
        content=content.strip(),
        created_by=int(user["sub"]),
        working_unit_id=user["working_unit_id"],
        status="pending",
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    background_tasks.add_task(run_ai_categorization, new_entry.id)

    return RedirectResponse(url="/kayitlar", status_code=303)


@router.get("/kayitlar/{entry_id}/duzenle", response_class=HTMLResponse)
def edit_entry_form(
    entry_id: int,
    request: Request,
    user: dict = Depends(require_data_entry),
    db: Session = Depends(get_db),
):
    entry = db.query(Entry).filter(Entry.id == entry_id).first()

    if not entry or entry.created_by != int(user["sub"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kayıt bulunamadı.",
        )

    return templates.TemplateResponse(
        request,
        "entries/edit.html",
        {"entry": entry},
    )


@router.post("/kayitlar/{entry_id}/duzenle")
def update_entry(
    entry_id: int,
    content: str = Form(...),
    user: dict = Depends(require_data_entry),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    entry = db.query(Entry).filter(Entry.id == entry_id).first()

    if not entry or entry.created_by != int(user["sub"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kayıt bulunamadı.",
        )

    entry.content = content.strip()
    entry.category_id = None
    entry.ai_suggested_category_id = None
    entry.status = "pending"

    db.commit()

    background_tasks.add_task(run_ai_categorization, entry_id)

    return RedirectResponse(url="/kayitlar", status_code=303)
def run_ai_categorization(entry_id: int):
    db = SessionLocal()
    try:
        entry = db.query(Entry).filter(Entry.id == entry_id).first()
        if not entry:
            return

        existing_categories = (
            db.query(Category)
            .filter(Category.working_unit_id == entry.working_unit_id)
            .all()
        )

        category_names = [c.name for c in existing_categories]

        result = categorize_entry(entry.content, category_names)

        if result["matched_category"]:
            matched = (
                db.query(Category)
                .filter(
                    Category.working_unit_id == entry.working_unit_id,
                    Category.name == result["matched_category"],
                )
                .first()
            )

            if matched:
                entry.ai_suggested_category_id = matched.id
                entry.status = "categorized"

        elif result["suggested_new_category"]:
            new_category = Category(
                name=result["suggested_new_category"],
                working_unit_id=entry.working_unit_id,
                created_by=entry.created_by,
                created_by_ai=1,
            )

            db.add(new_category)
            db.commit()
            db.refresh(new_category)

            entry.ai_suggested_category_id = new_category.id
            entry.status = "categorized"

        db.commit()

    finally:
        db.close()