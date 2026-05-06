from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_DIR = Path(__file__).absolute().parent.parent.parent


class SurveySettings(BaseModel):
    config_path: Path = REPO_DIR / "survey.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    survey: SurveySettings = SurveySettings()

    # Replaced by env variable in docker
    db_path: Path = REPO_DIR / "data/nutri.db"
    env: str = "dev"
    admin_api_key: str | None = None


def get_settings():
    return Settings()
