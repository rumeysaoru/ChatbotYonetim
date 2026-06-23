"""
Routerları korumak için kullanılan bağımlılıklar
"""

from fastapi import Request, Depends, HTTPException, status

from app.services.auth_service import decode_access_token


def get_current_user(request: Request) -> dict:
    
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Giriş yapmanız gerekiyor.",
        )

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Oturumunuzun süresi dolmuş, lütfen tekrar giriş yapın.",
        )

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





