from hsr.domain.hsr import ProductCategory


class HsrRules:
    @classmethod
    def map_hsr(
        cls,
        product_category: ProductCategory,
        score: int,
    ) -> float:
        match product_category:
            case ProductCategory.BEVERAGE_1:
                return cls._map_beverage1_hsr(score)
            case ProductCategory.DAIRY_BEVERAGE_1D:
                return cls._map_dairy_beverage1d_hsr(score)
            case ProductCategory.FOOD_2:
                return cls._map_food2_hsr(score)
            case ProductCategory.DAIRY_FOOD_2D:
                return cls._map_dairy_food2d_hsr(score)
            case ProductCategory.FAT_OIL_3:
                return cls._map_fat_oil3_hsr(score)
            case ProductCategory.CHEESE_3D:
                return cls._map_cheese3d_hsr(score)
            case _:
                raise ValueError(f"Unknown product category: {product_category}")

    @staticmethod
    def _map_beverage1_hsr(
        score: int,
    ) -> float:
        match score:
            case s if s <= 0:
                return 4.0
            case 1:
                return 3.5
            case s if s <= 3:
                return 3.0
            case s if s <= 5:
                return 2.5
            case s if s <= 7:
                return 2.0
            case s if s <= 9:
                return 1.5
            case s if s <= 11:
                return 1.0
            case _:
                return 0.5

    @staticmethod
    def _map_dairy_beverage1d_hsr(
        score: int,
    ) -> float:
        match score:
            case s if s <= -2:
                return 5.0
            case -1:
                return 4.5
            case 0:
                return 4.0
            case 1:
                return 3.5
            case 2:
                return 3.0
            case 3:
                return 2.5
            case 4:
                return 2.0
            case 5:
                return 1.5
            case 6:
                return 1.0
            case _:
                return 0.5

    @staticmethod
    def _map_food2_hsr(
        score: int,
    ) -> float:
        match score:
            case s if s <= -11:
                return 5.0
            case s if s <= -7:
                return 4.5
            case s if s <= -2:
                return 4.0
            case s if s <= 2:
                return 3.5
            case s if s <= 6:
                return 3.0
            case s if s <= 11:
                return 2.5
            case s if s <= 15:
                return 2.0
            case s if s <= 20:
                return 1.5
            case s if s <= 24:
                return 1.0
            case _:
                return 0.5

    @staticmethod
    def _map_dairy_food2d_hsr(
        score: int,
    ) -> float:
        match score:
            case s if s <= -2:
                return 5.0
            case s if s <= 0:
                return 4.5
            case s if s <= 2:
                return 4.0
            case 3:
                return 3.5
            case s if s <= 5:
                return 3.0
            case s if s <= 7:
                return 2.5
            case 8:
                return 2.0
            case s if s <= 10:
                return 1.5
            case s if s <= 12:
                return 1.0
            case _:
                return 0.5

    @staticmethod
    def _map_fat_oil3_hsr(
        score: int,
    ) -> float:
        match score:
            case s if s <= 13:
                return 5.0
            case s if s <= 16:
                return 4.5
            case s if s <= 20:
                return 4.0
            case s if s <= 23:
                return 3.5
            case s if s <= 27:
                return 3.0
            case s if s <= 30:
                return 2.5
            case s if s <= 34:
                return 2.0
            case s if s <= 37:
                return 1.5
            case s if s <= 41:
                return 1.0
            case _:
                return 0.5

    @staticmethod
    def _map_cheese3d_hsr(
        score: int,
    ) -> float:
        match score:
            case s if s <= 24:
                return 5.0
            case s if s <= 26:
                return 4.5
            case s if s <= 28:
                return 4.0
            case s if s <= 30:
                return 3.5
            case 31:
                return 3.0
            case s if s <= 33:
                return 2.5
            case s if s <= 35:
                return 2.0
            case s if s <= 37:
                return 1.5
            case s if s <= 39:
                return 1.0
            case _:
                return 0.5
