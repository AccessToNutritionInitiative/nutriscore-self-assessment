import json

import pytest

from nutri.domain.survey import Question
from nutri.settings import get_settings


settings = get_settings()


@pytest.fixture()
def raw_questions() -> list[dict]:
    with settings.survey.config_path.open("r") as f:
        return json.load(f)


def test_validate_questions_config(raw_questions):
    for question in raw_questions:
        Question.model_validate(question)
