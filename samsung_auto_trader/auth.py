"""
Authentication and token management for Korea Investment Open API.

Handles:
- Loading credentials from environment variables
- Token acquisition and caching for same-day reuse
- Token validation
"""

import json
import os
from datetime import datetime
from typing import Optional, Tuple

import requests

import config
import logger as log_module

logger = log_module.setup_logger(__name__)


class TokenManager:
    """Manages token acquisition, caching, and validation."""
    
    def __init__(self, cache_file: str = config.TOKEN_CACHE_FILE):
        """
        Initialize token manager.
        
        Args:
            cache_file: Path to token cache file
        """
        self.cache_file = cache_file
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.appkey: Optional[str] = None
        self.appsecret: Optional[str] = None
    
    def load_credentials(self) -> bool:
        """
        Load credentials from environment variables.
        
        Expected environment variables:
        - GH_APPKEY: Korea Investment app key
        - GH_APPSECRET: Korea Investment app secret
        
        Returns:
            True if credentials loaded successfully, False otherwise
        """
        self.appkey = os.getenv("GH_APPKEY")
        self.appsecret = os.getenv("GH_APPSECRET")
        
        if not self.appkey or not self.appsecret:
            log_module.log_error(
                logger,
                "Credential Load Failed",
                "GH_APPKEY and GH_APPSECRET environment variables are required"
            )
            return False
        
        logger.info("✅ Credentials loaded from environment variables")
        return True
    
    def _save_token_to_cache(self, token: str, expiry: datetime) -> None:
        """
        Save token to cache file.
        
        Args:
            token: Access token
            expiry: Token expiration datetime
        """
        try:
            cache_data = {
                "token": token,
                "expiry": expiry.isoformat(),
                "saved_at": datetime.now().isoformat()
            }
            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
            logger.debug(f"Token cached to {self.cache_file}")
        except Exception as e:
            log_module.log_error(logger, "Token Cache Write Failed", str(e), e)
    
    def _load_token_from_cache(self) -> Optional[Tuple[str, datetime]]:
        """
        Load token from cache file if it's still valid.
        
        Returns:
            Tuple of (token, expiry) if valid cached token exists, None otherwise
        """
        if not os.path.exists(self.cache_file):
            return None
        
        try:
            with open(self.cache_file, "r") as f:
                cache_data = json.load(f)
            
            token = cache_data.get("token")
            expiry_str = cache_data.get("expiry")
            
            if not token or not expiry_str:
                return None
            
            expiry = datetime.fromisoformat(expiry_str)
            
            # Check if token is still valid (not expired)
            if datetime.now() < expiry:
                logger.info("✅ Valid cached token found, reusing for today")
                return (token, expiry)
            else:
                logger.info("Token cache expired, will request new token")
                return None
        
        except Exception as e:
            log_module.log_error(logger, "Token Cache Read Failed", str(e), e)
            return None
    
    def authenticate(self, base_url: str) -> bool:
        """
        Authenticate with Korea Investment API.
        
        Attempts to reuse cached token if valid, otherwise requests new token.
        
        Args:
            base_url: API base URL (e.g., https://openapivts.koreainvestment.com:29443)
                     Use 29443 port for mock trading (VTS), 9443 for real trading
        
        Returns:
            True if authentication successful, False otherwise
        """
        # Try to reuse cached token
        cached_result = self._load_token_from_cache()
        if cached_result:
            self.token, self.token_expiry = cached_result
            log_module.log_token_management(
                logger, 
                "Reused",
                f"Valid today (expires {self.token_expiry})"
            )
            return True
        
        # Request new token
        logger.info("Requesting new access token...")
        
        url = f"{base_url}/oauth2/tokenP"
        headers = {
            "Content-Type": "application/json",
            "charset": "UTF-8",
        }
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "appsecret": self.appsecret,
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=config.API_TIMEOUT_SECONDS
            )
            
            if response.status_code != 200:
                log_module.log_error(
                    logger,
                    "Token Request Failed",
                    f"Status {response.status_code}: {response.text}"
                )
                return False
            
            data = response.json()
            self.token = data.get("access_token")
            
            # Parse expiry time from response
            # Format: "2026-03-25 12:00:00" (1 day from now)
            expiry_str = data.get("access_token_token_expired")
            if expiry_str:
                # Try parsing as datetime string
                try:
                    self.token_expiry = datetime.strptime(
                        expiry_str, "%Y-%m-%d %H:%M:%S"
                    )
                except ValueError:
                    # Fallback: set to tomorrow
                    from datetime import timedelta
                    self.token_expiry = datetime.now() + timedelta(days=1)
            
            # Cache the token
            self._save_token_to_cache(self.token, self.token_expiry)
            
            log_module.log_token_management(
                logger,
                "Issued",
                f"Token valid until {self.token_expiry}"
            )
            return True
        
        except requests.exceptions.Timeout:
            log_module.log_error(
                logger,
                "Token Request Timeout",
                "API request timed out"
            )
            return False
        except requests.exceptions.RequestException as e:
            log_module.log_error(
                logger,
                "Token Request Error",
                f"Network error: {str(e)}",
                e
            )
            return False
    
    def get_token(self) -> Optional[str]:
        """
        Get the current access token.
        
        Returns:
            Access token if available, None otherwise
        """
        return self.token
    
    def is_valid(self) -> bool:
        """
        Check if token is still valid.
        
        Returns:
            True if token is valid, False otherwise
        """
        if not self.token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry


def create_auth_manager() -> Optional[TokenManager]:
    """
    Create and authenticate a TokenManager instance.
    
    Steps:
    1. Load credentials from environment variables
    2. Authenticate with API (mock trading URL)
    3. Return authenticated manager or None if failed
    
    Returns:
        Authenticated TokenManager or None if authentication failed
    """
    manager = TokenManager()
    
    if not manager.load_credentials():
        return None
    
    # Use VTS endpoint for mock trading (port 29443)
    # For real trading, use: https://openapi.koreainvestment.com:9443
    api_base_url = "https://openapivts.koreainvestment.com:29443"
    
    if not manager.authenticate(api_base_url):
        return None
    
    return manager
