from abc import ABC, abstractmethod
from datetime import datetime

from nutri.domain.survey import Question, ReadSubmission, Submission


class ISurveyRepository(ABC):
    @abstractmethod
    def store_answers(self, submission: Submission, questions: list[Question]) -> None: ...

    @abstractmethod
    def list_submissions(self, since: datetime) -> list[ReadSubmission]: ...
