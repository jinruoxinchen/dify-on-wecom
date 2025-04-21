from flask import Blueprint, request, jsonify, current_app
import logging
import json
import os
from datetime import datetime

from src.gewechat.client import GewechatApiClient

logger = logging.getLogger(__name__)
gewechat_bp = Blueprint('gewechat', __name__, url_prefix='/api/gewechat')

# Initialize the gewechat client
gewechat_client = GewechatApiClient()

@gewechat_bp.route('/login/qrcode', methods=['GET'])
def get_login_qrcode():
    """
    Generate a QR code for login.
    
    Returns:
        JSON response with QR code URL and token.
    """
    try:
        result = gewechat_client.get_login_qrcode()
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@gewechat_bp.route('/login/status', methods=['GET'])
def check_login_status():
    """
    Check the status of a login attempt.
    
    Query Parameters:
        token: The token received when generating the QR code.
        
    Returns:
        JSON response with login status.
    """
    token = request.args.get('token')
    
    if not token:
        return jsonify({
            "success": False,
            "message": "Token is required"
        }), 400
    
    try:
        result = gewechat_client.check_login_status(token)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        logger.error(f"Error checking login status: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@gewechat_bp.route('/config/save', methods=['POST'])
def save_config():
    """
    Save the gewechat configuration.
    
    Request Body:
        JSON object containing the gewechat configuration.
        
    Returns:
        JSON response indicating success or failure.
    """
    try:
        config = request.json
        
        if not config:
            return jsonify({
                "success": False,
                "message": "Configuration data is required"
            }), 400
        
        # Create config directory if it doesn't exist
        config_dir = os.path.join(current_app.root_path, '..', 'config')
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
        
        return jsonify({
            "success": True,
            "message": "Configuration saved successfully",
            "config_path": config_path
        }), 200
    
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@gewechat_bp.route('/message/send', methods=['POST'])
def send_message():
    """
    Send a message to a user.
    
    Request Body:
        to_user: The user ID to send the message to.
        type: The type of message (text, image, etc.).
        content: The content of the message.
        
    Returns:
        JSON response indicating success or failure.
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "message": "Message data is required"
            }), 400
        
        required_fields = ['to_user', 'type', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Field '{field}' is required"
                }), 400
        
        result = gewechat_client.send_message(
            to_user=data['to_user'],
            message_type=data['type'],
            content=data['content']
        )
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500
