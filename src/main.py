from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import os
import threading
import logging

# 导入路由模块
from src.wecom.message import router as wecom_router
from src.gewechat.routes import router as gewechat_router

# 导入消息队列模块
from src.message_queue.client import RabbitMQClient
from src.message_queue.processor import MessageProcessor
from src.dify.client import DifyClient

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="微信企业级智能客服后台服务",
    description="基于微信客服API和Dify的智能客服后台服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(wecom_router)
app.include_router(gewechat_router)

# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "ok", "services": {"message_queue": "active"}}

# 初始化消息队列处理器
def init_message_processor():
    try:
        # 初始化RabbitMQ客户端
        rabbitmq_client = RabbitMQClient(
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            port=int(os.getenv("RABBITMQ_PORT", "5672")),
            username=os.getenv("RABBITMQ_USERNAME", "guest"),
            password=os.getenv("RABBITMQ_PASSWORD", "guest"),
            virtual_host=os.getenv("RABBITMQ_VHOST", "/")
        )
        
        # 初始化Dify客户端
        dify_client = DifyClient()
        
        # 初始化消息处理器
        processor = MessageProcessor(rabbitmq_client, dify_client)
        
        # 启动消息处理
        logger.info("启动消息处理器...")
        processor.start_processing()
        
    except Exception as e:
        logger.error(f"初始化消息处理器失败: {str(e)}")

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    # 在单独的线程中启动消息处理器
    threading.Thread(target=init_message_processor, daemon=True).start()
    logger.info("应用启动完成，消息队列处理器已初始化")

# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("应用关闭，停止所有服务")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
