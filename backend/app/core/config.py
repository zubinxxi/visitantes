import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


class Settings:
    DB_HOST: str = _require_env("DB_HOST")
    DB_PORT: int = int(_require_env("DB_PORT"))
    DB_NAME: str = _require_env("DB_NAME")
    DB_USER: str = _require_env("DB_USER")
    DB_PASS: str = _require_env("DB_PASS")

    SECRET_KEY: str = _require_env("SECRET_KEY")
    ADMIN_GROUP_ID: int = int(os.getenv("ADMIN_GROUP_ID", "1"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480")
    )

    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    PHOTOS_DIR: Path = (
        Path(__file__).resolve().parent.parent.parent / "photos" / "visitors"
    )

    # SMTP Configuration
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() == "true"
    SMTP_SSL: bool = os.getenv("SMTP_SSL", "false").lower() == "true"
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "info@visitantesdb.com")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "Visitantes AMP")

    # Database pool
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_POOL_MAX_OVERFLOW: int = int(os.getenv("DB_POOL_MAX_OVERFLOW", "10"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "300"))

    # Frontend
    FRONTEND_HOST: str = os.getenv("FRONTEND_HOST", "http://localhost:5173")

    @property
    def database_url(self) -> str:
        from urllib.parse import quote_plus
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASS)
        return (
            f"mysql+asyncmy://{user}:{password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def sync_database_url(self) -> str:
        from urllib.parse import quote_plus
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASS)
        return (
            f"mysql+pymysql://{user}:{password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
