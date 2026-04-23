from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings

REPO_DIR = Path(__file__).absolute().parent.parent.parent


class SurveySettings(BaseModel):
    config_path: Path = REPO_DIR / "survey.json"


class Settings(BaseSettings):
    survey: SurveySettings = SurveySettings()

    # Replaced by env variable in docker
    db_path: Path = REPO_DIR / "data/nutri.db"
    env: str = "dev"


def get_settings():
    return Settings()
