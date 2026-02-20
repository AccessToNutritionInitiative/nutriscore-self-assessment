import csv
import io

from fastapi import APIRouter, HTTPException, UploadFile

from nutri.application.nutriscore import NutriscoreService
from nutri.interface.schemas.nutriscore import (
    NutriscoreBulkResponse,
    ProductRequest,
    NutriscoreResponse,
)

router = APIRouter(prefix="/nutriscore", tags=["Nutriscore"])


@router.post("")
async def calculate_nutriscore(payload: ProductRequest) -> NutriscoreResponse:
    product = payload.to_product()
    score, grade = NutriscoreService().calculate_nutriscore(product=product)
    return NutriscoreResponse(score=score, grade=grade)


@router.post("/bulk")
def calculate_nutriscore_batch(file: UploadFile) -> NutriscoreBulkResponse:
    if file.content_type not in ("text/csv", "application/csv", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    products = [ProductRequest.model_validate(row).to_product() for i, row in enumerate(reader, start=1)]
    results = NutriscoreService.bulk_calculation(products=products)
    nutriscore_responses = [NutriscoreResponse(score=score, grade=grade) for score, grade in results]
    return NutriscoreBulkResponse(
        results=nutriscore_responses,
        total=len(nutriscore_responses),
    )
