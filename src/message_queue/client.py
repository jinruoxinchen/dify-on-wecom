import pika
import json
import logging
from typing import Dict, Any, Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)

class RabbitMQClient:
    """RabbitMQ客户端
    
    该客户端负责与RabbitMQ服务器通信，处理消息的发送和接收
    """
    
    def __init__(self, host: str = 'localhost', port: int = 5672, 
                 username: str = 'guest', password: str = 'guest',
                 virtual_host: str = '/'):
        """初始化RabbitMQ客户端
        
        Args:
            host: RabbitMQ服务器地址
            port: RabbitMQ服务器端口
            username: RabbitMQ用户名
            password: RabbitMQ密码
            virtual_host: RabbitMQ虚拟主机
        """
        self.connection_params = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=pika.PlainCredentials(username, password)
        )
        self.connection = None
        self.channel = None
    
    def connect(self) -> None:
        """连接到RabbitMQ服务器"""
        try:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            logger.info("成功连接到RabbitMQ服务器")
        except Exception as e:
            logger.error(f"连接RabbitMQ服务器失败: {str(e)}")
            raise
    
    def close(self) -> None:
        """关闭与RabbitMQ服务器的连接"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("已关闭与RabbitMQ服务器的连接")
    
    def ensure_connection(method):
        """确保连接装饰器
        
        确保在调用方法前已经建立了与RabbitMQ的连接
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.connection or not self.connection.is_open:
                self.connect()
            return method(self, *args, **kwargs)
        return wrapper
    
    @ensure_connection
    def declare_queue(self, queue_name: str, durable: bool = True) -> None:
        """声明队列
        
        Args:
            queue_name: 队列名称
            durable: 是否持久化
        """
        self.channel.queue_declare(queue=queue_name, durable=durable)
        logger.info(f"已声明队列: {queue_name}")
    
    @ensure_connection
    def publish_message(self, queue_name: str, message: Dict[str, Any], 
                       persistent: bool = True) -> None:
        """发布消息到队列
        
        Args:
            queue_name: 队列名称
            message: 消息内容，将被转换为JSON字符串
            persistent: 是否持久化消息
        """
        # 确保队列存在
        self.declare_queue(queue_name)
        
        # 发布消息
        properties = pika.BasicProperties(
            delivery_mode=2 if persistent else 1  # 2表示持久化
        )
        
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=properties
        )
        
        logger.info(f"已发布消息到队列 {queue_name}: {message}")
    
    @ensure_connection
    def consume_messages(self, queue_name: str, callback: Callable, 
                        auto_ack: bool = False) -> None:
        """从队列消费消息
        
        Args:
            queue_name: 队列名称
            callback: 回调函数，接收消息体作为参数
            auto_ack: 是否自动确认消息
        """
        # 确保队列存在
        self.declare_queue(queue_name)
        
        # 定义回调包装器，处理JSON解析
        def callback_wrapper(ch, method, properties, body):
            try:
                message = json.loads(body)
                callback(message)
                if not auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except json.JSONDecodeError:
                logger.error(f"解析消息失败: {body}")
                if not auto_ack:
                    # 消息格式错误，仍然确认以避免消息堆积
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"处理消息时发生错误: {str(e)}")
                if not auto_ack:
                    # 处理失败，拒绝消息并重新入队
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # 设置QoS，每次只处理一条消息
        self.channel.basic_qos(prefetch_count=1)
        
        # 开始消费
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback_wrapper,
            auto_ack=auto_ack
        )
        
        logger.info(f"开始从队列 {queue_name} 消费消息")
        
        # 开始事件循环
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            logger.info("已停止消费消息")
        except Exception as e:
            self.channel.stop_consuming()
            logger.error(f"消费消息时发生错误: {str(e)}")
            raise