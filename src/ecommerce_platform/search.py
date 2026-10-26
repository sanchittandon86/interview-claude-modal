"""
Buyer-facing product search.

Implements:
- US-3: Search Products by Query
- US-4: Filter Search Results
- US-5: View Ranked Search Results
- US-6: Navigate via Facets
"""

from typing import Any, Dict, List, Optional

from .catalog import ProductCatalog
from .models import Product


class SearchService:
    """Executes query + filter + ranking + facet logic over the product catalog."""

    def __init__(self, catalog: ProductCatalog):
        self._catalog = catalog

    def search(self, query_text: str = "", filters: Optional[Dict[str, Any]] = None) -> List[Product]:
        """
        US-3/US-4: Search products by free-text query, optionally narrowed
        by one or more filters.

        - An empty/blank query matches all products rather than erroring
          (TC-3.3).
        - A query/filter combination with no matches returns an empty list,
          never an error (TC-3.2, TC-4.3).
        - Multiple filters are combined with AND semantics (TC-4.1, TC-4.2);
          removing a filter and re-calling search() naturally re-expands
          results (TC-4.4).
        Results are passed through _rank() before being returned (US-5).
        """
        filters = filters or {}
        candidates = self._catalog.all()

        normalized_query = (query_text or "").strip().lower()
        if normalized_query:
            candidates = [
                p for p in candidates
                if normalized_query in p.name.lower() or normalized_query in p.category.lower()
            ]

        for field_name, value in filters.items():
            candidates = [p for p in candidates if self._matches_filter(p, field_name, value)]

        return self._rank(candidates, normalized_query)

    @staticmethod
    def _matches_filter(product: Product, field_name: str, value: Any) -> bool:
        """Check a single filter against a product's top-level fields or its attributes dict."""
        if hasattr(product, field_name):
            return getattr(product, field_name) == value
        return product.attributes.get(field_name) == value

    @staticmethod
    def _rank(products: List[Product], normalized_query: str) -> List[Product]:
        """
        US-5: Rank results by relevance.

        Relevance score weighs an exact name match highest, then a partial
        name match, then a category match. Ties are broken by product_id so
        that identical queries over unchanged data always return the same
        order (TC-5.2), and a single-match query ranks without error
        (TC-5.3).
        """

        def score(p: Product) -> tuple:
            relevance = 0
            if normalized_query:
                name = p.name.lower()
                if normalized_query == name:
                    relevance = 3
                elif normalized_query in name:
                    relevance = 2
                elif normalized_query in p.category.lower():
                    relevance = 1
            return (-relevance, p.product_id)

        return sorted(products, key=score)

    def get_facets(self, products: List[Product]) -> Dict[str, List[Any]]:
        """
        US-6: Derive available facet options from a result set.

        Returns a mapping of attribute name -> sorted distinct values found
        across the given products' `attributes`. Selecting one of these
        values is just another filter passed back into search() (TC-6.2).
        Returns an empty dict when no products/attributes are present, so
        the caller shows no facets rather than erroring (TC-6.3).
        """
        facets: Dict[str, set] = {}
        for product in products:
            for key, value in product.attributes.items():
                facets.setdefault(key, set()).add(value)
        return {key: sorted(values) for key, values in facets.items()}
