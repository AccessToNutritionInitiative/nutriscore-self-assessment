import json
import sqlite3
from pathlib import Path

from loguru import logger

from nutri.application.ports.survey_repository import ISurveyRepository
from nutri.domain.survey import Answers, Question


class SqliteSurveyRepository(ISurveyRepository):
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def store_answers(self, answers: Answers, questions: list[Question]) -> None:
        questions_dict = {q.question_id: q for q in questions}
        rows = []
        for answer in answers.answers:
            question = questions_dict.get(answer.question_id)
            rows.append(
                {
                    "question_id": answer.question_id,
                    "question": question.question if question else None,
                    "answer": answer.value,
                }
            )
            if not question:
                logger.warning("Question not found from answer.question_id: {}", answer.question_id)
        data = json.dumps(rows)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO submissions (submission_id, submitted_at, answers) VALUES (?, ?, ?)",
                (str(answers.submission_id), answers.submitted_at.isoformat(), data),
            )
