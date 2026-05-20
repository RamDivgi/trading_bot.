"""Binance Futures API client wrapper."""

import requests
import logging
import hmac
import hashlib
import time
from typing import Dict, Any, Optional
from urllib.parse import urlencode

from .validators import OrderSide, OrderType


class BinanceAPIError(Exception):
    """Custom exception for Binance API errors."""
    pass


class BinanceFuturesClient:
    """
    Client for interacting with Binance Futures Testnet API.
    
    Handles authentication, request signing, and order placement.
    """
    
    BASE_URL = "https://testnet.binancefuture.com"
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize Binance Futures client.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger = logging.getLogger("trading_bot")
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Accept": "application/json",
            "User-Agent": "Trading-Bot/1.0"
        })
    
    def _sign_request(self, params: Dict[str, Any]) -> str:
        """
        Sign API request with HMAC SHA256.
        
        Args:
            params: Request parameters
            
        Returns:
            Signed query string
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{query_string}&signature={signature}"
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Binance API.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint path
            params: Request parameters
            signed: Whether request needs to be signed
            
        Returns:
            Response JSON as dictionary
            
        Raises:
            BinanceAPIError: If API returns an error
            requests.RequestException: If network error occurs
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        if params is None:
            params = {}
        
        # Add timestamp for signed requests
        if signed:
            params["timestamp"] = int(time.time() * 1000)
            query_string = self._sign_request(params)
            url = f"{url}?{query_string}"
        else:
            if params:
                url = f"{url}?{urlencode(params)}"
        
        try:
            self.logger.debug(f"{method} {endpoint}")
            if params and not signed:
                self.logger.debug(f"Params: {params}")
            
            response = self.session.request(method, url)
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug(f"Response: {data}")
            
            # Check for Binance API error response
            if "code" in data and data.get("code") != 0:
                error_msg = data.get("msg", "Unknown error")
                raise BinanceAPIError(f"Binance API Error ({data['code']}): {error_msg}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise BinanceAPIError(f"Request failed: {str(e)}") from e
    
    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place an order on Binance Futures Testnet.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            side: Order side (BUY/SELL)
            order_type: Order type (MARKET/LIMIT)
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            
        Returns:
            Order response from API
            
        Raises:
            BinanceAPIError: If order placement fails
            ValueError: If parameters are invalid
        """
        if order_type == OrderType.LIMIT and price is None:
            raise ValueError("Price is required for LIMIT orders")
        
        params = {
            "symbol": symbol,
            "side": side.value,
            "type": order_type.value,
            "quantity": quantity,
        }
        
        if order_type == OrderType.LIMIT:
            params["price"] = price
            params["timeInForce"] = "GTC"  # Good Till Cancel
        
        self.logger.info(
            f"Placing {order_type.value} order: {side.value} {quantity} {symbol} "
            f"@ {price if price else 'market price'}"
        )
        
        return self._request("POST", "/fapi/v1/order", params, signed=True)
    
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Account details
        """
        return self._request("GET", "/fapi/v2/account", signed=True)
    
    def get_balance(self) -> Dict[str, float]:
        """
        Get account balances.
        
        Returns:
            Dictionary of {asset: balance}
        """
        account = self.get_account()
        balances = {}
        for asset in account.get("assets", []):
            balances[asset["asset"]] = float(asset["availableBalance"])
        return balances
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel an existing order.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID to cancel
            
        Returns:
            Cancellation response
        """
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        return self._request("DELETE", "/fapi/v1/order", params, signed=True)
    
    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get order details.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID
            
        Returns:
            Order details
        """
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        return self._request("GET", "/fapi/v1/order", params, signed=True)
    
    def close(self):
        """Close the session."""
        self.session.close()
