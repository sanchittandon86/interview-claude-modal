"""
In-memory product catalog shared by the inventory (US-1, US-2) and
search (US-3 - US-6) modules. Acts as the single source of truth for
product data so that writes from sellers are immediately visible to
buyer-facing search.
"""

from typing import Dict, List, Optional

from .models import Product


class ProductCatalog:
    """In-memory store standing in for a real product database."""

    def __init__(self):
        self._products: Dict[str, Product] = {}

    def save(self, product: Product) -> None:
        """Insert or overwrite a product record."""
        self._products[product.product_id] = product

    def get(self, product_id: str) -> Optional[Product]:
        """Fetch a product by ID, or None if it doesn't exist."""
        return self._products.get(product_id)

    def exists(self, product_id: str) -> bool:
        """Check whether a product ID is present in the catalog."""
        return product_id in self._products

    def all(self) -> List[Product]:
        """Return all products currently in the catalog."""
        return list(self._products.values())
