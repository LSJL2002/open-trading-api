# Samsung Electronics Auto Trader 🤖

A simple, modular automated trading system for Samsung Electronics (005930) using the **Korea Investment Open API** with Python and REST API only (no websocket).

## ⚠️ Important Warnings

- **MOCK TRADING ONLY**: This system is configured for mock trading (VTS environment)
- **DO NOT MODIFY** the `TRADING_ENV` setting to "real" without full understanding of the risks
- This is for educational and testing purposes only
- No financial advice; trading involves substantial risk of loss
- Past performance does not guarantee future results

---

## 🎯 Features

✅ **Mock Trading**: Safely test trading logic without real money  
✅ **Token Caching**: Reuses token for same day to minimize API calls  
✅ **Conservative Rate Limiting**: Long polling intervals to avoid API limits  
✅ **Structured Logging**: Comprehensive logging for all actions  
✅ **Modular Design**: Easy to understand, modify, and extend  
✅ **Production-Style Code**: Type hints, docstrings, error handling  
✅ **Trading Window**: Operates only 09:10 - 15:30 (Korean market hours)  

---

## 📋 Trading Logic

The system repeats the following trading cycle:

1. **Check Current Price** for Samsung Electronics (005930)
2. **Check Account Balance** and current holdings
3. **Place Buy Order** at `current_price - 2,000 KRW`
4. **Wait & Verify**: Check if buy order executed
5. **Place Sell Order** at `current_price + 2,000 KRW`
6. **Wait & Verify**: Check if sell order executed
7. **Rest**: Wait before next cycle
8. **Loop**: Repeat during trading window (09:10 - 15:30)

---

## 📁 Project Structure

```
samsung_auto_trader/
├── main.py                  # Entry point, orchestration
├── config.py               # All configuration & constants
├── auth.py                 # Authentication & token caching
├── api_client.py           # REST API wrapper
├── market_data.py          # Stock price queries
├── account.py              # Account balance & holdings
├── orders.py               # Order placement & tracking
├── trader.py               # Trading logic & loops
├── logger.py               # Structured logging
├── token_cache.json        # Token cache (auto-generated)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| **config.py** | Stock code, order amounts, trading hours, API settings, rate limits |
| **logger.py** | Structured logging with consistent formatting |
| **auth.py** | Load env vars, authenticate, cache token, validate |
| **api_client.py** | Low-level REST API (GET/POST, headers, error retry) |
| **market_data.py** | Fetch and cache current stock prices |
| **account.py** | Query account balance and stock holdings |
| **orders.py** | Place buy/sell orders, track status |
| **trader.py** | High-level trading logic and main loop |
| **main.py** | Initialize system, orchestrate components, run loop |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (3.10+ recommended)
- **Active Korea Investment Account** (demo/mock trading account)
- **API Credentials** (app key and secret)

### 1. Set Up Environment Variables

Export your Korea Investment API credentials:

```bash
export GH_APPKEY="your_app_key"
export GH_APPSECRET="your_app_secret"
export GH_ACCOUNT="12345678-01"       # Format: AAAAAAAA-PP (account-product)
```

**Account Format**:
- First 8 digits: Account number
- Last 2 digits: Product code (01 for stocks)
- Example: `12345678-01` or `1234567801`

**Where to find credentials**:
- Log in to [Korea Investment API Portal](https://apiportal.koreainvestment.com/)
- Go to "My Applications" → Your app
- Copy `App Key` and `App Secret`
- Copy your account number from the account info

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Only requires: `requests` library

### 3. Run the Trader

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
ORDER_PRICE_OFFSET_BUY = -2000           # Buy at price - 2000
ORDER_PRICE_OFFSET_SELL = 2000           # Sell at price + 2000
```

### Trading Window

```python
TRADING_START_TIME = time(9, 10)    # 09:10 AM
TRADING_END_TIME = time(15, 30)     # 03:30 PM
```

### Rate Limiting

```python
PRICE_POLL_INTERVAL_SECONDS = 30    # Check price every 30s
BALANCE_POLL_INTERVAL_SECONDS = 60  # Check balance every 60s
API_TIMEOUT_SECONDS = 10             # Timeout for API calls
```

### Logging

```python
LOG_LEVEL = "INFO"   # Can be DEBUG, INFO, WARNING, ERROR
```

---

## 📖 How to Use

### Starting a Trading Session

1. **Set up environment variables** (see above)
2. **Run the script**:
   ```bash
   python main.py
   ```
3. **Monitor the logs** for each trading cycle
4. **Check holdings and balance** in the logs
5. **Stop with Ctrl+C** when done

### Understanding the Logs

Each trading cycle shows:

```
======================================================================
🔄 Starting trading cycle...
======================================================================
💹 Current price: 70,000 KRW
📦 Holdings before order: 0 shares
💰 Balance: 5,000,000 KRW available
📍 Price offsets: Buy 68,000 (current 70,000 - 2000), Sell 72,000...
----------------------------------------------------------------------
📤 Placing BUY order: 1 shares of 005930 @ 68,000 KRW...
✅ API Response: 200 - GET /uapi/domestic-stock/v1/trading/order-cash
📤 Buy Order: Order ID: 12345, Status: 접수됨
⏳ Waiting 5s for buy order execution...
📦 Holdings after buy: 1 shares
✅ Buy order EXECUTED (+1 shares)
----------------------------------------------------------------------
📤 Placing SELL order: 1 shares of 005930 @ 72,000 KRW...
✅ API Response: 200 - POST /uapi/domestic-stock/v1/trading/order-cash
📤 Sell Order: Order ID: 12346, Status: 접수됨
⏳ Waiting 5s for sell order execution...
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
🔐 Token Issued: Token valid until 2026-03-26 12:00:00
```

Subsequent runs same day: Reuses cached token
```
🔐 Token Reused: Valid today (expires 2026-03-26 12:00:00)
```

---

## 🔧 Debugging

### Enable Debug Logging

Edit `config.py`:
```python
LOG_LEVEL = "DEBUG"
```

This shows:
- All HTTP requests and parameters
- Full API responses
- Cache data and token details

### Common Issues

**❌ "GH_ACCOUNT environment variable not set"**
- Export the account number: `export GH_ACCOUNT="12345678-01"`

**❌ "Credentials loaded failed"**
- Check `GH_APPKEY` and `GH_APPSECRET` are set correctly
- Verify they match your API credentials from the portal

**❌ "Token Request Failed"**
- Verify API credentials are correct
- Check internet connection
- Ensure you're using mock trading endpoint (29443 port)

**❌ "No response from API" / Price Query Failed**
- Might be outside trading hours (09:10 - 15:30)
- Check if market is open
- Verify internet connection

**❌ SSL/Certificate errors**
- The code disables SSL verification (`verify=False`) for mock trading
- This is safe for VTS environment but avoid in production

---

## 📈 Performance Tips

To minimize API calls:

1. **Increase poll intervals** in `config.py`:
   ```python
   PRICE_POLL_INTERVAL_SECONDS = 60  # 60 seconds instead of 30
   ```

2. **Reduce trading cycle frequency**:
   - The script naturally waits between cycles
   - Adjust `PRICE_POLL_INTERVAL_SECONDS` to control this

3. **Cache first**:
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
- Token cached locally in simple JSON (not encrypted - use separate data for prod)
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

### Manual Testing

1. **Test authentication**:
   ```python
   import auth
   mgr = auth.create_auth_manager()
   if mgr:
       print("✅ Auth successful:", mgr.get_token()[:20] + "...")
   ```

2. **Test API client**:
   ```python
   from api_client import APIClient
   client = APIClient("YOUR_TOKEN")
   response = client.get("/uapi/domestic-stock/v1/quotations/inquire-price", 
                         "FHKST01010100",
                         {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "005930"})
   print(response)
   ```

3. **Test market data**:
   ```python
   from market_data import MarketData
   market = MarketData(client)
   price = market.get_current_price("005930")
   print(f"Samsung price: {price:,} KRW")
   ```

---

## 📚 Related Documentation

- [Korea Investment Open API Portal](https://apiportal.koreainvestment.com/)
- [Korea Investment GitHub (Official Samples)](https://github.com/koreainvestment/open-trading-api)
- [Korea Exchange (KRX) Market Hours](https://www.krx.co.kr/)

---

## 📝 License

This is sample code for educational purposes. Use responsibly.

---

## ⚡ Quick Reference

| What | Command |
|------|---------|
| Run normally | `python main.py` |
| Test run (5 min) | `python main.py --test-duration 5` |
| Set credentials | `export GH_APPKEY="..."; export GH_APPSECRET="..."; export GH_ACCOUNT="..."` |
| Check logs | Look at console output |
| Enable debug | Edit `config.py`, set `LOG_LEVEL = "DEBUG"` |
| Change trading times | Edit `TRADING_START_TIME` and `TRADING_END_TIME` in `config.py` |

---

## 🤝 Contributing

To extend this system:

1. **Add new order types**: Edit `orders.py`, add methods to `OrderManager`
2. **Add technical indicators**: Create new module (e.g., `indicators.py`)
3. **Add risk limits**: Extend `config.py` and check in `trader.py`
4. **Add backtesting**: Create `backtest.py` module with simulated trading

---

## ❓ FAQ

**Q: Why only mock trading?**
A: It's safer for learning and testing. Modify `TRADING_ENV` in `config.py` to use real trading (but be very careful!).

**Q: Can I trade outside 09:10 - 15:30?**
A: The system will skip trading but keep running. Modify `TRADING_START_TIME`/`TRADING_END_TIME` in `config.py` to change.

**Q: What if the order doesn't execute?**
A: The system logs it and continues. Orders remain pending in the broker system. Check your account in Korea Investment app.

**Q: How often can I trade?**
A: Controlled by `PRICE_POLL_INTERVAL_SECONDS` in `config.py`. Default is 30 seconds between cycles.

**Q: What happens if the script crashes?**
A: Pending orders remain in your account (you must cancel them manually). Re-run the script to continue trading.

**Q: Can I modify order parameters?**
A: Yes! Edit `config.py`:
- `ORDER_QUANTITY`: Number of shares
- `ORDER_PRICE_OFFSET_BUY`: Price offset for buy
- `ORDER_PRICE_OFFSET_SELL`: Price offset for sell

**Q: What's the minimum balance needed?**
A: Depends on Samsung's current price. If price is 70,000 KRW and you buy 1 share, you need ~70,000 KRW + buffer.

---

**Created for Korea Investment Open API v1.0**  
**Last Updated: 2026-03-25**
