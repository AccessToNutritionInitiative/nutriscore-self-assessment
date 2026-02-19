from fastapi import APIRouter

from nutri.application.nutriscore import NutriscoreService
from nutri.interface.schemas.nutriscore import NutriscoreRequest, NutriscoreResponse


router = APIRouter(prefix="/nutriscore", tags=["Nutriscore"])


@router.post("")
async def calculate_nutriscore(payload: NutriscoreRequest) -> NutriscoreResponse:
    product = payload.to_product()
    score, grade = NutriscoreService.calculate_nutriscore_beverage(product=product)
    return NutriscoreResponse(score=score, grade=grade)
