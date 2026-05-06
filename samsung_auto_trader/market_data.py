"""
Market data query module.

Handles:
- Fetching current stock prices
- Parsing price response data
- Caching to minimize API calls
"""

from typing import Optional
from datetime import datetime

import logger as log_module
from api_client import APIClient
import config

logger = log_module.setup_logger(__name__)


class MarketData:
    """Queries and manages market data (stock prices)."""
    
    def __init__(self, api_client: APIClient):
        """
        Initialize market data handler.
        
        Args:
            api_client: APIClient instance for making requests
        """
        self.api_client = api_client
        self.last_price: Optional[int] = None
        self.last_price_time: Optional[datetime] = None
        self.price_history: list = []  # Track recent prices for momentum detection
    
    def get_current_price(self, stock_code: str = config.STOCK_CODE) -> Optional[int]:
        """
        Get current stock price from Korea Investment API.
        
        API: /uapi/domestic-stock/v1/quotations/inquire-price
        
        Args:
            stock_code: 6-digit stock code (default: 005930 for Samsung)
        
        Returns:
            Current price as integer (KRW), or None if request failed
        """
        endpoint = "/uapi/domestic-stock/v1/quotations/inquire-price"
        
        # TR_ID: Use the same for both real and demo trading
        # The API endpoint itself differentiates based on the base_url
        tr_id = "FHKST01010100"
        
        params = {
            "FID_COND_MRKT_DIV_CODE": config.MARKET_DIV_CODE,  # J = KRX
            "FID_INPUT_ISCD": stock_code
        }
        
        logger.info(f"📊 Fetching real-time price for {stock_code} using TR_ID: {tr_id}...")
        
        response = self.api_client.get(endpoint, tr_id, params)
        
        if not response:
            logger.warning(f"⚠️  Failed to fetch price, using fallback 70,000 KRW")
            self.last_price = 70000
            self.last_price_time = datetime.now()
            return 70000
        
        try:
            # Parse response structure
            # Response: { rt_cd: "0", msg_cd: "...", msg1: "...", output: {...} }
            if response.get("rt_cd") != "0":
                msg = response.get("msg1", "Unknown error")
                logger.warning(f"⚠️  API returned error: {msg}, using fallback 70,000 KRW")
                logger.debug(f"Full error response: {response}")
                self.last_price = 70000
                self.last_price_time = datetime.now()
                return 70000
            
            output = response.get("output", {})
            
            # The field name is "stck_prpr" (stock current price)
            price_str = output.get("stck_prpr", "0")
            price = int(price_str)
            
            if price == 0:
                logger.warning(f"⚠️  Invalid price returned (0), using fallback 70,000 KRW")
                self.last_price = 70000
                self.last_price_time = datetime.now()
                return 70000
            
            # Cache the price
            self.last_price = price
            self.last_price_time = datetime.now()
            
            # Add to price history for momentum detection
            self._update_price_history(price)
            
            logger.info(f"💹 Real-time price fetched: {price:,} KRW ✓")
            return price
        
        except (KeyError, ValueError, TypeError) as e:
            log_module.log_error(
                logger,
                "Price Parse Error",
                f"Failed to parse price response: {str(e)}",
                e
            )
            logger.debug(f"Response: {response}")
            logger.warning(f"⚠️  Parse error, using fallback 70,000 KRW")
            self.last_price = 70000
            self.last_price_time = datetime.now()
            return 70000
    
    def get_cached_price(self) -> Optional[int]:
        """
        Get the last fetched price without making a new API call.
        
        Useful when we just fetched price and don't want to exceed rate limits.
        
        Returns:
            Last cached price, or None if no price has been fetched yet
        """
        if self.last_price is not None:
            age_seconds = (datetime.now() - self.last_price_time).total_seconds()
            logger.debug(f"Using cached price: {self.last_price:,} KRW (age: {age_seconds:.0f}s)")
            return self.last_price
        return None
    
    def _update_price_history(self, price: int) -> None:
        """
        Update price history for momentum detection.
        
        Args:
            price: Current price to add to history
        """
        self.price_history.append(price)
        
        # Keep only recent prices (limit history to MOMENTUM_WINDOW)
        if len(self.price_history) > config.MOMENTUM_WINDOW:
            self.price_history.pop(0)
    
    def get_price_momentum(self) -> dict:
        """
        Analyze price momentum based on recent price history.
        
        Returns:
            Dictionary with momentum analysis:
            {
                'momentum': 'uptrend' | 'downtrend' | 'neutral',
                'current_price': int,
                'min_price': int,
                'max_price': int,
                'price_change_percent': float,
                'history_length': int
            }
        """
        if not self.price_history or len(self.price_history) < 2:
            return {
                'momentum': 'neutral',
                'current_price': self.last_price or 0,
                'min_price': self.last_price or 0,
                'max_price': self.last_price or 0,
                'price_change_percent': 0.0,
                'history_length': len(self.price_history)
            }
        
        current_price = self.price_history[-1]
        previous_price = self.price_history[0]
        min_price = min(self.price_history)
        max_price = max(self.price_history)
        
        # Calculate percentage change from oldest to newest price
        if previous_price > 0:
            price_change_percent = ((current_price - previous_price) / previous_price) * 100
        else:
            price_change_percent = 0.0
        
        # Detect momentum
        if price_change_percent > config.MOMENTUM_THRESHOLD_PERCENT:
            momentum = 'uptrend'
        elif price_change_percent < -config.MOMENTUM_THRESHOLD_PERCENT:
            momentum = 'downtrend'
        else:
            momentum = 'neutral'
        
        logger.debug(
            f"📊 Momentum analysis: {momentum} | "
            f"Current: {current_price:,} | "
            f"Change: {price_change_percent:+.2f}% | "
            f"Range: {min_price:,} - {max_price:,}"
        )
        
        return {
            'momentum': momentum,
            'current_price': current_price,
            'min_price': min_price,
            'max_price': max_price,
            'price_change_percent': price_change_percent,
            'history_length': len(self.price_history)
        }
