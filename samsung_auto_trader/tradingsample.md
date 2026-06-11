2026-06-11 10:24:23,525 | INFO | market_data | get_current_price | 💹 Real-time price fetched: 302,000 KRW ✓
2026-06-11 10:24:23,525 | INFO | trader | execute_trading_cycle | ----------------------------------------------------------------------
2026-06-11 10:24:23,525 | INFO | trader | execute_trading_cycle | 📋 Pending sell order waiting: 1 shares @ 301,500
2026-06-11 10:24:23,525 | INFO | trader | execute_trading_cycle |    Current price: 302,000 KRW
2026-06-11 10:24:23,525 | INFO | trader | execute_trading_cycle |    Target price: 301,500 KRW (bought @ 299,000)
2026-06-11 10:24:23,525 | INFO | trader | execute_trading_cycle | ✅ Price reached target! Executing pending sell at 302,000
2026-06-11 10:24:23,525 | INFO | account | execute_pending_sell_order | 💰 Pending sell order EXECUTED at 302,000: 1 shares, Profit: 3,000 KRW
2026-06-11 10:24:23,526 | INFO | trader | execute_trading_cycle | 💰 SOLD at 302,000 KRW
2026-06-11 10:24:23,526 | INFO | trader | execute_trading_cycle | 💰 Trade profit: 3,000 KRW
2026-06-11 10:24:23,526 | INFO | trader | execute_trading_cycle | 📈 Total profit: 3,000 KRW (1 trades)
2026-06-11 10:24:23,526 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-11 10:24:23,526 | INFO | trader | run_trading_loop | ⏳ Waiting 15s until next cycle...
2026-06-11 10:24:38,526 | INFO | trader | log_trading_window | 🟢 Trading window at 10:24:38: OPEN ✅
2026-06-11 10:24:38,526 | INFO | trader | run_trading_loop | 
🔢 Cycle #9
2026-06-11 10:24:38,526 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-11 10:24:38,526 | INFO | trader | execute_trading_cycle | 🔄 Starting trading cycle (Realistic Order Matching)...
2026-06-11 10:24:38,526 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-11 10:24:38,526 | INFO | market_data | get_current_price | 📊 Fetching real-time price for 005930 using TR_ID: FHKST01010100...
/home/codespace/.local/lib/python3.12/site-packages/urllib3/connectionpool.py:1097: InsecureRequestWarning: Unverified HTTPS request is being made to host 'openapivts.koreainvestment.com'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
  warnings.warn(
2026-06-11 10:24:38,776 | INFO | api_client | log_api_response | ✅ API Response: 200 - GET /uapi/domestic-stock/v1/quotations/inquire-price
2026-06-11 10:24:38,778 | INFO | market_data | get_current_price | 💹 Real-time price fetched: 302,000 KRW ✓
2026-06-11 10:24:38,778 | INFO | trader | execute_trading_cycle | ----------------------------------------------------------------------
2026-06-11 10:24:38,778 | INFO | account | get_holdings | 📦 Mock trading: Returning tracked holdings
2026-06-11 10:24:38,778 | INFO | account | get_holdings | 📊 No holdings found
2026-06-11 10:24:38,778 | INFO | trader | execute_trading_cycle | 📦 Holdings before order: 0 shares
2026-06-11 10:24:38,778 | INFO | account | get_balance | 💰 Mock trading: Using tracked balance
2026-06-11 10:24:38,778 | INFO | account | get_balance | 💵 Balance: 10,003,000 KRW available, 10,003,000 KRW total (Holdings: 0 shares)
2026-06-11 10:24:38,778 | INFO | trader | get_order_prices_from_momentum | 📍 Momentum-based orders: Buy 300,000 (low 300,500), Sell 302,500 (high 302,000) | Signal: uptrend (+0.33%)
2026-06-11 10:24:38,778 | INFO | trader | execute_trading_cycle | 📈 Momentum: uptrend - Placing BUY at 300,000 KRW
2026-06-11 10:24:38,778 | INFO | orders | place_order | 📤 Mock trading: BUY order: 1 shares of 005930 @ 300,000 KRW...
2026-06-11 10:24:38,778 | INFO | orders | log_trading_action | 🔄 BUY Order: Order ID: MOCK00003, Status: 완료 (MOCK - EXECUTED)
2026-06-11 10:24:38,778 | INFO | trader | execute_trading_cycle | ⏳ Waiting 5s for buy order execution...
2026-06-11 10:24:43,779 | INFO | account | get_holdings | 📦 Mock trading: Returning tracked holdings
2026-06-11 10:24:43,779 | INFO | account | get_holdings | 📊 Holding: Samsung Electronics (Mock) (005930) x1 @ 70,000 KRW (Value: 70,000 KRW, P/L: -230,000 KRW)
2026-06-11 10:24:43,779 | INFO | trader | execute_trading_cycle | 📦 Holdings after buy: 1 shares
2026-06-11 10:24:43,779 | INFO | trader | execute_trading_cycle | ✅ Buy order EXECUTED at 300,000 (+1 shares)
2026-06-11 10:24:43,779 | INFO | trader | execute_trading_cycle | ----------------------------------------------------------------------
2026-06-11 10:24:43,779 | INFO | trader | execute_trading_cycle | 📉 Placing SELL order as PENDING: 302,500 KRW
2026-06-11 10:24:43,779 | INFO | trader | execute_trading_cycle |    Current profit target: +2,500 KRW per share
2026-06-11 10:24:43,779 | INFO | orders | place_order | 📤 Mock trading: SELL order: 1 shares of 005930 @ 302,500 KRW...
2026-06-11 10:24:43,779 | INFO | account | place_pending_sell_order | 📋 Pending sell order placed: 1 shares (bought @ 300,000, target sell @ 302,500)
2026-06-11 10:24:43,779 | INFO | orders | log_trading_action | 🔄 SELL Order: Order ID: MOCK00004, Status: 대기 (MOCK - PENDING)
2026-06-11 10:24:43,779 | INFO | trader | execute_trading_cycle | ⏳ Stock held at 1 shares, waiting for price to reach 302,500...
2026-06-11 10:24:43,779 | INFO | account | get_balance | 💰 Mock trading: Using tracked balance
2026-06-11 10:24:43,780 | INFO | account | get_balance | 💵 Balance: 9,703,000 KRW available, 9,773,000 KRW total (Holdings: 1 shares)
2026-06-11 10:24:43,780 | INFO | trader | execute_trading_cycle | 💵 Balance: 9,703,000 KRW available
2026-06-11 10:24:43,780 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-11 10:24:43,780 | INFO | trader | execute_trading_cycle | ✅ Buy placed, sell pending (waiting for market price)
2026-06-11 10:24:43,780 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-11 10:24:43,780 | INFO | trader | run_trading_loop | ⏳ Waiting 15s until next cycle...
2026-06-11 10:24:58,780 | INFO | trader | log_trading_window | 🟢 Trading window at 10:24:58: OPEN ✅
2026-06-11 10:24:58,780 | INFO | trader | run_trading_loop | 
🔢 Cycle #10
2026-06-11 10:24:58,780 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-11 10:24:58,780 | INFO | trader | execute_trading_cycle | 🔄 Starting trading cycle (Realistic Order Matching)...
2026-06-11 10:24:58,780 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-11 10:24:58,780 | INFO | market_data | get_current_price | 📊 Fetching real-time price for 005930 using TR_ID: FHKST01010100...
/home/codespace/.local/lib/python3.12/site-packages/urllib3/connectionpool.py:1097: InsecureRequestWarning: Unverified HTTPS request is being made to host 'openapivts.koreainvestment.com'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
  warnings.warn(
2026-06-11 10:25:00,076 | INFO | api_client | log_api_response | ✅ API Response: 200 - GET /uapi/domestic-stock/v1/quotations/inquire-price
2026-06-11 10:25:00,077 | INFO | market_data | get_current_price | 💹 Real-time price fetched: 302,500 KRW ✓
2026-06-11 10:25:00,077 | INFO | trader | execute_trading_cycle | ----------------------------------------------------------------------
2026-06-11 10:25:00,077 | INFO | trader | execute_trading_cycle | 📋 Pending sell order waiting: 1 shares @ 302,500
2026-06-11 10:25:00,077 | INFO | trader | execute_trading_cycle |    Current price: 302,500 KRW
2026-06-11 10:25:00,077 | INFO | trader | execute_trading_cycle |    Target price: 302,500 KRW (bought @ 300,000)
2026-06-11 10:25:00,077 | INFO | trader | execute_trading_cycle | ✅ Price reached target! Executing pending sell at 302,500
2026-06-11 10:25:00,077 | INFO | account | execute_pending_sell_order | 💰 Pending sell order EXECUTED at 302,500: 1 shares, Profit: 2,500 KRW
2026-06-11 10:25:00,077 | INFO | trader | execute_trading_cycle | 💰 SOLD at 302,500 KRW
2026-06-11 10:25:00,077 | INFO | trader | execute_trading_cycle | 💰 Trade profit: 2,500 KRW
2026-06-11 10:25:00,077 | INFO | trader | execute_trading_cycle | 📈 Total profit: 5,500 KRW (2 trades)
2026-06-11 10:25:00,078 | INFO | trader | execute_trading_cycle | ======================================================================
2026-06-11 10:25:00,078 | INFO | trader | run_trading_loop | ⏳ Waiting 15s until next cycle...
^C2026-06-11 10:25:13,471 | INFO | trader | run_trading_loop | 
🛑 Trading stopped by user
2026-06-11 10:25:13,471 | INFO | trader | run_trading_loop | ======================================================================
2026-06-11 10:25:13,471 | INFO | trader | run_trading_loop | 📊 Trading session ended
2026-06-11 10:25:13,471 | INFO | trader | run_trading_loop | ⏱️  Total duration: 2.9 minutes
2026-06-11 10:25:13,471 | INFO | trader | run_trading_loop | 🔢 Total cycles executed: 10
2026-06-11 10:25:13,471 | INFO | trader | run_trading_loop | ✔️  Completed trades: 2
2026-06-11 10:25:13,471 | INFO | trader | run_trading_loop | ======================================================================
2026-06-11 10:25:13,471 | INFO | trader | run_trading_loop | 💹 TOTAL PROFIT: 5,500 KRW 📈
2026-06-11 10:25:13,472 | INFO | trader | run_trading_loop | ====================================================