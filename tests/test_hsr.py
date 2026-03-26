import json
from pathlib import Path

import pytest

from nutri.application.hsr import HsrCalculator
from nutri.interface.schemas.hsr import ProductRequest

DATA_FILE = Path(__file__).parent / "data" / "sample_hsr_case.json"


def load_cases():
    cases = json.loads(DATA_FILE.read_text())
    return [
        pytest.param(
            ProductRequest.model_validate(case["product"]),
            case["expected_score"],
            case["expected_star_rating"],
            id=case["description"],
        )
        for case in cases
    ]


@pytest.mark.parametrize("hsr_request,expected_score,expected_rating", load_cases())
def test_hsr(hsr_request: ProductRequest, expected_score: int, expected_rating: float):
    product = hsr_request.to_product()

    service = HsrCalculator()
    score, star = service.get_result(product)

    assert score == expected_score
    assert star == expected_rating
