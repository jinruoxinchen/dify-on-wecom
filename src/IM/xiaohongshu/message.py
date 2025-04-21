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
router = APIRouter(prefix="/xiaohongshu", tags=["xiaohongshu"])

def verify_signature(timestamp: str, signature: str, body: str) -> bool:
    """验证小红书消息签名"""
    secret = os.getenv("XHS_SECRET")
    string_to_sign = f"{timestamp}\n{body}"
    hmac_code = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return signature == hmac_code

@router.post("/callback")
async def handle_message(request: Request):
    """处理小红书回调消息"""
    try:
        # 获取请求头中的签名信息
        timestamp = request.headers.get("X-XHS-Timestamp")
        signature = request.headers.get("X-XHS-Signature")
        
        # 获取请求体
        body = await request.body()
        body_str = body.decode()
        
        # 验证签名
        if not verify_signature(timestamp, signature, body_str):
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # 解析消息
        body_json = json.loads(body_str)
        msg_type = body_json.get("type")
        
        if msg_type == "message":
            content = body_json.get("content", "")
            
            # TODO: 调用Dify API处理消息
            reply_content = f"收到消息：{content}"
            
            # 构造回复
            response = {
                "type": "text",
                "content": reply_content
            }
            
            return response
            
        return {"msg": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
def verify_url(
    signature: str,
    timestamp: str,
    challenge: str
) -> Dict:
    """验证URL有效性"""
    try:
        if verify_signature(timestamp, signature, challenge):
            return {"challenge": challenge}
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
