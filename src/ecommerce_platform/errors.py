"""Custom exceptions used across the platform."""


class ValidationError(Exception):
    """Raised when submitted product data fails required-field validation (US-1)."""


class ProductNotFoundError(Exception):
    """Raised when an operation references a product that does not exist (US-2)."""
