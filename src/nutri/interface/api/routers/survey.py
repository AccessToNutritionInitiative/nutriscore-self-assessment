from fastapi import APIRouter

from nutri.interface.schemas.survey import AnswerRequest, QuestionResponse, RecommandationResponse
from nutri.application.survey.service import SurveyService
from nutri.settings import get_settings

settings = get_settings()

router = APIRouter(prefix="/survey", tags=["Survey"])


@router.get("/questions")
def get_questions() -> list[QuestionResponse]:
    questions = SurveyService.get_questions(config_path=settings.survey.config_path)
    return [QuestionResponse.from_question(question=question) for question in questions]


@router.post("/answers")
def submit_answers(payload: list[AnswerRequest]) -> list[RecommandationResponse]:
    recommmandations = SurveyService.get_recommandations(answers=[answer.to_answer() for answer in payload], config_path=settings.survey.config_path)
    return [RecommandationResponse.from_recommandation(recommandation=recommandation) for recommandation in recommmandations]
