from pydantic import BaseModel


class SurveyRequest(BaseModel):
    answers: dict[str, float]


class RecommandationResponse(BaseModel):
    question: str
    question_text: str
    score: str
    content: str


class SurveyResponse(BaseModel):
    recommandations: list[RecommandationResponse]
