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
        self.orders = OrderManager(api_client, account_number, account_product_code)
        
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
        Execute one complete trading cycle:
        1. Get current price
        2. Check current holdings
        3. Check account balance
        4. Place buy order (at current price - 2000)
        5. Wait briefly for execution
        6. Check holdings again
        7. If time permits, place sell order (at current price + 2000)
        8. Verify execution
        
        Returns:
            True if cycle completed successfully, False if error occurred
        """
        logger.info("=" * 70)
        logger.info("🔄 Starting trading cycle...")
        logger.info("=" * 70)
        
        # Step 1: Get current price
        current_price = self.market.get_current_price(self.stock_code)
        if not current_price:
            log_module.log_error(logger, "Trading Cycle", "Failed to get current price")
            return False
        
        # Step 2: Check current holdings before order
        holdings_before = self.account.get_holdings(self.stock_code)
        qty_before = holdings_before[0].quantity if holdings_before else 0
        logger.info(f"📦 Holdings before order: {qty_before} shares")
        
        # Step 3: Check account balance
        balance = self.account.get_balance()
        if not balance:
            log_module.log_error(logger, "Trading Cycle", "Failed to get account balance")
            return False
        
        # Calculate order prices
        buy_price, sell_price = self.get_order_prices(current_price)
        
        # Step 4: Place BUY order
        logger.info("-" * 70)
        buy_order = self.orders.place_buy_order(
            self.stock_code,
            buy_price,
            config.ORDER_QUANTITY
        )
        if not buy_order:
            log_module.log_error(logger, "Trading Cycle", "Failed to place buy order")
            return False
        
        # Step 5: Wait for execution and re-check holdings
        logger.info(f"⏳ Waiting {config.MARKET_DATA_POLL_INTERVAL_SECONDS}s for buy order execution...")
        time.sleep(config.MARKET_DATA_POLL_INTERVAL_SECONDS)
        
        holdings_after_buy = self.account.get_holdings(self.stock_code)
        qty_after_buy = holdings_after_buy[0].quantity if holdings_after_buy else 0
        buy_executed = qty_after_buy > qty_before
        
        logger.info(f"📦 Holdings after buy: {qty_after_buy} shares")
        if buy_executed:
            logger.info(f"✅ Buy order EXECUTED (+{qty_after_buy - qty_before} shares)")
        else:
            logger.info("⏳ Buy order still pending or not executed")
        
        # Step 6: Place SELL order (if we don't have holdings already)
        logger.info("-" * 70)
        sell_order = self.orders.place_sell_order(
            self.stock_code,
            sell_price,
            config.ORDER_QUANTITY
        )
        if not sell_order:
            log_module.log_error(logger, "Trading Cycle", "Failed to place sell order")
            return False
        
        # Step 7: Wait and verify sell execution
        logger.info(f"⏳ Waiting {config.MARKET_DATA_POLL_INTERVAL_SECONDS}s for sell order execution...")
        time.sleep(config.MARKET_DATA_POLL_INTERVAL_SECONDS)
        
        holdings_after_sell = self.account.get_holdings(self.stock_code)
        qty_after_sell = holdings_after_sell[0].quantity if holdings_after_sell else 0
        
        logger.info(f"📦 Holdings after sell: {qty_after_sell} shares")
        if qty_after_sell < qty_after_buy:
            logger.info(f"✅ Sell order EXECUTED (-{qty_after_buy - qty_after_sell} shares)")
        else:
            logger.info("⏳ Sell order still pending or not executed")
        
        # Final balance check
        final_balance = self.account.get_balance()
        if final_balance:
            logger.info(f"💵 Final balance: {final_balance.available_cash:,} KRW available")
        
        logger.info("=" * 70)
        logger.info("✅ Trading cycle completed")
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
        logger.info(f"💹 Buy offset: {config.ORDER_PRICE_OFFSET_BUY} KRW")
        logger.info(f"💹 Sell offset: {config.ORDER_PRICE_OFFSET_SELL} KRW")
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
            logger.info("=" * 70)
