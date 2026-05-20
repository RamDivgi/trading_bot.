"""Input validation for trading orders."""

import re
from typing import Tuple
from enum import Enum


class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type enumeration."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_symbol(symbol: str) -> str:
    """
    Validate trading symbol format (e.g., BTCUSDT).
    
    Args:
        symbol: Trading pair symbol
        
    Returns:
        Uppercase symbol if valid
        
    Raises:
        ValidationError: If symbol format is invalid
    """
    symbol = symbol.upper().strip()
    
    if not symbol:
        raise ValidationError("Symbol cannot be empty")
    
    # Check if symbol matches pattern: 3+ letters + 4 letters (e.g., BTCUSDT)
    if not re.match(r"^[A-Z]{3,}[A-Z]{4}$", symbol):
        raise ValidationError(
            f"Invalid symbol format: {symbol}. Expected format like BTCUSDT"
        )
    
    return symbol


def validate_side(side: str) -> OrderSide:
    """
    Validate order side.
    
    Args:
        side: Order side (BUY/SELL)
        
    Returns:
        OrderSide enum value
        
    Raises:
        ValidationError: If side is invalid
    """
    side = side.upper().strip()
    
    try:
        return OrderSide[side]
    except KeyError:
        raise ValidationError(
            f"Invalid side: {side}. Must be BUY or SELL"
        )


def validate_order_type(order_type: str) -> OrderType:
    """
    Validate order type.
    
    Args:
        order_type: Order type (MARKET/LIMIT)
        
    Returns:
        OrderType enum value
        
    Raises:
        ValidationError: If order type is invalid
    """
    order_type = order_type.upper().strip()
    
    try:
        return OrderType[order_type]
    except KeyError:
        raise ValidationError(
            f"Invalid order type: {order_type}. Must be MARKET or LIMIT"
        )


def validate_quantity(quantity: str) -> float:
    """
    Validate order quantity.
    
    Args:
        quantity: Order quantity as string
        
    Returns:
        Quantity as float
        
    Raises:
        ValidationError: If quantity is invalid
    """
    try:
        qty = float(quantity)
        if qty <= 0:
            raise ValidationError("Quantity must be greater than 0")
        return qty
    except ValueError:
        raise ValidationError(f"Invalid quantity: {quantity}. Must be a number")


def validate_price(price: str) -> float:
    """
    Validate order price.
    
    Args:
        price: Order price as string
        
    Returns:
        Price as float
        
    Raises:
        ValidationError: If price is invalid
    """
    try:
        p = float(price)
        if p <= 0:
            raise ValidationError("Price must be greater than 0")
        return p
    except ValueError:
        raise ValidationError(f"Invalid price: {price}. Must be a number")


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str = None
) -> Tuple[str, OrderSide, OrderType, float, float]:
    """
    Validate all order parameters together.
    
    Args:
        symbol: Trading pair symbol
        side: Order side
        order_type: Order type
        quantity: Order quantity
        price: Order price (required for LIMIT orders)
        
    Returns:
        Tuple of validated (symbol, side, order_type, quantity, price)
        
    Raises:
        ValidationError: If any parameter is invalid
    """
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_type = validate_order_type(order_type)
    validated_qty = validate_quantity(quantity)
    
    validated_price = None
    if validated_type == OrderType.LIMIT:
        if price is None or price.strip() == "":
            raise ValidationError("Price is required for LIMIT orders")
        validated_price = validate_price(price)
    elif validated_type == OrderType.MARKET:
        if price is not None and price.strip() != "":
            import logging
            logging.getLogger("trading_bot").warning(
                "Price parameter is ignored for MARKET orders"
            )
    
    return validated_symbol, validated_side, validated_type, validated_qty, validated_price
