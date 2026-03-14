from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str


def get_settings():
    return Settings()  # type: ignore
