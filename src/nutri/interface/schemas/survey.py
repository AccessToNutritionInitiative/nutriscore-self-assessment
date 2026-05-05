from typing import Annotated
from pydantic import BaseModel, Field

from nutri.domain.survey import (
    Answer,
    Answers,
    ChoicesPropositions,
    CompanySize,
    OptionPropositions,
    Question,
    Recommandation,
    TextProposition,
    Topic,
)


class QuestionResponse(BaseModel):
    topic: Topic
    question: str
    question_id: str
    dependency: str
    propositions: OptionPropositions | ChoicesPropositions | TextProposition

    @classmethod
    def from_question(cls, question: Question):
        return cls(
            topic=question.topic,
            question=question.question,
            question_id=question.question_id,
            dependency=question.dependency,
            propositions=question.propositions,
        )


class SurveyResponse(BaseModel):
    max_score: float
    questions: list[QuestionResponse]


class AnswerPayload(BaseModel):
    question_id: str
    score: float
    value: str | list[str] | None = None

    def to_answer(self) -> Answer:
        return Answer(
            question_id=self.question_id,
            score=self.score,
            value=self.value,
        )


class SubmissionPayload(BaseModel):
    company_name: Annotated[str, Field(min_length=2, max_length=50)]
    country: str
    company_size: CompanySize
    answers: list[AnswerPayload]

    def to_answers(self) -> Answers:
        return Answers(
            answers=[a.to_answer() for a in self.answers],
            company_name=self.company_name,
            country=self.country,
            company_size=self.company_size,
        )


class RecommandationResponse(BaseModel):
    question_id: str
    recommandation: str

    @classmethod
    def from_recommandation(cls, recommandation: Recommandation) -> "RecommandationResponse":
        return cls(question_id=recommandation.question_id, recommandation=recommandation.recommandation)
