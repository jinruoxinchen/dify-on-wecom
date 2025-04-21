from fastapi import APIRouter, Request, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from src.gewechat.client import GewechatApiClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/gewechat", tags=["gewechat"])

# Initialize the gewechat client
gewechat_client = GewechatApiClient()

@router.get("/login/qrcode")
async def get_login_qrcode():
    """
    Generate a QR code for login.
    
    Returns:
        JSON response with QR code URL and token.
    """
    try:
        result = gewechat_client.get_login_qrcode()
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to generate QR code"))
    
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/login/status")
async def check_login_status(token: str):
    """
    Check the status of a login attempt.
    
    Args:
        token: The token received when generating the QR code.
        
    Returns:
        JSON response with login status.
    """
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    
    try:
        result = gewechat_client.check_login_status(token)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to check login status"))
    
    except Exception as e:
        logger.error(f"Error checking login status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.post("/config/save")
async def save_config(config: Dict[str, Any], request: Request):
    """
    Save the gewechat configuration.
    
    Args:
        config: JSON object containing the gewechat configuration.
        
    Returns:
        JSON response indicating success or failure.
    """
    try:
        if not config:
            raise HTTPException(status_code=400, detail="Configuration data is required")
        
        # Create config directory if it doesn't exist
        config_dir = os.path.join(os.path.dirname(request.app.openapi_schema["info"]["version"]), 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        # Save configuration to file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        config_path = os.path.join(config_dir, f'gewechat_config_{timestamp}.json')
        
        # Add timestamp to the configuration
        config['timestamp'] = timestamp
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # Also save to a static file for easy access
        latest_config_path = os.path.join(config_dir, 'gewechat_config_latest.json')
        with open(latest_config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": "Configuration saved successfully",
            "config_path": config_path
        }
    
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


class MessageRequest:
    def __init__(self, to_user: str, type: str, content: str):
        self.to_user = to_user
        self.type = type
        self.content = content


@router.post("/message/send")
async def send_message(message: Dict[str, Any]):
    """
    Send a message to a user.
    
    Args:
        message: Dictionary containing message details
            - to_user: The user ID to send the message to.
            - type: The type of message (text, image, etc.).
            - content: The content of the message.
        
    Returns:
        JSON response indicating success or failure.
    """
    try:
        required_fields = ['to_user', 'type', 'content']
        for field in required_fields:
            if field not in message:
                raise HTTPException(status_code=400, detail=f"Field '{field}' is required")
        
        result = gewechat_client.send_message(
            to_user=message['to_user'],
            message_type=message['type'],
            content=message['content']
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to send message"))
    
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
