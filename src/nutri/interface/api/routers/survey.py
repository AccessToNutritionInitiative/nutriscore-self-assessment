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
def submit_answers(answers: list[AnswerRequest]) -> list[RecommandationResponse]:
    questions = SurveyService.get_questions(config_path=settings.survey.config_path)
    questions_by_id = {q.question_id: q for q in questions}

    results = []
    for answer in answers:
        question = questions_by_id.get(answer.question_id)
        if question is None:
            continue
        result = SurveyService.compute_result(
            question=question,
            selected_option=answer.selected_option,
            selected_choices=answer.selected_choices,
        )
        results.append(
            RecommandationResponse(
                question_id=result.question_id,
                question=result.question,
                topic=question.topic,
                score=result.score,
                recommandation=result.recommandation,
            )
        )
    return results
