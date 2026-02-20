from pathlib import Path

from fastapi.testclient import TestClient

from nutri.interface.api.main import app
from nutri.interface.schemas.nutriscore import NutriscoreBulkResponse

CSV_FILE = Path(__file__).parent / "data" / "beverages.csv"

client = TestClient(app)


def test_bulk_returns_200():
    with CSV_FILE.open("rb") as f:
        response = client.post("/nutriscore/bulk", files={"file": ("beverages.csv", f, "text/csv")})
    assert response.status_code == 200
    response = NutriscoreBulkResponse.model_validate(response.json())
    assert response.total == 6


def test_bulk_scores_and_grades():
    expected = [
        {"score": 0, "grade": "A"},  # Still water
        {"score": 4, "grade": "C"},  # Orange juice 100%
        {"score": 4, "grade": "C"},  # Diet cola
        {"score": 16, "grade": "E"},  # Redbull
        {"score": 12, "grade": "E"},  # Cola
        {"score": 5, "grade": "C"},  # Soft drink with sweeteners
    ]
    with CSV_FILE.open("rb") as f:
        response = client.post("/nutriscore/bulk", files={"file": ("beverages.csv", f, "text/csv")})
    response = NutriscoreBulkResponse.model_validate(response.json())
    for exp, resp in zip(expected, response.results, strict=True):
        assert exp["score"] == resp.score
        assert exp["grade"] == resp.grade


def test_bulk_rejects_non_csv():
    response = client.post(
        "/nutriscore/bulk",
        files={"file": ("data.json", b'{"key": "value"}', "application/json")},
    )
    assert response.status_code == 400
