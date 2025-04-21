import json
import logging
import requests
from urllib.parse import urljoin
import os
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class GewechatApiClient:
    """
    API client for interacting with the Gewechat service.
    
    This client provides methods to interact with the Gewechat API, including:
    - Generating QR codes for login
    - Checking login status
    - Sending messages
    - Receiving messages
    """
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Initialize the Gewechat API client.
        
        Args:
            base_url: The base URL of the Gewechat API. Defaults to the value in the environment.
            api_key: The API key for authentication. Defaults to the value in the environment.
        """
        self.base_url = base_url or os.environ.get("GEWECHAT_API_URL", "http://gewechat:2531")
        self.api_key = api_key or os.environ.get("GEWECHAT_API_KEY", "342dfws111f504edaacc597a7b1brewfd")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Key": self.api_key
        })
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Tuple[Dict, int]:
        """
        Make a request to the Gewechat API.
        
        Args:
            method: The HTTP method to use (GET, POST, etc.).
            endpoint: The API endpoint to call.
            params: Query parameters to include in the request.
            data: JSON data to include in the request body.
            
        Returns:
            Tuple containing the JSON response and the HTTP status code.
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Attempt to parse JSON response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"success": False, "message": "Invalid JSON response from server"}
            
            return response_data, response.status_code
            
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {"success": False, "message": f"Request error: {str(e)}"}, 500
    
    def get_login_qrcode(self) -> Dict[str, Any]:
        """
        Generate a QR code for login.
        
        Returns:
            A dictionary containing the QR code URL and token.
        """
        # Based on investigated API, the endpoint would likely be something like:
        response_data, status_code = self._make_request("GET", "/api/wechat/login/qrcode")
        
        if status_code == 200 and response_data.get("success", False):
            return {
                "success": True,
                "qrcodeUrl": response_data.get("qrcode_url"),
                "token": response_data.get("token")
            }
        else:
            return {
                "success": False,
                "message": response_data.get("message", "Failed to generate QR code")
            }
    
    def check_login_status(self, token: str) -> Dict[str, Any]:
        """
        Check the status of a login attempt.
        
        Args:
            token: The token received when generating the QR code.
            
        Returns:
            A dictionary containing the login status.
        """
        response_data, status_code = self._make_request(
            "GET", 
            "/api/wechat/login/status", 
            params={"token": token}
        )
        
        if status_code == 200 and response_data.get("success", False):
            return {
                "success": True,
                "status": response_data.get("status", 0),
                "accountInfo": response_data.get("account_info", {}),
                "config": response_data.get("config", {})
            }
        else:
            return {
                "success": False,
                "message": response_data.get("message", "Failed to check login status")
            }
    
    def send_message(self, to_user: str, message_type: str, content: str) -> Dict[str, Any]:
        """
        Send a message to a user.
        
        Args:
            to_user: The user ID to send the message to.
            message_type: The type of message (text, image, etc.).
            content: The content of the message.
            
        Returns:
            A dictionary indicating success or failure.
        """
        data = {
            "to_user": to_user,
            "type": message_type,
            "content": content
        }
        
        response_data, status_code = self._make_request("POST", "/api/wechat/message/send", data=data)
        
        if status_code == 200 and response_data.get("success", False):
            return {
                "success": True,
                "messageId": response_data.get("message_id")
            }
        else:
            return {
                "success": False,
                "message": response_data.get("message", "Failed to send message")
            }
