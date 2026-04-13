from pathlib import Path
import json

from nutri.application.survey.schemas import Question


class SurveyService:
    @staticmethod
    def get_questions(config_path: Path) -> list[Question]:
        with config_path.open("r") as f:
            config = json.load(f)
            questions = [Question.model_validate(q) for q in config]

