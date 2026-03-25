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
    
    def get_current_price(self, stock_code: str = config.STOCK_CODE) -> Optional[int]:
        """
        Get current stock price from Korea Investment API.
        
        API: /uapi/domestic-stock/v1/quotations/inquire-price
        
        Args:
            stock_code: 6-digit stock code (default: 005930 for Samsung)
        
        Returns:
            Current price as integer (KRW), or None if request failed
        """
        # For mock trading, return a dummy price since the API may not be available
        if self.api_client.mock_trading:
            logger.info("Mock trading: Using dummy price 70000 KRW")
            self.last_price = 70000
            self.last_price_time = datetime.now()
            return 70000
        
        endpoint = "/uapi/domestic-stock/v1/quotations/inquire-price"
        
        # TR_ID for real trading
        tr_id = "FHKST01010100"
        
        params = {
            "FID_COND_MRKT_DIV_CODE": config.MARKET_DIV_CODE,  # J = KRX
            "FID_INPUT_ISCD": stock_code
        }
        
        logger.info(f"📊 Fetching current price for {stock_code}...")
        
        response = self.api_client.get(endpoint, tr_id, params)
        
        if not response:
            log_module.log_error(logger, "Price Query Failed", f"No response for {stock_code}")
            return None
        
        try:
            # Parse response structure
            # Response: { rt_cd: "0", msg_cd: "...", msg1: "...", output: {...} }
            if response.get("rt_cd") != "0":
                msg = response.get("msg1", "Unknown error")
                log_module.log_error(logger, "Price Query Error", f"API returned error: {msg}")
                return None
            
            output = response.get("output", {})
            
            # The field name is "stck_prpr" (stock current price)
            price_str = output.get("stck_prpr", "0")
            price = int(price_str)
            
            # Cache the price
            self.last_price = price
            self.last_price_time = datetime.now()
            
            logger.info(f"💹 Current price: {price:,} KRW")
            return price
        
        except (KeyError, ValueError, TypeError) as e:
            log_module.log_error(
                logger,
                "Price Parse Error",
                f"Failed to parse price response: {str(e)}",
                e
            )
            logger.debug(f"Response: {response}")
            return None
    
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
