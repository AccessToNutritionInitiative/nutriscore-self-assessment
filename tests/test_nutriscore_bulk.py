from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nutri.interface.api.main import app

BEVERAGES_CSV = Path(__file__).parent / "data" / "beverages.csv"
GENERAL_CSV = Path(__file__).parent / "data" / "general_foods.csv"
CHEESE_CSV = Path(__file__).parent / "data" / "cheese_foods.csv"
RED_MEAT_CSV = Path(__file__).parent / "data" / "red_meat_foods.csv"
FATS_CSV = Path(__file__).parent / "data" / "fats_foods.csv"

client = TestClient(app)


def parse_response(response) -> list[dict]:
    return response.json()


def test_bulk_rejects_non_csv():
    response = client.post(
        "/nutriscores",
        files={"file": ("data.json", b'{"key": "value"}', "application/json")},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    "csv_file,expected_count",
    [
        (BEVERAGES_CSV, 6),
        (GENERAL_CSV, 5),
        (CHEESE_CSV, 5),
        (RED_MEAT_CSV, 5),
        (FATS_CSV, 5),
    ],
)
def test_bulk_returns_200(csv_file, expected_count):
    with csv_file.open("rb") as f:
        response = client.post("/nutriscores", files={"file": (csv_file.name, f, "text/csv")})
    assert response.status_code == 200
    assert len(parse_response(response)) == expected_count


@pytest.mark.parametrize(
    "csv_file,expected",
    [
        (
            BEVERAGES_CSV,
            [
                {"score": 0, "grade": "A"},
                {"score": 4, "grade": "C"},
                {"score": 4, "grade": "C"},
                {"score": 16, "grade": "E"},
                {"score": 12, "grade": "E"},
                {"score": 5, "grade": "C"},
            ],
        ),
        (
            GENERAL_CSV,
            [
                {"score": 21, "grade": "E"},
                {"score": 10, "grade": "C"},
                {"score": -2, "grade": "A"},
                {"score": -3, "grade": "A"},
                {"score": 32, "grade": "E"},
            ],
        ),
        (
            CHEESE_CSV,
            [
                {"score": 14, "grade": "D"},
                {"score": 24, "grade": "E"},
                {"score": 16, "grade": "D"},
                {"score": 3, "grade": "C"},
                {"score": 17, "grade": "D"},
            ],
        ),
        (
            RED_MEAT_CSV,
            [
                {"score": 2, "grade": "B"},
                {"score": 8, "grade": "C"},
                {"score": 12, "grade": "D"},
                {"score": 14, "grade": "D"},
                {"score": 16, "grade": "D"},
            ],
        ),
        (
            FATS_CSV,
            [
                {"score": 19, "grade": "E"},
                {"score": -3, "grade": "B"},
                {"score": 1, "grade": "B"},
                {"score": 4, "grade": "C"},
                {"score": -3, "grade": "B"},
            ],
        ),
    ],
)
def test_bulk_scores_and_grades(csv_file, expected):
    with csv_file.open("rb") as f:
        response = client.post("/nutriscores", files={"file": (csv_file.name, f, "text/csv")})
    items = parse_response(response)
    for exp, item in zip(expected, items, strict=True):
        assert exp["score"] == item["score"]
        assert exp["grade"] == item["grade"]
