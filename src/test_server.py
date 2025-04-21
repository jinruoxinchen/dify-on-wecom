#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试用简易后端服务器
提供基本的API端点用于测试
"""

import os
import json
import logging
import datetime
from fastapi import FastAPI, Request, Response, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

# 初始化FastAPI应用
app = FastAPI(
    title="Dify-on-WeChat 测试服务器",
    description="用于测试Docker部署的简易API服务",
    version="0.1.0",
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "../logs/test_server.log"))
    ]
)
logger = logging.getLogger(__name__)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存存储模拟DB
messages_db = []
webhooks_db = []

# 请求模型
class MessageRequest(BaseModel):
    content: str
    sender: str
    timestamp: Optional[datetime.datetime] = None

class WebhookRequest(BaseModel):
    event: str
    data: Dict[str, Any]

# 响应模型
class MessageResponse(BaseModel):
    id: str
    content: str
    sender: str
    timestamp: datetime.datetime
    status: str

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime.datetime
    services: Dict[str, str]

class StatusResponse(BaseModel):
    status: str
    message: str

# 路由
@app.get("/", tags=["Root"])
async def root():
    """根路径，返回API信息"""
    return {
        "api": "Dify-on-WeChat 测试服务器",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """健康检查接口"""
    logger.info("收到健康检查请求")
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": datetime.datetime.now(),
        "services": {
            "api": "running",
            "db": "simulated",
            "rabbitmq": "connected" if os.environ.get("RABBITMQ_HOST") else "not_configured"
        }
    }

@app.get("/api/messages", tags=["Messages"])
async def get_messages():
    """获取所有消息"""
    logger.info(f"获取消息列表，当前有 {len(messages_db)} 条消息")
    return messages_db

@app.post("/api/messages", response_model=MessageResponse, tags=["Messages"])
async def create_message(message: MessageRequest):
    """创建新消息"""
    message_id = f"msg_{len(messages_db) + 1}"
    timestamp = message.timestamp or datetime.datetime.now()
    
    new_message = {
        "id": message_id,
        "content": message.content,
        "sender": message.sender,
        "timestamp": timestamp,
        "status": "received"
    }
    
    messages_db.append(new_message)
    logger.info(f"创建新消息: {message_id}")
    return new_message

@app.get("/wecom/callback", tags=["WeChat"])
async def wecom_echo(
    msg_signature: str, 
    timestamp: str, 
    nonce: str, 
    echostr: Optional[str] = None
):
    """处理企业微信回调验证请求"""
    logger.info(f"企业微信回调验证: msg_signature={msg_signature}, timestamp={timestamp}, nonce={nonce}")
    
    # 在实际实现中，这里需要验证签名
    # 这里简化处理，直接返回echostr
    if echostr:
        return Response(content=echostr, media_type="text/plain")
    return {"status": "success"}

@app.post("/wecom/callback", tags=["WeChat"])
async def wecom_message(request: Request):
    """处理企业微信消息回调"""
    try:
        body = await request.body()
        logger.info(f"收到企业微信回调: {body.decode('utf-8')}")
        
        # 在实际实现中，这里需要解密消息
        # 这里简化处理，返回成功
        return {
            "status": "success",
            "message": "回调消息已接收"
        }
    except Exception as e:
        logger.error(f"处理企业微信回调时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhooks/dify", tags=["Webhooks"])
async def dify_webhook(webhook: WebhookRequest):
    """处理Dify回调"""
    webhooks_db.append({
        "event": webhook.event,
        "data": webhook.data,
        "timestamp": datetime.datetime.now()
    })
    
    logger.info(f"收到Dify回调: {webhook.event}")
    return {"status": "success"}

@app.get("/test/error", tags=["Testing"])
async def test_error():
    """测试错误响应"""
    logger.error("测试错误端点被调用")
    raise HTTPException(status_code=500, detail="这是一个测试错误")

@app.get("/test/delay/{seconds}", tags=["Testing"])
async def test_delay(seconds: int):
    """测试延迟响应"""
    import asyncio
    if seconds > 30:
        seconds = 30  # 限制最大延迟
        
    logger.info(f"测试延迟端点被调用，延迟 {seconds} 秒")
    await asyncio.sleep(seconds)
    return {"status": "success", "delay": f"{seconds}s"}

# 主入口
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"启动测试服务器，端口: {port}")
    uvicorn.run("test_server:app", host="0.0.0.0", port=port, reload=True)
