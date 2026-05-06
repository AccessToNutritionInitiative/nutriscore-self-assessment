from datetime import datetime
from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, Field

from nutri.domain.survey import (
    ChoicesPropositions,
    CompanySize,
    OptionPropositions,
    Question,
    ReadAnswer,
    Recommandation,
    ReadSubmission,
    Submission,
    TextProposition,
    Topic,
    WriteAnswer,
)


class QuestionResponse(BaseModel):
    topic: Topic
    question: str
    question_id: str
    info: str | None
    dependency: str
    propositions: OptionPropositions | ChoicesPropositions | TextProposition

    @classmethod
    def from_question(cls, question: Question):
        return cls(
            topic=question.topic,
            question=question.question,
            question_id=question.question_id,
            info=question.info,
            dependency=question.dependency,
            propositions=question.propositions,
        )


class SurveyResponse(BaseModel):
    max_score: float
    max_score_by_topic: dict[Topic, float]
    questions: list[QuestionResponse]


class AnswerPayload(BaseModel):
    question_id: str
    score: float
    value: str | list[str] | None = None

    def to_answer(self) -> WriteAnswer:
        return WriteAnswer(
            question_id=self.question_id,
            score=self.score,
            value=self.value,
        )


class SubmissionPayload(BaseModel):
    company_name: Annotated[str, Field(min_length=2, max_length=50)]
    country: str
    company_size: CompanySize
    answers: list[AnswerPayload]

    def to_submission(self) -> Submission:
        return Submission(
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


class SubmissionAnswerResponse(BaseModel):
    question_id: str
    question: str | None
    answer: str | list[str] | None

    @classmethod
    def from_domain(cls, answer: ReadAnswer) -> "SubmissionAnswerResponse":
        return cls(question_id=answer.question_id, question=answer.question, answer=answer.value)


class SubmissionResponse(BaseModel):
    submission_id: UUID
    submitted_at: datetime
    company_name: str
    country: str
    company_size: CompanySize
    answers: list[SubmissionAnswerResponse]

    @classmethod
    def from_domain(cls, submission: ReadSubmission) -> "SubmissionResponse":
        return cls(
            submission_id=submission.submission_id,
            submitted_at=submission.submitted_at,
            company_name=submission.company_name,
            country=submission.country,
            company_size=submission.company_size,
            answers=[SubmissionAnswerResponse.from_domain(a) for a in submission.answers],
        )
