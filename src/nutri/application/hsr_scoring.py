from nutri.domain.hsr import Product, ProductCategory, Thresholds
import bisect


class HsrScoring:
    """Apply scoring to a single scalar value"""

    def compute_hsrscore(self, product: Product) -> int:
        base_energy = self._score_energy(product=product)
        base_satfat = self._score_satfat(product=product)
        base_sodium = self._score_sodium(product=product)
        base_sugar = self._score_sugar(product=product)
        mod_fibre = self._score_fibre(product=product)
        mod_fvnl = self._score_fvnl(product=product)
        mod_protein = self._score_protein(product=product)

        baseline_pts = base_energy + base_satfat + base_sodium + base_sugar
        modifying_pts = mod_fibre + mod_fvnl

        hsr_score = baseline_pts - modifying_pts

        if baseline_pts < 13:
            hsr_score -= mod_protein
        elif baseline_pts >= 13 and mod_fvnl >= 5:
            hsr_score -= mod_protein

        return hsr_score

    def _score_energy(self, product: Product) -> int:
        match product.category:
            case ProductCategory.BEVERAGE_1:
                # starts from score = 1 for the lowest score
                return self._apply_threshold(product.energy_kj, Thresholds.KJ_BEVERAGE) + 1
            case _:
                return self._apply_threshold(product.energy_kj, Thresholds.KJ_FOOD)

    def _score_sodium(self, product: Product) -> int:
        match product.category:
            case ProductCategory.BEVERAGE_1:
                return 0
            case _:
                return self._apply_threshold(product.sodium_mg, Thresholds.SODIUM_FOOD)

    def _score_satfat(self, product: Product) -> int:
        match product.category:
            case ProductCategory.BEVERAGE_1:
                return 0
            case ProductCategory.DAIRY_BEVERAGE_1D | ProductCategory.FOOD_2 | ProductCategory.DAIRY_FOOD_2D:
                return self._apply_threshold(product.satfat_g, Thresholds.SATFAT_FOOD_12)
            case _:
                return self._apply_threshold(product.satfat_g, Thresholds.SATFAT_FOOD_3)

    def _score_sugar(self, product: Product) -> int:
        match product.category:
            case ProductCategory.BEVERAGE_1:
                return self._apply_threshold(product.sugar_g, Thresholds.SUGAR_BEV)
            case ProductCategory.DAIRY_BEVERAGE_1D | ProductCategory.FOOD_2 | ProductCategory.DAIRY_FOOD_2D:
                return self._apply_threshold(product.sugar_g, Thresholds.SUGAR_FOOD_12)
            case _:
                return self._apply_threshold(product.sugar_g, Thresholds.SUGAR_FOOD_3)

    def _score_protein(self, product: Product) -> int:
        match product.category:
            case ProductCategory.BEVERAGE_1:
                return 0
            case _:
                return self._protein_threshold(product.protein_g, Thresholds.PROTEIN)

    def _score_fibre(self, product: Product) -> int:
        match product.category:
            case ProductCategory.BEVERAGE_1 | ProductCategory.DAIRY_BEVERAGE_1D:
                return 0
            case _:
                return self._apply_threshold(product.fibre_g or 0, Thresholds.FIBRE)

    def _score_fvnl(self, product: Product) -> int:
        match product.category:
            case ProductCategory.BEVERAGE_1:
                return self._apply_threshold(product.fvnl_percent or 0, Thresholds.FVNL_BEV, right=False)
            case _ if product.fvnl_percent == 100:
                return 8
            case _ if product.is_concentrated:
                return self._apply_threshold(product.fvnl_percent or 0, Thresholds.CONC_FVNL, right=False)
            case _:
                return self._apply_threshold(product.fvnl_percent or 0, Thresholds.NONCONC_FVNL)

    def _apply_threshold(self, value: float, threshold: Thresholds, right: bool = True) -> int:
        """
        Upper-bound based threshold scorer.
        Example:
            When right = True
            (list[0], list[1]] -> 1

            When right = False
            [list[0], list[1]) -> 0
        """
        if right:
            return bisect.bisect_left(threshold, value)  # for lower < x <= upper

        return bisect.bisect_right(threshold, value)  # for lower <= x < upper

    def _protein_threshold(
        self,
        value: float,
        threshold: Thresholds,
    ) -> int:
        for i, upper in enumerate(threshold):
            if i == 1:
                if value < upper:
                    return i
            else:
                if value <= upper:
                    return i
        return len(threshold)
