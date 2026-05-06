from pydantic import BaseModel

from nutri.domain.survey import Question, ReadAnswer, WriteAnswer


class AnswerSchema(BaseModel):
    question_id: str
    question: str | None
    answer: str | list[str] | None

    def to_answer(self) -> ReadAnswer:
        return ReadAnswer(question_id=self.question_id, question=self.question, value=self.answer)

    @classmethod
    def from_answer(cls, answer: WriteAnswer, question: Question | None) -> "AnswerSchema":
        return cls(
            question_id=answer.question_id,
            question=question.question if question else None,
            answer=answer.value,
        )
