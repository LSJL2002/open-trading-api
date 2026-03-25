"""
Low-level REST API client for Korea Investment Open API.

Handles:
- HTTP GET/POST requests
- Headers and authentication
- Response parsing
- Error handling and retries
"""

import json
import time
from typing import Optional, Dict, Any

import requests

import config
import logger as log_module

logger = log_module.setup_logger(__name__)


class APIClient:
    """REST API client for Korea Investment Open API."""
    
    def __init__(self, token: str, mock_trading: bool = True):
        """
        Initialize API client.
        
        Args:
            token: Access token for API authentication
            mock_trading: If True use mock trading endpoint, else real trading
        """
        self.token = token
        self.mock_trading = mock_trading
        
        # Use VTS (Virtual Trading System) endpoint for mock trading
        # Use production endpoint for real trading
        if mock_trading:
            self.base_url = "https://openapivts.koreainvestment.com:29443"
        else:
            self.base_url = "https://openapi.koreainvestment.com:9443"
        
        logger.info(f"API Client initialized. Trading mode: {'MOCK' if mock_trading else 'REAL'}")
    
    def _get_headers(self, tr_id: str, post: bool = False) -> Dict[str, str]:
        """
        Build request headers for API call.
        
        Args:
            tr_id: Transaction ID (API identifier)
            post: If True, add headers for POST request
        
        Returns:
            Headers dictionary
        """
        headers = {
            "Content-Type": "application/json",            "Accept": "text/plain",            "Authorization": f"Bearer {self.token}",
            "charset": "UTF-8",
            "tr_id": tr_id,
            "custtype": "P",  # Personal customer
            "tr-cont": "",    # No continuation
        }
        return headers
    
    def get(
        self,
        endpoint: str,
        tr_id: str,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Make GET request to API.
        
        Args:
            endpoint: API endpoint (e.g., "/uapi/domestic-stock/v1/quotations/inquire-price")
            tr_id: Transaction ID (API identifier)
            params: Query parameters
            retry_count: Internal retry counter (used during recursion)
        
        Returns:
            Response JSON as dict, or None if request failed
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(tr_id, post=False)
        
        log_module.log_api_call(logger, "GET", endpoint, params)
        
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params or {},
                timeout=config.API_TIMEOUT_SECONDS,
                verify=False  # Disable SSL verification for mock trading
            )
            
            # Log response status
            is_success = response.status_code == 200
            log_module.log_api_response(
                logger,
                response.status_code,
                is_success,
                f"GET {endpoint}"
            )
            
            if is_success:
                return response.json()
            else:
                # Log error details
                try:
                    error_data = response.json()
                    logger.warning(f"API Error: {error_data}")
                except:
                    logger.warning(f"API Error: {response.text}")
                return None
        
        except requests.exceptions.Timeout:
            log_module.log_error(logger, "API Timeout", f"GET {endpoint} timed out")
            if retry_count < config.MAX_RETRIES:
                wait_time = config.RETRY_BACKOFF_SECONDS * (retry_count + 1)
                logger.info(f"Retrying after {wait_time}s (attempt {retry_count + 1}/{config.MAX_RETRIES})")
                time.sleep(wait_time)
                return self.get(endpoint, tr_id, params, retry_count + 1)
            return None
        
        except requests.exceptions.RequestException as e:
            log_module.log_error(logger, "API Request Error", f"GET {endpoint}", e)
            return None
    
    def post(
        self,
        endpoint: str,
        tr_id: str,
        payload: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Make POST request to API.
        
        Used for placing orders and other state-changing operations.
        
        Args:
            endpoint: API endpoint
            tr_id: Transaction ID
            payload: Request body as dictionary
            retry_count: Internal retry counter
        
        Returns:
            Response JSON as dict, or None if request failed
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(tr_id, post=True)
        
        log_module.log_api_call(logger, "POST", endpoint, payload)
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload or {}),
                timeout=config.API_TIMEOUT_SECONDS,
                verify=False  # Disable SSL verification for mock trading
            )
            
            # Log response status
            is_success = response.status_code == 200
            log_module.log_api_response(
                logger,
                response.status_code,
                is_success,
                f"POST {endpoint}"
            )
            
            if is_success:
                return response.json()
            else:
                # Log error details
                try:
                    error_data = response.json()
                    logger.warning(f"API Error: {error_data}")
                except:
                    logger.warning(f"API Error: {response.text}")
                return None
        
        except requests.exceptions.Timeout:
            log_module.log_error(logger, "API Timeout", f"POST {endpoint} timed out")
            if retry_count < config.MAX_RETRIES:
                wait_time = config.RETRY_BACKOFF_SECONDS * (retry_count + 1)
                logger.info(f"Retrying after {wait_time}s (attempt {retry_count + 1}/{config.MAX_RETRIES})")
                time.sleep(wait_time)
                return self.post(endpoint, tr_id, payload, retry_count + 1)
            return None
        
        except requests.exceptions.RequestException as e:
            log_module.log_error(logger, "API Request Error", f"POST {endpoint}", e)
            return None
