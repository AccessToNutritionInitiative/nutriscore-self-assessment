import csv
import io

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import ValidationError

from nutri.application.hsr import HsrCalculator
from nutri.interface.schemas.hsr import ProductRequest, HsrResponse, HsrBulkResponse

router = APIRouter(prefix="/hsr", tags=["HSR"])


@router.post("")
async def calculate_hsr(payload: ProductRequest) -> HsrResponse:
    product = payload.to_product()
    score, hsr_stars = HsrCalculator.get_result(product=product)
    return HsrResponse(final_score=score, star_rating=hsr_stars)


@router.post("_bulk")
def calculate_hsr_bulk(file: UploadFile) -> HsrBulkResponse:
    if file.content_type not in ("text/csv", "application/csv", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    errors = []
    products = []

    for i, row in enumerate(reader, start=1):
        try:
            products.append(ProductRequest.model_validate(row).to_product())
        except ValidationError as e:
            for error in e.errors():
                errors.append({"row": i, "field": error["loc"][-1], "message": error["msg"]})

    if errors:
        raise HTTPException(status_code=422, detail={"message": "Some rows contain invalid data.", "errors": errors})

    results = HsrCalculator.bulk_result(products=products)
    hsr_responses = [HsrResponse(final_score=score, star_rating=hsr_stars) for score, hsr_stars in results]

    return HsrBulkResponse(
        results=hsr_responses,
        total=len(hsr_responses),
    )
