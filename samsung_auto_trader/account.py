"""
Account management module.

Handles:
- Fetching account balance and cash available
- Fetching stock holdings
- Parsing and formatting account data
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

import logger as log_module
from api_client import APIClient
import config

logger = log_module.setup_logger(__name__)


@dataclass
class AccountBalance:
    """Account balance information."""
    total_balance: int      # Total account balance (KRW)
    available_cash: int     # Available cash for trading (KRW)
    total_assets: int       # Total assets including holdings (KRW)


@dataclass
class StockHolding:
    """Single stock holding information."""
    stock_code: str         # Stock code (e.g., "005930")
    stock_name: str         # Stock name
    quantity: int           # Shares held
    purchase_price: int     # Average purchase price (KRW)
    current_price: int      # Current price (KRW)
    total_value: int        # Total value of holding (KRW)
    profit_loss: int        # Unrealized P&L (KRW)


class Account:
    """Manages account information and holdings."""
    
    def __init__(
        self,
        api_client: APIClient,
        account_number: str,
        account_product_code: str
    ):
        """
        Initialize account manager.
        
        Args:
            api_client: APIClient instance
            account_number: 8-digit account number
            account_product_code: 2-digit product code (01 for stocks)
        """
        self.api_client = api_client
        self.account_number = account_number
        self.account_product_code = account_product_code
        self.last_balance: Optional[AccountBalance] = None
        self.last_holdings: Optional[List[StockHolding]] = None
    
    def get_balance(self) -> Optional[AccountBalance]:
        """
        Get account balance and available cash.
        
        API: /uapi/domestic-stock/v1/trading/inquire-account-balance
        
        Returns:
            AccountBalance object or None if request failed
        """
        endpoint = "/uapi/domestic-stock/v1/trading/inquire-account-balance"
        tr_id = "CTRP6548R"  # Account balance inquiry TR ID
        
        params = {
            "CANO": self.account_number,
            "ACNT_PRDT_CD": self.account_product_code,
            "INQR_DVSN_1": "",
            "BSPR_BF_DT_APLY_YN": ""
        }
        
        logger.info("💰 Fetching account balance...")
        
        response = self.api_client.get(endpoint, tr_id, params)
        
        if not response:
            log_module.log_error(logger, "Balance Query Failed", "No response from API")
            return None
        
        try:
            if response.get("rt_cd") != "0":
                msg = response.get("msg1", "Unknown error")
                log_module.log_error(logger, "Balance Query Error", msg)
                return None
            
            # Response has output1 (holdings list) and output2 (account summary)
            # We need output2 for balance information
            output2 = response.get("output2", {})
            
            # Parse balance fields
            # Field names are in Korean, but API returns uppercase keys
            total_balance = int(output2.get("dnca_tot_amt", "0") or "0")           # Total balance
            available_cash = int(output2.get("avbl_buy_amt", "0") or "0")         # Available cash
            total_assets = int(output2.get("tot_evlu_amt", "0") or "0")           # Total asset value
            
            balance = AccountBalance(
                total_balance=total_balance,
                available_cash=available_cash,
                total_assets=total_assets
            )
            
            self.last_balance = balance
            
            logger.info(f"💵 Balance: {available_cash:,} KRW available, {total_assets:,} KRW total")
            return balance
        
        except (KeyError, ValueError, TypeError) as e:
            log_module.log_error(
                logger,
                "Balance Parse Error",
                f"Failed to parse balance response: {str(e)}",
                e
            )
            logger.debug(f"Response: {response}")
            return None
    
    def get_holdings(self, stock_code: Optional[str] = None) -> Optional[List[StockHolding]]:
        """
        Get current stock holdings.
        
        API: /uapi/domestic-stock/v1/trading/inquire-balance
        
        Args:
            stock_code: If provided, only return holdings for this stock. Otherwise return all.
        
        Returns:
            List of StockHolding objects, or None if request failed
        """
        endpoint = "/uapi/domestic-stock/v1/trading/inquire-balance"
        tr_id = "TTTC8434R"  # Holdings inquiry TR ID for mock trading
        
        params = {
            "CANO": self.account_number,
            "ACNT_PRDT_CD": self.account_product_code,
            "AFHR_FLPR_YN": config.BALANCE_AFHR_FLPR_YN,      # N = standard
            "INQR_DVSN": config.BALANCE_INQR_DVSN,             # 02 = by stock
            "UNPR_DVSN": config.BALANCE_UNPR_DVSN,             # 01 = standard price
            "FUND_STTL_ICLD_YN": config.BALANCE_FUND_STTL,     # N = exclude funds
            "FNCG_AMT_AUTO_RDPT_YN": config.BALANCE_FNCG_AUTO_RDPT,  # N = no auto repay
            "PRCS_DVSN": config.BALANCE_PRCS_DVSN              # 00 = include previous day
        }
        
        logger.info(f"📦 Fetching holdings for account {self.account_number}...")
        
        response = self.api_client.get(endpoint, tr_id, params)
        
        if not response:
            log_module.log_error(logger, "Holdings Query Failed", "No response from API")
            return None
        
        try:
            if response.get("rt_cd") != "0":
                msg = response.get("msg1", "Unknown error")
                log_module.log_error(logger, "Holdings Query Error", msg)
                return None
            
            # Response has output1 (holdings list) and output2 (balance summary)
            output1 = response.get("output1", [])
            
            holdings = []
            for item in output1:
                code = item.get("pdno", "")
                
                # If filtering by stock, skip others
                if stock_code and code != stock_code:
                    continue
                
                holding = StockHolding(
                    stock_code=code,
                    stock_name=item.get("prdt_name", ""),
                    quantity=int(item.get("hldg_qty", "0") or "0"),
                    purchase_price=int(item.get("pchs_avg_pric", "0") or "0"),
                    current_price=int(item.get("prpr", "0") or "0"),
                    total_value=int(item.get("evlu_amt", "0") or "0"),
                    profit_loss=int(item.get("evlu_pfls_amt", "0") or "0")
                )
                holdings.append(holding)
            
            self.last_holdings = holdings
            
            if holdings:
                for h in holdings:
                    logger.info(
                        f"📊 Holding: {h.stock_name} ({h.stock_code}) "
                        f"x{h.quantity} @ {h.current_price:,} KRW "
                        f"(Value: {h.total_value:,} KRW, P/L: {h.profit_loss:+,} KRW)"
                    )
            else:
                logger.info("📊 No holdings found")
            
            return holdings
        
        except (KeyError, ValueError, TypeError) as e:
            log_module.log_error(
                logger,
                "Holdings Parse Error",
                f"Failed to parse holdings response: {str(e)}",
                e
            )
            logger.debug(f"Response: {response}")
            return None
    
    def get_samsung_holding(self) -> Optional[StockHolding]:
        """
        Get Samsung Electronics holding specifically.
        
        Returns:
            StockHolding for Samsung (005930) or None if not held or error
        """
        holdings = self.get_holdings(config.STOCK_CODE)
        if holdings and len(holdings) > 0:
            return holdings[0]
        return None
    
    def get_available_cash(self) -> Optional[int]:
        """
        Get available cash without fetching full balance.
        
        Returns available cash from last cached balance, or None if not cached.
        """
        if self.last_balance:
            return self.last_balance.available_cash
        return None
