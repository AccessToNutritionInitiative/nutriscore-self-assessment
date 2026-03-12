from nutri.application.hsr_scoring import HsrScoring
from nutri.application.hsr_mapping import HsrRules
from nutri.domain.hsr import Product


class HsrCalculator:
    def get_results(self, product: Product) -> tuple[int, float]:
        score = HsrScoring.compute_hsrscore(product=product)
        hsr_stars = HsrRules.map_hsr(product=product, score=score)

        return score, hsr_stars
