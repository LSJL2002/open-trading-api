# Samsung Electronics Auto Trader Assignment

A lightweight, modular automated trading system for Samsung Electronics (005930) using the **Korea Investment Open API** with Python and REST API (no websocket).

**Note**: See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design and data flow.

## 📁 Project Structure

```
samsung_auto_trader/
├── main.py                  # Entry point and orchestration
├── config.py                # All configuration and constants
├── auth.py                  # Authentication and token caching
├── api_client.py            # Low-level REST API client
├── market_data.py           # Stock price queries and caching
├── account.py               # Account balance and holdings
├── orders.py                # Order placement and tracking
├── trader.py                # High-level trading logic
├── logger.py                # Structured logging utility
├── requirements.txt         # Python dependencies
├── token_cache.json         # Token cache (auto-generated)
├── README.md                # This file
└── ARCHITECTURE.md          # System design and data flow
```

---

## 📄 File Descriptions

### **main.py** - Entry Point and Orchestration
Responsibilities:
- Parse command-line arguments and environment variables
- Initialize all components in correct order
- Orchestrate the trading loop with error handling
- Gracefully handle shutdown and cleanup

Key Functions:
- `parse_account_number()`: Parse account format (12345678-01 → tuple)
- `main()`: Initialize system and run trading loop

### **config.py** - Centralized Configuration
Responsibilities:
- Define all constants and configuration values
- Make system easily configurable without code changes
- Manage trading parameters, API settings, and timing

Key Constants:
- `STOCK_CODE`: "005930" (Samsung Electronics)
- `TRADING_ENV`: "demo" (mock trading)
- `TRADING_START_TIME` / `TRADING_END_TIME`: Market hours (09:10 - 15:30)
- `ORDER_QUANTITY`: Shares per order
- `ORDER_BUFFER_KRW`: Price offset for orders (500 KRW)
- `MOMENTUM_WINDOW`: Recent prices to track (5)
- `PRICE_POLL_INTERVAL_SECONDS`: Check price every 15s
- `BALANCE_POLL_INTERVAL_SECONDS`: Check balance every 60s

### **logger.py** - Structured Logging Utility
Responsibilities:
- Provide consistent logging across all modules
- Handle log formatting and output configuration
- Offer helper functions for common log patterns

Key Functions:
- `setup_logger()`: Create and configure logger instance
- `log_api_call()`: Log API request details
- `log_error()`: Log errors with context

### **auth.py** - Authentication and Token Management
Responsibilities:
- Load credentials from environment variables (supports multiple naming conventions)
- Authenticate with Korea Investment API
- Cache tokens for same-day reuse to minimize API calls
- Validate and refresh tokens when needed

Key Classes:
- `TokenManager`: Manages token acquisition, caching, and validation

Environment Variables Supported:
- `GH_APPKEY` / `GH_APPSECRET` (primary)
- `GITHUB_APPKEY` / `GITHUB_APPSECRET`
- `KIS_APPKEY` / `KIS_APPSECRET`
- `APPKEY` / `APPSECRET` (legacy)

### **api_client.py** - Low-Level REST API Client
Responsibilities:
- Handle all HTTP GET/POST requests to Korea Investment API
- Manage request headers and authentication tokens
- Parse JSON responses and handle errors
- Implement retry logic for transient failures

Key Classes:
- `APIClient`: REST API wrapper with GET/POST methods

Features:
- Automatic header management (authentication, content-type)
- Base URL selection based on trading mode (mock vs. real)
- Error response parsing and retry logic
- Request timeout handling

### **market_data.py** - Stock Price Queries
Responsibilities:
- Fetch current stock prices from Korea Investment API
- Cache prices to avoid unnecessary API calls
- Track price history for momentum detection
- Parse and format price response data

Key Classes:
- `MarketData`: Query and manage market data

Key Methods:
- `get_current_price()`: Fetch current price for stock code
- `get_price_range()`: Calculate min/max from recent prices
- `detect_momentum()`: Analyze price trends for trading signals

### **account.py** - Account Management
Responsibilities:
- Query account balance and available cash
- Fetch current stock holdings
- Track account state across trading loop
- Format account data for display and decision-making

Key Classes:
- `Account`: Manage account information and holdings
- `AccountBalance`: Dataclass for balance information
- `StockHolding`: Dataclass for individual stock holdings

Key Methods:
- `get_balance()`: Fetch account balance and cash available
- `get_holdings()`: Fetch current stock holdings
- `has_stock()`: Check if specific stock is held

### **orders.py** - Order Placement and Tracking
Responsibilities:
- Place buy and sell orders via Korea Investment API
- Track order execution status
- Verify order fills and update mock holdings
- Handle order response parsing

Key Classes:
- `OrderManager`: Manage order placement and tracking
- `Order`: Dataclass for order information
- `OrderType`: Enum for BUY/SELL

Key Methods:
- `place_buy_order()`: Place a buy order at specified price
- `place_sell_order()`: Place a sell order at specified price
- `check_order_status()`: Verify if order was executed

### **trader.py** - High-Level Trading Logic
Responsibilities:
- Implement core trading strategy and decision logic
- Coordinate market data, account, and order managers
- Enforce trading window constraints
- Execute trading loop with proper timing

Key Classes:
- `Trader`: Main trading logic and coordination

Key Methods:
- `run()`: Execute trading loop until market close
- `execute_trading_cycle()`: Perform one complete buy-sell cycle
- `is_within_trading_window()`: Check if current time is during market hours

---

## 🔄 Trading Logic

The system operates in cycles during trading hours (09:10 - 15:30):

1. **Check Current Price**: Fetch real-time Samsung stock price via API
2. **Analyze Holdings**: Check account balance and current positions
3. **Place Buy Order**: Order at (lowest recent price - 500 KRW)
4. **Wait & Verify**: Poll order status until execution confirmed
5. **Place Sell Order**: Order at (highest recent price + 500 KRW)
6. **Wait & Verify**: Poll order status until execution confirmed
7. **Rest**: Wait before next cycle (respect rate limits)
8. **Repeat**: Continue until market close (15:30)

---

## 🚀 Getting Started

### 1. Run the Trader

```bash
python main.py
```

**Options**:
```bash
# Run until market closes (15:30)
python main.py

# Run for testing: 5 minutes only
python main.py --test-duration 5

# Get help
python main.py --help
```

---

## 📊 Configuration

Edit `config.py` to customize:

### Trading Parameters

```python
STOCK_CODE = "005930"                    # Samsung Electronics
ORDER_QUANTITY = 1                       # Shares per order
ORDER_BUFFER_KRW = 500                   # Buy/sell at price ± 500 KRW
MOMENTUM_WINDOW = 5                      # Track last 5 prices
MOMENTUM_THRESHOLD_PERCENT = 0.3         # 0.3% threshold for trend
```

### Trading Window

```python
TRADING_START_TIME = time(9, 10)    # 09:10 AM
TRADING_END_TIME = time(15, 30)     # 03:30 PM
```

### Rate Limiting

```python
PRICE_POLL_INTERVAL_SECONDS = 15       # Check price every 15s
BALANCE_POLL_INTERVAL_SECONDS = 60     # Check balance every 60s
MARKET_DATA_POLL_INTERVAL_SECONDS = 5  # Quick check after order
API_TIMEOUT_SECONDS = 10                # Timeout for API calls
```

### Logging

```python
LOG_LEVEL = "INFO"   # Can be DEBUG, INFO, WARNING, ERROR
```

---


### Understanding the Logs

Each trading cycle shows:

```
======================================================================
🔄 Starting trading cycle...
======================================================================
💹 Current price: 70,000 KRW
📦 Holdings before order: 0 shares
💰 Balance: 5,000,000 KRW available
📍 Price offsets: Buy 69,500 (current 70,000 - 500), Sell 70,500...
----------------------------------------------------------------------
📤 Placing BUY order: 1 shares of 005930 @ 69,500 KRW...
✅ API Response: 200 - POST /uapi/domestic-stock/v1/trading/order-cash
📤 Buy Order: Order ID: 12345, Status: 접수됨
⏳ Waiting for buy order execution...
📦 Holdings after buy: 1 shares
✅ Buy order EXECUTED (+1 shares)
----------------------------------------------------------------------
📤 Placing SELL order: 1 shares of 005930 @ 70,500 KRW...
✅ API Response: 200 - POST /uapi/domestic-stock/v1/trading/order-cash
📤 Sell Order: Order ID: 12346, Status: 접수됨
⏳ Waiting for sell order execution...
📦 Holdings after sell: 0 shares
✅ Sell order EXECUTED (-1 shares)
💵 Final balance: 5,000,100 KRW available
======================================================================
✅ Trading cycle completed
======================================================================
```

### Token Caching

First run: Gets new token from API, saves to `token_cache.json`
```
🔐 Token Issued: Token valid until 2026-05-31 16:00:00
```

Subsequent runs same day: Reuses cached token
```
🔐 Token Reused: Valid today (expires 2026-05-31 16:00:00)
```

## 📈 Performance Tips

To minimize API calls:

1. **Increase poll intervals** in `config.py`:
   ```python
   PRICE_POLL_INTERVAL_SECONDS = 60  # 60 seconds instead of 15
   ```

2. **Reduce trading cycle frequency**:
   - The script naturally waits between cycles
   - Adjust `PRICE_POLL_INTERVAL_SECONDS` to control this

3. **Cache is automatic**:
   - Token caches for same day automatically
   - Holdings cache internally after each query

4. **Use test-duration** for testing:
   ```bash
   python main.py --test-duration 5  # 5 minutes only
   ```

---

## 🔐 Security Considerations

✅ **What's safe**:
- Credentials loaded from environment variables (not hardcoded)
- Token cached locally in simple JSON (not encrypted)
- SSL verification disabled only for VTS (mock) endpoint
- No credentials logged

⚠️ **For production**:
- Use encrypted token storage
- Use `verify=True` for SSL/TLS validation
- Store credentials in secure vault (AWS Secrets, Azure Key Vault, etc.)
- Implement OAuth token refresh pipeline
- Audit all API calls and trades

---

## 🧪 Testing

### Quick Test Run

```bash
# Run for 5 minutes to test the system
python main.py --test-duration 5
```

## 📚 Related Documentation

- [Korea Investment Open API Portal](https://apiportal.koreainvestment.com/)
- [Korea Investment GitHub (Official Samples)](https://github.com/koreainvestment/open-trading-api)
- [Korea Exchange (KRX) Market Hours](https://www.krx.co.kr/)
- See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design

---

## 📝 License

This is sample code for educational purposes. Use responsibly.

---

**Created for Korea Investment Open API v1.0**  
**Last Updated: 2026-03-25**
