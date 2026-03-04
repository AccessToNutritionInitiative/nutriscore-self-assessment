import csv
import io

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import ValidationError

from nutri.application.hsr import HsrCalculator
from nutri.interface.schemas.hsr import (
    ProductRequest,
    HsrResponse,
)

router = APIRouter(prefix="", tags=[""])

@router.post("")
async def calculate_hsr(payload: ProductRequest) -> HsrResponse:
    product = payload.to_product()
    score, hsr_stars = HsrCalculator().get_results(product=product)
    return HsrResponse(final_score=score, star_rating=hsr_stars)
