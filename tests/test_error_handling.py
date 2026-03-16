from pathlib import Path

from fastapi.testclient import TestClient

from nutri.interface.api.main import app


client = TestClient(app)

WRONG_CSV = Path(__file__).parent / "data" / "wrong_beverages.csv"


def test_single_product_invalid_payload():
    response = client.post("/nutriscore", json={"energy_kj": -1, "sugar_g": 5.0, "category": "beverage"})
    assert response.status_code == 422
    body = response.json()
    assert body["errors"][0]["field"] == "energy_kj"


def test_bulk_invalid_csv_returns_row_errors():
    with WRONG_CSV.open("rb") as f:
        response = client.post("/nutriscores", files={"file": ("wrong_beverages.csv", f, "text/csv")})
    assert response.status_code == 200
    items = response.json()
    errors = [item for item in items if item.get("grade") is None]
    assert len(errors) == 2
