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
router = APIRouter(prefix="/dingtalk", tags=["dingtalk"])

def verify_signature(timestamp: str, signature: str) -> bool:
    """验证钉钉消息签名"""
    secret = os.getenv("DINGTALK_SECRET")
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    return signature == base64.b64encode(hmac_code).decode('utf-8')

@router.post("/callback")
async def handle_message(request: Request):
    """处理钉钉回调消息"""
    try:
        # 获取请求头中的签名信息
        timestamp = request.headers.get("timestamp")
        signature = request.headers.get("sign")
        
        # 验证签名
        if not verify_signature(timestamp, signature):
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # 获取请求体
        body = await request.json()
        
        # 解析消息
        msg_type = body.get("msgtype")
        if msg_type != "text":
            return {"msg": "success"}
            
        content = body.get("text", {}).get("content", "")
        
        # TODO: 调用Dify API处理消息
        reply_content = f"收到消息：{content}"
        
        # 构造回复
        response = {
            "msgtype": "text",
            "text": {
                "content": reply_content
            }
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
def verify_url(timestamp: str, signature: str) -> Dict:
    """验证URL有效性"""
    try:
        if verify_signature(timestamp, signature):
            return {"success": True}
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
