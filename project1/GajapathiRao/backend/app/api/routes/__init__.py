"""Application route modules grouped by responsibility."""

from .etl import router as etl_router
from .locations import router as locations_router
from .news import router as news_router
from .weather import router as weather_router

__all__ = [
    "etl_router",
    "locations_router",
    "news_router",
    "weather_router",
]
