from pathlib import Path
import json

from loguru import logger

from nutri.domain.survey import Question, Answer, Recommandation


class SurveyService:
    @staticmethod
    def get_questions(config_path: Path) -> list[Question]:
        with config_path.open("r") as f:
            raw_questions = json.load(f)
        questions = [Question.model_validate(q) for q in raw_questions]
        return questions

    @staticmethod
    def get_recommandations(answers: list[Answer], config_path: Path) -> list[Recommandation]:
        with config_path.open("r") as f:
            raw_questions = json.load(f)
        questions = [Question.model_validate(q) for q in raw_questions]
        questions_dict = {question.question_id: question for question in questions}
        recommandations: list[Recommandation] = []
        for answer in answers:
            question = questions_dict.get(answer.question_id)
            if question:
                if question_recommandations := question.recommandations:
                    if question_recommandations.type == "fixed":
                        recommandations.append(
                            Recommandation(question_id=question.question_id, recommandation=question_recommandations.recommandation)
                        )
                    elif question_recommandations.type == "scored":
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
