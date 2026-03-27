from app.api.routes.deals import router as deals_router
from app.api.routes.lots import router as lots_router
from app.api.routes.matches import router as matches_router

__all__ = [
    "lots_router",
    "matches_router",
    "deals_router",
]