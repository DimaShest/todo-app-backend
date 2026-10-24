import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    cors_origins: list[str]


def get_settings() -> Settings:
    database_url = os.getenv("DATABASE_URL")
    cors_origins_str = os.getenv("CORS_ORIGINS")

    if database_url is None:
        raise ValueError("database_url имеет значение None")
    if cors_origins_str is None:
        raise ValueError("cors_origins имеет значение None")

    cors_origins = cors_origins_str[1:-1].split(",")
    cors_origins = [cors_origin[1:-1] for cors_origin in cors_origins]

    return Settings(database_url, cors_origins)
