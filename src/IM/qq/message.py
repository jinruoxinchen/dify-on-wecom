from typing import Dict, Optional
from fastapi import APIRouter, Request, HTTPException
from dotenv import load_dotenv
import hashlib
import json
import os

# 加载环境变量
load_dotenv()

# 创建路由
router = APIRouter(prefix="/qq", tags=["qq"])

def verify_signature(signature: str, timestamp: str, nonce: str) -> bool:
    """验证QQ消息签名"""
    token = os.getenv("QQ_TOKEN")
    params = [token, timestamp, nonce]
    params.sort()
    string_to_sign = ''.join(params)
    sha1 = hashlib.sha1()
    sha1.update(string_to_sign.encode('utf-8'))
    return signature == sha1.hexdigest()

@router.post("/callback")
async def handle_message(request: Request):
    """处理QQ回调消息"""
    try:
        # 获取请求参数
        params = request.query_params
        signature = params.get("signature")
        timestamp = params.get("timestamp")
        nonce = params.get("nonce")
        
        # 验证签名
        if not verify_signature(signature, timestamp, nonce):
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # 获取请求体
        body = await request.json()
        
        # 解析消息
        post_type = body.get("post_type")
        
        if post_type == "message":
            message_type = body.get("message_type")
            if message_type == "private":
                user_id = body.get("user_id")
                content = body.get("message", "")
                
                # TODO: 调用Dify API处理消息
                reply_content = f"收到消息：{content}"
                
                # 构造回复
                response = {
                    "reply": reply_content,
                    "auto_escape": False
                }
                
                return response
        
        return {"msg": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
def verify_url(
    signature: str,
    timestamp: str,
    nonce: str,
    echo: str
) -> str:
    """验证URL有效性"""
    try:
        if verify_signature(signature, timestamp, nonce):
            return echo
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
