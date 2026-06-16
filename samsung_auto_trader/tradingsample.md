🔢 Cycle #9
2026-06-16 09:23:44,925 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-16 09:23:44,925 | INFO | trader | execute_trading_cycle | 🔄 Starting trading cycle (Realistic Order Matching)...
2026-06-16 09:23:44,925 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-16 09:23:44,925 | INFO | market_data | get_current_price | 📊 Fetching real-time price for 005930 using TR_ID: FHKST01010100...
/home/codespace/.local/lib/python3.12/site-packages/urllib3/connectionpool.py:1097: InsecureRequestWarning: Unverified HTTPS request is being made to host 'openapivts.koreainvestment.com'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
  warnings.warn(
2026-06-16 09:23:49,760 | INFO | api_client | log_api_response | ✅ API Response: 200 - GET /uapi/domestic-stock/v1/quotations/inquire-price
2026-06-16 09:23:49,761 | INFO | market_data | get_current_price | 💹 Real-time price fetched: 339,250 KRW ✓
2026-06-16 09:23:49,761 | INFO | trader | execute_trading_cycle | ----------------------------------------------------------------------
2026-06-16 09:23:49,761 | INFO | account | get_holdings | 📦 Mock trading: Returning tracked holdings
2026-06-16 09:23:49,761 | INFO | account | get_holdings | 📊 No holdings found
2026-06-16 09:23:49,761 | INFO | trader | execute_trading_cycle | 📦 Holdings before order: 0 shares
2026-06-16 09:23:49,761 | INFO | account | get_balance | 💰 Mock trading: Using tracked balance
2026-06-16 09:23:49,761 | INFO | account | get_balance | 💵 Balance: 10,000,000 KRW available, 10,000,000 KRW total (Holdings: 0 shares)
2026-06-16 09:23:49,762 | INFO | trader | get_order_prices_from_momentum | 📍 Momentum-based orders: Buy 337,500 (low 338,000), Sell 340,000 (high 339,500) | Signal: uptrend (+0.37%)
2026-06-16 09:23:49,762 | INFO | trader | execute_trading_cycle | 📈 Momentum: uptrend - Placing BUY at 337,500 KRW
2026-06-16 09:23:49,762 | INFO | orders | place_order | 📤 Mock trading: BUY order: 1 shares of 005930 @ 337,500 KRW...
2026-06-16 09:23:49,762 | INFO | orders | log_trading_action | 🔄 BUY Order: Order ID: MOCK00001, Status: 완료 (MOCK - EXECUTED)
2026-06-16 09:23:49,762 | INFO | trader | execute_trading_cycle | ⏳ Waiting 5s for buy order execution...
2026-06-16 09:23:54,762 | INFO | account | get_holdings | 📦 Mock trading: Returning tracked holdings
2026-06-16 09:23:54,762 | INFO | account | get_holdings | 📊 Holding: Samsung Electronics (Mock) (005930) x1 @ 70,000 KRW (Value: 70,000 KRW, P/L: -267,500 KRW)
2026-06-16 09:23:54,762 | INFO | trader | execute_trading_cycle | 📦 Holdings after buy: 1 shares
2026-06-16 09:23:54,762 | INFO | trader | execute_trading_cycle | ✅ Buy order EXECUTED at 337,500 (+1 shares)
2026-06-16 09:23:54,762 | INFO | trader | execute_trading_cycle | ----------------------------------------------------------------------
2026-06-16 09:23:54,762 | INFO | trader | execute_trading_cycle | 📉 Placing SELL order as PENDING: 340,000 KRW
2026-06-16 09:23:54,763 | INFO | trader | execute_trading_cycle |    Current profit target: +2,500 KRW per share
2026-06-16 09:23:54,763 | INFO | orders | place_order | 📤 Mock trading: SELL order: 1 shares of 005930 @ 340,000 KRW...
2026-06-16 09:23:54,763 | INFO | account | place_pending_sell_order | 📋 Pending sell order placed: 1 shares (bought @ 337,500, target sell @ 340,000)
2026-06-16 09:23:54,763 | INFO | orders | log_trading_action | 🔄 SELL Order: Order ID: MOCK00002, Status: 대기 (MOCK - PENDING)
2026-06-16 09:23:54,763 | INFO | trader | execute_trading_cycle | ⏳ Stock held at 1 shares, waiting for price to reach 340,000...
2026-06-16 09:23:54,763 | INFO | account | get_balance | 💰 Mock trading: Using tracked balance
2026-06-16 09:23:54,763 | INFO | account | get_balance | 💵 Balance: 9,662,500 KRW available, 9,732,500 KRW total (Holdings: 1 shares)
2026-06-16 09:23:54,763 | INFO | trader | execute_trading_cycle | 💵 Balance: 9,662,500 KRW available
2026-06-16 09:23:54,763 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-16 09:23:54,763 | INFO | trader | execute_trading_cycle | ✅ Buy placed, sell pending (waiting for market price)
2026-06-16 09:23:54,763 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-16 09:23:54,763 | INFO | trader | run_trading_loop | ⏳ Waiting 15s until next cycle...
2026-06-16 09:24:09,763 | INFO | trader | log_trading_window | 🟢 Trading window at 09:24:09: OPEN ✅
2026-06-16 09:24:09,764 | INFO | trader | run_trading_loop | 
🔢 Cycle #10
2026-06-16 09:24:09,764 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-16 09:24:09,764 | INFO | trader | execute_trading_cycle | 🔄 Starting trading cycle (Realistic Order Matching)...
2026-06-16 09:24:09,764 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-16 09:24:09,764 | INFO | market_data | get_current_price | 📊 Fetching real-time price for 005930 using TR_ID: FHKST01010100...
/home/codespace/.local/lib/python3.12/site-packages/urllib3/connectionpool.py:1097: InsecureRequestWarning: Unverified HTTPS request is being made to host 'openapivts.koreainvestment.com'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
  warnings.warn(
2026-06-16 09:24:10,011 | INFO | api_client | log_api_response | ✅ API Response: 200 - GET /uapi/domestic-stock/v1/quotations/inquire-price
2026-06-16 09:24:10,013 | INFO | market_data | get_current_price | 💹 Real-time price fetched: 340,000 KRW ✓
2026-06-16 09:24:10,013 | INFO | trader | execute_trading_cycle | ----------------------------------------------------------------------
2026-06-16 09:24:10,013 | INFO | trader | execute_trading_cycle | 📋 Pending sell order waiting: 1 shares @ 340,000
2026-06-16 09:24:10,013 | INFO | trader | execute_trading_cycle |    Current price: 340,000 KRW
2026-06-16 09:24:10,013 | INFO | trader | execute_trading_cycle |    Target price: 340,000 KRW (bought @ 337,500)
2026-06-16 09:24:10,014 | INFO | trader | execute_trading_cycle | ✅ Price reached target! Executing pending sell at 340,000
2026-06-16 09:24:10,014 | INFO | account | execute_pending_sell_order | 💰 Pending sell order EXECUTED at 340,000: 1 shares, Profit: 2,500 KRW
2026-06-16 09:24:10,014 | INFO | trader | execute_trading_cycle | 💰 SOLD at 340,000 KRW
2026-06-16 09:24:10,014 | INFO | trader | execute_trading_cycle | 💰 Trade profit: 2,500 KRW
2026-06-16 09:24:10,014 | INFO | trader | execute_trading_cycle | 📈 Total profit: 2,500 KRW (1 trades)
2026-06-16 09:24:10,014 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-16 09:24:10,014 | INFO | trader | run_trading_loop | ⏳ Waiting 15s until next cycle...
^C2026-06-16 09:24:18,945 | INFO | trader | run_trading_loop | 
🛑 Trading stopped by user
2026-06-16 09:24:18,945 | INFO | trader | run_trading_loop | ======================================================================
2026-06-16 09:24:18,945 | INFO | trader | run_trading_loop | 📊 Trading session ended
2026-06-16 09:24:18,945 | INFO | trader | run_trading_loop | ⏱️  Total duration: 3.0 minutes
2026-06-16 09:24:18,945 | INFO | trader | run_trading_loop | 🔢 Total cycles executed: 10
2026-06-16 09:24:18,945 | INFO | trader | run_trading_loop | ✔️  Completed trades: 1
2026-06-16 09:24:18,945 | INFO | trader | run_trading_loop | ======================================================================
2026-06-16 09:24:18,945 | INFO | trader | run_trading_loop | 💹 TOTAL PROFIT: 2,500 KRW 📈
2026-06-16 09:24:18,945 | INFO | trader | run_trading_loop | ======================================================================