from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal, NewType
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Topic(StrEnum):
    management = "Management & Products"
    marketing = "Marketing"
    workforce = "Workforce Programs"
    labeling = "Labeling"
    engagement = "Engagement"


class ScoredRecommandation(BaseModel):
    score: float
    recommandation: str


class ScoredRecommandations(BaseModel):
    type: Literal["scored"]
    recommandations: list[ScoredRecommandation]


class FixedRecommandation(BaseModel):
    type: Literal["fixed"]
    recommandation: str


class OptionProposition(BaseModel):
    proposition: str
    score: float
    text_inputs: bool = False


class TextProposition(BaseModel):
    type: Literal["text"]
    proposition: str


class OptionPropositions(BaseModel):
    type: Literal["option"]
    propositions: list[OptionProposition]


class ChoicesPropositions(BaseModel):
    type: Literal["choices"]
    count_score_coeff: Annotated[
        float,
        Field(
            description="Count the number of selection and multiply by the score coeff to get the final score. 0 if unscored.",
            default=0,
        ),
    ]
    count_score_map: Annotated[
        list[float],
        Field(
            description="Map from count of selections (index) to score. When present, takes precedence over count_score_coeff.",
            default_factory=list,
        ),
    ]
    none_of_the_above: Annotated[
        bool,
        Field(
            description="None of the above choice that cancels all other choices.",
            default=False,
        ),
    ]
    propositions: list[str]


class Question(BaseModel):
    topic: Topic
    question: str
    question_id: str
    dependency: str = ""  # Question id | Such as "if yes"
    recommandations: Annotated[
        ScoredRecommandations | FixedRecommandation | None,
        Field(discriminator="type", default=None),
    ]
    propositions: Annotated[
        OptionPropositions | ChoicesPropositions | TextProposition,
        Field(discriminator="type"),
    ]


@dataclass
class Answer:
    question_id: str
    score: float
    value: str | list[str] | None = None


SubmissionId = NewType("SubmissionId", UUID)


@dataclass
class Answers:
    answers: list[Answer]
    submission_id: SubmissionId = field(default_factory=lambda: SubmissionId(uuid4()))
    submitted_at: datetime = datetime.now()


@dataclass
class Recommandation:
    question_id: str
    recommandation: str
