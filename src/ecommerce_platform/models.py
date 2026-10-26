"""Core data models shared across the e-commerce platform modules."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def utc_now() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Product:
    """A single product listed by a seller (US-1, US-2)."""

    product_id: str
    seller_id: str
    name: str
    category: str
    price: float
    stock_quantity: int
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)


@dataclass
class Event:
    """A single captured buyer interaction event (US-8)."""

    event_id: str
    event_type: str  # search | click | product_view | scroll | time_spent | add_to_cart
    user_id: Optional[str]
    session_id: str
    product_id: Optional[str] = None
    query_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=utc_now)
