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
        recommandation = SurveyService.get_recommandation(question=question, score=answer.score)
        results.append(
            RecommandationResponse(
                question_id=question.question_id,
                question=question.question,
                topic=question.topic,
                score=answer.score,
                recommandation=recommandation,
            )
        )
    return results
