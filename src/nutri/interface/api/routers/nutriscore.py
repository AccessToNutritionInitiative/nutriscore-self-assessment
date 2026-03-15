import csv
import codecs
import json
from collections.abc import Generator

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
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
def calculate_nutriscore_batch(file: UploadFile) -> StreamingResponse:
    """Stream data to avoid OOM. Stream response as NDJSON (json-line)"""
    if file.content_type not in ("text/csv", "application/csv", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    def generate() -> Generator[str, None, None]:
        reader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
        service = NutriscoreService()
        for i, row in enumerate(reader, start=1):
            try:
                product = ProductRequest.model_validate(row).to_product()
                score, grade = service.calculate_nutriscore(product=product)
                yield json.dumps({"score": score, "grade": str(grade)}) + "\n"
            except ValidationError as e:
                for error in e.errors():
                    yield json.dumps({"error": True, "row": i, "field": error["loc"][-1], "message": error["msg"]}) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
