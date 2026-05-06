"""
Core trading logic module.

Implements:
- Price monitoring
- Order placement logic (buy 2000 below, sell 2000 above current price)
- Execution verification
- Trading loop
"""

import time
from datetime import datetime, time as dt_time
from typing import Optional, Tuple

import logger as log_module
from api_client import APIClient
from market_data import MarketData
from account import Account
from orders import OrderManager
import config

logger = log_module.setup_logger(__name__)


class Trader:
    """High-level trading logic and coordination."""
    
    def __init__(
        self,
        api_client: APIClient,
        account_number: str,
        account_product_code: str,
        stock_code: str = config.STOCK_CODE
    ):
        """
        Initialize trader.
        
        Args:
            api_client: APIClient instance
            account_number: 8-digit account number
            account_product_code: 2-digit product code
            stock_code: Target stock code (default: Samsung 005930)
        """
        self.api_client = api_client
        self.stock_code = stock_code
        
        # Initialize sub-managers
        self.market = MarketData(api_client)
        self.account = Account(api_client, account_number, account_product_code)
        self.orders = OrderManager(api_client, account_number, account_product_code, self.account)
        
        # Track trading performance
        self.total_profit = 0  # Total profit/loss in KRW
        self.completed_trades = 0  # Number of completed buy-sell cycles
        
        logger.info(f"🤖 Trader initialized for {stock_code}")
    
    def is_trading_window_open(self) -> bool:
        """
        Check if current time is within trading window.
        
        Trading window: 09:10 - 15:30 (Korean market hours)
        
        Returns:
            True if within trading window, False otherwise
        """
        now = datetime.now().time()
        is_open = config.TRADING_START_TIME <= now < config.TRADING_END_TIME
        
        log_module.log_trading_window(logger, is_open, now.strftime("%H:%M:%S"))
        return is_open
    
    def get_order_prices_from_momentum(self) -> Tuple[int, int, str]:
        """
        Calculate buy and sell order prices based on momentum analysis.
        
        Strategy:
        - Buy: At recent low price + buffer (capture upswing)
        - Sell: At recent high price - buffer (capture downswing)
        - Only trade if clear momentum detected
        
        Returns:
            Tuple of (buy_price, sell_price, momentum_signal)
            momentum_signal: 'uptrend' | 'downtrend' | 'neutral'
        """
        momentum = self.market.get_price_momentum()
        
        buy_price = momentum['min_price'] - config.ORDER_BUFFER_KRW
        sell_price = momentum['max_price'] + config.ORDER_BUFFER_KRW
        momentum_signal = momentum['momentum']
        
        logger.info(
            f"📍 Momentum-based orders: "
            f"Buy {buy_price:,} (low {momentum['min_price']:,}), "
            f"Sell {sell_price:,} (high {momentum['max_price']:,}) | "
            f"Signal: {momentum_signal} ({momentum['price_change_percent']:+.2f}%)"
        )
        
        return buy_price, sell_price, momentum_signal
    
    def should_place_orders(self) -> bool:
        """
        Determine if we should place orders based on momentum.
        
        Returns:
            True if we should place orders, False if momentum is too weak
        """
        momentum = self.market.get_price_momentum()
        
        # Need enough price history to detect momentum
        if momentum['history_length'] < 3:
            logger.info(f"⏳ Insufficient price history ({momentum['history_length']}/{config.MOMENTUM_WINDOW}), waiting...")
            return False
        
        # Only trade on clear momentum signals
        if momentum['momentum'] == 'neutral':
            logger.info(f"😑 No clear momentum ({momentum['price_change_percent']:+.2f}%), waiting...")
            return False
        
        return True
    
    def get_order_prices(self, current_price: int) -> Tuple[int, int]:
        """
        Calculate buy and sell order prices based on current price.
        
        Buy: current_price + ORDER_PRICE_OFFSET_BUY (usually -2000)
        Sell: current_price + ORDER_PRICE_OFFSET_SELL (usually +2000)
        
        Args:
            current_price: Current market price
        
        Returns:
            Tuple of (buy_price, sell_price)
        """
        buy_price = current_price + config.ORDER_PRICE_OFFSET_BUY
        sell_price = current_price + config.ORDER_PRICE_OFFSET_SELL
        
        logger.debug(
            f"📍 Price offsets: Buy {buy_price:,} (current {current_price:,} - 2000), "
            f"Sell {sell_price:,} (current {current_price:,} + 2000)"
        )
        
        return buy_price, sell_price
    
    def execute_trading_cycle(self) -> bool:
        """
        Execute one complete trading cycle with realistic sell waiting:
        1. Get current price
        2. Check if we have a pending sell order waiting for price target
        3. If pending sell exists and price >= target, execute the sell (real profit!)
        4. If no pending sell, check momentum and place a new buy order
        5. Place sell order (pending) at target price
        
        Returns:
            True if cycle completed successfully, False if error occurred
        """
        logger.info("=" * 70)
        logger.info("🔄 Starting trading cycle (Realistic Order Matching)...")
        logger.info("=" * 70)
        
        # Step 1: Get current price
        current_price = self.market.get_current_price(self.stock_code)
        if not current_price:
            log_module.log_error(logger, "Trading Cycle", "Failed to get current price")
            return False
        
        # Step 2: Check if we have a pending sell order waiting for execution
        pending_sell = self.account.get_pending_sell_order()
        if pending_sell:
            target_sell_price = pending_sell['target_sell_price']
            buy_price = pending_sell['buy_price']
            quantity = pending_sell['quantity']
            
            logger.info("-" * 70)
            logger.info(f"📋 Pending sell order waiting: {quantity} shares @ {target_sell_price:,}")
            logger.info(f"   Current price: {current_price:,} KRW")
            logger.info(f"   Target price: {target_sell_price:,} KRW (bought @ {buy_price:,})")
            
            # Check if current price meets or exceeds target
            if current_price >= target_sell_price:
                logger.info(f"✅ Price reached target! Executing pending sell at {current_price:,}")
                
                # Execute the pending sell
                result = self.account.execute_pending_sell_order(current_price)
                if result:
                    profit = result['profit']
                    self.total_profit += profit
                    self.completed_trades += 1
                    
                    logger.info(f"💰 SOLD at {current_price:,} KRW")
                    logger.info(f"💰 Trade profit: {profit:,} KRW")
                    logger.info(f"📈 Total profit: {self.total_profit:,} KRW ({self.completed_trades} trades)")
                    logger.info("=" * 70)
                    return True
            else:
                # Price not yet at target, wait
                price_diff = target_sell_price - current_price
                percent_diff = (price_diff / current_price) * 100
                logger.info(f"⏳ Waiting for price to rise {price_diff:,} KRW (+{percent_diff:.2f}%)")
                logger.info("=" * 70)
                return True
        
        # Step 3: No pending sell, so do a new buy-sell cycle
        logger.info("-" * 70)
        
        # Check momentum and decide whether to trade
        if not self.should_place_orders():
            logger.info("⏭️  Skipping this cycle due to weak momentum")
            logger.info("=" * 70)
            return True
        
        # Step 4: Check current holdings before order
        holdings_before = self.account.get_holdings(self.stock_code)
        qty_before = holdings_before[0].quantity if holdings_before else 0
        logger.info(f"📦 Holdings before order: {qty_before} shares")
        
        # Step 5: Check account balance
        balance = self.account.get_balance()
        if not balance:
            log_module.log_error(logger, "Trading Cycle", "Failed to get account balance")
            return False
        
        # Calculate momentum-based order prices
        buy_price, sell_target_price, momentum_signal = self.get_order_prices_from_momentum()
        
        # Step 6: Place BUY order
        logger.info(f"📈 Momentum: {momentum_signal} - Placing BUY at {buy_price:,} KRW")
        buy_order = self.orders.place_buy_order(
            self.stock_code,
            buy_price,
            config.ORDER_QUANTITY
        )
        if not buy_order:
            log_module.log_error(logger, "Trading Cycle", "Failed to place buy order")
            return False
        
        # Step 7: Wait for execution and re-check holdings
        logger.info(f"⏳ Waiting {config.MARKET_DATA_POLL_INTERVAL_SECONDS}s for buy order execution...")
        time.sleep(config.MARKET_DATA_POLL_INTERVAL_SECONDS)
        
        holdings_after_buy = self.account.get_holdings(self.stock_code)
        qty_after_buy = holdings_after_buy[0].quantity if holdings_after_buy else 0
        buy_executed = qty_after_buy > qty_before
        
        logger.info(f"📦 Holdings after buy: {qty_after_buy} shares")
        if buy_executed:
            logger.info(f"✅ Buy order EXECUTED at {buy_price:,} (+{qty_after_buy - qty_before} shares)")
        else:
            logger.info("⏳ Buy order still pending or not executed")
            logger.info("=" * 70)
            return True
        
        # Step 8: Place SELL order as pending (will wait for price)
        logger.info("-" * 70)
        logger.info(f"📉 Placing SELL order as PENDING: {sell_target_price:,} KRW")
        logger.info(f"   Current profit target: +{sell_target_price - buy_price:,} KRW per share")
        
        sell_order = self.orders.place_sell_order(
            self.stock_code,
            sell_target_price,
            config.ORDER_QUANTITY
        )
        if not sell_order:
            log_module.log_error(logger, "Trading Cycle", "Failed to place sell order")
            return False
        
        logger.info(f"⏳ Stock held at {qty_after_buy} shares, waiting for price to reach {sell_target_price:,}...")
        
        # Final balance check
        final_balance = self.account.get_balance()
        if final_balance:
            logger.info(f"💵 Balance: {final_balance.available_cash:,} KRW available")
        
        logger.info("=" * 70)
        logger.info("✅ Buy placed, sell pending (waiting for market price)")
        logger.info("=" * 70)
        
        return True
    
    def run_trading_loop(self, duration_minutes: int = 0) -> None:
        """
        Run the main trading loop.
        
        Loop behavior:
        - Only executes trading cycles during trading window (09:10 - 15:30)
        - Polls every PRICE_POLL_INTERVAL_SECONDS when not trading
        - Executes trading cycle TRADING_INTERVAL_SECONDS apart
        - Continues until trading window closes
        - Set duration_minutes > 0 to run for limited time (mostly for testing)
        
        Args:
            duration_minutes: If > 0, run for this many minutes then stop (for testing)
        """
        import time
        from datetime import datetime, timedelta
        
        start_time = datetime.now()
        cycle_count = 0
        
        logger.info("=" * 70)
        logger.info("🚀 SAMSUNG ELECTRONICS AUTO TRADER STARTED")
        logger.info(f"📅 Trading window: {config.TRADING_START_TIME} - {config.TRADING_END_TIME}")
        logger.info(f"🎯 Target: {config.STOCK_NAME} ({self.stock_code})")
        logger.info(f"� Strategy: Momentum Detection (window: {config.MOMENTUM_WINDOW} prices)")
        logger.info(f"📊 Momentum threshold: {config.MOMENTUM_THRESHOLD_PERCENT}%")
        logger.info(f"💹 Order buffer: {config.ORDER_BUFFER_KRW} KRW")
        logger.info(f"⏱️  Poll interval: {config.PRICE_POLL_INTERVAL_SECONDS}s")
        logger.info("=" * 70)
        
        try:
            while True:
                current_time = datetime.now()
                
                # Check if test duration exceeded
                if duration_minutes > 0:
                    elapsed = (current_time - start_time).total_seconds() / 60
                    if elapsed > duration_minutes:
                        logger.info(f"⏱️  Test duration ({duration_minutes}m) exceeded, stopping")
                        break
                
                # Check trading window
                if not self.is_trading_window_open():
                    logger.info("🔴 Trading window closed, waiting for next session...")
                    time.sleep(60)  # Check again in 60 seconds
                    continue
                
                # Execute trading cycle
                cycle_count += 1
                logger.info(f"\n🔢 Cycle #{cycle_count}")
                
                success = self.execute_trading_cycle()
                if not success:
                    logger.warning("⚠️  Trading cycle failed, but continuing...")
                
                # Wait before next cycle
                logger.info(f"⏳ Waiting {config.PRICE_POLL_INTERVAL_SECONDS}s until next cycle...")
                time.sleep(config.PRICE_POLL_INTERVAL_SECONDS)
        
        except KeyboardInterrupt:
            logger.info("\n🛑 Trading stopped by user")
        
        except Exception as e:
            log_module.log_error(
                logger,
                "Trading Loop Error",
                f"Unexpected error in trading loop: {str(e)}",
                e
            )
        
        finally:
            total_time = (datetime.now() - start_time).total_seconds() / 60
            logger.info("=" * 70)
            logger.info(f"📊 Trading session ended")
            logger.info(f"⏱️  Total duration: {total_time:.1f} minutes")
            logger.info(f"🔢 Total cycles executed: {cycle_count}")
            logger.info(f"✔️  Completed trades: {self.completed_trades}")
            logger.info("=" * 70)
            if self.total_profit >= 0:
                logger.info(f"💹 TOTAL PROFIT: {self.total_profit:,} KRW 📈")
            else:
                logger.info(f"📉 TOTAL LOSS: {self.total_profit:,} KRW")
            logger.info("=" * 70)
