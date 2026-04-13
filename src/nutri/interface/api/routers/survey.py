from fastapi import APIRouter

from nutri.interface.schemas.survey import QuestionResponse
from nutri.application.survey.service import SurveyService
from nutri.settings import get_settings

settings = get_settings()

router = APIRouter(prefix="/survey", tags=["Survey"])


@router.get("/questions")
def get_questions() -> list[QuestionResponse]:
    questions = SurveyService.get_questions(config_path=settings.survey.config_path)
    return [QuestionResponse.from_question(question=question) for question in questions]
