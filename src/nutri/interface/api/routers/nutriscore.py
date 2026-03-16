import csv
import codecs
from typing import Iterable

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import ValidationError

from nutri.application.nutriscore import NutriscoreService
from nutri.interface.schemas.nutriscore import (
    ProductRequest,
    NutriscoreResponse,
)

router = APIRouter(prefix="/nutriscore", tags=["Nutriscore"])


@router.post("")
async def calculate_nutriscore(payload: ProductRequest) -> NutriscoreResponse:
    product = payload.to_product()
    score, grade = NutriscoreService().calculate_nutriscore(product=product)
    return NutriscoreResponse(score=score, grade=grade)


@router.post("s")
def calculate_nutriscore_batch(file: UploadFile) -> Iterable[NutriscoreResponse]:
    """Stream data to avoid OOM. Stream response as NDJSON (json-line)"""
    if file.content_type not in ("text/csv", "application/csv", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    reader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
    for row in reader:
        try:
            product = ProductRequest.model_validate(row).to_product()
            score, grade = NutriscoreService.calculate_nutriscore(product=product)
            yield NutriscoreResponse(score=score, grade=grade)
        except ValidationError:
            yield NutriscoreResponse(score=-100, grade=None)
