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
router = APIRouter(prefix="/telegram", tags=["telegram"])

@router.post("/callback")
async def handle_message(request: Request):
    """处理Telegram回调消息"""
    try:
        # 获取请求体
        body = await request.json()
        
        # 解析消息
        if "message" in body:
            message = body["message"]
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")
            
            # TODO: 调用Dify API处理消息
            reply_content = f"收到消息：{text}"
            
            # 构造回复
            response = {
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": reply_content
            }
            
            return response
            
        return {"msg": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
def verify_url() -> Dict:
    """验证URL有效性"""
    try:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if bot_token:
            return {"status": "ok"}
        raise HTTPException(status_code=400, detail="Bot token not configured")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
