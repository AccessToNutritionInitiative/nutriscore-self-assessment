import pytest

from nutri.application.survey import SurveyService
from nutri.domain.survey import Answer, Recommandation
from nutri.settings import REPO_DIR

CONFIG_PATH = REPO_DIR / "tests/data/survey_questions.json"


@pytest.fixture
def answers() -> list[Answer]:
    return [
        Answer(question_id="1.1.1", score=5),
        Answer(question_id="1.2.2", score=2.5),
        Answer(question_id="1.4.2", score=2.5),
        Answer(question_id="2.1.1", score=0),
        Answer(question_id="1.7", score=8.0),
    ]


@pytest.fixture
def expected_recommandations() -> list[Recommandation]:
    return [
        Recommandation(question_id="1.1.1", recommandation="A business plan will help keep your company financially healthy."),
        Recommandation(question_id="1.2.2", recommandation="Following national/international guidelines helps develop healthier products."),
        Recommandation(question_id="1.4.2", recommandation="Chemical analysis in analytical laboratories is the preferred method."),
        Recommandation(
            question_id="1.7",
            recommandation="Consider extending the range of experts you work with, to improve the nutritional quality of your products and ensure food quality and safety.",
        ),
    ]


def test_get_recommandations(answers: list[Answer], expected_recommandations: list[Recommandation]):
    questions = SurveyService.get_questions(config_path=CONFIG_PATH)
    recommandations = SurveyService._get_recommandations(answers=answers, questions=questions)
    for recommandation, expected_recommandation in zip(recommandations, expected_recommandations):
        assert recommandation == expected_recommandation
