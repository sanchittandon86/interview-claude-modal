"""
Buyer interaction event capture.

Implements US-8: Capture User Interaction Events (search, click,
product_view, scroll, time_spent, add_to_cart).
"""

import uuid
from typing import Any, Dict, Optional

from .event_store import EventStore
from .models import Event


class EventCaptureService:
    """
    Builds a structured Event for each supported interaction type and hands
    it to the EventStore for persistence (US-9). Each capture_* call builds
    and persists its event independently, so rapid sequential actions
    (TC-8.7) are each logged individually with no dropping or merging.
    """

    def __init__(self, event_store: EventStore):
        self._store = event_store

    def _capture(
        self,
        event_type: str,
        user_id: Optional[str],
        session_id: str,
        product_id: Optional[str] = None,
        query_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """Shared construction + persistence path for all six event types."""
        event = Event(
            event_id=f"EVT-{uuid.uuid4().hex[:10]}",
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            product_id=product_id,
            query_id=query_id,
            metadata=metadata or {},
        )
        self._store.persist(event)
        return event

    def capture_search(self, user_id: Optional[str], session_id: str, query_id: str,
                        metadata: Optional[Dict[str, Any]] = None) -> Event:
        """TC-8.1: Log a search event."""
        return self._capture("search", user_id, session_id, query_id=query_id, metadata=metadata)

    def capture_click(self, user_id: Optional[str], session_id: str, product_id: str,
                       metadata: Optional[Dict[str, Any]] = None) -> Event:
        """TC-8.2: Log a click event (e.g., on a search result)."""
        return self._capture("click", user_id, session_id, product_id=product_id, metadata=metadata)

    def capture_product_view(self, user_id: Optional[str], session_id: str, product_id: str,
                              metadata: Optional[Dict[str, Any]] = None) -> Event:
        """TC-8.3: Log a product detail page view."""
        return self._capture("product_view", user_id, session_id, product_id=product_id, metadata=metadata)

    def capture_scroll(self, user_id: Optional[str], session_id: str, product_id: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> Event:
        """TC-8.4: Log a scroll event, e.g. metadata={"scroll_depth_percent": 65}."""
        return self._capture("scroll", user_id, session_id, product_id=product_id, metadata=metadata)

    def capture_time_spent(self, user_id: Optional[str], session_id: str, product_id: str,
                            duration_seconds: float) -> Event:
        """TC-8.5: Log time spent on a page/product."""
        return self._capture(
            "time_spent", user_id, session_id, product_id=product_id,
            metadata={"duration_seconds": duration_seconds},
        )

    def capture_add_to_cart(self, user_id: Optional[str], session_id: str, product_id: str,
                             quantity: int = 1) -> Event:
        """TC-8.6: Log an add-to-cart event."""
        return self._capture(
            "add_to_cart", user_id, session_id, product_id=product_id,
            metadata={"quantity": quantity},
        )
