from dataclasses import dataclass
from pathlib import Path
import json

from nutri.application.survey.schemas import (
    ChoicesPropositions,
    FixedRecommandation,
    OptionPropositions,
    Question,
    ScoredRecommandations,
)


@dataclass
class QuestionResult:
    question_id: str
    question: str
    topic: str
    score: float
    recommandation: str


class SurveyService:
    @staticmethod
    def get_questions(config_path: Path) -> list[Question]:
        with config_path.open("r") as f:
            config = json.load(f)
        questions = [Question.model_validate(q) for q in config]
        return questions

    @staticmethod
    def compute_result(
        question: Question,
        selected_option: str | None = None,
        selected_choices: list[str] | None = None,
    ) -> QuestionResult:
        score = 0.0
        props = question.propositions

        if isinstance(props, OptionPropositions) and selected_option is not None:
            for p in props.propositions:
                if p.proposition == selected_option:
                    score = p.score
                    break

        elif isinstance(props, ChoicesPropositions) and selected_choices is not None:
            count = len(selected_choices)
            if props.count_score_map:
                score = props.count_score_map[min(count, len(props.count_score_map) - 1)]
            else:
                score = count * props.count_score_coeff

        recommandation = ""
        rec = question.recommandations
        if isinstance(rec, ScoredRecommandations):
            exact = [r for r in rec.recommandations if r.score == score]
            if exact:
                recommandation = exact[0].recommandation
            else:
                closest = min(rec.recommandations, key=lambda r: abs(r.score - score))
                recommandation = closest.recommandation
        elif isinstance(rec, FixedRecommandation):
            recommandation = rec.recommandation

        return QuestionResult(
            question_id=question.question_id,
            question=question.question,
            topic=question.topic.value,
            score=score,
            recommandation=recommandation,
        )
