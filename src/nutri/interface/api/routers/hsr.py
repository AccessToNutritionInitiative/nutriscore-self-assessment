import csv
import codecs
from typing import Iterable

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import ValidationError

from nutri.application.hsr import HsrCalculator
from nutri.interface.schemas.hsr import ProductRequest, HsrResponse

router = APIRouter(prefix="/hsr", tags=["HSR"])
DEFAULT_ZERO = { "satfat_g", "sodium_mg", "protein_g", "fibre_g"}


@router.post("")
async def calculate_hsr(payload: ProductRequest) -> HsrResponse:
    product = payload.to_product()
    score, hsr_stars = HsrCalculator.get_result(product=product)
    return HsrResponse(final_score=score, star_rating=hsr_stars)


@router.post("s")
def calculate_hsr_bulk(file: UploadFile) -> Iterable[HsrResponse]:
    """Stream data to avoid OOM. Stream response as NDJSON (json-line)"""
    if file.content_type not in ("text/csv", "application/csv", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    reader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
    for row in reader:
        try:
            if row.get("category") == "1-beverage":
                row = {k: (0.0 if k in DEFAULT_ZERO and v in (None, "", "NaN", "nan") else v) for k, v in row.items()}

            product = ProductRequest.model_validate(row).to_product()
            score, hsr_stars = HsrCalculator.get_result(product=product)
            yield HsrResponse(final_score=score, star_rating=hsr_stars)
        except ValidationError:
            yield HsrResponse(final_score=-100, star_rating=None)
