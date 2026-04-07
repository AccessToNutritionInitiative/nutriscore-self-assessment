from .nutriscore import router as nutri_router
from .hsr import router as hsr_router
from .survey import router as survey_router

__all__ = ["nutri_router", "hsr_router", "survey_router"]
