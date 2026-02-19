from pydantic import BaseModel, Field

from nutri.domain.nutriscore import NutriscoreGrade, Product, ProductCategory


class NutriscoreRequest(BaseModel):
    energy_kj: float
    sugar_g: float
    sat_fat_g: float = 0
    salt_g: float = 0
    fruit_veg_pct: float = Field(default=0, ge=0, le=100)
    fibre_g: float = 0
    protein_g: float = 0
    has_sweeteners: bool = False
    is_water: bool = False
    category: ProductCategory = ProductCategory.GENERAL

    def to_product(self) -> Product:
        return Product(
            energy_kj=self.energy_kj,
            sugar_g=self.sugar_g,
            sat_fat_g=self.sat_fat_g,
            salt_g=self.salt_g,
            fruit_veg_pct=self.fruit_veg_pct,
            fibre_g=self.fibre_g,
            protein_g=self.protein_g,
            has_sweeteners=self.has_sweeteners,
            is_water=self.is_water,
            category=self.category,
        )


class NutriscoreResponse(BaseModel):
    score: int
    grade: NutriscoreGrade
