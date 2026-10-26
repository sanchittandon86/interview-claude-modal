"""
E-commerce search & recommendations platform — foundational package.

Covers US-1 through US-9:
- SellerInventoryService: add/update products (US-1, US-2)
- SearchService: query, filter, ranking, facets (US-3 - US-6)
- RecommendationService: display of black-box ML recommendations (US-7)
- EventCaptureService: capture buyer interaction events (US-8)
- EventStore: persist and provide events to the ML system (US-9)
"""

from .catalog import ProductCatalog
from .errors import ProductNotFoundError, ValidationError
from .event_store import EventStore
from .events import EventCaptureService
from .inventory import SellerInventoryService
from .models import Event, Product
from .recommendations import RecommendationMLClient, RecommendationService
from .search import SearchService

__all__ = [
    "ProductCatalog",
    "ValidationError",
    "ProductNotFoundError",
    "EventStore",
    "EventCaptureService",
    "SellerInventoryService",
    "Event",
    "Product",
    "RecommendationMLClient",
    "RecommendationService",
    "SearchService",
]
