from typing import Annotated
from fastapi import APIRouter, Depends

from nutri.application.ports.survey_repository import ISurveyRepository
from nutri.application.survey import SurveyService
from nutri.domain.survey import Answers
from nutri.interface import dependencies
from nutri.interface.schemas.survey import AnswerRequest, QuestionResponse, RecommandationResponse
from nutri.settings import get_settings

settings = get_settings()

router = APIRouter(prefix="/survey", tags=["Survey"])


@router.get("/questions")
def get_questions() -> list[QuestionResponse]:
    questions = SurveyService.get_questions(config_path=settings.survey.config_path)
    return [QuestionResponse.from_question(question=question) for question in questions]


@router.post("/answers")
def submit_answers(
    payload: list[AnswerRequest], survey_repository: Annotated[ISurveyRepository, Depends(dependencies.get_survey_repository)]
) -> list[RecommandationResponse]:
    keep_data = True
    recommmandations = SurveyService.submit_answers(
        answers=Answers(answers=[answer.to_answer() for answer in payload]),
        config_path=settings.survey.config_path,
        keep_data=keep_data,
        survey_repository=survey_repository,
    )
    return [RecommandationResponse.from_recommandation(recommandation=recommandation) for recommandation in recommmandations]
