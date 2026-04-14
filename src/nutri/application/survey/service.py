from pathlib import Path
import json

from nutri.application.survey.schemas import (
    FixedRecommandation,
    Question,
    ScoredRecommandations,
)


class SurveyService:
    @staticmethod
    def get_questions(config_path: Path) -> list[Question]:
        with config_path.open("r") as f:
            raw_questions = json.load(f)
        questions = [Question.model_validate(q) for q in raw_questions]
        return questions

    @staticmethod
    def get_recommandation(question: Question, score: float) -> str:
        rec = question.recommandations
        if isinstance(rec, ScoredRecommandations):
            for r in rec.recommandations:
                if r.score == score:
                    return r.recommandation
            raise ValueError(
                f"No recommandation matches score {score} for question {question.question_id}"
            )
        if isinstance(rec, FixedRecommandation):
            return rec.recommandation
        return ""
