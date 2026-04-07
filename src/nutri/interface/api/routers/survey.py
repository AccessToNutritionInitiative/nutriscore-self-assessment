from fastapi import APIRouter

from nutri.application.survey import SurveyService
from nutri.interface.schemas.survey import (
    RecommandationResponse,
    SurveyRequest,
    SurveyResponse,
)

router = APIRouter(prefix="/survey", tags=["Survey"])


@router.post("")
async def get_recommandations(payload: SurveyRequest) -> SurveyResponse:
    answers = payload.to_answers()
    recos = SurveyService.get_recommandations(answers=answers)
    return SurveyResponse(
        recommandations=[
            RecommandationResponse(
                question=r.question,
                question_text=r.question_text,
                score=r.score,
                content=r.content,
            )
            for r in recos
        ]
    )
