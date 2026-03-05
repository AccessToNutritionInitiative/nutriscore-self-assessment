from nutri.application.hsr_scoring import HsrScoring
from nutri.application.hsr_mapping import HsrRules
from nutri.domain.hsr import Product


class HsrCalculator:
    def __init__(self):
        self._scoring = HsrScoring()

    def get_results(self, product: Product) -> tuple[int, float]:
        score = self._scoring.compute_hsrscore(product=product)
        hsr_stars = HsrRules.map_hsr(product_category=product.category, score=score)

        return score, hsr_stars
