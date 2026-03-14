import csv
import io

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import ValidationError

from nutri.application.nutriscore import NutriscoreService
from nutri.interface.schemas.nutriscore import (
    NutriscoreBulkResponse,
    NutriscoreResponse,
    ProductRequest,
)


router = APIRouter(prefix="/nutriscore", tags=["Nutriscore"])


@router.post("")
async def calculate_nutriscore(payload: ProductRequest) -> NutriscoreResponse:
    product = payload.to_product()
    score, grade = NutriscoreService().calculate_nutriscore(product=product)
    return NutriscoreResponse(score=score, grade=grade)


@router.post("s")
def calculate_nutriscore_batch(file: UploadFile) -> NutriscoreBulkResponse:
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
        raise HTTPException(
            status_code=422,
            detail={"message": "Some rows contain invalid data.", "errors": errors},
        )

    results = NutriscoreService.calculate_nutriscores(products=products)
    nutriscore_responses = [NutriscoreResponse(score=score, grade=grade) for score, grade in results]
    return NutriscoreBulkResponse(
        results=nutriscore_responses,
        total=len(nutriscore_responses),
    )
