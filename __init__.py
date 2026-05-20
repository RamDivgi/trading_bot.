"""Trading bot package."""

from .client import BinanceFuturesClient, BinanceAPIError
from .orders import OrderManager, OrderResult
from .validators import (
    OrderSide, OrderType, ValidationError,
    validate_symbol, validate_side, validate_order_type,
    validate_quantity, validate_price, validate_order_params
)
from .logging_config import setup_logging

__all__ = [
    "BinanceFuturesClient",
    "BinanceAPIError",
    "OrderManager",
    "OrderResult",
    "OrderSide",
    "OrderType",
    "ValidationError",
    "validate_symbol",
    "validate_side",
    "validate_order_type",
    "validate_quantity",
    "validate_price",
    "validate_order_params",
    "setup_logging",
]
