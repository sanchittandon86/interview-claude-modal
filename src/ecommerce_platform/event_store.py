"""
Event storage & handoff to the recommendation/ML system.

Implements US-9: Store and Provide Events to Recommendation System.
"""

from typing import List, Optional

from .models import Event


class EventStore:
    """In-memory, append-only store for captured interaction events."""

    def __init__(self):
        self._events: List[Event] = []

    def persist(self, event: Event) -> None:
        """
        TC-9.1/TC-9.3: Persist a single captured event.

        Appends are unconditional and O(1), so a burst of events captured
        in a short time window (TC-9.3) is retained in full, with no loss.
        """
        self._events.append(event)

    def get_events_for_ml(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[Event]:
        """
        TC-9.2: Provide stored events to the recommendation/ML system.

        The ML system itself is out of scope; this method only exposes the
        persisted event stream (optionally scoped to a session and/or user)
        for that external system to consume.
        """
        events = self._events
        if session_id is not None:
            events = [e for e in events if e.session_id == session_id]
        if user_id is not None:
            events = [e for e in events if e.user_id == user_id]
        return events
