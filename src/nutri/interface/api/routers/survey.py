from typing import Annotated
from fastapi import APIRouter, Depends

from nutri.application.ports.survey_repository import ISurveyRepository
from nutri.application.survey import SurveyService
from nutri.interface import dependencies
from nutri.interface.schemas.survey import QuestionResponse, RecommandationResponse, SubmissionRequest
from nutri.settings import get_settings

settings = get_settings()

router = APIRouter(prefix="/survey", tags=["Survey"])


@router.get("/questions")
def get_questions() -> list[QuestionResponse]:
    questions = SurveyService.get_questions(config_path=settings.survey.config_path)
    return [QuestionResponse.from_question(question=question) for question in questions]


@router.post("/answers")
def submit_answers(
    payload: SubmissionRequest, survey_repository: Annotated[ISurveyRepository, Depends(dependencies.get_survey_repository)]
) -> list[RecommandationResponse]:
    keep_data = True
    recommmandations = SurveyService.submit_answers(
        answers=payload.to_answers(),
        config_path=settings.survey.config_path,
        keep_data=keep_data,
        survey_repository=survey_repository,
    )
    return [RecommandationResponse.from_recommandation(recommandation=recommandation) for recommandation in recommmandations]
