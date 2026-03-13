from dataclasses import dataclass
from enum import StrEnum


class ProductCategory(StrEnum):
    BEVERAGE_1 = "1-beverage"
    DAIRY_BEVERAGE_1D = "1D-dairy-beverage"
    FOOD_2 = "2-food"
    DAIRY_FOOD_2D = "2D-dairy-food"
    FAT_OIL_3 = "3-fat"
    CHEESE_3D = "3D-cheese"


@dataclass
class Product:
    category: ProductCategory
    energy_kj: float
    sodium_mg: float
    satfat_g: float
    sugar_g: float
    protein_g: float | None = None
    fibre_g: float | None = None
    fvnl_percent: float | None = None
    is_concentrated: bool = False
    is_water: bool = False
    is_unsweeten: bool = False


class Thresholds:
    """
    Threshold rule: lower < x <= upper -> left index.
    Edge cases for KJ_BEV, CONC_FVNl, FVNL_BEV and PROTEIN
    """

    # Energy kj thresholds
    KJ_FOOD: list[float] = [335, 670, 1005, 1340, 1675, 2010, 2345, 2680, 3015, 3350, 3685]
    KJ_BEVERAGE: list[float] = [30 * i + 1 for i in range(1, 10)]

    # Sodium thresholds
    SODIUM_FOOD: list[float] = [90 * i for i in range(1, 31)]

    # Saturate fat thresholds
    SATFAT_FOOD_12: list[float] = [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0,
        11.2,
        12.5,
        13.9,
        15.5,
        17.3,
        19.3,
        21.6,
        24.1,
        26.9,
        30.0,
        33.5,
        37.4,
        41.7,
        46.6,
        52.0,
        58.0,
        64.7,
        72.3,
        80.6,
        90.0,
    ]
    SATFAT_FOOD_3: list[float] = [float(i) for i in range(1, 31)]

    # Total sugar thresholds
    SUGAR_FOOD_12: list[float] = [
        5.0,
        8.9,
        12.8,
        16.8,
        20.7,
        24.6,
        28.5,
        32.4,
        36.3,
        40.3,
        44.2,
        48.1,
        52.0,
        55.9,
        59.8,
        63.8,
        67.7,
        71.6,
        75.5,
        79.4,
        83.3,
        87.3,
        91.2,
        95.1,
        99.0,
    ]
    SUGAR_FOOD_3: list[float] = [
        5.0,
        9.0,
        13.5,
        18.0,
        22.5,
        27.0,
        31.0,
        36.0,
        40.0,
        45.0,
    ]
    SUGAR_BEV: list[float] = [
        0.1,
        1.6,
        3.1,
        4.6,
        6.1,
        7.6,
        9.1,
        10.6,
        12.1,
        13.6,
    ]

    # Protein thresholds
    # index 1 threshold rule: 1.6 < x < 3.2
    # index 2 threshold rule: 3.2 <= x <= 4.8
    PROTEIN: list[float] = [
        1.6,
        3.2,
        4.8,
        6.4,
        8.0,
        9.6,
        11.6,
        13.9,
        16.7,
        20.0,
        24.0,
        28.9,
        34.7,
        41.6,
        50.0,
    ]

    # Fibre thresholds
    FIBRE: list[float] = [
        0.9,
        1.9,
        2.8,
        3.7,
        4.7,
        5.4,
        6.3,
        7.3,
        8.4,
        9.7,
        11.2,
        13.0,
        15.0,
        17.3,
        20.0,
    ]

    # FVNL thresholds
    NONCONC_FVNL: list[float] = [40, 60, 67, 75, 80, 90, 95]
    CONC_FVNL: list[float] = [25, 43, 52, 63, 67, 80, 90]  # threshold rule: lower <= x < upper
    FVNL_BEV: list[float] = [25, 33, 41, 49, 57, 65, 73, 81, 89, 96]  # threshold rule: lower <= x < upper


class Feature:
    @staticmethod
    def create_template() -> bytes:
        headers = [
            "product_name",
            "category",
            "energy_kj",
            "sodium_mg",
            "satfat_g",
            "sugar_g",
            "protein_g",
            "fibre_g",
            "fvnl_percent",
            "is_concentrated",
            "is_water",
            "is_unsweeten",
        ]
        example_row = ["product1", "1-beverage", 250, 5.0, 1.2, 0.3, 10.0, 2.1, 50.0, False, False, False]

        csv_str = "\n".join([",".join(headers), ",".join(str(v) for v in example_row)])
        return csv_str.encode()

    @staticmethod
    def get_stars(rating: float, html: bool = True) -> str:
        full_stars = int(rating)
        half_star = 1 if (rating % 1) == 0.5 else 0
        empty_stars = 5 - full_stars - half_star

        if html:
            return (
                '<span style = "color: #1b75ba; font-size:2rem;">'
                + "★" * full_stars
                + ("⯪" if half_star else "")
                + '<span style="color: #1b75ba;">☆</span>' * empty_stars
                + "</span>"
            )

        else:
            return "★" * full_stars + ("⯪" if half_star else "") + "☆" * empty_stars + f" ({rating} / 5.0 stars)"
