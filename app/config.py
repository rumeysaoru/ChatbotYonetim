"""
.env dosyasını okuyup doğrulamayı sağlar.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_expire_minutes: int = 480

   
    gemini_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings() # type: ignore