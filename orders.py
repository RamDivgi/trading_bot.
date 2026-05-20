"""Order placement and management logic."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .client import BinanceFuturesClient, BinanceAPIError
from .validators import OrderSide, OrderType


class OrderResult:
    """Represents the result of an order placement."""
    
    def __init__(self, success: bool, order_data: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        """
        Initialize order result.
        
        Args:
            success: Whether the order was placed successfully
            order_data: Order response from API
            error: Error message if failed
        """
        self.success = success
        self.order_data = order_data or {}
        self.error = error
        self.timestamp = datetime.now()
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the order result."""
        if self.success:
            order_id = self.order_data.get("orderId")
            symbol = self.order_data.get("symbol")
            side = self.order_data.get("side")
            order_type = self.order_data.get("type")
            quantity = self.order_data.get("origQty")
            status = self.order_data.get("status")
            avg_price = self.order_data.get("avgPrice", "N/A")
            executed_qty = self.order_data.get("executedQty", 0)
            
            summary = f"""
╔════════════════════════════════════════════════════════╗
║                   ORDER PLACED SUCCESSFULLY            ║
╠════════════════════════════════════════════════════════╣
║ Order ID:        {order_id}
║ Symbol:          {symbol}
║ Side:            {side}
║ Type:            {order_type}
║ Quantity:        {quantity}
║ Status:          {status}
║ Executed Qty:    {executed_qty}
║ Avg Price:       {avg_price}
║ Timestamp:       {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
╚════════════════════════════════════════════════════════╝"""
            return summary
        else:
            return f"""
╔════════════════════════════════════════════════════════╗
║                    ORDER FAILED                        ║
╠════════════════════════════════════════════════════════╣
║ Error: {self.error}
║ Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
╚════════════════════════════════════════════════════════╝"""


class OrderManager:
    """Manages order placement and tracking."""
    
    def __init__(self, client: BinanceFuturesClient):
        """
        Initialize order manager.
        
        Args:
            client: BinanceFuturesClient instance
        """
        self.client = client
        self.logger = logging.getLogger("trading_bot")
        self.order_history = []
    
    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None
    ) -> OrderResult:
        """
        Place an order and return formatted result.
        
        Args:
            symbol: Trading pair symbol
            side: Order side
            order_type: Order type
            quantity: Order quantity
            price: Order price (for LIMIT orders)
            
        Returns:
            OrderResult with success status and details
        """
        try:
            # Log order request
            self.logger.info(
                f"Order Request - Symbol: {symbol}, Side: {side.value}, "
                f"Type: {order_type.value}, Quantity: {quantity}, Price: {price}"
            )
            
            # Place order via API
            response = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price
            )
            
            # Log successful response
            self.logger.info(f"Order Response: {response}")
            
            # Track in history
            result = OrderResult(success=True, order_data=response)
            self.order_history.append(result)
            
            return result
            
        except BinanceAPIError as e:
            error_msg = str(e)
            self.logger.error(f"Binance API Error: {error_msg}")
            result = OrderResult(success=False, error=error_msg)
            self.order_history.append(result)
            return result
            
        except ValueError as e:
            error_msg = str(e)
            self.logger.error(f"Validation Error: {error_msg}")
            result = OrderResult(success=False, error=error_msg)
            self.order_history.append(result)
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            result = OrderResult(success=False, error=error_msg)
            self.order_history.append(result)
            return result
    
    def get_account_balance(self) -> Dict[str, float]:
        """
        Get current account balance.
        
        Returns:
            Dictionary of asset balances
        """
        try:
            return self.client.get_balance()
        except BinanceAPIError as e:
            self.logger.error(f"Failed to fetch balance: {str(e)}")
            return {}
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """
        Cancel an order.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        try:
            self.client.cancel_order(symbol, order_id)
            self.logger.info(f"Order {order_id} cancelled successfully")
            return True
        except BinanceAPIError as e:
            self.logger.error(f"Failed to cancel order: {str(e)}")
            return False
    
    def get_order_details(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get order details.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID
            
        Returns:
            Order details
        """
        try:
            return self.client.get_order(symbol, order_id)
        except BinanceAPIError as e:
            self.logger.error(f"Failed to fetch order details: {str(e)}")
            return {}
    
    def get_order_history(self) -> list:
        """Get order placement history from this session."""
        return self.order_history
