from typing import Dict, Optional
from fastapi import APIRouter, Request, HTTPException
from dotenv import load_dotenv
import hmac
import hashlib
import json
import os

# 加载环境变量
load_dotenv()

# 创建路由
router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

def verify_signature(signature: str, body: str) -> bool:
    """验证WhatsApp消息签名"""
    app_secret = os.getenv("WHATSAPP_APP_SECRET")
    hmac_obj = hmac.new(
        app_secret.encode('utf-8'),
        body,
        hashlib.sha256
    )
    expected_signature = f"sha256={hmac_obj.hexdigest()}"
    return hmac.compare_digest(signature, expected_signature)

@router.post("/callback")
async def handle_message(request: Request):
    """处理WhatsApp回调消息"""
    try:
        # 获取请求头中的签名
        signature = request.headers.get("X-Hub-Signature-256")
        
        # 获取请求体
        body = await request.body()
        
        # 验证签名
        if not verify_signature(signature, body):
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # 解析消息
        body_json = json.loads(body)
        
        if "entry" in body_json:
            for entry in body_json["entry"]:
                for change in entry.get("changes", []):
                    if change.get("value", {}).get("messages"):
                        message = change["value"]["messages"][0]
                        if message.get("type") == "text":
                            content = message.get("text", {}).get("body", "")
                            
                            # TODO: 调用Dify API处理消息
                            reply_content = f"收到消息：{content}"
                            
                            # 构造回复
                            response = {
                                "messaging_product": "whatsapp",
                                "recipient_type": "individual",
                                "to": message["from"],
                                "type": "text",
                                "text": {
                                    "body": reply_content
                                }
                            }
                            
                            return response
        
        return {"msg": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
def verify_url(
    hub_mode: str,
    hub_verify_token: str,
    hub_challenge: str
) -> str:
    """验证URL有效性"""
    try:
        verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
        if hub_mode == "subscribe" and hub_verify_token == verify_token:
            return hub_challenge
        raise HTTPException(status_code=400, detail="Invalid verification token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
