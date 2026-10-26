"""
Seller inventory management.

Implements:
- US-1: Add New Product
- US-2: Update Existing Product
"""

import uuid
from typing import Any, Dict, Optional

from .catalog import ProductCatalog
from .errors import ProductNotFoundError, ValidationError
from .models import Product, utc_now

REQUIRED_DETAIL_FIELDS = ("name", "category", "price")


class SellerInventoryService:
    """Lets sellers add and update products in the shared catalog."""

    def __init__(self, catalog: ProductCatalog):
        self._catalog = catalog

    def add_product(
        self,
        seller_id: str,
        name: str,
        category: str,
        price: float,
        stock_quantity: Optional[int],
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Product:
        """
        US-1: Add a new product to the seller's inventory.

        Raises ValidationError if a required detail field is missing/blank
        (TC-1.2) or if stock_quantity is not provided (TC-1.3). On success,
        the product is saved to the shared catalog and is immediately
        visible to search (TC-1.1, TC-1.4).
        """
        details = {"name": name, "category": category, "price": price}
        missing = [field for field in REQUIRED_DETAIL_FIELDS if not details.get(field) and details.get(field) != 0]
        if missing:
            raise ValidationError(f"Missing required product details: {', '.join(missing)}")

        if stock_quantity is None:
            raise ValidationError("stock_quantity is required")

        product = Product(
            product_id=f"PRD-{uuid.uuid4().hex[:8]}",
            seller_id=seller_id,
            name=name,
            category=category,
            price=price,
            stock_quantity=stock_quantity,
            attributes=attributes or {},
        )
        self._catalog.save(product)
        return product

    def update_product(
        self,
        product_id: str,
        name: Optional[str] = None,
        category: Optional[str] = None,
        price: Optional[float] = None,
        stock_quantity: Optional[int] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Product:
        """
        US-2: Update an existing product's details and/or stock.

        Raises ProductNotFoundError if the product does not exist (TC-2.3).
        Only the fields explicitly provided (not None) are changed; all
        other fields are left as-is. updated_at is refreshed so the change
        is reflected immediately in subsequent search/view (TC-2.1, TC-2.2,
        TC-2.4).
        """
        product = self._catalog.get(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product '{product_id}' does not exist")

        if name is not None:
            product.name = name
        if category is not None:
            product.category = category
        if price is not None:
            product.price = price
        if stock_quantity is not None:
            product.stock_quantity = stock_quantity
        if attributes is not None:
            product.attributes.update(attributes)

        product.updated_at = utc_now()
        self._catalog.save(product)
        return product
