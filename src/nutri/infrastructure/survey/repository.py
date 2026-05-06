import json
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import UUID

from loguru import logger

from nutri.application.ports.survey_repository import ISurveyRepository
from nutri.domain.survey import (
    CompanySize,
    Question,
    ReadSubmission,
    Submission,
    SubmissionId,
)
from nutri.infrastructure.survey.schemas import AnswerSchema


class SqliteSurveyRepository(ISurveyRepository):
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def store_answers(self, submission: Submission, questions: list[Question]) -> None:
        questions_dict = {q.question_id: q for q in questions}
        rows = []
        for answer in submission.answers:
            question = questions_dict.get(answer.question_id)
            if not question:
                logger.warning("Question not found from answer.question_id: {}", answer.question_id)
            answer_schema = AnswerSchema.from_answer(answer=answer, question=question)
            rows.append(answer_schema.model_dump())
        data = json.dumps(rows)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO submissions (submission_id, submitted_at, company_name, country, company_size, answers) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(submission.submission_id),
                    submission.submitted_at.isoformat(),
                    submission.company_name,
                    submission.country,
                    submission.company_size.value,
                    data,
                ),
            )

    def list_submissions(self, since: datetime) -> list[ReadSubmission]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT submission_id, submitted_at, company_name, country, company_size, answers"
                " FROM submissions WHERE submitted_at >= ? ORDER BY submitted_at DESC",
                (since.isoformat(),),
            )
            rows = cursor.fetchall()
        submissions: list[ReadSubmission] = []
        for row in rows:
            raw_answers = json.loads(row["answers"])
            answers = [AnswerSchema.model_validate(a).to_answer() for a in raw_answers]
            submissions.append(
                ReadSubmission(
                    submission_id=SubmissionId(UUID(row["submission_id"])),
                    submitted_at=datetime.fromisoformat(row["submitted_at"]),
                    company_name=row["company_name"],
                    country=row["country"],
                    company_size=CompanySize(row["company_size"]),
                    answers=answers,
                )
            )
        return submissions
