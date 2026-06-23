"""
FastAPI uygulamasının giriş noktası. Template ve static dosya
kurulumu burada yapılır, routelar ayrı dosyalarda tanımlanır.
"""
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.faculty import Faculty
from app.models.user import User
from app.models.category import Category
from app.models.entry import Entry
from app.services.auth_service import verify_password, create_access_token
from app.dependencies import get_current_user

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@app.post("/login")
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Kullanıcı adı veya şifre hatalı."},
        )

    token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role,
        faculty_id=user.faculty_id,
    )

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 8,
    )
    return response


@app.get("/", response_class=HTMLResponse)
def home(user: dict = Depends(get_current_user)):
    return HTMLResponse(f"<h1>Giriş başarılı.</h1><p>Kullanıcı: {user['username']}, Rol: {user['role']}</p>")