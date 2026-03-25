"""
Configuration and constants for Samsung Auto Trader.

This module centralizes all configuration settings to make the system
easy to modify without touching the business logic.
"""

from datetime import time
from typing import Final

# ============================================================================
# Trading Target
# ============================================================================
STOCK_CODE: Final[str] = "005930"  # Samsung Electronics
STOCK_NAME: Final[str] = "Samsung Electronics (삼성전자)"

# ============================================================================
# Trading Environment
# ============================================================================
# "real" for live trading, "demo" for mock trading
TRADING_ENV: Final[str] = "demo"  # ⚠️ ALWAYS use "demo" for mock trading

# Exchange ID
EXCHANGE_ID: Final[str] = "KRX"  # Korea Exchange

# ============================================================================
# Order Configuration
# ============================================================================
ORDER_PRICE_OFFSET_BUY: Final[int] = -2000   # Buy at price - 2000 KRW
ORDER_PRICE_OFFSET_SELL: Final[int] = 2000   # Sell at price + 2000 KRW
ORDER_QUANTITY: Final[int] = 1               # Buy/sell 1 share per order

# Order division (주문구분)
# 00: 지정가주문 (limit order)
ORDER_DIVISION: Final[str] = "00"

# ============================================================================
# Trading Window (Korean Market Hours)
# ============================================================================
TRADING_START_TIME: Final[time] = time(9, 10)    # 09:10 AM
TRADING_END_TIME: Final[time] = time(15, 30)     # 03:30 PM (15:30)

# ============================================================================
# API Rate Limiting
# ============================================================================
# Conservative polling intervals to avoid hitting rate limits
# Mock trading has strict request limits, so we use long intervals
PRICE_POLL_INTERVAL_SECONDS: Final[int] = 30      # Check price every 30s
BALANCE_POLL_INTERVAL_SECONDS: Final[int] = 60    # Check balance every 60s
MARKET_DATA_POLL_INTERVAL_SECONDS: Final[int] = 5 # After order, quick check

# Timeout for API calls (seconds)
API_TIMEOUT_SECONDS: Final[int] = 10

# ============================================================================
# Token Caching
# ============================================================================
TOKEN_CACHE_FILE: Final[str] = "token_cache.json"

# ============================================================================
# Logging
# ============================================================================
LOG_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s"
)
LOG_LEVEL: Final[str] = "INFO"  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL

# ============================================================================
# Market Code
# ============================================================================
# FID_COND_MRKT_DIV_CODE for inquire_price API
# J: KRX (Korea Exchange)
MARKET_DIV_CODE: Final[str] = "J"

# ============================================================================
# API Parameters for inquire_balance (account holdings)
# ============================================================================
# inqr_dvsn: 02 = inquiry by stock
BALANCE_INQR_DVSN: Final[str] = "02"

# unpr_dvsn: 01 = standard price
BALANCE_UNPR_DVSN: Final[str] = "01"

# afhr_flpr_yn: N = standard, Y = afterhours, X = NXT
BALANCE_AFHR_FLPR_YN: Final[str] = "N"

# fund_sttl_icld_yn: N = exclude fund settlement
BALANCE_FUND_STTL: Final[str] = "N"

# fncg_amt_auto_rdpt_yn: N = do not auto repay financing
BALANCE_FNCG_AUTO_RDPT: Final[str] = "N"

# prcs_dvsn: 00 = include previous day's transactions
BALANCE_PRCS_DVSN: Final[str] = "00"

# ============================================================================
# Retry Logic
# ============================================================================
MAX_RETRIES: Final[int] = 3
RETRY_BACKOFF_SECONDS: Final[int] = 2  # Exponential backoff multiplier
