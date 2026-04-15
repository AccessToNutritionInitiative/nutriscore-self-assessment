from typing import Annotated, Literal

from pydantic import BaseModel, Field


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
    count_score_coeff: float = 0
    count_score_map: list[float] = Field(default_factory=list)
    none_of_the_above: bool = False
    propositions: list[str]


class Question(BaseModel):
    topic: str
    question: str
    question_id: str
    dependency: str = ""
    recommandations: Annotated[
        ScoredRecommandations | FixedRecommandation | None,
        Field(discriminator="type", default=None),
    ]
    propositions: Annotated[
        OptionPropositions | ChoicesPropositions | TextProposition,
        Field(discriminator="type"),
    ]


class Recommandation(BaseModel):
    question_id: str
    recommandation: str
