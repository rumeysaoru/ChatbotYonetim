from fastapi import Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from app.services.auth_service import decode_access_token


class RedirectException(Exception):
    def __init__(self, url: str):
        self.url = url


def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")

    if not token:
        raise RedirectException(url="/login")

    payload = decode_access_token(token)

    if payload is None:
        raise RedirectException(url="/login")

    return payload


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için yönetici yetkisi gerekiyor.",
        )
    return user


def require_data_entry(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "data_entry":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem için veri girişçisi yetkisi gerekiyor.",
        )
    return user