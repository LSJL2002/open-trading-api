# Samsung Electronics Auto Trader - Quick Start Guide

## 🎯 In 3 Minutes

### 1️⃣ Set Your Credentials (1 minute)

Open a terminal and set these environment variables (or map GitHub Secrets in CI):

```bash
# Local run
export GH_APPKEY="your_api_key_here"
export GH_APPSECRET="your_api_secret_here"
export GH_ACCOUNT="12345678-01"

# GitHub Actions example (in workflow YAML):
#   env:
#     GH_APPKEY: ${{ secrets.GH_APPKEY }}
#     GH_APPSECRET: ${{ secrets.GH_APPSECRET }}
#     GH_ACCOUNT: ${{ secrets.GH_ACCOUNT }}
```

Where:
- `GH_APPKEY` and `GH_APPSECRET`: Get from [Korea Investment API Portal](https://apiportal.koreainvestment.com/)
- `GH_ACCOUNT`: Your account number (format: 8-digit account + 2-digit product code)

### 2️⃣ Install & Test (1 minute)

```bash
# Navigate to the project
cd samsung_auto_trader

# Install dependencies
pip install -r requirements.txt

# Test with a 5-minute run (before going live)
python main.py --test-duration 5
```

### 3️⃣ Run Live (1 minute)

```bash
# Run until market closes (15:30)
python main.py

# Trade will start at 09:10 and stop at 15:30 automatically
# Press Ctrl+C to stop anytime
```

---

## 📊 What Happens

The system will:

1. **Check current price** of Samsung Electronics (005930)
2. **Place a BUY order** at `current_price - 2,000 KRW`
3. **Place a SELL order** at `current_price + 2,000 KRW`
4. **Verify execution** by checking holdings
5. **Repeat** every 30 seconds (configurable)
6. **Stop automatically** at 15:30 (market close)

Example output:
```
📊 Currently price: 70,000 KRW
📤 Placing BUY order: 1 shares @ 68,000 KRW
✅ Buy order EXECUTED
📤 Placing SELL order: 1 shares @ 72,000 KRW
✅ Sell order EXECUTED
```

---

## 🔧 Customization

Edit `config.py` to change:

```python
# What to trade
STOCK_CODE = "005930"          # Change to different stock
ORDER_QUANTITY = 1              # Shares per order
ORDER_PRICE_OFFSET_BUY = -2000  # Buy 2000 below current
ORDER_PRICE_OFFSET_SELL = 2000  # Sell 2000 above current

# When to trade
TRADING_START_TIME = time(9, 10)   # Start at 09:10
TRADING_END_TIME = time(15, 30)    # Stop at 15:30

# How often
PRICE_POLL_INTERVAL_SECONDS = 30   # Check every 30s
```

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| "GH_ACCOUNT not set" | Run: `export GH_ACCOUNT="12345678-01"` |
| "Credentials load failed" | Check GH_APPKEY and GH_APPSECRET are correct |
| "Token Request Failed" | Verify API credentials and internet connection |
| "No price returned" | Check if market is open (09:10 - 15:30 KST) |
| "API Timeout" | Market might be busy; script will retry automatically |

---

## 📚 Full Documentation

See `README.md` for:
- Complete module descriptions
- API details
- Advanced configuration
- Security considerations
- FAQ

---

## ⚡ Key Features

✅ **Token Caching**: Reuses token entire day (no re-auth needed)  
✅ **Rate Limited**: Conservative polling to avoid API limits  
✅ **Modular**: Well-organized code, easy to extend  
✅ **Logged**: Every action is logged with timestamps  
✅ **Production-ready**: Type hints, error handling, docstrings  
✅ **Safe**: Mock trading only by default  

---

## 🚨 Important

- ⚠️ **MOCK TRADING ONLY** - configured for virtual trading (VTS)
- ❌ **DO NOT CHANGE** `TRADING_ENV` to "real" without understanding risks
- 🔐 **NEVER commit credentials** to version control
- 💾 **Token caches locally** in `token_cache.json` - keep it private
- 📋 **Check pending orders** in your Korea Investment account manually

---

Created for Korea Investment Open API | Safe to use for testing
