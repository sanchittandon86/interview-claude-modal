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
        - The query is split into whitespace-separated tokens; a product
          matches only if every token is found somewhere in its name,
          category, or attribute values (e.g. "black sneakers" requires
          both "black" and "sneakers" to each match, regardless of which
          field each word is found in).
        Results are passed through _rank() before being returned (US-5).
        """
        filters = filters or {}
        candidates = self._catalog.all()

        normalized_query = (query_text or "").strip().lower()
        query_tokens = normalized_query.split()
        if query_tokens:
            candidates = [
                p for p in candidates
                if all(self._token_matches(p, token) for token in query_tokens)
            ]

        for field_name, value in filters.items():
            candidates = [p for p in candidates if self._matches_filter(p, field_name, value)]

        return self._rank(candidates, query_tokens)

    @staticmethod
    def _token_matches(product: Product, token: str) -> bool:
        """Check whether a single query word appears in a product's name, category, or attributes."""
        if token in product.name.lower() or token in product.category.lower():
            return True
        return any(token in str(value).lower() for value in product.attributes.values())

    @staticmethod
    def _matches_filter(product: Product, field_name: str, value: Any) -> bool:
        """Check a single filter against a product's top-level fields or its attributes dict."""
        if hasattr(product, field_name):
            return getattr(product, field_name) == value
        return product.attributes.get(field_name) == value

    @staticmethod
    def _rank(products: List[Product], query_tokens: List[str]) -> List[Product]:
        """
        US-5: Rank results by relevance.

        Each query token contributes its own score (name match weighted
        highest, then category, then attribute values), summed across all
        tokens so multi-word queries like "black sneakers" still rank
        stronger matches first. Ties are broken by product_id so that
        identical queries over unchanged data always return the same order
        (TC-5.2), and a single-match query ranks without error (TC-5.3).
        """

        def score(p: Product) -> tuple:
            relevance = 0
            if query_tokens:
                name = p.name.lower()
                category = p.category.lower()
                attr_values = [str(value).lower() for value in p.attributes.values()]
                for token in query_tokens:
                    if token == name:
                        relevance += 3
                    elif token in name:
                        relevance += 2
                    elif token in category:
                        relevance += 1
                    elif any(token in av for av in attr_values):
                        relevance += 1
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
