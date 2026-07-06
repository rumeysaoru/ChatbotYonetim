import requests as http_client

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routers import admin
from app.routers import entries
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.auth_service import create_access_token, verify_password
from app.dependencies import get_current_user


limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
from app.dependencies import RedirectException

@app.exception_handler(RedirectException)
def redirect_exception_handler(request: Request, exc: RedirectException):
    return RedirectResponse(url=exc.url, status_code=302)

app.state.limiter = limiter 
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(entries.router)
app.include_router(admin.router)

OKUL_AUTH_URL = "https://api.mu.edu.tr/v1/auth/login"


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@app.post("/login")
@limiter.limit("5/minute")
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    okul_onayladi = False
    try:
        okul_cevabi = http_client.post(
            OKUL_AUTH_URL,
            json={
                "ServiceToken": "MSKU_CHATBOT_SECURE_TOKEN_2026",
                "ProjectName": "ChatbotYonetimSistemi",
                "Email": username,
                "Password": password,
            },
            timeout=5,
        )
        json_response = okul_cevabi.json()
        okul_onayladi = json_response.get("status", False)
    except Exception:
        user_fallback = db.query(User).filter(User.username == username).first()
        if user_fallback and verify_password(password, user_fallback.password_hash):
            okul_onayladi = True

    if not okul_onayladi:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Kullanıcı adı veya şifre hatalı."},
        )

    user = db.query(User).filter(User.username == username).first()
    if not user:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Bu kullanıcı sistemde tanımlı değil. Yöneticinizle iletişime geçin."},
        )

    token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role,
        working_unit_id=user.working_unit_id,
    )

    if user.role == "admin":
        redirect_url = "/admin/dashboard"
    else:
        redirect_url = "/kayitlar"

    response = RedirectResponse(url=redirect_url, status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 8,
    )
    return response


@app.get("/")
def home(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    try:
        user = get_current_user(request)
        if user["role"] == "admin":
            return RedirectResponse(url="/admin/kayitlar", status_code=302)
        else:
            return RedirectResponse(url="/kayitlar", status_code=302)
    except Exception:
        return RedirectResponse(url="/login", status_code=302)
    
@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response