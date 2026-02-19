from nutri.domain.nutriscore import NutriscoreGrade, Product, ProductCategory


class NutriscoreService:
    def calculate_nutriscore(self, product: Product) -> tuple[int, NutriscoreGrade]:
        """Calculate Nutri-Score for a product. Returns (score, grade)."""

        if product.category == ProductCategory.BEVERAGE:
            return self._calculate_beverage(product)

        raise NotImplementedError(f"Nutri-Score calculation not implemented for category '{product.category}'")

    def _calculate_beverage(self, product: Product) -> tuple[int, NutriscoreGrade]:
        if product.is_water:
            return 0, NutriscoreGrade.A

        # --- N-points (unfavorable) ---
        n_energy = self._score_from_thresholds(product.energy_kj, [30, 90, 150, 210, 240, 270, 300, 330, 360, 390])
        n_sugar = self._score_from_thresholds(product.sugar_g, [0.5, 2, 3.5, 5, 6, 7, 8, 9, 10, 11])
        n_sat_fat = self._score_from_thresholds(product.sat_fat_g, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        n_salt = self._score_from_thresholds(
            product.salt_g,
            [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0],
        )
        n_sweetener = 4 if product.has_sweeteners else 0

        n_total = n_energy + n_sugar + n_sat_fat + n_salt + n_sweetener

        # --- P-points (favorable) ---
        p_fruit = self._score_from_thresholds(product.fruit_veg_pct, [40, 60, 80], points=[0, 2, 4, 6])
        p_fibre = self._score_from_thresholds(product.fibre_g, [3.0, 4.1, 5.2, 6.3, 7.4])
        p_protein = self._score_from_thresholds(product.protein_g, [1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0])

        p_total = p_fruit + p_fibre + p_protein

        # --- Final score & grade ---
        score = n_total - p_total
        grade = self._beverage_grade(score)

        return score, grade

    def _score_from_thresholds(
        self,
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

    def _beverage_grade(self, score: int) -> NutriscoreGrade:
        if score <= 2:
            return NutriscoreGrade.B
        elif score <= 6:
            return NutriscoreGrade.C
        elif score <= 9:
            return NutriscoreGrade.D
        else:
            return NutriscoreGrade.E
