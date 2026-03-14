from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_host: str


def get_settings():
    return Settings()  # type: ignore
