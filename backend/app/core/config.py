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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480")
    )

    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    PHOTOS_DIR: Path = (
        Path(__file__).resolve().parent.parent.parent / "photos" / "visitors"
    )

    @property
    def database_url(self) -> str:
        return (
            f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
