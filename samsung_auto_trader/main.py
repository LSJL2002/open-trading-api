#!/usr/bin/env python3
"""
Samsung Electronics Auto Trader - Main Entry Point

This is a simple automated trading system that:
1. Authenticates with Korea Investment Open API (mock trading only)
2. Monitors Samsung Electronics stock price (005930)
3. Places buy orders at (current price - 2000 KRW)
4. Places sell orders at (current price + 2000 KRW)
5. Operates only during trading window (09:10 - 15:30)
6. Caches token for same-day reuse to minimize API calls

IMPORTANT: This is mock trading only (VTS environment)
Do NOT modify the config to use real trading without understanding the risks.

Usage:
    python main.py [--test-duration 5]

Environment Variables Required:
    GH_APPKEY: Korea Investment API app key
    GH_APPSECRET: Korea Investment API app secret
    GH_ACCOUNT: Account number (format: 12345678-01, gets parsed to 12345678 and 01)
"""

import sys
import os
import argparse
from typing import Optional

import config
import logger as log_module
import auth
from api_client import APIClient
from trader import Trader

# Setup logger
logger = log_module.setup_logger(__name__)


def parse_account_number(account_str: str) -> Optional[tuple]:
    """
    Parse account string to account number and product code.
    
    Expected formats:
    - "12345678-01" → ("12345678", "01")
    - "1234567801" → ("12345678", "01")
    
    Args:
        account_str: Account string
    
    Returns:
        Tuple of (account_number, product_code) or None if invalid
    """
    if not account_str:
        return None
    
    # Remove dash if present
    account_str = account_str.replace("-", "")
    
    # Should be 10 digits (8 account + 2 product)
    if len(account_str) == 10 and account_str.isdigit():
        account_number = account_str[:8]
        product_code = account_str[8:10]
        return (account_number, product_code)
    
    logger.error(f"Invalid account format: {account_str}")
    logger.error("Expected format: 12345678-01 or 1234567801")
    return None


def main():
    """Main entry point."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Samsung Electronics Auto Trader (Mock Trading Only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
    Run automated trading until 15:30 (market close)
  
  python main.py --test-duration 5
    Run for 5 minutes (for testing)
        """
    )
    parser.add_argument(
        "--test-duration",
        type=int,
        default=0,
        help="For testing: run for N minutes then stop (default: 0 = run until market close)"
    )
    
    args = parser.parse_args()
    
    # Log system info
    logger.info("=" * 70)
    logger.info("🚀 Samsung Electronics Auto Trader Initialization")
    logger.info("=" * 70)
    logger.info(f"📍 Target Stock: {config.STOCK_NAME} ({config.STOCK_CODE})")
    logger.info(f"🌐 Environment: {config.TRADING_ENV.upper()} Trading (Mock)")
    logger.info(f"⏰ Trading Window: {config.TRADING_START_TIME} - {config.TRADING_END_TIME}")
    
    # Step 1: Load and parse account number from environment
    logger.info("\n📋 Step 1: Loading configuration...")
    account_sources = [
        ("GH_ACCOUNT", os.getenv("GH_ACCOUNT")),
        ("GITHUB_ACCOUNT", os.getenv("GITHUB_ACCOUNT")),
        ("KIS_ACCOUNT", os.getenv("KIS_ACCOUNT")),
        ("ACCOUNT", os.getenv("ACCOUNT")),
    ]

    account_str = None
    for name, value in account_sources:
        if value:
            account_str = value
            logger.info(f"Using account from env var: {name}")
            break

    if not account_str:
        log_module.log_error(
            logger,
            "Configuration",
            "Account environment variable not set. Please set GH_ACCOUNT (or GITHUB_ACCOUNT/KIS_ACCOUNT/ACCOUNT) to your account number (e.g., 12345678-01)"
        )
        return 1
    
    account_info = parse_account_number(account_str)
    if not account_info:
        return 1
    
    account_number, product_code = account_info
    logger.info(f"✅ Account: {account_number}-{product_code}")
    
    # Step 2: Authenticate
    logger.info("\n🔐 Step 2: Authenticating with Korea Investment API...")
    token_manager = auth.create_auth_manager()
    if not token_manager:
        log_module.log_error(
            logger,
            "Authentication",
            "Failed to authenticate. Check your credentials and try again."
        )
        return 1
    
    token = token_manager.get_token()
    if not token:
        log_module.log_error(
            logger,
            "Authentication",
            "Token acquisition failed."
        )
        return 1
    
    logger.info("✅ Authentication successful")
    
    # Step 3: Initialize API client
    logger.info("\n📡 Step 3: Initializing API client...")
    api_client = APIClient(
        token,
        token_manager.appkey,
        token_manager.appsecret,
        mock_trading=(config.TRADING_ENV == "demo")
    )
    logger.info("✅ API client ready")
    
    # Step 4: Initialize trader
    logger.info("\n🤖 Step 4: Initializing trader...")
    try:
        trader = Trader(
            api_client,
            account_number,
            product_code,
            config.STOCK_CODE
        )
        logger.info("✅ Trader initialized")
    except Exception as e:
        log_module.log_error(
            logger,
            "Trader Initialization",
            f"Failed to initialize trader: {str(e)}",
            e
        )
        return 1
    
    # Step 5: Verify connection by getting current price
    logger.info("\n✅ Step 5: Verifying connection (getting current price)...")
    current_price = trader.market.get_current_price(config.STOCK_CODE)
    if not current_price:
        log_module.log_error(
            logger,
            "Connection Verification",
            "Failed to get current price. Check your API credentials and network."
        )
        return 1
    
    logger.info(f"✅ Connection verified. Current price: {current_price:,} KRW")
    
    # Step 6: Check if market is open
    logger.info("\n📊 Step 6: Checking market status...")
    if not trader.is_trading_window_open():
        logger.info("❌ Not opened")
        logger.info("Market trading window (09:10 - 15:30 KST) is closed.")
        return 0
    
    # Step 7: Run trading loop
    logger.info("\n🔄 Step 7: Starting trading loop...")
    logger.info("Press Ctrl+C to stop trading at any time\n")
    
    try:
        trader.run_trading_loop(duration_minutes=args.test_duration)
        return 0
    except Exception as e:
        log_module.log_error(
            logger,
            "Trading Loop",
            f"Error in trading loop: {str(e)}",
            e
        )
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
