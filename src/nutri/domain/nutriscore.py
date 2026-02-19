from dataclasses import dataclass


@dataclass
class Product:
    energy_kj: float
    sugar_g: float
    sat_fat_g: float
    salt_g: float
    fruit_veg_pct: float
    fibre_g: float
    protein_g: float
    has_sweeteners: bool
    is_water: bool
