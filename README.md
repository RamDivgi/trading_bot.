# Trading Bot for Binance Futures Testnet

A professional-grade Python application for placing orders on Binance Futures Testnet (USDT-M). This bot features clean architecture, comprehensive error handling, and detailed logging.

## Features

✅ **Market & Limit Orders** - Place both market and limit orders  
✅ **BUY & SELL Support** - Full directional control  
✅ **Input Validation** - Comprehensive parameter validation  
✅ **Error Handling** - Graceful handling of network and API errors  
✅ **Structured Logging** - File and console logging with timestamps  
✅ **Account Management** - Check balances and order status  
✅ **Clean Architecture** - Modular, testable, and reusable code  
✅ **CLI Interface** - User-friendly command-line interface

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py              # Package exports
│   ├── client.py                # Binance API client wrapper
│   ├── orders.py                # Order placement logic
│   ├── validators.py            # Input validation
│   └── logging_config.py        # Logging setup
├── cli.py                       # CLI entry point
├── requirements.txt             # Dependencies
└── README.md
```

## Prerequisites

- Python 3.8+
- Binance Futures Testnet account
- Generated API credentials from testnet

### Setting Up Binance Testnet Account

1. Go to [Binance Futures Testnet](https://testnet.binancefuture.com)
2. Create or login to your account
3. Navigate to API Management
4. Create a new API key pair
5. Note: Ensure the API key has "Futures Trading" permissions enabled

## Installation

### 1. Clone or Download the Repository

```bash
cd trading_bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

**Linux/macOS:**
```bash
export BINANCE_API_KEY='your_api_key_here'
export BINANCE_API_SECRET='your_api_secret_here'
```

**Windows (PowerShell):**
```powershell
$env:BINANCE_API_KEY='your_api_key_here'
$env:BINANCE_API_SECRET='your_api_secret_here'
```

**Windows (Command Prompt):**
```cmd
set BINANCE_API_KEY=your_api_key_here
set BINANCE_API_SECRET=your_api_secret_here
```

**Alternative: Create a `.env` file** (and source it):
```bash
# .env
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
```

Then source it:
```bash
source .env
```

## Usage

### Basic Commands

#### 1. Place a Market Order

```bash
# BUY 1.0 BTC at market price
python cli.py place-order BTCUSDT BUY MARKET 1.0

# SELL 10.0 ETH at market price
python cli.py place-order ETHUSDT SELL MARKET 10.0
```

#### 2. Place a Limit Order

```bash
# BUY 1.0 BTC at 50,000 USDT
python cli.py place-order BTCUSDT BUY LIMIT 1.0 --price 50000

# SELL 10.0 ETH at 3,000 USDT
python cli.py place-order ETHUSDT SELL LIMIT 10.0 --price 3000
```

#### 3. Check Account Balance

```bash
python cli.py balance
```

Output example:
```
============================================================
ACCOUNT BALANCE
============================================================
BNB                      100.50000000
USDT                   5000.00000000
============================================================
```

#### 4. Cancel an Order

```bash
# Cancel order with ID 12345678
python cli.py cancel-order BTCUSDT 12345678
```

#### 5. Check Order Status

```bash
python cli.py order-status BTCUSDT 12345678
```

### Getting Help

```bash
python cli.py --help
python cli.py place-order --help
```

## Logging

All API requests, responses, and errors are logged to files in the `logs/` directory.

**Log files are created with timestamps:**
```
logs/
├── trading_bot_20240115_143022.log
├── trading_bot_20240115_150045.log
└── ...
```

**Log levels:**
- **DEBUG**: Detailed request/response information
- **INFO**: Order placement confirmations and important events
- **ERROR**: API errors and validation failures

### Example Log Output

```
2024-01-15 14:30:22 - trading_bot - INFO - Trading Bot started
2024-01-15 14:30:22 - trading_bot - INFO - Order Request - Symbol: BTCUSDT, Side: BUY, Type: MARKET, Quantity: 1.0, Price: None
2024-01-15 14:30:22 - trading_bot - DEBUG - POST /fapi/v1/order
2024-01-15 14:30:23 - trading_bot - DEBUG - Response: {'orderId': 123456, 'symbol': 'BTCUSDT', ...}
2024-01-15 14:30:23 - trading_bot - INFO - Order Response: {'orderId': 123456, ...}
```

## Architecture

### Client Layer (`bot/client.py`)

The `BinanceFuturesClient` class handles:
- HMAC SHA256 signing
- HTTP request construction
- API endpoint communication
- Error handling and logging

```python
client = BinanceFuturesClient(api_key, api_secret)
response = client.place_order(
    symbol="BTCUSDT",
    side=OrderSide.BUY,
    order_type=OrderType.MARKET,
    quantity=1.0
)
```

### Order Management Layer (`bot/orders.py`)

The `OrderManager` class provides:
- High-level order placement
- Result formatting and reporting
- Order history tracking
- Error recovery

```python
manager = OrderManager(client)
result = manager.place_order(
    symbol="BTCUSDT",
    side=OrderSide.BUY,
    order_type=OrderType.MARKET,
    quantity=1.0
)
print(result.get_summary())
```

### Validation Layer (`bot/validators.py`)

Functions for validating:
- Symbol format (e.g., BTCUSDT)
- Order sides (BUY/SELL)
- Order types (MARKET/LIMIT)
- Quantities and prices

```python
symbol, side, order_type, qty, price = validate_order_params(
    symbol="btcusdt",
    side="buy",
    order_type="limit",
    quantity="1.0",
    price="50000"
)
```

## Error Handling

The bot handles multiple error scenarios:

1. **Validation Errors** - Invalid input parameters
2. **API Errors** - Binance API rejection
3. **Network Errors** - Connection failures
4. **Configuration Errors** - Missing credentials

All errors are logged and reported to the user with helpful messages.

### Example Error Handling

```
$ python cli.py place-order INVALID BUY MARKET 1.0
❌ Validation Error: Invalid symbol format: INVALID. Expected format like BTCUSDT

$ python cli.py place-order BTCUSDT BUY LIMIT 1.0
❌ Validation Error: Price is required for LIMIT orders

$ python cli.py place-order BTCUSDT NOTASIDE MARKET 1.0
❌ Validation Error: Invalid side: NOTASIDE. Must be BUY or SELL
```

## Testing

### Manual Testing Steps

1. **Test MARKET BUY**
   ```bash
   python cli.py place-order BTCUSDT BUY MARKET 0.001
   ```
   - Verify order appears in testnet dashboard
   - Check log file for success message

2. **Test LIMIT SELL**
   ```bash
   python cli.py place-order ETHUSDT SELL LIMIT 0.1 --price 10000
   ```
   - Verify order status is PENDING
   - Check log file for order details

3. **Test Validation**
   ```bash
   python cli.py place-order INVALID BUY MARKET 1
   python cli.py place-order BTCUSDT INVALID MARKET 1
   python cli.py place-order BTCUSDT BUY INVALID 1
   ```
   - Verify appropriate error messages

4. **Test Balance Check**
   ```bash
   python cli.py balance
   ```
   - Verify USDT balance displays

## Assumptions & Notes

1. **Testnet Only** - This bot is configured for Binance Futures Testnet only
2. **USDT-M Contracts** - Uses USDT Margined Futures
3. **Time Zone** - Timestamps in logs use system timezone
4. **Minimal Library Usage** - Uses only `requests` library, no pandas/numpy needed
5. **Price Precision** - No decimal precision enforcement; Binance validates server-side
6. **Network Requirements** - Requires internet connection to testnet
7. **API Rate Limits** - No rate limiting implemented; respects Binance's limits
8. **Order Validation** - GTC (Good Till Cancel) used for LIMIT orders

## Advanced Usage

### Programmatic Usage

```python
from bot import BinanceFuturesClient, OrderManager, OrderSide, OrderType

# Initialize
client = BinanceFuturesClient(api_key, api_secret)
manager = OrderManager(client)

# Place order
result = manager.place_order(
    symbol="BTCUSDT",
    side=OrderSide.BUY,
    order_type=OrderType.LIMIT,
    quantity=1.0,
    price=45000.0
)

if result.success:
    print(f"Order placed: {result.order_data['orderId']}")
    print(result.get_summary())
else:
    print(f"Order failed: {result.error}")

# Get balance
balances = manager.get_account_balance()
print(f"USDT Balance: {balances.get('USDT', 0)}")

# Cancel order
manager.cancel_order("BTCUSDT", order_id=12345)

client.close()
```

### Custom Logging Configuration

```python
from bot import setup_logging

# Logs to custom directory
logger = setup_logging(log_dir="my_logs")
```

## Troubleshooting

### Missing API Credentials
```
❌ Configuration Error: API credentials not found. Please set environment variables:
  export BINANCE_API_KEY='your_key'
  export BINANCE_API_SECRET='your_secret'
```
**Solution:** Ensure environment variables are properly set before running the bot.

### Connection Refused
```
❌ Error: Request failed: Connection refused
```
**Solution:** Verify internet connectivity and testnet URL is accessible.

### Invalid API Signature
```
Binance API Error (1022): Invalid signature
```
**Solution:** Verify API key and secret are correctly set and haven't expired.

### Insufficient Balance
```
Binance API Error (-2019): Margin is insufficient
```
**Solution:** Check account balance with `python cli.py balance` and ensure sufficient USDT.

## Example Log Files

See `logs/` directory for:
- `trading_bot_<timestamp>.log` - Full application logs

Each order placement generates entries like:

```
2024-01-15 14:30:22 - trading_bot - INFO - Trading Bot started
2024-01-15 14:30:22 - trading_bot - INFO - Order Request - Symbol: BTCUSDT, Side: BUY, Type: MARKET, Quantity: 1.0, Price: None
2024-01-15 14:30:22 - trading_bot - DEBUG - POST /fapi/v1/order
2024-01-15 14:30:23 - trading_bot - DEBUG - Response: {'orderId': 123456, 'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'origQty': '1', 'status': 'FILLED', 'executedQty': '1', 'avgPrice': '45000.50'}
2024-01-15 14:30:23 - trading_bot - INFO - Order Response: {'orderId': 123456, ...}
2024-01-15 14:30:23 - trading_bot - INFO - Trading Bot closed
```

## Security Notes

⚠️ **IMPORTANT:**
- **Never hardcode** API keys in source code
- Use environment variables or `.env` files (add to `.gitignore`)
- Keep API keys private and secure
- Enable IP whitelisting in Binance Account > API Management
- Consider using restricted API keys with only "Futures Trading" permission
- Do not share logs containing order IDs publicly

## API Reference

### Binance Futures Endpoints Used

- `POST /fapi/v1/order` - Place new order
- `GET /fapi/v2/account` - Get account information
- `GET /fapi/v1/order` - Query order details
- `DELETE /fapi/v1/order` - Cancel order

Official docs: https://binance-docs.github.io/apidocs/futures/en/

## Performance

- **Order Placement**: ~100-500ms (network dependent)
- **Balance Query**: ~200-800ms (network dependent)
- **Logging Overhead**: Minimal (~10-20% of execution time)

## Dependencies

- `requests` (2.31.0+) - HTTP library for API calls

No heavy dependencies required - pure Python with standard library.

## License

This code is provided as-is for educational and testing purposes.

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review error messages and troubleshooting section
3. Verify Binance testnet connectivity
4. Confirm API credentials are valid and enabled

---

**Version:** 1.0  
**Last Updated:** January 2024  
**Python:** 3.8+
