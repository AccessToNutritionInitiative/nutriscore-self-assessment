from pathlib import Path

from fastapi.testclient import TestClient

from nutri.interface.api.main import app
from nutri.interface.schemas.hsr import HsrBulkResponse

CSV_FILE = Path(__file__).parent / "data" / "sample_hsr_case.csv"

client = TestClient(app)


def test_bulk_returns_200():
    with CSV_FILE.open("rb") as f:
        response = client.post("/hsr_bulk", files={"file": ("sample_hsr_case.csv", f, "text/csv")})
    assert response.status_code == 200
    response = HsrBulkResponse.model_validate(response.json())
    assert response.total == 36


def test_bulk_rating():
    expected = [
        {"expected_score": 0, "expected_star_rating": 4.0},
        {"expected_score": 0, "expected_star_rating": 4.0},
        {"expected_score": -1, "expected_star_rating": 4.5},
        {"expected_score": 1, "expected_star_rating": 3.5},
        {"expected_score": 1, "expected_star_rating": 3.5},
        {"expected_score": 0, "expected_star_rating": 4.0},
        {"expected_score": 22, "expected_star_rating": 1.0},
        {"expected_score": 2, "expected_star_rating": 3.5},
        {"expected_score": 8, "expected_star_rating": 2.5},
        {"expected_score": 4, "expected_star_rating": 3.0},
        {"expected_score": 26, "expected_star_rating": 0.5},
        {"expected_score": 7, "expected_star_rating": 2.5},
        {"expected_score": 2, "expected_star_rating": 4.0},
        {"expected_score": 4, "expected_star_rating": 3.0},
        {"expected_score": 21, "expected_star_rating": 0.5},
        {"expected_score": 5, "expected_star_rating": 3.0},
        {"expected_score": 4, "expected_star_rating": 3.0},
        {"expected_score": 30, "expected_star_rating": 0.5},
        {"expected_score": 41, "expected_star_rating": 1.0},
        {"expected_score": 20, "expected_star_rating": 4.0},
        {"expected_score": 25, "expected_star_rating": 3.0},
        {"expected_score": 14, "expected_star_rating": 4.5},
        {"expected_score": 23, "expected_star_rating": 3.5},
        {"expected_score": 23, "expected_star_rating": 3.5},
        {"expected_score": 33, "expected_star_rating": 2.5},
        {"expected_score": 19, "expected_star_rating": 5.0},
        {"expected_score": 29, "expected_star_rating": 3.5},
        {"expected_score": 32, "expected_star_rating": 2.5},
        {"expected_score": 29, "expected_star_rating": 3.5},
        {"expected_score": 33, "expected_star_rating": 2.5},
        {"expected_score": -2, "expected_star_rating": 4.0},
        {"expected_score": 14, "expected_star_rating": 0.5},
        {"expected_score": 14, "expected_star_rating": 4.5},
        {"expected_score": 0, "expected_star_rating": 4.0},
        {"expected_score": 4, "expected_star_rating": 5.0},
        {"expected_score": 0, "expected_star_rating": 4.0},
    ]

    with CSV_FILE.open("rb") as f: 
        response = client.post("/hsr_bulk", files={"file": ("sample_hsr_case.cvs", f, "text/csv")})
    response = HsrBulkResponse.model_validate(response.json())
    for exp, resp in zip (expected, response.results, strict=True): 
        assert exp["expected_score"] == resp.final_score
        assert exp["expected_star_rating"] == resp.star_rating

def test_rejects_non_csv(): 
    response = client.post(
        "/hsr_bulk", 
        files={"file": ("data.json", b'{"key": "value"}', "application/json")}, 
    )
    assert response.status_code == 400