from nutri.domain.nutriscore import NutriscoreGrade, Product, ProductCategory


class NutriscoreService:
    @classmethod
    def calculate_nutriscore(cls, product: Product) -> tuple[int, NutriscoreGrade]:
        """Calculate Nutri-Score for a product. Returns (score, grade)."""

        if product.category == ProductCategory.BEVERAGE:
            return cls._calculate_beverage(product)

        if product.category == ProductCategory.FATS:
            return cls._calculate_fats(product)

        if product.category == ProductCategory.GENERAL:
            return cls._calculate_general(product)

        raise NotImplementedError(f"Nutri-Score calculation not implemented for category '{product.category}'")

    @classmethod
    def _calculate_beverage(cls, product: Product) -> tuple[int, NutriscoreGrade]:
        if product.is_water:
            return 0, NutriscoreGrade.A

        # --- N-points (unfavorable) ---
        n_energy = cls._score_from_thresholds(product.energy_kj, [30, 90, 150, 210, 240, 270, 300, 330, 360, 390])
        n_sugar = cls._score_from_thresholds(product.sugar_g, [0.5, 2, 3.5, 5, 6, 7, 8, 9, 10, 11])
        n_sat_fat = cls._score_from_thresholds(product.sat_fat_g, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        n_salt = cls._score_from_thresholds(
            product.salt_g,
            [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0],
        )
        n_sweetener = 4 if product.has_sweeteners else 0

        n_total = n_energy + n_sugar + n_sat_fat + n_salt + n_sweetener

        # --- P-points (favorable) ---
        p_fruit = cls._score_from_thresholds(product.fruit_veg_pct, [40, 60, 80], points=[0, 2, 4, 6])
        p_fibre = cls._score_from_thresholds(product.fibre_g, [3.0, 4.1, 5.2, 6.3, 7.4])
        p_protein = cls._score_from_thresholds(product.protein_g, [1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0])

        p_total = p_fruit + p_fibre + p_protein

        # --- Final score & grade ---
        score = n_total - p_total
        grade = cls._beverage_grade(score)

        return score, grade

    @classmethod
    def _calculate_general(cls, product: Product) -> tuple[int, NutriscoreGrade]:
        # --- N-points (unfavorable) ---
        n_energy = cls._score_from_thresholds(product.energy_kj, [335, 670, 1005, 1340, 1675, 2010, 2345, 2680, 3015, 3350])
        n_sugar = cls._score_from_thresholds(product.sugar_g, [3.4, 6.8, 10, 14, 17, 20, 24, 27, 31, 34, 37, 41, 44, 48, 51])
        n_sat_fat = cls._score_from_thresholds(product.sat_fat_g, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        n_salt = cls._score_from_thresholds(
            product.salt_g,
            [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0],
        )
        n_total = n_energy + n_sugar + n_sat_fat + n_salt

        # --- P-points (favorable) ---
        p_fruit = cls._score_from_thresholds(product.fruit_veg_pct, [40, 60, 80], points=[0, 1, 2, 5])
        p_fibre = cls._score_from_thresholds(product.fibre_g, [3.0, 4.1, 5.2, 6.3, 7.4])
        p_protein = cls._score_from_thresholds(product.protein_g, [2.4, 4.8, 7.2, 9.6, 12.0, 14.0, 17.0])

        # Protein is excluded when n_total >= 11
        if n_total >= 11:
            score = n_total - p_fruit - p_fibre
        else:
            score = n_total - p_fruit - p_fibre - p_protein

        return score, cls._general_grade(score)

    @classmethod
    def _calculate_fats(cls, product: Product) -> tuple[int, NutriscoreGrade]:
        # --- N-points (unfavorable) ---
        # Energy for fats is derived from saturated fat content (sat_fat * 37 kJ/g)
        energy_from_sat_fat = product.sat_fat_g * 37
        n_energy = cls._score_from_thresholds(energy_from_sat_fat, [120, 240, 360, 480, 600, 720, 840, 960, 1080, 1200])
        n_sugar = cls._score_from_thresholds(product.sugar_g, [3.4, 6.8, 10, 14, 17, 20, 24, 27, 31, 34, 37, 41, 44, 48, 51])
        n_sat_fat = cls._score_from_thresholds(product.sat_fat_g, [10, 16, 22, 28, 34, 40, 46, 52, 58, 64])
        n_salt = cls._score_from_thresholds(
            product.salt_g,
            [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0],
        )
        n_total = n_energy + n_sugar + n_sat_fat + n_salt

        # --- P-points (favorable) ---
        p_fruit = cls._score_from_thresholds(product.fruit_veg_pct, [40, 60, 80], points=[0, 1, 2, 5])
        p_fibre = cls._score_from_thresholds(product.fibre_g, [3.0, 4.1, 5.2, 6.3, 7.4])
        p_protein = cls._score_from_thresholds(product.protein_g, [2.4, 4.8, 7.2, 9.6, 12.0, 14.0, 17.0])

        # Protein is excluded when n_total >= 7
        if n_total >= 7:
            score = n_total - p_fruit - p_fibre
        else:
            score = n_total - p_fruit - p_fibre - p_protein

        return score, cls._fats_grade(score)

    @staticmethod
    def _score_from_thresholds(
        value: float,
        thresholds: list[float],
        points: list[int] | None = None,
    ) -> int:
        """
        Return points based on where value falls among thresholds.

        Default points are 0, 1, 2, ... len(thresholds).
        value <= thresholds[0] → points[0]
        value >  thresholds[-1] → points[-1]
        """
        if points is None:
            points = list(range(len(thresholds) + 1))

        for i, threshold in enumerate(thresholds):
            if value <= threshold:
                return points[i]
        return points[-1]

    @staticmethod
    def _beverage_grade(score: int) -> NutriscoreGrade:
        if score <= 2:
            return NutriscoreGrade.B
        elif score <= 6:
            return NutriscoreGrade.C
        elif score <= 9:
            return NutriscoreGrade.D
        else:
            return NutriscoreGrade.E

    @staticmethod
    def _general_grade(score: int) -> NutriscoreGrade:
        if score <= 0:
            return NutriscoreGrade.A
        elif score <= 2:
            return NutriscoreGrade.B
        elif score <= 10:
            return NutriscoreGrade.C
        elif score <= 18:
            return NutriscoreGrade.D
        else:
            return NutriscoreGrade.E

    @staticmethod
    def _fats_grade(score: int) -> NutriscoreGrade:
        if score <= -6:
            return NutriscoreGrade.A
        elif score <= 2:
            return NutriscoreGrade.B
        elif score <= 10:
            return NutriscoreGrade.C
        elif score <= 18:
            return NutriscoreGrade.D
        else:
            return NutriscoreGrade.E
