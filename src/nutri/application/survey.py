from pathlib import Path
import json

from loguru import logger

from nutri.application.ports.survey_repository import ISurveyRepository
from nutri.domain.survey import Answers, FixedRecommandation, Question, Answer, Recommandation, ScoredRecommandations


class SurveyService:
    @staticmethod
    def get_questions(config_path: Path) -> list[Question]:
        with config_path.open("r") as f:
            raw_questions = json.load(f)
        questions = [Question.model_validate(q) for q in raw_questions]
        return questions

    @classmethod
    def submit_answers(cls, answers: Answers, keep_data: bool, config_path: Path, survey_repository: ISurveyRepository) -> list[Recommandation]:
        with config_path.open("r") as f:
            raw_questions = json.load(f)
        questions = [Question.model_validate(q) for q in raw_questions]
        recommandations = cls._get_recommandations(answers=answers.answers, questions=questions)
        if keep_data:
            survey_repository.store_answers(answers=answers, questions=questions)
        return recommandations

    @staticmethod
    def _get_recommandations(answers: list[Answer], questions: list[Question]) -> list[Recommandation]:
        questions_dict = {question.question_id: question for question in questions}
        recommandations: list[Recommandation] = []
        for answer in answers:
            question = questions_dict.get(answer.question_id)
            if question:
                if question_recommandations := question.recommandations:
                    if isinstance(question_recommandations, FixedRecommandation):
                        recommandations.append(
                            Recommandation(question_id=question.question_id, recommandation=question_recommandations.recommandation)
                        )
                    elif isinstance(question_recommandations, ScoredRecommandations):
                        found = False
                        for recommandation in question_recommandations.recommandations:
                            if recommandation.score == answer.score:
                                recommandations.append(Recommandation(question_id=answer.question_id, recommandation=recommandation.recommandation))
                                found = True
                                break
                        if not found:
                            logger.error(
                                "Score not matching between answer: {}, and question {} recommandations: {}",
                                answer,
                                question.question_id,
                                question.recommandations,
                            )
                            raise ValueError(f"No recommandation matches score {answer.score} for question {question.question_id}")
        return recommandations
