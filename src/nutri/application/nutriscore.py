from nutri.domain.nutriscore import Product


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


def _beverage_grade(score: int) -> str:
    if score <= 2:
        return "B"
    elif score <= 6:
        return "C"
    elif score <= 9:
        return "D"
    else:
        return "E"


class NutriscoreService:
    @staticmethod
    def calculate_nutriscore_beverage(product: Product) -> tuple[int, str]:
        """Calculate Nutri-Score for a beverage. Returns (score, grade)."""

        if is_water:
            return 0, "A"

        # --- N-points (unfavorable) ---
        n_energy = _score_from_thresholds(energy_kj, [30, 90, 150, 210, 240, 270, 300, 330, 360, 390])
        n_sugar = _score_from_thresholds(sugar_g, [0.5, 2, 3.5, 5, 6, 7, 8, 9, 10, 11])
        n_sat_fat = _score_from_thresholds(sat_fat_g, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        n_salt = _score_from_thresholds(
            salt_g,
            [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0],
        )
        n_sweetener = 4 if has_sweeteners else 0

        n_total = n_energy + n_sugar + n_sat_fat + n_salt + n_sweetener

        # --- P-points (favorable) ---
        p_fruit = _score_from_thresholds(fruit_veg_pct, [40, 60, 80], points=[0, 2, 4, 6])
        p_fibre = _score_from_thresholds(fibre_g, [3.0, 4.1, 5.2, 6.3, 7.4])
        p_protein = _score_from_thresholds(protein_g, [1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0])

        p_total = p_fruit + p_fibre + p_protein

        # --- Final score & grade ---
        score = n_total - p_total
        grade = _beverage_grade(score)

        return score, grade
