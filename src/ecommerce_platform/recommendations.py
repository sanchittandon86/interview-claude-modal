"""
Personalized recommendation display.

Implements US-7: View Personalized Recommendations.

The recommendation/ML model itself is out of scope (per the business
problem definition). This module only defines the interface the platform
uses to request recommendations from that black-box system, and how the
returned list is passed through for display — it implements no ranking
or ML logic of its own.
"""

from typing import List, Protocol


class RecommendationMLClient(Protocol):
    """
    Interface the platform calls to reach the black-box recommendation/ML
    system. Any concrete client satisfying this interface (e.g., an HTTP
    client to the real ML service) can be plugged in; that system's
    internal logic is out of scope here.
    """

    def get_recommendations(self, user_id: str, session_id: str) -> List[str]:
        ...


class RecommendationService:
    """Requests recommendations from the ML client and prepares them for display."""

    def __init__(self, ml_client: RecommendationMLClient):
        self._ml_client = ml_client

    def get_recommendations_for_display(self, user_id: str, session_id: str) -> List[str]:
        """
        TC-7.1/TC-7.2: Return the recommendation/ML system's output verbatim
        for the given account/session, without the platform altering its
        content or ordering.

        TC-7.3: If the ML system returns no recommendations, an empty list
        is returned so the caller can render an empty/no-recommendations
        state without error.
        """
        recommendations = self._ml_client.get_recommendations(user_id, session_id)
        return recommendations or []
