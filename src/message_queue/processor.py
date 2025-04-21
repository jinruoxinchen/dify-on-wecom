import logging
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from .client import RabbitMQClient
from .models import QueueMessage, MessageStatus
from ..dify.client import DifyClient

logger = logging.getLogger(__name__)

class MessageProcessor:
    """消息处理器
    
    负责从消息队列中获取消息，并根据消息类型进行处理
    """
    
    def __init__(self, rabbitmq_client: RabbitMQClient, dify_client: DifyClient):
        """初始化消息处理器
        
        Args:
            rabbitmq_client: RabbitMQ客户端实例
            dify_client: Dify API客户端实例
        """
        self.rabbitmq_client = rabbitmq_client
        self.dify_client = dify_client
        self.handlers = {}
        
        # 注册默认处理器
        self.register_default_handlers()
    
    def register_handler(self, message_type: str, handler: Callable) -> None:
        """注册消息处理器
        
        Args:
            message_type: 消息类型
            handler: 处理函数，接收消息作为参数
        """
        self.handlers[message_type] = handler
        logger.info(f"已注册消息处理器: {message_type}")
    
    def register_default_handlers(self) -> None:
        """注册默认的消息处理器"""
        # 注册文本消息处理器
        self.register_handler("text", self.handle_text_message)
        
        # 可以注册更多类型的处理器
        # self.register_handler("image", self.handle_image_message)
        # self.register_handler("voice", self.handle_voice_message)
    
    async def handle_text_message(self, message: Dict[str, Any]) -> None:
        """处理文本消息
        
        Args:
            message: 消息内容
        """
        try:
            # 更新消息状态为处理中
            message['status'] = MessageStatus.PROCESSING
            message['updated_at'] = datetime.now().isoformat()
            
            # 调用Dify API处理消息
            response = await self.call_dify_api(message)
            
            # 发送回复消息到回复队列
            await self.send_reply(message, response)
            
            # 更新消息状态为已完成
            message['status'] = MessageStatus.COMPLETED
            message['updated_at'] = datetime.now().isoformat()
            
            logger.info(f"消息处理完成: {message['message_id']}")
            
        except Exception as e:
            # 更新消息状态为失败
            message['status'] = MessageStatus.FAILED
            message['error_message'] = str(e)
            message['updated_at'] = datetime.now().isoformat()
            
            # 重试逻辑
            if message['retry_count'] < message['max_retries']:
                message['retry_count'] += 1
                logger.warning(f"消息处理失败，准备重试 ({message['retry_count']}/{message['max_retries']}): {message['message_id']}")
                await self.retry_message(message)
            else:
                logger.error(f"消息处理失败，已达到最大重试次数: {message['message_id']}")
    
    async def call_dify_api(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """调用Dify API处理消息
        
        Args:
            message: 消息内容
            
        Returns:
            Dict: Dify API的响应结果
        """
        try:
            # 从消息中提取必要信息
            user_id = message['from_user']
            content = message['content']
            conversation_id = message.get('conversation_id')
            
            # 调用Dify API
            response = self.dify_client.send_message(user_id, content, conversation_id)
            
            return response
        except Exception as e:
            logger.error(f"调用Dify API失败: {str(e)}")
            raise
    
    async def send_reply(self, message: Dict[str, Any], dify_response: Dict[str, Any]) -> None:
        """发送回复消息
        
        Args:
            message: 原始消息
            dify_response: Dify API的响应结果
        """
        try:
            # 从Dify响应中提取回复内容
            reply_content = self.dify_client.get_reply(dify_response)
            
            # 构造回复消息
            reply_message = {
                'message_id': f"reply-{message['message_id']}",
                'message_type': 'text',  # 目前只支持文本回复
                'content': reply_content,
                'from_user': 'system',  # 系统发送
                'to_user': message['from_user'],  # 发送给原消息的发送者
                'conversation_id': message.get('conversation_id'),
                'created_at': datetime.now().isoformat(),
                'status': MessageStatus.PENDING,
                'priority': message['priority'],  # 保持与原消息相同的优先级
                'retry_count': 0,
                'max_retries': 3
            }
            
            # 发布回复消息到回复队列
            self.rabbitmq_client.publish_message('wecom_reply_queue', reply_message)
            
            logger.info(f"已发送回复消息: {reply_message['message_id']}")
            
        except Exception as e:
            logger.error(f"发送回复消息失败: {str(e)}")
            raise
    
    async def retry_message(self, message: Dict[str, Any]) -> None:
        """重试处理消息
        
        Args:
            message: 消息内容
        """
        try:
            # 更新消息状态为待处理
            message['status'] = MessageStatus.PENDING
            message['updated_at'] = datetime.now().isoformat()
            
            # 重新发布消息到队列
            self.rabbitmq_client.publish_message('wecom_message_queue', message)
            
            logger.info(f"已重新发布消息: {message['message_id']}")
            
        except Exception as e:
            logger.error(f"重新发布消息失败: {str(e)}")
            raise
    
    def start_processing(self, queue_name: str = 'wecom_message_queue') -> None:
        """开始处理消息
        
        Args:
            queue_name: 队列名称
        """
        def message_handler(message: Dict[str, Any]) -> None:
            # 获取消息类型
            message_type = message.get('message_type', 'text')
            
            # 查找对应的处理器
            handler = self.handlers.get(message_type)
            
            if handler:
                # 创建异步任务
                asyncio.create_task(handler(message))
            else:
                logger.warning(f"未找到消息类型 {message_type} 的处理器")
        
        # 开始消费消息
        self.rabbitmq_client.consume_messages(queue_name, message_handler)