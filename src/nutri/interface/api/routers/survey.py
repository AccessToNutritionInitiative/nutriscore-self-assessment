from typing import Annotated
from fastapi import APIRouter, Depends, Query

from nutri.application.ports.survey_repository import ISurveyRepository
from nutri.application.survey import SurveyService
from nutri.interface import dependencies
from nutri.interface.schemas.survey import (
    QuestionResponse,
    RecommandationResponse,
    SubmissionPayload,
    SubmissionResponse,
    SurveyResponse,
)
from nutri.settings import get_settings

settings = get_settings()

router = APIRouter(prefix="/survey", tags=["Survey"])


@router.get("/questions")
def get_questions() -> SurveyResponse:
    questions = SurveyService.get_questions(config_path=settings.survey.config_path)
    max_score = SurveyService.get_max_score(questions)
    max_score_by_topic = SurveyService.get_max_score_by_topic(questions)
    return SurveyResponse(
        max_score=max_score,
        max_score_by_topic=max_score_by_topic,
        questions=[QuestionResponse.from_question(q) for q in questions],
    )


@router.post("/answers")
def submit_answers(
    payload: SubmissionPayload, survey_repository: Annotated[ISurveyRepository, Depends(dependencies.get_survey_repository)]
) -> list[RecommandationResponse]:
    keep_data = True
    recommmandations = SurveyService.submit_answers(
        submission=payload.to_submission(),
        config_path=settings.survey.config_path,
        keep_data=keep_data,
        survey_repository=survey_repository,
    )
    return [RecommandationResponse.from_recommandation(recommandation=recommandation) for recommandation in recommmandations]


@router.get("/submissions", dependencies=[Depends(dependencies.require_admin)])
def list_submissions(
    survey_repository: Annotated[ISurveyRepository, Depends(dependencies.get_survey_repository)],
    days: Annotated[int, Query(ge=1, le=365)] = 30,
) -> list[SubmissionResponse]:
    submissions = SurveyService.list_submissions(days=days, survey_repository=survey_repository)
    return [SubmissionResponse.from_domain(s) for s in submissions]
