from nutri.domain.hsr import ProductCategory, Product


class HsrRules:
    @classmethod
    def map_hsr(
        cls,
        product: Product,
        score: int,
    ) -> float:

        if product.category == ProductCategory.BEVERAGE_1:
            if product.is_water:
                return 5.0
            if product.is_unsweeten:
                return 4.5
            return cls._map_beverage1_hsr(score)
        if product.category == ProductCategory.DAIRY_BEVERAGE_1D:
            return cls._map_dairy_beverage1d_hsr(score)
        if product.category == ProductCategory.FOOD_2:
            return cls._map_food2_hsr(score)
        if product.category == ProductCategory.DAIRY_FOOD_2D:
            return cls._map_dairy_food2d_hsr(score)
        if product.category == ProductCategory.FAT_OIL_3:
            return cls._map_fat_oil3_hsr(score)
        if product.category == ProductCategory.CHEESE_3D:
            return cls._map_cheese3d_hsr(score)

        raise ValueError(f"Unknown product category: {product.category}")

    @staticmethod
    def _map_beverage1_hsr(
        score: int,
    ) -> float:
        if score <= 0:
            return 4.0
        elif score == 1:
            return 3.5
        elif score <= 3:
            return 3.0
        elif score <= 5:
            return 2.5
        elif score <= 7:
            return 2.0
        elif score <= 9:
            return 1.5
        elif score <= 11:
            return 1.0
        else:
            return 0.5

    @staticmethod
    def _map_dairy_beverage1d_hsr(
        score: int,
    ) -> float:
        if score <= -2:
            return 5.0
        elif score == -1:
            return 4.5
        elif score == 0:
            return 4.0
        elif score == 1:
            return 3.5
        elif score == 2:
            return 3.0
        elif score == 3:
            return 2.5
        elif score == 4:
            return 2.0
        elif score == 5:
            return 1.5
        elif score == 6:
            return 1.0
        else:
            return 0.5

    @staticmethod
    def _map_food2_hsr(
        score: int,
    ) -> float:
        if score <= -11:
            return 5.0
        elif score <= -7:
            return 4.5
        elif score <= -2:
            return 4.0
        elif score <= 2:
            return 3.5
        elif score <= 6:
            return 3.0
        elif score <= 11:
            return 2.5
        elif score <= 15:
            return 2.0
        elif score <= 20:
            return 1.5
        elif score <= 24:
            return 1.0
        else:
            return 0.5

    @staticmethod
    def _map_dairy_food2d_hsr(
        score: int,
    ) -> float:
        if score <= -2:
            return 5.0
        elif score <= 0:
            return 4.5
        elif score <= 2:
            return 4.0
        elif score == 3:
            return 3.5
        elif score <= 5:
            return 3.0
        elif score <= 7:
            return 2.5
        elif score == 8:
            return 2.0
        elif score <= 10:
            return 1.5
        elif score <= 12:
            return 1.0
        else:
            return 0.5

    @staticmethod
    def _map_fat_oil3_hsr(
        score: int,
    ) -> float:
        if score <= 13:
            return 5.0
        elif score <= 16:
            return 4.5
        elif score <= 20:
            return 4.0
        elif score <= 23:
            return 3.5
        elif score <= 27:
            return 3.0
        elif score <= 30:
            return 2.5
        elif score <= 34:
            return 2.0
        elif score <= 37:
            return 1.5
        elif score <= 41:
            return 1.0
        else:
            return 0.5

    @staticmethod
    def _map_cheese3d_hsr(
        score: int,
    ) -> float:
        if score <= 24:
            return 5.0
        elif score <= 26:
            return 4.5
        elif score <= 28:
            return 4.0
        elif score <= 30:
            return 3.5
        elif score == 31:
            return 3.0
        elif score <= 33:
            return 2.5
        elif score <= 35:
            return 2.0
        elif score <= 37:
            return 1.5
        elif score <= 39:
            return 1.0
        else:
            return 0.5
