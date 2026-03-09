from pydantic import BaseModel, Field

from nutri.domain.nutriscore import NutriscoreGrade, Product, ProductCategory


class ProductRequest(BaseModel):
    energy_kj: float = Field(ge=0, le=3700)
    sugar_g: float = Field(ge=0, le=100)
    sat_fat_g: float = Field(default=0, ge=0, le=100)
    salt_g: float = Field(default=0, ge=0, le=100)
    fruit_veg_pct: float = Field(default=0, ge=0, le=100)
    fibre_g: float = Field(default=0, ge=0, le=100)
    protein_g: float = Field(default=0, ge=0, le=100)
    has_sweeteners: bool = False
    is_water: bool = False
    category: ProductCategory

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


class NutriscoreBulkResponse(BaseModel):
    results: list[NutriscoreResponse]
    total: int


class HsrResponse(BaseModel):
    final_score: int
    star_rating: float
