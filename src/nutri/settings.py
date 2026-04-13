from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings

REPO_DIR = Path(__file__).absolute().parent.parent.parent
print(REPO_DIR)


class SurveySettings(BaseModel):
    config_path: Path = REPO_DIR / "survey.json"


class Settings(BaseSettings):
    survey: SurveySettings = SurveySettings()


def get_settings():
    return Settings()
