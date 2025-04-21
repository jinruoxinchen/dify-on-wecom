from typing import Dict, Optional
from fastapi import APIRouter, Request, HTTPException
from dotenv import load_dotenv
import hmac
import hashlib
import base64
import json
import os

# 加载环境变量
load_dotenv()

# 创建路由
router = APIRouter(prefix="/feishu", tags=["feishu"])

def verify_signature(timestamp: str, signature: str, body: str) -> bool:
    """验证飞书消息签名"""
    secret = os.getenv("FEISHU_SECRET")
    string_to_sign = f"{timestamp}\n{body}"
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    return signature == base64.b64encode(hmac_code).decode('utf-8')

@router.post("/callback")
async def handle_message(request: Request):
    """处理飞书回调消息"""
    try:
        # 获取请求头中的签名信息
        timestamp = request.headers.get("X-Lark-Request-Timestamp")
        signature = request.headers.get("X-Lark-Signature")
        
        # 获取请求体
        body = await request.body()
        body_str = body.decode()
        
        # 验证签名
        if not verify_signature(timestamp, signature, body_str):
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # 解析消息
        body_json = json.loads(body_str)
        event_type = body_json.get("type")
        
        if event_type == "message":
            content = body_json.get("event", {}).get("message", {}).get("content", "")
            
            # TODO: 调用Dify API处理消息
            reply_content = f"收到消息：{content}"
            
            # 构造回复
            response = {
                "msg_type": "text",
                "content": {
                    "text": reply_content
                }
            }
            
            return response
            
        return {"msg": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
def verify_url(
    challenge: str,
    timestamp: str,
    signature: str
) -> Dict:
    """验证URL有效性"""
    try:
        if verify_signature(timestamp, signature, challenge):
            return {"challenge": challenge}
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
