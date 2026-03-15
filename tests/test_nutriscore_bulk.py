import json
from pathlib import Path

from fastapi.testclient import TestClient

from nutri.interface.api.main import app

CSV_FILE = Path(__file__).parent / "data" / "beverages.csv"

client = TestClient(app)


def parse_ndjson(response) -> list[dict]:
    return [json.loads(line) for line in response.text.splitlines() if line.strip()]


def test_bulk_returns_200():
    with CSV_FILE.open("rb") as f:
        response = client.post("/nutriscores", files={"file": ("beverages.csv", f, "text/csv")})
    assert response.status_code == 200
    items = parse_ndjson(response)
    assert len(items) == 6


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
        response = client.post("/nutriscores", files={"file": ("beverages.csv", f, "text/csv")})
    items = parse_ndjson(response)
    for exp, item in zip(expected, items, strict=True):
        assert exp["score"] == item["score"]
        assert exp["grade"] == item["grade"]


def test_bulk_rejects_non_csv():
    response = client.post(
        "/nutriscores",
        files={"file": ("data.json", b'{"key": "value"}', "application/json")},
    )
    assert response.status_code == 400
