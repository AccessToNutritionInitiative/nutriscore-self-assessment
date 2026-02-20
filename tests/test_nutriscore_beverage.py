import json
from pathlib import Path

import pytest

from nutri.application.nutriscore import NutriscoreService
from nutri.domain.nutriscore import NutriscoreGrade
from nutri.interface.schemas.nutriscore import ProductRequest

DATA_FILE = Path(__file__).parent / "data" / "beverages.json"


def load_cases():
    cases = json.loads(DATA_FILE.read_text())
    return [
        pytest.param(
            ProductRequest.model_validate(case["product"]),
            case["expected_score"],
            case["expected_grade"],
            id=case["name"],
        )
        for case in cases
    ]


@pytest.mark.parametrize("nutriscore_request,expected_score,expected_grade", load_cases())
def test_beverage_nutriscore(nutriscore_request: ProductRequest, expected_score: int, expected_grade: str):
    product = nutriscore_request.to_product()

    service = NutriscoreService()
    score, grade = service.calculate_nutriscore(product)

    assert score == expected_score
    assert grade == NutriscoreGrade(expected_grade)
