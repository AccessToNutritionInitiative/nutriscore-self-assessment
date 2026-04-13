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
    selected_option: str | None = None  # For "option" type questions
    selected_choices: list[str] = []  # For "choices" type questions
    text_input: str = ""  # For "text" type or option text_inputs


class RecommandationResponse(BaseModel):
    question_id: str
    question: str
    topic: Topic
    score: float
    recommandation: str
