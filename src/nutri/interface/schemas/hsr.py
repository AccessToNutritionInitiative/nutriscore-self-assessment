from pydantic import BaseModel, Field, field_validator, model_validator

from nutri.domain.hsr import Product, ProductCategory

_EMPTY = {None, "", "NaN", "nan"}


# https://docs.pydantic.dev/latest/concepts/validators/
class ProductRequest(BaseModel):
    category: ProductCategory
    energy_kj: float = Field(ge=0, le=3700)
    sodium_mg: float = Field(default=0, ge=0, le=5000)
    satfat_g: float = Field(default=0, ge=0, le=100)
    sugar_g: float = Field(ge=0, le=100)
    protein_g: float = Field(default=0, ge=0, le=100)
    fibre_g: float = Field(default=0, ge=0, le=100)
    fvnl_percent: float = Field(default=0, ge=0, le=100)
    is_concentrated: bool = False
    is_water: bool = False
    is_unsweeten: bool = False

    @model_validator(mode="before")
    @classmethod
    def empty_numeric_specific_cat(cls, values):
        def _zero_if_empty(fields: tuple) -> None:
            for field in fields:
                if values.get(field) in _EMPTY:
                    values[field] = 0

        if values.get("category") == ProductCategory.BEVERAGE_1:
            _zero_if_empty(("sodium_mg", "satfat_g"))

        if values.get("is_water") or values.get("is_unsweeten"):
            _zero_if_empty(("energy_kj", "sugar_g"))

        return values

    @field_validator("protein_g", "fibre_g", "fvnl_percent", mode="before")
    @classmethod
    def empty_numeric_to_default(cls, v):
        return 0 if v in _EMPTY else v

    @field_validator("is_concentrated", "is_water", "is_unsweeten", mode="before")
    @classmethod
    def empty_bool_to_false(cls, v):
        return False if v in _EMPTY else v

    def to_product(self) -> Product:
        return Product(
            category=self.category,
            energy_kj=self.energy_kj,
            sodium_mg=self.sodium_mg,
            satfat_g=self.satfat_g,
            sugar_g=self.sugar_g,
            protein_g=self.protein_g,
            fibre_g=self.fibre_g,
            fvnl_percent=self.fvnl_percent,
            is_concentrated=self.is_concentrated,
            is_water=self.is_water,
            is_unsweeten=self.is_unsweeten,
        )


class HsrResponse(BaseModel):
    final_score: int
    star_rating: float | None
