"""
Order placement and tracking module.

Handles:
- Placing buy/sell orders
- Tracking order execution status
- Verifying order fills
"""

from typing import Optional
from dataclasses import dataclass
from enum import Enum

import logger as log_module
from api_client import APIClient
import config

logger = log_module.setup_logger(__name__)


class OrderType(str, Enum):
    """Order type enumeration."""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """Order information."""
    order_type: OrderType           # BUY or SELL
    stock_code: str                 # Stock code (e.g., "005930")
    quantity: int                   # Quantity
    price: int                       # Order price (KRW)
    order_id: Optional[str] = None   # Order ID from API response
    execution_status: str = ""      # Execution status from response


class OrderManager:
    """Manages order placement and tracking."""
    
    def __init__(
        self,
        api_client: APIClient,
        account_number: str,
        account_product_code: str,
        account=None
    ):
        """
        Initialize order manager.
        
        Args:
            api_client: APIClient instance
            account_number: 8-digit account number
            account_product_code: 2-digit product code (01 for stocks)
            account: Account object for updating mock holdings (optional)
        """
        self.api_client = api_client
        self.account_number = account_number
        self.account_product_code = account_product_code
        self.account = account
        self.last_orders = []
    
    def place_order(
        self,
        order_type: OrderType,
        stock_code: str,
        quantity: int,
        price: int
    ) -> Optional[Order]:
        """
        Place a buy or sell order.
        
        API: /uapi/domestic-stock/v1/trading/order-cash
        
        Args:
            order_type: OrderType.BUY or OrderType.SELL
            stock_code: 6-digit stock code (e.g., "005930")
            quantity: Number of shares
            price: Order price in KRW
        
        Returns:
            Order object with order ID if successful, None if failed
        """
        action_str = "SELL" if order_type == OrderType.SELL else "BUY"
        
        # For mock trading, return a simulated successful order
        if self.api_client.mock_trading:
            logger.info(
                f"📤 Mock trading: Simulating {action_str} order: {quantity} shares of {stock_code} @ {price:,} KRW..."
            )
            
            # Generate a mock order ID
            order_id = f"MOCK{len(self.last_orders) + 1:05d}"
            
            order = Order(
                order_type=order_type,
                stock_code=stock_code,
                quantity=quantity,
                price=price,
                order_id=order_id,
                execution_status="완료"  # "Completed" in Korean
            )
            
            self.last_orders.append(order)
            
            # Update mock holdings when an order is placed
            if self.account:
                qty_change = quantity if order_type == OrderType.BUY else -quantity
                self.account.update_mock_holding(qty_change, price)
            
            log_module.log_trading_action(
                logger,
                f"{action_str} Order",
                f"Order ID: {order.order_id}, Status: {order.execution_status} (MOCK)"
            )
            
            return order
        
        endpoint = "/uapi/domestic-stock/v1/trading/order-cash"
        
        # Determine TR_ID based on order type and environment
        # For mock trading, use V prefix for order TRs
        if order_type == OrderType.BUY:
            tr_id = "VTTC0012U"  # Mock buy order
        else:  # SELL
            tr_id = "VTTC0011U"  # Mock sell order
        
        # Map order type to API value
        ord_dv = "buy" if order_type == OrderType.BUY else "sell"
        
        payload = {
            "CANO": self.account_number,
            "ACNT_PRDT_CD": self.account_product_code,
            "PDNO": stock_code,
            "ORD_DVSN": config.ORDER_DIVISION,  # 00 = limit order
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
            "EXCG_ID_DVSN_CD": config.EXCHANGE_ID,  # KRX
            "SLL_TYPE": "",  # Not used for buy orders
            "CNDT_PRIC": ""  # Not used for standard limit orders
        }
        
        logger.info(
            f"📤 Placing {action_str} order: {quantity} shares of {stock_code} @ {price:,} KRW..."
        )
        
        response = self.api_client.post(endpoint, tr_id, payload)
        
        if not response:
            log_module.log_error(
                logger,
                "Order Placement Failed",
                f"{action_str} order failed - no response"
            )
            return None
        
        try:
            if response.get("rt_cd") != "0":
                msg = response.get("msg1", "Unknown error")
                log_module.log_error(
                    logger,
                    "Order Placement Error",
                    f"{action_str} order error: {msg}"
                )
                return None
            
            # Parse order response
            output = response.get("output", {})
            
            order = Order(
                order_type=order_type,
                stock_code=stock_code,
                quantity=quantity,
                price=price,
                order_id=output.get("ODNO", ""),  # Order number/ID
                execution_status=output.get("ord_sts", "")  # Order status
            )
            
            self.last_orders.append(order)
            
            log_module.log_trading_action(
                logger,
                f"{action_str} Order",
                f"Order ID: {order.order_id}, Status: {order.execution_status}"
            )
            
            return order
        
        except (KeyError, ValueError, TypeError) as e:
            log_module.log_error(
                logger,
                "Order Response Parse Error",
                f"Failed to parse order response: {str(e)}",
                e
            )
            logger.debug(f"Response: {response}")
            return None
    
    def place_buy_order(
        self,
        stock_code: str,
        price: int,
        quantity: int = config.ORDER_QUANTITY
    ) -> Optional[Order]:
        """
        Convenience method to place a buy order.
        
        Args:
            stock_code: Stock code
            price: Buy price
            quantity: Number of shares (default 1)
        
        Returns:
            Order object or None if failed
        """
        return self.place_order(OrderType.BUY, stock_code, quantity, price)
    
    def place_sell_order(
        self,
        stock_code: str,
        price: int,
        quantity: int = config.ORDER_QUANTITY
    ) -> Optional[Order]:
        """
        Convenience method to place a sell order.
        
        Args:
            stock_code: Stock code
            price: Sell price
            quantity: Number of shares (default 1)
        
        Returns:
            Order object or None if failed
        """
        return self.place_order(OrderType.SELL, stock_code, quantity, price)
