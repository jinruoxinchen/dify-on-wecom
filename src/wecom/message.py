from typing import Dict, Optional, Union
import uuid
from fastapi import APIRouter, Request, HTTPException, Depends
from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException as InvalidSignatureError
from wechatpy.enterprise.messages import TextMessage
from wechatpy.messages import BaseMessage
from wechatpy.enterprise.replies import TextReply
from dotenv import load_dotenv
import os
import logging

from ..message_queue.client import RabbitMQClient
from ..message_queue.models import MessageType, MessagePriority, MessageStatus
from ..dify.client import DifyClient
from .client import WeComClient
from .message_handler import WeComMessageHandler

# 加载环境变量
load_dotenv()

# 创建路由
router = APIRouter(prefix="/wecom", tags=["wecom"])

# 初始化日志
logger = logging.getLogger(__name__)

# 初始化微信加密类
crypto = WeChatCrypto(
    token=os.getenv("WECHAT_TOKEN"),
    encoding_aes_key=os.getenv("WECHAT_ENCODING_AES_KEY"),
    corp_id=os.getenv("WECHAT_CORP_ID")
)

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

# 初始化企业微信客户端
wecom_client = WeComClient()

# 初始化消息处理器
message_handler = WeComMessageHandler(wecom_client, dify_client)

def get_rabbitmq_client():
    """获取RabbitMQ客户端实例"""
    return rabbitmq_client

@router.post("/callback")
async def handle_message(request: Request, mq_client: RabbitMQClient = Depends(get_rabbitmq_client)):
    """处理微信回调消息
    
    将消息放入消息队列进行异步处理，并立即返回确认消息
    """
    try:
        # 获取请求参数
        params = request.query_params
        msg_signature = params.get("msg_signature")
        timestamp = params.get("timestamp")
        nonce = params.get("nonce")
        
        # 获取请求体
        body = await request.body()
        xml_content = body.decode()
        
        # 解密消息
        decrypted_xml = crypto.decrypt_message(
            xml_content,
            msg_signature,
            timestamp,
            nonce
        )
        
        # 解析消息
        msg = BaseMessage.from_xml(decrypted_xml)
        
        # 生成消息ID
        message_id = str(uuid.uuid4())
        
        # 构造队列消息
        queue_message = {
            'message_id': message_id,
            'message_type': msg.type,  # 使用消息的实际类型
            'content': getattr(msg, 'content', '') if hasattr(msg, 'content') else '',
            'from_user': msg.source,
            'to_user': msg.target,
            'raw_data': {
                'xml': decrypted_xml,
                'msg_type': msg.type,
                'msg_id': getattr(msg, 'id', None),
                'create_time': getattr(msg, 'create_time', None),
            },
            'priority': MessagePriority.NORMAL,
            'status': MessageStatus.PENDING,
            'retry_count': 0,
            'max_retries': 3
        }
        
        # 发布消息到队列
        mq_client.publish_message('wecom_message_queue', queue_message)
        logger.info(f"已将消息 {message_id} 发送到队列")
        
        # 使用消息处理器处理消息并获取回复
        reply = await message_handler.handle_message(msg)
        
        # 加密回复
        encrypted_reply = crypto.encrypt_message(
            reply.render(),
            nonce,
            timestamp
        )
        
        return encrypted_reply
        
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
def verify_url(
    msg_signature: str,
    timestamp: str,
    nonce: str,
    echostr: str
) -> str:
    """验证URL有效性"""
    try:
        decrypted_echo = crypto.decrypt_message(
            echostr,
            msg_signature,
            timestamp,
            nonce
        )
        return decrypted_echo
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
