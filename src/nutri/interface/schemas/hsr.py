from pydantic import BaseModel, Field

from nutri.domain.hsr import Product, ProductCategory


class ProductRequest(BaseModel):
    category: ProductCategory
    energy_kj: float = Field(ge=0, le=3700)
    sodium_mg: float = Field(default=0, ge=0, le=5000)
    satfat_g: float = Field(default=0, ge=0, le=100)
    sugar_g: float = Field(ge=0, le=100)
    protein_g: float = Field(default=0, ge=0, le=100)
    fibre_g: float = Field(default=0, ge=0, le=100)
    fvnl_percent: float = Field(default=0, ge=0, le=100)
    is_conc: bool = False
    is_water: bool = False
    is_unsweeten: bool = False

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
            is_concentrated=self.is_conc,
            is_water=self.is_water,
            is_unsweeten=self.is_unsweeten,
        )


class HsrResponse(BaseModel):
    final_score: int
    star_rating: float
