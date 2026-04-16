from abc import ABC, abstractmethod

from nutri.domain.survey import Answers, Question


class ISurveyRepository(ABC):
    @abstractmethod
    def store_answers(self, answers: Answers, questions: list[Question]) -> None: ...
