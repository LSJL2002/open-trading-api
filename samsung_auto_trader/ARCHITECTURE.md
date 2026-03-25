# Samsung Electronics Auto Trader - Architecture Overview

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         MAIN ENTRY POINT                        │
│                          (main.py)                              │
│  • Initialize system                                            │
│  • Load credentials                                             │
│  • Start trading loop                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        ┌────────────┐ ┌─────────┐ ┌──────────────┐
        │ auth.py    │ │config.py│ │ logger.py    │
        │ • Token    │ │ Settings│ │ • Logging    │
        │ • Cache    │ │ • Consts│ │ • Formatting│
        └────────────┘ └─────────┘ └──────────────┘
                │
                ▼
        ┌──────────────────┐
        │  api_client.py   │
        │ ────────────────│
        │ • GET requests   │
        │ • POST requests  │
        │ • Retry Logic    │
        │ • Error Handling │
        └──────────────────┘
                │
    ┌───────────┼───────────┬───────────┐
    │           │           │           │
    ▼           ▼           ▼           ▼
┌─────────┐ ┌──────────┐ ┌────────┐ ┌────────┐
│market   │ │account   │ │orders  │ │trader  │
│_data.py │ │.py       │ │.py     │ │.py     │
├─────────┤ ├──────────┤ ├────────┤ ├────────┤
│ Get     │ │ Balance  │ │ Place  │ │ Trading│
│ price   │ │ Holdings │ │ orders │ │ logic  │
│ Cache   │ │ Verify   │ │ Notify │ │ Loop   │
└─────────┘ └──────────┘ └────────┘ └────────┘
```

---

## 📊 Data Flow for One Trading Cycle

```
┌─────────────────────────────────────────┐
│ TRADING CYCLE (30-60 seconds)           │
└─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌───────────┐ ┌──────────┐ ┌─────────────┐
│GET PRICE  │ │GET BALANCE│ │GET HOLDINGS │
│market_data│ │account.py │ │account.py   │
│.py        │ │           │ │             │
└────┬──────┘ └─────┬──────┘ └────┬────────┘
     │              │             │
     └──────────────┼─────────────┘
                    │
          ┌─────────▼─────────┐
          │ CALCULATE PRICES  │
          │ Buy = Price-2000  │
          │ Sell = Price+2000 │
          └────┬──────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌──────────────┐  ┌──────────────┐
│ PLACE BUY    │  │ PLACE SELL   │
│ ORDER        │  │ ORDER        │
│ orders.py    │  │ orders.py    │
└────┬─────────┘  └──────┬───────┘
     │                   │
     └───────┬───────────┘
             │
    ┌────────▼─────────┐
    │   WAIT & VERIFY  │
    │ Check holdings   │
    │ account.py       │
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │ NEXT CYCLE or    │
    │ END TRADING      │
    └──────────────────┘
```

---

## 🔄 Component Relationships

### 1️⃣ **config.py** → Shared Configuration
- All constants and settings
- Used by: All modules
- Example: `STOCK_CODE`, `TRADING_START_TIME`, API timeouts

### 2️⃣ **logger.py** → Structured Logging
- Consistent log formatting
- Log levels and styling
- Used by: All modules for logging

### 3️⃣ **auth.py** → Authentication & Tokens
```
Load Env → Request Token → Cache Token → Provide Token
   ↓           ↓              ↓             ↓
 (env        (Korea API)  (JSON file)  (to api_client)
  vars)
```

### 4️⃣ **api_client.py** → HTTP Communication
```
Input: Token, Endpoint, TR_ID, Params
         ↓
    Build Headers
         ↓
    [GET|POST] Request
         ↓
    Handle Response/Errors
         ↓
Output: JSON Response or None
```

### 5️⃣ **market_data.py** → Price Queries
```
Calls: api_client.get()
API: /uapi/domestic-stock/v1/quotations/inquire-price
Output: Current price (int) or None
Cache: stck_prpr field
```

### 6️⃣ **account.py** → Account & Holdings
```
Method 1: get_balance()
  ├─ API: /uapi/domestic-stock/v1/trading/inquire-account-balance
  └─ Output: AccountBalance (total_balance, available_cash, total_assets)

Method 2: get_holdings()
  ├─ API: /uapi/domestic-stock/v1/trading/inquire-balance
  └─ Output: List[StockHolding] with quantities, prices, valuations
```

### 7️⃣ **orders.py** → Order Management
```
place_order(BUY|SELL, stock_code, qty, price)
  ├─ API: /uapi/domestic-stock/v1/trading/order-cash
  ├─ Headers: TR_ID (VTTC0012U for buy, VTTC0011U for sell)
  └─ Output: Order with order_id and execution_status
```

### 8️⃣ **trader.py** → Trading Logic
```
┌─ is_trading_window_open() ─ Check 09:10-15:30
├─ get_order_prices() ─ Calculate buy/sell prices
├─ execute_trading_cycle() ─ One complete buy+sell
└─ run_trading_loop() ─ Main loop with retries
```

### 9️⃣ **main.py** → Orchestration
```
Parse Args
    ↓
Parse Account Number
    ↓
Create TokenManager → Authenticate
    ↓
Create APIClient
    ↓
Create Trader
    ↓
Verify Connection
    ↓
Run Trading Loop
```

---

## 🔐 Authentication Flow

```
①PROGRAM START
    ↓
②CHECK ENV VARS (GH_APPKEY, GH_APPSECRET)
    ↓
③CHECK TOKEN CACHE
    ├─ Cached? ─Yes → Use it
    └─ No/Expired → ④
    ↓
④REQUEST NEW TOKEN
    │ POST /oauth2/tokenP
    │ Params: appkey, appsecret
    ↓
⑤RECEIVE TOKEN
    │ access_token: "......"
    │ access_token_token_expired: "2026-03-25 12:00:00"
    ↓
⑥CACHE TOKEN
    │ Save to token_cache.json
    ↓
⑦USE TOKEN FOR ALL API CALLS
    │ Authorization: Bearer {token}
    ↓
⑧NEXT DAY: REPEAT ①-⑥
```

---

## 📋 API Endpoints Used

| Endpoint | Method | Purpose | Module |
|----------|--------|---------|--------|
| `/oauth2/tokenP` | POST | Get access token | auth.py |
| `/uapi/domestic-stock/v1/quotations/inquire-price` | GET | Get current price | market_data.py |
| `/uapi/domestic-stock/v1/trading/inquire-account-balance` | GET | Get account balance | account.py |
| `/uapi/domestic-stock/v1/trading/inquire-balance` | GET | Get holdings | account.py |
| `/uapi/domestic-stock/v1/trading/order-cash` | POST | Place order | orders.py |

---

## 🎯 Type Hints & Data Structures

### auth.py
```python
class TokenManager:
    token: Optional[str]
    token_expiry: Optional[datetime]
    load_credentials() → bool
    authenticate() → bool
    get_token() → Optional[str]
    is_valid() → bool
```

### api_client.py
```python
class APIClient:
    def get(endpoint: str, tr_id: str, params: Dict) → Optional[Dict]
    def post(endpoint: str, tr_id: str, payload: Dict) → Optional[Dict]
```

### market_data.py
```python
class MarketData:
    def get_current_price(stock_code: str) → Optional[int]  # KRW
```

### account.py
```python
@dataclass
class AccountBalance:
    total_balance: int
    available_cash: int
    total_assets: int

@dataclass
class StockHolding:
    stock_code: str
    quantity: int
    current_price: int
    total_value: int
    profit_loss: int

class Account:
    def get_balance() → Optional[AccountBalance]
    def get_holdings() → Optional[List[StockHolding]]
```

### orders.py
```python
class Order:
    order_type: OrderType  # BUY | SELL
    stock_code: str
    quantity: int
    price: int
    order_id: Optional[str]

class OrderManager:
    def place_order(...) → Optional[Order]
```

### trader.py
```python
class Trader:
    def is_trading_window_open() → bool
    def get_order_prices(current_price: int) → Tuple[int, int]
    def execute_trading_cycle() → bool
    def run_trading_loop(duration_minutes: int) → None
```

---

## 🔍 Error Handling Strategy

```
API Request
    ├─ Status 200? ─No → Check rt_cd
    │             └─ rt_cd="0"? → Success
    │             └─ Else → Error (log and return None)
    │
    ├─ Timeout? → Retry up to MAX_RETRIES with backoff
    │
    ├─ Network Error? → Log and return None
    │
    └─ Parse Error? → Log response, return None
```

---

## 📈 Minimizing API Calls

| Strategy | Savings |
|----------|---------|
| Token caching (same day) | ~10 requests/day |
| Price caching between checks | Variable |
| Conservative polling intervals | Depends on interval |
| Holdings cache after query | Avoids redundant calls |
| Selective account updates | Only on demand |

Example: 30-min polling = ~0.5 calls/min = 30 calls in full trading session

---

## 🧪 Testing Strategy

```
Unit Level:
├─ auth.py → Test token caching, refresh
├─ api_client.py → Test GET/POST, retry logic
├─ market_data.py → Test price parsing
├─ account.py → Test balance/holdings parsing
└─ orders.py → Test order placement response

Integration Level:
├─ main.py → Full initialization
├─ trader.py → Full trading cycle
└─ End-to-end → Run with --test-duration 5

Production Level:
└─ Run with --test-duration 1-5 before live trading
```

---

**System Created: 2026-03-25**  
**Total Lines of Code: ~1000 (production-ready)**  
**Time Complexity: O(1) per cycle**  
**Space Complexity: O(1) (basic data structures)**
