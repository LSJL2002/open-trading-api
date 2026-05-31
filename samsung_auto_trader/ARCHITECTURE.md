# Samsung Electronics Auto Trader - System Architecture

This document describes the system design, component interactions, and data flow of the Samsung Auto Trader.

---

## 🏗️ System Overview

The Samsung Auto Trader is built on a modular, layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      main.py (Orchestrator)                 │
│     Initializes system, coordinates components, runs loop   │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌────────────┐ ┌─────────────┐ ┌──────────────┐
   │   auth.py  │ │ config.py   │ │  logger.py   │
   │  (Token    │ │(Constants & │ │  (Logging)   │
   │Management) │ │ Config)     │ │              │
   └────────────┘ └─────────────┘ └──────────────┘
        │                                │
        └────────┬─────────────────────────┘
                 │
                 ▼
   ┌────────────────────────────────────┐
   │   trader.py (Trading Logic)        │
   │  - Coordinates market & orders     │
   │  - Implements trading strategy     │
   │  - Manages trading loop            │
   └────────┬───────────────────────────┘
            │
      ┌─────┼────────┬──────────────┐
      │     │        │              │
      ▼     ▼        ▼              ▼
┌──────────────┐ ┌────────────┐ ┌────────────┐
│market_data.py│ │ account.py │ │ orders.py  │
│ (Price Data) │ │(Balances & │ │(Order Mgmt)│
│              │ │ Holdings)  │ │            │
└──────┬───────┘ └─────┬──────┘ └─────┬──────┘
       │              │               │
       └──────────────┼───────────────┘
                      │
                      ▼
          ┌──────────────────────────┐
          │   api_client.py          │
          │  (REST API Client)       │
          │  - HTTP GET/POST         │
          │  - Headers & Auth        │
          │  - Error Handling        │
          └────────┬─────────────────┘
                   │
                   ▼
        ┌──────────────────────────┐
        │  Korea Investment API    │
        │  (VTS - Mock Trading)    │
        └──────────────────────────┘
```

---

## 📊 Component Details

### 1. **main.py** - Entry Point & Orchestrator

**Responsibilities:**
- Parse command-line arguments and environment variables
- Load account credentials
- Initialize all components in correct order
- Coordinate trading loop execution
- Handle graceful shutdown

**Key Flow:**
```
main()
  ├── Parse arguments (--test-duration)
  ├── Load GH_ACCOUNT env var
  ├── Parse account number (8 digits + 2 product code)
  ├── Create TokenManager (auth.py)
  ├── Get token
  ├── Create APIClient
  ├── Create Trader
  ├── Call trader.run()
  └── Handle errors and exit codes
```

**Entry Point for Users:**
- Users run: `python main.py [--test-duration N]`

---

### 2. **config.py** - Configuration & Constants

**Responsibilities:**
- Centralize all configuration values
- Make system configurable without code changes
- Define trading parameters and timing

**Key Constants:**
- `STOCK_CODE = "005930"` - Samsung Electronics
- `TRADING_ENV = "demo"` - Mock trading (NEVER change)
- `TRADING_START_TIME = time(9, 10)` - Market open
- `TRADING_END_TIME = time(15, 30)` - Market close
- `ORDER_QUANTITY = 1` - Shares per order
- `ORDER_BUFFER_KRW = 500` - Price offset
- `PRICE_POLL_INTERVAL_SECONDS = 15` - Check price every 15 seconds
- `BALANCE_POLL_INTERVAL_SECONDS = 60` - Check balance every 60 seconds
- `MOMENTUM_WINDOW = 5` - Track last 5 prices
- `API_TIMEOUT_SECONDS = 10` - Timeout for API calls

**Imported By:**
- Every module imports config for constants
- This is the single source of truth for configuration

---

### 3. **logger.py** - Structured Logging

**Responsibilities:**
- Provide consistent logging across all modules
- Handle log formatting and output configuration
- Offer helper functions for common log patterns

**Key Functions:**
- `setup_logger(name)` - Create logger for a module
- `log_api_call(logger, method, url, params)` - Log API calls
- `log_error(logger, context, message)` - Log errors with context

**Usage Pattern:**
```python
import logger as log_module
logger = log_module.setup_logger(__name__)
logger.info("Message")
logger.debug("Debug info")
```

---

### 4. **auth.py** - Authentication & Token Management

**Responsibilities:**
- Load credentials from environment variables
- Authenticate with Korea Investment API
- Cache tokens for same-day reuse
- Validate and refresh tokens

**Key Class: TokenManager**

**Flow:**
```
TokenManager()
  ├── load_credentials()
  │   ├── Try GH_APPKEY / GH_APPSECRET (primary)
  │   ├── Try GITHUB_APPKEY / GITHUB_APPSECRET
  │   ├── Try KIS_APPKEY / KIS_APPSECRET
  │   └── Try APPKEY / APPSECRET (legacy)
  │
  ├── get_token()
  │   ├── Check cache (token_cache.json)
  │   ├── If cached and valid, return cached token
  │   ├── Otherwise, call API to get new token
  │   ├── Save to cache with expiry time
  │   └── Return token
  │
  └── is_token_valid()
      └── Check if token not expired
```

**API Call for Token:**
- Endpoint: `POST /oauth2/tokenP` (Korea Investment API)
- Headers: app_key, app_secret
- Returns: access_token with expiry

**Cache File: token_cache.json**
```json
{
  "token": "eyJ...",
  "issued_at": "2026-05-31T10:30:00",
  "expires_at": "2026-05-31T16:00:00",
  "appkey": "..."
}
```

---

### 5. **api_client.py** - Low-Level REST API Client

**Responsibilities:**
- Handle all HTTP GET/POST requests
- Manage request headers and authentication
- Parse JSON responses
- Implement error handling and retries

**Key Class: APIClient**

**Initialization:**
```python
APIClient(token, app_key, app_secret, mock_trading=True)
  ├── Store token and credentials
  ├── Set base_url to VTS (mock) or production
  └── Prepare for API requests
```

**Base URLs:**
- Mock: `https://openapivts.koreainvestment.com:29443` (port 29443)
- Real: `https://openapi.koreainvestment.com:9443` (port 9443)

**Methods:**

**GET(endpoint, tr_id, params)** - Query API
- Adds authentication headers
- Includes TR_ID (transaction ID)
- Parameters sent as query string
- Returns JSON response

**POST(endpoint, tr_id, data, body_params)** - Send order
- Adds authentication headers
- Includes TR_ID
- Body parameters in JSON
- Returns JSON response

**Headers for All Requests:**
```
Authorization: Bearer {token}
appKey: {app_key}
appSecret: {app_secret}
Content-Type: application/json
tr_id: {tr_id}
```

**Error Handling:**
- Parses response body for error messages
- Retries on transient failures (timeout, 503)
- Logs all API calls and responses

---

### 6. **market_data.py** - Stock Price Queries

**Responsibilities:**
- Fetch current stock prices from Korea Investment API
- Cache prices to avoid unnecessary API calls
- Track price history for momentum detection
- Parse and format price response data

**Key Class: MarketData**

**Initialization:**
```python
MarketData(api_client)
  ├── Store api_client reference
  ├── Initialize price cache (None)
  ├── Initialize price history list []
  └── Initialize timestamp tracking
```

**Key Methods:**

**get_current_price(stock_code="005930") → Optional[int]**
```
1. Build endpoint: /uapi/domestic-stock/v1/quotations/inquire-price
2. Build params:
   - FID_COND_MRKT_DIV_CODE: "J" (Korea Exchange)
   - FID_INPUT_ISCD: "005930" (Samsung)
3. Call api_client.get()
4. Parse response for output1.stck_prpr (current price)
5. Cache price and timestamp
6. Add to price history
7. Return price as integer
```

**API Response Structure:**
```json
{
  "rt_cd": "0",  // Return code (0 = success)
  "msg_cd": "0",
  "msg1": "OK",
  "output1": {
    "stck_prpr": "70000",  // Current price (string)
    "stck_oprc": "69500",  // Open price
    ...
  }
}
```

**get_price_range() → Tuple[int, int]**
- Returns (min_price, max_price) from recent price history
- Used to calculate buy/sell prices based on momentum

**detect_momentum() → str**
- Analyzes recent price trends
- Returns "uptrend", "downtrend", or "neutral"
- Threshold: `MOMENTUM_THRESHOLD_PERCENT`

---

### 7. **account.py** - Account Management

**Responsibilities:**
- Query account balance and available cash
- Fetch current stock holdings
- Track account state across trading loop
- Format account data for display

**Key Classes:**

**AccountBalance (Dataclass)**
```python
@dataclass
class AccountBalance:
    total_balance: int      # Total account balance (KRW)
    available_cash: int     # Available cash for trading (KRW)
    total_assets: int       # Total assets including holdings (KRW)
```

**StockHolding (Dataclass)**
```python
@dataclass
class StockHolding:
    stock_code: str         # Stock code (e.g., "005930")
    stock_name: str         # Stock name
    quantity: int           # Shares held
    purchase_price: int     # Average purchase price (KRW)
    current_price: int      # Current price (KRW)
    total_value: int        # Total value of holding (KRW)
    profit_loss: int        # Unrealized P&L (KRW)
```

**Account (Main Class)**

**Initialization:**
```python
Account(api_client, account_number, account_product_code)
  ├── Store credentials
  ├── Store api_client reference
  └── Initialize cache for balance/holdings
```

**Key Methods:**

**get_balance() → Optional[AccountBalance]**
```
1. Build endpoint: /uapi/domestic-stock/v1/trading/inquire-psbl-order
2. Build params:
   - CANO: account_number (8 digits)
   - ACNT_PRDT_CD: account_product_code (2 digits, "01" for stocks)
   - INQR_DVSN: "02" (inquiry by stock)
   - UNPR_DVSN: "01" (standard price)
3. Call api_client.get()
4. Parse response for:
   - output1.ord_psbl_cash (available cash)
   - output1.psbl_buy_amt (total balance)
5. Cache and return as AccountBalance
```

**get_holdings() → Optional[List[StockHolding]]**
```
1. Build endpoint: /uapi/domestic-stock/v1/trading/inquire-balance
2. Build params:
   - CANO: account_number
   - ACNT_PRDT_CD: account_product_code
   - INQR_DVSN: "02" (by stock)
   - UNPR_DVSN: "01" (standard price)
3. Call api_client.get()
4. Parse output2 array for each holding:
   - hldg_qty (quantity)
   - pchs_avg_pric (purchase price)
   - prpr (current price)
   - stck_name (stock name)
5. Calculate total_value and profit_loss
6. Cache and return list
```

**has_stock(stock_code) → bool**
- Check if account holds specific stock
- Uses cached holdings

**API Response for Balance:**
```json
{
  "output1": {
    "ord_psbl_cash": "5000000",  // Available cash for orders
    "psbl_buy_amt": "5000000"    // Total available to buy
  }
}
```

---

### 8. **orders.py** - Order Placement and Tracking

**Responsibilities:**
- Place buy and sell orders via Korea Investment API
- Track order execution status
- Verify order fills and update mock holdings
- Handle order response parsing

**Key Classes:**

**OrderType (Enum)**
```python
class OrderType(str, Enum):
    BUY = "buy"
    SELL = "sell"
```

**Order (Dataclass)**
```python
@dataclass
class Order:
    order_type: OrderType
    stock_code: str
    quantity: int
    price: int
    order_id: Optional[str] = None
    execution_status: str = ""
```

**OrderManager (Main Class)**

**Initialization:**
```python
OrderManager(api_client, account_number, account_product_code, account=None)
  ├── Store credentials
  ├── Store api_client reference
  ├── Store account reference (for mock trading)
  └── Initialize order tracking
```

**Key Methods:**

**place_buy_order(stock_code, quantity, price) → Optional[Order]**
```
1. Build endpoint: /uapi/domestic-stock/v1/trading/order-cash
2. Build body params:
   - CANO: account_number
   - ACNT_PRDT_CD: account_product_code
   - PDNO: stock_code (6-digit)
   - ORD_DVSN: "00" (limit order)
   - ORD_QTY: quantity
   - ORD_UNPR: price
   - INQR_DVSN: "01" (inquiry type)
3. Call api_client.post()
4. Extract order_id from response (output.ORD_NO)
5. Extract execution status
6. Log and return Order object
```

**place_sell_order(stock_code, quantity, price) → Optional[Order]**
- Same as place_buy_order but with different ORD_DVSN

**check_order_status(order) → bool**
```
1. Build endpoint: /uapi/domestic-stock/v1/trading/inquire-order
2. Build params:
   - CANO: account_number
   - ACNT_PRDT_CD: account_product_code
   - ORD_No: order.order_id
3. Call api_client.get()
4. Parse output for order status:
   - "체결" (executed) = completed
   - "접수" (received) = received
   - "주문중" = ordering
5. Return True if executed, False otherwise
6. For mock trading, update Account holdings if executed
```

**API Response for Place Order:**
```json
{
  "output": {
    "ORD_NO": "12345",  // Order ID
    "msg1": "주문이 접수 되었습니다."  // Status message
  }
}
```

---

### 9. **trader.py** - High-Level Trading Logic

**Responsibilities:**
- Implement core trading strategy
- Coordinate market data, account, and order managers
- Enforce trading window constraints
- Execute trading loop with proper timing

**Key Class: Trader**

**Initialization:**
```python
Trader(api_client, account_number, account_product_code, stock_code="005930")
  ├── Store parameters
  ├── Create MarketData instance
  ├── Create Account instance
  ├── Create OrderManager instance
  └── Initialize trading state
```

**Key Methods:**

**run(test_duration_minutes=0) → bool**
```
Main trading loop:

1. Log start time and parameters
2. Enter loop until market close or timeout:
   
   a. Check if within trading window (09:10 - 15:30)
      └── If outside, wait or exit
   
   b. Call execute_trading_cycle()
   
   c. Log cycle results
   
   d. Wait before next cycle
      └── Respect PRICE_POLL_INTERVAL_SECONDS
   
   e. Check for test duration timeout
      └── Exit if test_duration exceeded

3. Log final statistics
4. Return True if completed successfully
```

**execute_trading_cycle() → bool**
```
One complete buy-sell cycle:

1. Fetch current price
   ├── Call market.get_current_price()
   ├── Log price
   └── Return False if failed

2. Analyze market momentum
   ├── Get price range from history
   ├── Detect trend (uptrend, downtrend, neutral)
   └── Calculate buy/sell prices:
       - Buy price = min_recent_price - ORDER_BUFFER_KRW
       - Sell price = max_recent_price + ORDER_BUFFER_KRW

3. Check account balance
   ├── Call account.get_balance()
   ├── Verify sufficient cash
   └── Return False if insufficient

4. Place buy order
   ├── Call orders.place_buy_order()
   ├── Wait for confirmation
   └── Verify execution status

5. Wait for order execution
   ├── Poll order status every MARKET_DATA_POLL_INTERVAL_SECONDS
   ├── Timeout after max attempts
   └── Verify holdings increased

6. Update market data
   ├── Fetch latest price
   └── Update price history

7. Place sell order
   ├── Call orders.place_sell_order()
   ├── Use updated price information
   └── Wait for confirmation

8. Wait for order execution
   ├── Poll order status
   ├── Timeout after max attempts
   └── Verify holdings decreased

9. Calculate P&L
   ├── Buy price vs. sell price
   ├── Transaction cost impact
   └── Log profit/loss

10. Return True if cycle completed successfully
```

**is_within_trading_window() → bool**
```
Check if current time is within trading hours:
1. Get current time (local Korean time)
2. Compare with TRADING_START_TIME (09:10)
3. Compare with TRADING_END_TIME (15:30)
4. Return True if between them, False otherwise
```

---

## 🔄 Complete Request-Response Flow

### Example: Full Trading Cycle (Buy & Sell)

```
START: main.py
  │
  ├─→ Load credentials from environment
  │    └─→ GH_APPKEY, GH_APPSECRET, GH_ACCOUNT
  │
  ├─→ Create TokenManager
  │    └─→ load_credentials()
  │    └─→ get_token()
  │         ├─→ Check cache (token_cache.json)
  │         └─→ If expired/missing, call auth API:
  │              POST /oauth2/tokenP
  │              Returns: access_token, expires_at
  │              Saves to token_cache.json
  │
  ├─→ Create APIClient(token, app_key, app_secret)
  │    └─→ Set base_url to VTS (29443)
  │
  └─→ Create Trader(api_client, account_number, product_code)
       ├─→ Create MarketData(api_client)
       ├─→ Create Account(api_client, account_number, product_code)
       └─→ Create OrderManager(api_client, account_number, product_code, account)
            │
            └─→ trader.run()
                 │
                 ├─→ Check time is between 09:10 - 15:30
                 │
                 └─→ CYCLE 1: execute_trading_cycle()
                      │
                      ├─→ GET /uapi/domestic-stock/v1/quotations/inquire-price
                      │    ├─→ params: FID_COND_MRKT_DIV_CODE=J, FID_INPUT_ISCD=005930
                      │    └─→ response: stck_prpr=70000
                      │
                      ├─→ GET /uapi/domestic-stock/v1/trading/inquire-balance
                      │    ├─→ params: CANO, ACNT_PRDT_CD, INQR_DVSN=02
                      │    └─→ response: ord_psbl_cash=5000000, output2=[holdings]
                      │
                      ├─→ Calculate prices:
                      │    ├─→ Get min/max from price history
                      │    ├─→ Buy price = 69500 (70000 - 500)
                      │    └─→ Sell price = 70500 (70000 + 500)
                      │
                      ├─→ POST /uapi/domestic-stock/v1/trading/order-cash (BUY)
                      │    ├─→ body: PDNO=005930, ORD_QTY=1, ORD_UNPR=69500
                      │    ├─→ response: ORD_NO=12345
                      │    │
                      │    └─→ GET /uapi/domestic-stock/v1/trading/inquire-order
                      │         ├─→ Poll until status=체결됨
                      │         └─→ Verify holdings increased to 1 share
                      │
                      ├─→ GET /uapi/domestic-stock/v1/quotations/inquire-price (refresh)
                      │    └─→ Update price in history
                      │
                      ├─→ POST /uapi/domestic-stock/v1/trading/order-cash (SELL)
                      │    ├─→ body: PDNO=005930, ORD_QTY=1, ORD_UNPR=70500
                      │    ├─→ response: ORD_NO=12346
                      │    │
                      │    └─→ GET /uapi/domestic-stock/v1/trading/inquire-order
                      │         ├─→ Poll until status=체결됨
                      │         └─→ Verify holdings decreased to 0 shares
                      │
                      ├─→ Calculate P&L: 70500 - 69500 = 1000 KRW profit
                      │
                      └─→ Wait 15 seconds (PRICE_POLL_INTERVAL_SECONDS)
                           │
                           └─→ Loop continues until 15:30 or test_duration expires
```

---

## 🔐 Security & Error Handling

### Authentication Security
- Credentials loaded from environment variables (never hardcoded)
- Token cached locally but marked for expiry
- Token refreshed automatically when expired
- API calls include auth headers

### Error Handling
- All API calls wrapped in try-except
- Retries on transient failures (timeout, 503)
- Graceful degradation on errors
- Comprehensive logging for debugging

### Rate Limiting
- Respect conservative polling intervals
- Token caching minimizes authentication calls
- Price polling: 15 seconds (configurable)
- Balance polling: 60 seconds (configurable)

---

## 📈 Data Flow Summary

**Environment Variables** → **main.py** → **auth.py** (Token)
    ↓
**TokenManager** → **api_client.py** → **Korea Investment API (VTS)**
    ↓
**APIClient** ← returns JSON
    ↓
**trader.py** ← coordinates all operations
    ├── **market_data.py** ← price data
    ├── **account.py** ← balance & holdings
    └── **orders.py** ← order responses

---

## 🎯 Key Design Principles

1. **Modular**: Each module has single responsibility
2. **Testable**: Components can be tested independently
3. **Configurable**: All parameters in config.py
4. **Logged**: Every action logged for debugging
5. **Resilient**: Error handling at every layer
6. **Simple**: Clear code over clever code
7. **Documented**: Docstrings in every function

---

## 📝 Summary

The Samsung Auto Trader demonstrates a clean, modular approach to API-based trading:

- **Single Entry Point**: main.py orchestrates everything
- **Clear Separation**: Each component handles one concern
- **API-First Design**: All functionality goes through api_client.py
- **Configuration-Driven**: Easy to modify behavior without code changes
- **Production-Ready**: Error handling, logging, timeouts, rate limiting
- **Educational**: Clear structure for learning and modification

