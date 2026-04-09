from enum import StrEnum
from typing import Annotated
from pydantic import BaseModel, Field


class Topic(StrEnum):
    management = "Management & Products"
    marketing = "Marketing"
    workforce = "Workforce Programs"
    labeling = "Labeling"
    engagement = "Engagement"


class Recommandation(BaseModel):
    score: float
    recommandation: str


class Proposition(BaseModel): ...


class OptionProposition(Proposition):
    proposition: str
    score: float


class ChoicesProposition(Proposition):
    proposition: str
    count_score_coeff: Annotated[
        float, Field(description="Count the number of selection and multiply by the score coeff to get the final score. 0 if unscored.")
    ]
    none_of_the_above: Annotated[bool, Field(description="None of the above choice that cancels all other choices.", default=False)]


class Question(BaseModel):
    topic: Topic
    question: str
    question_id: str
    recommandations: list[Recommandation]
    propositions: list[Proposition]
