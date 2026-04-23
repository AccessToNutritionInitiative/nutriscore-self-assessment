from pathlib import Path
from nutri.application.ports.survey_repository import ISurveyRepository
from nutri.infrastructure.survey_repository import SqliteSurveyRepository
from nutri.settings import get_settings

settings = get_settings()


def get_survey_repository(db_path: Path = settings.db_path) -> ISurveyRepository:
    return SqliteSurveyRepository(db_path=db_path)
