from pydantic import BaseModel

from nutri.application.survey.schemas import OptionPropositions, ChoicesPropositions, Question, TextProposition, Topic


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


class AnswerRequest(BaseModel):
    question_id: str
    score: float


class RecommandationResponse(BaseModel):
    question_id: str
    question: str
    topic: Topic
    score: float
    recommandation: str
