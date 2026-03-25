# Samsung Electronics Auto Trader - Implementation Guide

## 📍 Complete Step-by-Step Setup

### Phase 1: Preparation (5 minutes)

#### Step 1.1: Get Korea Investment API Credentials

1. Go to [Korea Investment API Portal](https://apiportal.koreainvestment.com/)
2. Sign up or sign in with your account
3. Create a virtual account for mock trading (VTS - Virtual Trading System)
4. Go to "My Applications" → Create New Application
5. Copy and save:
   - **App Key** (e.g., `ABC1234567`)
   - **App Secret** (e.g., `XYZ9876543`)
6. Find your account number (e.g., `12345678-01`)

#### Step 1.2: Verify Your System

Open terminal and check:

```bash
# Check Python version (need 3.8+)
python3 --version

# Check pip is available
pip3 --version

# Navigate to project
cd /workspaces/open-trading-api/samsung_auto_trader
```

---

### Phase 2: Configuration (3 minutes)

#### Step 2.1: Set Environment Variables

In your terminal session, set the credentials:

```bash
# Option A: One-time in current terminal
export GH_APPKEY="ABC1234567"
export GH_APPSECRET="XYZ9876543"
export GH_ACCOUNT="12345678-01"

# Option B: Persistent (add to ~/.bashrc or ~/.bash_profile)
echo 'export GH_APPKEY="ABC1234567"' >> ~/.bashrc
echo 'export GH_APPSECRET="XYZ9876543"' >> ~/.bashrc
echo 'export GH_ACCOUNT="12345678-01"' >> ~/.bashrc
source ~/.bashrc
```

#### Step 2.2: Verify Environment Variables

```bash
# Check they're set
echo $GH_APPKEY
echo $GH_APPSECRET
echo $GH_ACCOUNT
```

#### Step 2.3: Review Configuration (Optional)

Edit `config.py` to customize trading:

```python
# Trading parameters
STOCK_CODE = "005930"              # Stock to trade
ORDER_QUANTITY = 1                 # Shares per order
ORDER_PRICE_OFFSET_BUY = -2000     # Buy 2000 below
ORDER_PRICE_OFFSET_SELL = 2000     # Sell 2000 above

# Trading window (9:10 AM - 3:30 PM KST)
TRADING_START_TIME = time(9, 10)
TRADING_END_TIME = time(15, 30)

# Polling interval (seconds between cycles)
PRICE_POLL_INTERVAL_SECONDS = 30
```

---

### Phase 3: Installation (2 minutes)

#### Step 3.1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs only:
- `requests==2.31.0` (for HTTP calls)

#### Step 3.2: Verify Installation

```bash
python3 -c "import requests; print('✅ Requests library imported successfully')"
```

---

### Phase 4: Testing (5-10 minutes)

#### Step 4.1: Test Run (Limited Duration)

```bash
# Run the system for only 5 minutes to test
python main.py --test-duration 5
```

What you should see:
- ✅ Credentials loaded
- ✅ Token acquired or cached
- ✅ API client initialized
- ✅ Trader initialized
- ✅ Current price fetched
- ✅ Trading cycles executed

#### Step 4.2: Check Logs

Look for successful messages like:
```
✅ Credentials loaded from environment variables
🔐 Token Issued: Token valid until 2026-03-25 12:00:00
✅ API client ready
📊 Current price: 70,000 KRW
🔄 Trading cycle started
✅ Buy order EXECUTED
✅ Sell order EXECUTED
```

#### Step 4.3: Troubleshoot (If Needed)

| Error | Solution |
|-------|----------|
| `GH_APPKEY` not set | Run: `export GH_APPKEY="..."`|
| Token request failed | Check appkey and appsecret are correct |
| No price returned | Check if market is open (09:10-15:30 KST) |
| API timeout | Network issue; script will retry |
| Parse errors | Check API response format hasn't changed |

---

### Phase 5: Live Trading (Ongoing)

#### Step 5.1: Run the Live Trader

```bash
# Run until market closes (15:30) automatically
python main.py
```

#### Step 5.2: Monitor Trading

The system will:

1. **09:10-09:15**: Print startup logs
   ```
   🚀 SAMSUNG ELECTRONICS AUTO TRADER STARTED
   📅 Trading window: 09:10:00 - 15:30:00
   🎯 Target: Samsung Electronics (삼성전자) (005930)
   ```

2. **09:10-15:30**: Execute trading cycles every ~30 seconds
   ```
   🔄 Cycle #1
   💹 Current price: 70,000 KRW
   📤 Placing BUY order: 1 shares @ 68,000 KRW
   ✅ Buy order EXECUTED (+1 shares)
   📤 Placing SELL order: 1 shares @ 72,000 KRW
   ✅ Sell order EXECUTED (-1 shares)
   ```

3. **After 15:30**: Stop trading automatically
   ```
   🔴 Trading window closed, waiting for next session...
   ⏱️  Test duration exceeded, stopping
   📊 Trading session ended
   ```

#### Step 5.3: Stop Trading Manually

Press `Ctrl+C` at any time to stop:
```
^C
🛑 Trading stopped by user
```

---

### Phase 6: Monitoring & Maintenance (Daily)

#### Step 6.1: Daily Check

Before running trading:

```bash
# Set credentials (if not in ~/.bashrc)
export GH_APPKEY="..."
export GH_APPSECRET="..."
export GH_ACCOUNT="..."

# Run a quick test
python main.py --test-duration 2

# If successful, run live
python main.py
```

#### Step 6.2: Token Caching

First run of the day:
- System requests new token from API
- Saves to `token_cache.json`
- Takes ~1 second longer

Subsequent runs of the day:
- System reuses cached token
- Skips API request
- Instant startup

#### Step 6.3: Check Pending Orders

If trading stops unexpectedly, check your Korea Investment app:
- Go to "주문" (Orders)
- Look for pending orders on 005930
- Cancel manually if needed

---

## 📊 Sample Output - First Run

```
======================================================================
🚀 Samsung Electronics Auto Trader Initialization
======================================================================
📍 Target Stock: Samsung Electronics (삼성전자) (005930)
🌐 Environment: DEMO Trading (Mock)
⏰ Trading Window: 09:10:00 - 15:30:00

📋 Step 1: Loading configuration...
✅ Account: 12345678-01

🔐 Step 2: Authenticating with Korea Investment API...
Requesting new access token...
✅ Authentication successful
🔐 Token Issued: Token valid until 2026-03-25 12:00:00

📡 Step 3: Initializing API client...
✅ API client ready

🤖 Step 4: Initializing trader...
✅ Trader initialized for 005930

✅ Step 5: Verifying connection (getting current price)...
📊 Fetching current price for 005930...
💹 Current price: 70,000 KRW
✅ Connection verified. Current price: 70,000 KRW

🔄 Step 6: Starting trading loop...
Press Ctrl+C to stop trading at any time

======================================================================
🚀 SAMSUNG ELECTRONICS AUTO TRADER STARTED
======================================================================
📍 Target Stock: Samsung Electronics (삼성전자) (005930)
🌐 Environment: DEMO Trading (Mock)
⏰ Trading Window: 09:10:00 - 15:30:00
💹 Buy offset: -2000 KRW
💹 Sell offset: 2000 KRW
⏱️  Poll interval: 30s
======================================================================

🟢 Trading window at 09:11:45: OPEN ✅

🔢 Cycle #1
======================================================================
🔄 Starting trading cycle...
======================================================================
📊 Fetching current price for 005930...
💹 Current price: 70,000 KRW
📦 Fetching holdings for account 12345678...
📦 Holdings before order: 0 shares
💰 Fetching account balance...
💵 Balance: 5,000,000 KRW available, 5,000,000 KRW total
----------------------------------------------------------------------
📤 Placing BUY order: 1 shares of 005930 @ 68,000 KRW...
📡 API GET /uapi/domestic-stock/v1/trading/order-cash
✅ API Response: 200 - GET /uapi/domestic-stock/v1/trading/order-cash
📤 Buy Order: Order ID: 19940523, Status: 접수됨
⏳ Waiting 5s for buy order execution...
📦 Fetching holdings for account 12345678...
📦 Holdings before order: 1 shares
✅ Buy order EXECUTED (+1 shares)
----------------------------------------------------------------------
📤 Placing SELL order: 1 shares of 005930 @ 72,000 KRW...
📡 API GET /uapi/domestic-stock/v1/trading/order-cash
✅ API Response: 200 - POST /uapi/domestic-stock/v1/trading/order-cash
📤 Sell Order: Order ID: 19940524, Status: 접수됨
⏳ Waiting 5s for sell order execution...
📦 Fetching holdings for account 12345678...
💰 Fetching account balance...
💵 Balance: 5,000,004 KRW available, 5,000,004 KRW total
======================================================================
✅ Trading cycle completed
======================================================================

⏳ Waiting 30s until next cycle...
```

---

## 🔍 Understanding the Logs

### Log Levels & Icons

| Icon | Type | Meaning |
|------|------|---------|
| 🟢 | Status | Trading window open |
| 🔴 | Status | Trading window closed |
| ✅ | Success | Operation succeeded |
| ❌ | Error | Operation failed |
| ⚠️  | Warning | Potential issue, continuing |
| 🔐 | Auth | Token operation |
| 💹 | Data | Price information |
| 💰 | Account | Balance/holdings update |
| 📤 | Order | Order placed |
| ⏳ | Wait | Waiting for something |
| 📊| Query | API query executed |
| 🤖 | System | System status |
| 🔄 | Action | Action execution |

---

## 🚨 Safety Checklist Before Live Trading

Before running with real money (DO NOT DO WITHOUT READING DOCS):

- [ ] Credentials tested with mock trading
- [ ] `TRADING_ENV` is still set to `"demo"` (NOT `"real"`!)
- [ ] Trading hours are correct for your timezone
- [ ] Order quantities seem reasonable
- [ ] You understand the trading logic
- [ ] You've tested with `--test-duration` flag
- [ ] You have monitoring set up
- [ ] You can stop trading quickly if needed
- [ ] You've read all documentation

---

## 📈 Next Steps

After successful test run:

1. **Monitor first live session**: Watch logs for 30 minutes
2. **Check account**: Verify orders in Korea Investment app
3. **Adjust parameters**: Fine-tune trading settings if needed
4. **Schedule daily run**: Could use `cron` for automatic execution
5. **Extend functionality**: Add indicators, risk limits, etc.

---

## 📚 Documentation Reference

| Document | Purpose |
|----------|---------|
| **README.md** | Complete reference guide |
| **QUICKSTART.md** | 3-minute quick start |
| **ARCHITECTURE.md** | System design & data flow |
| **This file** | Step-by-step setup |

---

**Ready to trade? Run:**

```bash
python main.py --test-duration 5  # Test first!
```

Then:

```bash
python main.py                     # Live trading!
```

Good luck! 🚀
