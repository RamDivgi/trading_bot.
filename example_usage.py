"""
Example script demonstrating programmatic usage of the trading bot.

This script shows how to use the bot modules directly in your code
instead of through the CLI.
"""

import os
from bot import (
    BinanceFuturesClient,
    OrderManager,
    OrderSide,
    OrderType,
    setup_logging,
    ValidationError,
)


def main():
    """Demonstrate programmatic bot usage."""
    
    # Setup logging
    logger = setup_logging()
    
    # Load credentials from environment
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret:
        print("❌ Error: API credentials not found")
        print("Set environment variables: BINANCE_API_KEY, BINANCE_API_SECRET")
        return
    
    try:
        # Initialize client and manager
        client = BinanceFuturesClient(api_key, api_secret)
        manager = OrderManager(client)
        
        print("\n" + "="*60)
        print("Trading Bot - Programmatic Usage Example")
        print("="*60)
        
        # Example 1: Check balance
        print("\n1️⃣  Checking account balance...")
        balances = manager.get_account_balance()
        print(f"   USDT Balance: {balances.get('USDT', 0):.2f}")
        
        # Example 2: Place a MARKET BUY order
        print("\n2️⃣  Placing MARKET BUY order (0.001 BTCUSDT)...")
        result = manager.place_order(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=0.001
        )
        print(result.get_summary())
        
        if result.success:
            order_id = result.order_data.get("orderId")
            print(f"\n   ✓ Order placed with ID: {order_id}")
        
        # Example 3: Place a LIMIT SELL order
        print("\n3️⃣  Placing LIMIT SELL order (0.1 ETHUSDT @ 2500)...")
        result = manager.place_order(
            symbol="ETHUSDT",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=0.1,
            price=2500.0
        )
        print(result.get_summary())
        
        # Example 4: Check order status
        if result.success:
            order_id = result.order_data.get("orderId")
            print(f"\n4️⃣  Checking order status for order {order_id}...")
            order = manager.get_order_details("ETHUSDT", order_id)
            if order:
                print(f"   Status: {order.get('status')}")
                print(f"   Executed Qty: {order.get('executedQty')}")
        
        # Example 5: Display order history
        print("\n5️⃣  Order history from this session:")
        history = manager.get_order_history()
        for i, order_result in enumerate(history, 1):
            status = "✓ Success" if order_result.success else "✗ Failed"
            print(f"   {i}. {status}")
        
        print("\n" + "="*60)
        print("Example complete!")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}\n")
    
    finally:
        # Always close the client
        client.close()


if __name__ == "__main__":
    main()
