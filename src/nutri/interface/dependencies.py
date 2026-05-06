from pathlib import Path

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from nutri.application.ports.survey_repository import ISurveyRepository
from nutri.infrastructure.survey.repository import SqliteSurveyRepository
from nutri.settings import get_settings

settings = get_settings()


def get_survey_repository(db_path: Path = settings.db_path) -> ISurveyRepository:
    return SqliteSurveyRepository(db_path=db_path)


_admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


def require_admin(api_key: str | None = Security(_admin_key_header)) -> None:
    expected = settings.admin_api_key
    if not expected or api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin key")
