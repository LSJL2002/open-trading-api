# Samsung Auto Trader - Python Files Guide

This document describes the purpose and functionality of each Python file in the Samsung Auto Trader project.

---

## Core Application Files

### `main.py`
**Purpose:** Entry point for the trading application

**Key Functions:**
- Parses command-line arguments and account numbers
- Orchestrates initialization sequence:
  1. Load configuration
  2. Authenticate with Korea Investment API
  3. Initialize API client
  4. Initialize trader
  5. Start trading loop
- Handles graceful shutdown and error recovery
- Supports test duration argument (`--test-duration`)

**Key Entry Point:**
- Run with `python main.py` to start auto-trading
- Requires environment variables: `GH_APPKEY`, `GH_APPSECRET`, `GH_ACCOUNT`

---

### `trader.py`
**Purpose:** Core trading logic and orchestration

**Key Responsibilities:**
- Coordinates all trading components (market data, account, orders)
- Implements the main trading loop that:
  - Checks if market is within trading window (9:10 AM - 3:30 PM)
  - Monitors Samsung Electronics (005930) stock price
  - Places buy orders at (current price - 2,000 KRW)
  - Places sell orders at (current price + 2,000 KRW)
- Executes trading cycles with 30-second polling intervals
- Tracks trading session metrics (duration, cycles executed)
- Provides error handling and logging for each cycle

**Key Methods:**
- `run_trading_loop()` - Main infinite loop that runs trading cycles
- `execute_trading_cycle()` - Single trading iteration
- `is_trading_window_open()` - Validates if within trading hours

---

## API & Authentication

### `api_client.py`
**Purpose:** Low-level REST API client for Korea Investment Open API

**Key Responsibilities:**
- Manages HTTP GET/POST requests to Korea Investment API
- Builds request headers with proper authentication
- Handles two trading environments:
  - Demo (VTS): `https://openapivts.koreainvestment.com:29443`
  - Real: `https://openapi.koreainvestment.com:9443`
- Implements response parsing and error handling
- Supports retry logic for failed requests

**Key Methods:**
- `get()` - Sends GET requests
- `post()` - Sends POST requests
- `_get_headers()` - Constructs authentication headers

---

### `auth.py`
**Purpose:** Authentication and token management

**Key Responsibilities:**
- Loads API credentials from environment variables (supports multiple naming conventions)
- Manages token acquisition from Korea Investment API
- Implements token caching to same-day reuse (`token_cache.json`)
- Validates token expiry
- Minimizes API calls by checking token validity before requesting new ones

**Key Class:** `TokenManager`
**Key Methods:**
- `load_credentials()` - Retrieves app key and secret from environment
- `authenticate()` - Requests new access token
- `_load_token_from_cache()` - Retrieves cached token
- `_save_token_to_cache()` - Stores token for reuse

---

## Account & Market Data

### `account.py`
**Purpose:** Account management and balance/holding queries

**Key Responsibilities:**
- Fetches account balance and available cash
- Retrieves current stock holdings
- Parses and formats account data
- Provides account information for trading decisions

**Key Classes:**
- `AccountBalance` - Dataclass for balance information (total balance, available cash, total assets)
- `StockHolding` - Dataclass for individual stock holdings (code, name, quantity, prices, P&L)
- `Account` - Main class that queries API and manages account data

**Key Methods:**
- `get_balance()` - Fetches current account balance
- `get_holdings()` - Retrieves all stock holdings
- `get_samsung_holding()` - Queries Samsung Electronics holding specifically

---

### `market_data.py`
**Purpose:** Market data queries (stock prices)

**Key Responsibilities:**
- Fetches current stock prices from Korea Investment API
- Caches prices to minimize API calls
- Provides dummy price (70,000 KRW) for mock trading when API is unavailable
- Tracks last price and retrieval time

**Key Class:** `MarketData`
**Key Methods:**
- `get_current_price()` - Retrieves current stock price for given code
- Returns `None` if API request fails

---

### `orders.py`
**Purpose:** Order placement and tracking

**Key Responsibilities:**
- Places buy and sell orders via Korea Investment API
- Tracks order execution status
- Verifies order fills
- Manages order metadata

**Key Classes:**
- `OrderType` - Enum for BUY/SELL order types
- `Order` - Dataclass containing order details (type, stock code, quantity, price, order ID, status)
- `OrderManager` - Main class for order operations

**Key Methods:**
- `place_buy_order()` - Places a buy order at specified price
- `place_sell_order()` - Places a sell order at specified price
- `get_order_status()` - Queries order execution status

---

## Configuration & Utilities

### `config.py`
**Purpose:** Centralized configuration and constants

**Key Settings:**
- **Trading Target:** Samsung Electronics (005930)
- **Environment:** Demo trading (mock mode)
- **Order Configuration:** 
  - Buy offset: -2,000 KRW (buy below current price)
  - Sell offset: +2,000 KRW (sell above current price)
  - Order quantity: 1 share per order
- **Trading Window:** 9:10 AM - 3:30 PM KST
- **API Rate Limiting:** 
  - Price poll interval: 30 seconds
  - Balance poll interval: 60 seconds
- **File Paths:** Token cache, log files

**Usage:** Import constants to avoid hard-coding values throughout the application

---

### `logger.py`
**Purpose:** Structured logging for the application

**Key Responsibilities:**
- Provides consistent logging format across all modules
- Configures log level and output format
- Helper functions for common logging patterns (API calls, errors, etc.)

**Key Functions:**
- `setup_logger()` - Creates and returns configured logger instance
- Helper functions for domain-specific logging

**Format:**
```
TIMESTAMP | LEVEL | MODULE | FUNCTION | MESSAGE
```

Example:
```
2026-04-10 13:58:00,978 | INFO | trader | run_trading_loop | 🚀 SAMSUNG ELECTRONICS AUTO TRADER STARTED
```

---

## File Dependencies Diagram

```
main.py
├── config.py (settings)
├── logger.py (logging)
├── auth.py (authentication)
│   └── api_client.py
├── api_client.py (API communication)
└── trader.py (core logic)
    ├── market_data.py
    │   └── api_client.py
    ├── account.py
    │   └── api_client.py
    └── orders.py
        └── api_client.py
```

---

## Quick Reference: What Each File Does

| File | Purpose | Tier |
|------|---------|------|
| `main.py` | Application entry point | Application |
| `trader.py` | Trading loop and logic | Business Logic |
| `market_data.py` | Stock price queries | Business Logic |
| `account.py` | Balance and holdings | Business Logic |
| `orders.py` | Order placement | Business Logic |
| `api_client.py` | HTTP API communication | Infrastructure |
| `auth.py` | Token and authentication | Infrastructure |
| `config.py` | Settings and constants | Configuration |
| `logger.py` | Logging system | Utilities |

