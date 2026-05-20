"""CLI entry point for the trading bot."""

import argparse
import sys
import os
from pathlib import Path

from bot import (
    BinanceFuturesClient,
    OrderManager,
    ValidationError,
    validate_order_params,
    setup_logging
)


def load_credentials():
    """
    Load API credentials from environment variables.
    
    Returns:
        Tuple of (api_key, api_secret)
        
    Raises:
        ValueError: If credentials are not set
    """
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError(
            "API credentials not found. Please set environment variables:\n"
            "  export BINANCE_API_KEY='your_key'\n"
            "  export BINANCE_API_SECRET='your_secret'"
        )
    
    return api_key, api_secret


def create_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Trading Bot for Binance Futures Testnet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Place a MARKET BUY order
  python cli.py place-order BTCUSDT BUY MARKET 1.0
  
  # Place a LIMIT SELL order
  python cli.py place-order ETHUSDT SELL LIMIT 10.0 --price 2000.50
  
  # Check account balance
  python cli.py balance
  
  # Cancel an order
  python cli.py cancel-order BTCUSDT 12345678
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # place-order command
    place_parser = subparsers.add_parser(
        "place-order",
        help="Place a new order"
    )
    place_parser.add_argument("symbol", help="Trading pair (e.g., BTCUSDT)")
    place_parser.add_argument("side", help="Order side (BUY/SELL)")
    place_parser.add_argument("type", help="Order type (MARKET/LIMIT)")
    place_parser.add_argument("quantity", help="Order quantity")
    place_parser.add_argument(
        "--price",
        help="Order price (required for LIMIT orders)",
        default=None
    )
    
    # balance command
    subparsers.add_parser("balance", help="Check account balance")
    
    # cancel-order command
    cancel_parser = subparsers.add_parser(
        "cancel-order",
        help="Cancel an existing order"
    )
    cancel_parser.add_argument("symbol", help="Trading pair symbol")
    cancel_parser.add_argument("order_id", type=int, help="Order ID to cancel")
    
    # order-status command
    status_parser = subparsers.add_parser(
        "order-status",
        help="Get order status"
    )
    status_parser.add_argument("symbol", help="Trading pair symbol")
    status_parser.add_argument("order_id", type=int, help="Order ID")
    
    return parser


def place_order_command(args, manager):
    """Handle place-order command."""
    print("\n" + "="*60)
    print("ORDER REQUEST SUMMARY")
    print("="*60)
    print(f"Symbol:   {args.symbol.upper()}")
    print(f"Side:     {args.side.upper()}")
    print(f"Type:     {args.type.upper()}")
    print(f"Quantity: {args.quantity}")
    if args.price:
        print(f"Price:    {args.price}")
    print("="*60 + "\n")
    
    try:
        # Validate all parameters
        symbol, side, order_type, quantity, price = validate_order_params(
            args.symbol,
            args.side,
            args.type,
            args.quantity,
            args.price
        )
        
        # Place order
        result = manager.place_order(symbol, side, order_type, quantity, price)
        
        # Print result
        print(result.get_summary())
        
        return 0 if result.success else 1
        
    except ValidationError as e:
        print(f"\n❌ Validation Error: {str(e)}\n")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        return 1


def balance_command(manager):
    """Handle balance command."""
    print("\n" + "="*60)
    print("ACCOUNT BALANCE")
    print("="*60)
    
    try:
        balances = manager.get_account_balance()
        
        if not balances:
            print("No balances found or unable to fetch balances.")
        else:
            for asset, balance in sorted(balances.items()):
                if balance > 0:
                    print(f"{asset:10s} {balance:>15.8f}")
        
        print("="*60 + "\n")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error fetching balance: {str(e)}\n")
        return 1


def cancel_order_command(args, manager):
    """Handle cancel-order command."""
    print(f"\nCancelling order {args.order_id} for {args.symbol}...")
    
    try:
        success = manager.cancel_order(args.symbol, args.order_id)
        
        if success:
            print(f"✓ Order {args.order_id} cancelled successfully\n")
            return 0
        else:
            print(f"✗ Failed to cancel order {args.order_id}\n")
            return 1
            
    except Exception as e:
        print(f"✗ Error: {str(e)}\n")
        return 1


def order_status_command(args, manager):
    """Handle order-status command."""
    print(f"\nFetching status for order {args.order_id}...")
    
    try:
        order = manager.get_order_details(args.symbol, args.order_id)
        
        if order:
            print("\n" + "="*60)
            print(f"Order ID:     {order.get('orderId')}")
            print(f"Symbol:       {order.get('symbol')}")
            print(f"Side:         {order.get('side')}")
            print(f"Type:         {order.get('type')}")
            print(f"Status:       {order.get('status')}")
            print(f"Quantity:     {order.get('origQty')}")
            print(f"Executed:     {order.get('executedQty')}")
            print(f"Avg Price:    {order.get('avgPrice', 'N/A')}")
            print("="*60 + "\n")
            return 0
        else:
            print("Order not found\n")
            return 1
            
    except Exception as e:
        print(f"✗ Error: {str(e)}\n")
        return 1


def main():
    """Main entry point."""
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Trading Bot started")
    
    # Show help if no command
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        # Load credentials
        api_key, api_secret = load_credentials()
        
        # Initialize client and manager
        client = BinanceFuturesClient(api_key, api_secret)
        manager = OrderManager(client)
        
        # Route to appropriate command
        if args.command == "place-order":
            exit_code = place_order_command(args, manager)
        elif args.command == "balance":
            exit_code = balance_command(manager)
        elif args.command == "cancel-order":
            exit_code = cancel_order_command(args, manager)
        elif args.command == "order-status":
            exit_code = order_status_command(args, manager)
        else:
            print("Unknown command")
            exit_code = 1
        
        # Cleanup
        client.close()
        logger.info("Trading Bot closed")
        
        return exit_code
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}\n")
        return 1
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\n❌ Unexpected error: {str(e)}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
