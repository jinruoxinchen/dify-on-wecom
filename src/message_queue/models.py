from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class MessageType(str, Enum):
    """消息类型枚举
    
    定义系统中支持的各种消息类型
    """
    TEXT = "text"  # 文本消息
    IMAGE = "image"  # 图片消息
    VOICE = "voice"  # 语音消息
    VIDEO = "video"  # 视频消息
    FILE = "file"  # 文件消息
    LOCATION = "location"  # 位置消息
    LINK = "link"  # 链接消息
    EVENT = "event"  # 事件消息

class MessagePriority(str, Enum):
    """消息优先级枚举
    
    定义消息处理的优先级
    """
    HIGH = "high"  # 高优先级
    NORMAL = "normal"  # 普通优先级
    LOW = "low"  # 低优先级

class MessageStatus(str, Enum):
    """消息状态枚举
    
    定义消息在处理流程中的状态
    """
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 处理失败

class QueueMessage(BaseModel):
    """队列消息模型
    
    定义消息队列中传递的消息格式
    """
    # 消息基本信息
    message_id: str = Field(..., description="消息唯一标识符")
    message_type: MessageType = Field(..., description="消息类型")
    priority: MessagePriority = Field(default=MessagePriority.NORMAL, description="消息优先级")
    status: MessageStatus = Field(default=MessageStatus.PENDING, description="消息状态")
    
    # 消息内容
    content: str = Field(..., description="消息内容")
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="原始消息数据")
    
    # 消息来源信息
    from_user: str = Field(..., description="发送用户ID")
    to_user: Optional[str] = Field(default=None, description="接收用户ID")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    
    # 处理信息
    retry_count: int = Field(default=0, description="重试次数")
    max_retries: int = Field(default=3, description="最大重试次数")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    
    # 会话信息
    conversation_id: Optional[str] = Field(default=None, description="会话ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }