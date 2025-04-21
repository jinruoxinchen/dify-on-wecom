import logging
from typing import Dict, Any, Optional, Union, List
from gewechat.messages import (
    TextMessage,
    ImageMessage,
    VoiceMessage,
    VideoMessage,
    LocationMessage,
    EventMessage,
    BaseMessage
)
from gewechat.replies import (
    TextReply,
    ImageReply,
    VoiceReply,
    VideoReply,
    ArticlesReply,
    Article,
    BaseReply
)

from .client import WeComClient
from ..dify.client import DifyClient

logger = logging.getLogger(__name__)

class WeComMessageHandler:
    """企业微信消息处理器
    
    该类负责处理从企业微信接收到的各种类型的消息，并生成相应的回复
    """
    
    def __init__(self, wecom_client: WeComClient, dify_client: DifyClient):
        """初始化消息处理器
        
        Args:
            wecom_client: 企业微信客户端实例
            dify_client: Dify API客户端实例
        """
        self.wecom_client = wecom_client
        self.dify_client = dify_client
    
    async def handle_message(self, message: BaseMessage) -> BaseReply:
        """处理消息
        
        根据消息类型调用相应的处理方法
        
        Args:
            message: 企业微信消息对象
            
        Returns:
            BaseReply: 回复消息对象
        """
        # 根据消息类型分发到不同的处理方法
        if isinstance(message, TextMessage):
            return await self.handle_text_message(message)
        elif isinstance(message, ImageMessage):
            return await self.handle_image_message(message)
        elif isinstance(message, VoiceMessage):
            return await self.handle_voice_message(message)
        elif isinstance(message, VideoMessage):
            return await self.handle_video_message(message)
        elif isinstance(message, LocationMessage):
            return await self.handle_location_message(message)
        elif isinstance(message, EventMessage):
            return await self.handle_event_message(message)
        else:
            # 默认处理方法
            return self.create_text_reply(message, "暂不支持处理此类型的消息")
    
    async def handle_text_message(self, message: TextMessage) -> BaseReply:
        """处理文本消息
        
        Args:
            message: 文本消息对象
            
        Returns:
            BaseReply: 回复消息对象
        """
        try:
            # 获取用户ID和消息内容
            user_id = message.source
            content = message.content
            
            # 调用Dify API处理消息
            response = self.dify_client.send_message(user_id, content)
            
            # 从响应中提取回复内容
            reply_content = self.dify_client.get_reply(response)
            
            # 创建回复消息
            return self.create_text_reply(message, reply_content)
            
        except Exception as e:
            logger.error(f"处理文本消息异常: {str(e)}")
            return self.create_text_reply(message, "处理消息时发生错误，请稍后再试")
    
    async def handle_image_message(self, message: ImageMessage) -> BaseReply:
        """处理图片消息
        
        Args:
            message: 图片消息对象
            
        Returns:
            BaseReply: 回复消息对象
        """
        # 目前简单回复，后续可以实现图片处理逻辑
        return self.create_text_reply(message, "已收到您的图片，但暂不支持图片处理")
    
    async def handle_voice_message(self, message: VoiceMessage) -> BaseReply:
        """处理语音消息
        
        Args:
            message: 语音消息对象
            
        Returns:
            BaseReply: 回复消息对象
        """
        # 目前简单回复，后续可以实现语音识别和处理逻辑
        return self.create_text_reply(message, "已收到您的语音，但暂不支持语音处理")
    
    async def handle_video_message(self, message: VideoMessage) -> BaseReply:
        """处理视频消息
        
        Args:
            message: 视频消息对象
            
        Returns:
            BaseReply: 回复消息对象
        """
        # 目前简单回复，后续可以实现视频处理逻辑
        return self.create_text_reply(message, "已收到您的视频，但暂不支持视频处理")
    
    async def handle_location_message(self, message: LocationMessage) -> BaseReply:
        """处理位置消息
        
        Args:
            message: 位置消息对象
            
        Returns:
            BaseReply: 回复消息对象
        """
        # 提取位置信息
        location = f"纬度: {message.latitude}, 经度: {message.longitude}, 位置: {message.label}"
        return self.create_text_reply(message, f"已收到您的位置信息: {location}")
    
    async def handle_event_message(self, message: EventMessage) -> BaseReply:
        """处理事件消息
        
        Args:
            message: 事件消息对象
            
        Returns:
            BaseReply: 回复消息对象
        """
        # 根据事件类型处理
        event_type = message.event
        if event_type == 'subscribe':
            # 处理关注事件
            return self.create_text_reply(message, "感谢您的关注！")
        elif event_type == 'unsubscribe':
            # 处理取消关注事件
            logger.info(f"用户 {message.source} 取消了关注")
            return None  # 取消关注事件不需要回复
        elif event_type == 'click':
            # 处理菜单点击事件
            return self.handle_menu_click(message)
        else:
            # 其他事件类型
            logger.info(f"收到未处理的事件类型: {event_type}")
            return None  # 默认不回复
    
    def handle_menu_click(self, message: EventMessage) -> BaseReply:
        """处理菜单点击事件
        
        Args:
            message: 事件消息对象
            
        Returns:
            BaseReply: 回复消息对象
        """
        # 获取菜单KEY
        key = message.key
        
        # 根据不同的菜单项返回不同的回复
        if key == 'HELP':
            return self.create_text_reply(message, "这是帮助信息...")
        elif key == 'ABOUT':
            return self.create_text_reply(message, "关于我们...")
        else:
            return self.create_text_reply(message, f"您点击了菜单: {key}")
    
    def create_text_reply(self, message: BaseMessage, content: str) -> TextReply:
        """创建文本回复
        
        Args:
            message: 原始消息对象
            content: 回复内容
            
        Returns:
            TextReply: 文本回复对象
        """
        return TextReply(message=message, content=content)
    
    def create_image_reply(self, message: BaseMessage, media_id: str) -> ImageReply:
        """创建图片回复
        
        Args:
            message: 原始消息对象
            media_id: 媒体文件ID
            
        Returns:
            ImageReply: 图片回复对象
        """
        return ImageReply(message=message, media_id=media_id)
    
    def create_voice_reply(self, message: BaseMessage, media_id: str) -> VoiceReply:
        """创建语音回复
        
        Args:
            message: 原始消息对象
            media_id: 媒体文件ID
            
        Returns:
            VoiceReply: 语音回复对象
        """
        return VoiceReply(message=message, media_id=media_id)
    
    def create_video_reply(self, message: BaseMessage, media_id: str, title: Optional[str] = None, description: Optional[str] = None) -> VideoReply:
        """创建视频回复
        
        Args:
            message: 原始消息对象
            media_id: 媒体文件ID
            title: 视频标题
            description: 视频描述
            
        Returns:
            VideoReply: 视频回复对象
        """
        return VideoReply(message=message, media_id=media_id, title=title, description=description)
    
    def create_articles_reply(self, message: BaseMessage, articles: List[Dict[str, str]]) -> ArticlesReply:
        """创建图文回复
        
        Args:
            message: 原始消息对象
            articles: 图文消息列表，每个元素包含title, description, image, url字段
            
        Returns:
            ArticlesReply: 图文回复对象
        """
        # 创建Article对象列表
        article_objects = []
        for article in articles:
            article_obj = Article(
                title=article.get('title', ''),
                description=article.get('description', ''),
                image=article.get('image', ''),
                url=article.get('url', '')
            )
            article_objects.append(article_obj)
        
        # 创建图文回复
        return ArticlesReply(message=message, articles=article_objects)
