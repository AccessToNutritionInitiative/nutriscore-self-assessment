from nutri.application.hsr_scoring import HsrScoring
from nutri.application.hsr_mapping import HsrRules
from nutri.domain.hsr import Product


class HsrCalculator:
    @classmethod
    def bulk_result(cls, products: list[Product]) -> list[tuple[int, float]]:
        return [cls.get_result(product) for product in products]

    @staticmethod
    def get_result(product: Product) -> tuple[int, float]:
        score = HsrScoring.compute_hsrscore(product=product)
        hsr_stars = HsrRules.map_hsr(product=product, score=score)

        return score, hsr_stars
