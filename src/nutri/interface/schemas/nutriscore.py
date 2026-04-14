from pydantic import BaseModel, Field, model_validator

from nutri.domain.nutriscore import NutriscoreGrade, Product, ProductCategory


class ProductRequest(BaseModel):
    product_name: str
    energy_kj: float = Field(ge=0, le=3700)
    sugar_g: float = Field(ge=0, le=100)
    sat_fat_g: float = Field(default=0, ge=0, le=100)
    salt_g: float = Field(default=0, ge=0, le=100)
    fruit_veg_pct: float = Field(default=0, ge=0, le=100)
    fibre_g: float = Field(default=0, ge=0, le=100)
    protein_g: float = Field(default=0, ge=0, le=100)
    has_sweeteners: bool = False
    is_water: bool = False
    is_cheese: bool = False
    is_red_meat: bool = False
    category: ProductCategory

    @model_validator(mode="after")
    def check_category_flags(self) -> "ProductRequest":
        if (self.is_cheese or self.is_red_meat) and self.category != ProductCategory.GENERAL:
            raise ValueError("is_cheese and is_red_meat are only valid for the general category")
        if (self.is_water or self.has_sweeteners) and self.category != ProductCategory.BEVERAGE:
            raise ValueError("is_water and has_sweeteners are only valid for the beverage category")
        if self.is_cheese and self.is_red_meat:
            raise ValueError("a product cannot be both cheese and red meat")
        return self

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
            is_cheese=self.is_cheese,
            is_red_meat=self.is_red_meat,
            category=self.category,
        )


class NutriscoreResponse(BaseModel):
    score: int
    grade: NutriscoreGrade | None
