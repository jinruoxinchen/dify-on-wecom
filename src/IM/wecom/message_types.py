from enum import Enum
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

class MessageType(str, Enum):
    """企业微信消息类型枚举
    
    定义企业微信支持的各种消息类型
    """
    TEXT = "text"  # 文本消息
    IMAGE = "image"  # 图片消息
    VOICE = "voice"  # 语音消息
    VIDEO = "video"  # 视频消息
    FILE = "file"  # 文件消息
    LOCATION = "location"  # 位置消息
    LINK = "link"  # 链接消息
    EVENT = "event"  # 事件消息
    MARKDOWN = "markdown"  # markdown消息
    MINIPROGRAM = "miniprogram"  # 小程序消息
    TEMPLATE_CARD = "template_card"  # 模板卡片消息

class EventType(str, Enum):
    """企业微信事件类型枚举
    
    定义企业微信支持的各种事件类型
    """
    SUBSCRIBE = "subscribe"  # 关注事件
    UNSUBSCRIBE = "unsubscribe"  # 取消关注事件
    CLICK = "click"  # 菜单点击事件
    VIEW = "view"  # 菜单链接点击事件
    LOCATION = "LOCATION"  # 上报地理位置事件
    ENTER_AGENT = "enter_agent"  # 进入应用事件
    BATCH_JOB_RESULT = "batch_job_result"  # 异步任务完成事件
    CHANGE_EXTERNAL_CONTACT = "change_external_contact"  # 客户变更事件
    CHANGE_EXTERNAL_CHAT = "change_external_chat"  # 客户群变更事件
    SYS_APPROVAL_CHANGE = "sys_approval_change"  # 审批状态变更事件

class TextMessage(BaseModel):
    """文本消息
    
    企业微信文本消息格式
    """
    content: str = Field(..., description="消息内容")

class ImageMessage(BaseModel):
    """图片消息
    
    企业微信图片消息格式
    """
    media_id: str = Field(..., description="图片媒体文件ID")

class VoiceMessage(BaseModel):
    """语音消息
    
    企业微信语音消息格式
    """
    media_id: str = Field(..., description="语音媒体文件ID")

class VideoMessage(BaseModel):
    """视频消息
    
    企业微信视频消息格式
    """
    media_id: str = Field(..., description="视频媒体文件ID")
    title: Optional[str] = Field(None, description="视频标题")
    description: Optional[str] = Field(None, description="视频描述")

class FileMessage(BaseModel):
    """文件消息
    
    企业微信文件消息格式
    """
    media_id: str = Field(..., description="文件媒体文件ID")

class LocationMessage(BaseModel):
    """位置消息
    
    企业微信位置消息格式
    """
    latitude: float = Field(..., description="纬度")
    longitude: float = Field(..., description="经度")
    name: Optional[str] = Field(None, description="位置名称")
    address: Optional[str] = Field(None, description="地址详情")

class LinkMessage(BaseModel):
    """链接消息
    
    企业微信链接消息格式
    """
    title: str = Field(..., description="标题")
    description: Optional[str] = Field(None, description="描述")
    url: str = Field(..., description="链接URL")
    picurl: Optional[str] = Field(None, description="图片URL")

class MarkdownMessage(BaseModel):
    """Markdown消息
    
    企业微信Markdown消息格式
    """
    content: str = Field(..., description="markdown内容")

class MiniProgramMessage(BaseModel):
    """小程序消息
    
    企业微信小程序消息格式
    """
    appid: str = Field(..., description="小程序appid")
    title: str = Field(..., description="小程序消息标题")
    pagepath: str = Field(..., description="小程序页面路径")
    thumb_media_id: str = Field(..., description="小程序消息封面图片的mediaID")

class Article(BaseModel):
    """图文消息文章
    
    企业微信图文消息文章格式
    """
    title: str = Field(..., description="标题")
    description: Optional[str] = Field(None, description="描述")
    url: str = Field(..., description="链接")
    picurl: Optional[str] = Field(None, description="图片链接")

class NewsMessage(BaseModel):
    """图文消息
    
    企业微信图文消息格式
    """
    articles: List[Article] = Field(..., description="图文消息文章列表")

class TemplateCardMessage(BaseModel):
    """模板卡片消息
    
    企业微信模板卡片消息格式
    """
    card_type: str = Field(..., description="模板卡片类型")
    source: Optional[Dict[str, Any]] = Field(None, description="卡片来源信息")
    main_title: Optional[Dict[str, Any]] = Field(None, description="卡片主标题")
    emphasis_content: Optional[Dict[str, Any]] = Field(None, description="关键数据")
    quote_area: Optional[Dict[str, Any]] = Field(None, description="引用文献")
    sub_title_text: Optional[str] = Field(None, description="二级普通文本")
    horizontal_content_list: Optional[List[Dict[str, Any]]] = Field(None, description="二级标题+文本列表")
    jump_list: Optional[List[Dict[str, Any]]] = Field(None, description="跳转指引")
    card_action: Optional[Dict[str, Any]] = Field(None, description="整体卡片的点击跳转事件")

class WeComMessage(BaseModel):
    """企业微信消息
    
    企业微信消息通用格式
    """
    touser: Optional[str] = Field(None, description="指定接收消息的成员，成员ID列表，多个接收者用'|'分隔")
    toparty: Optional[str] = Field(None, description="指定接收消息的部门，部门ID列表，多个接收者用'|'分隔")
    totag: Optional[str] = Field(None, description="指定接收消息的标签，标签ID列表，多个接收者用'|'分隔")
    msgtype: MessageType = Field(..., description="消息类型")
    agentid: int = Field(..., description="企业应用的id")
    safe: Optional[int] = Field(0, description="表示是否是保密消息，0表示否，1表示是")
    enable_id_trans: Optional[int] = Field(0, description="表示是否开启id转译，0表示否，1表示是")
    enable_duplicate_check: Optional[int] = Field(0, description="表示是否开启重复消息检查，0表示否，1表示是")
    duplicate_check_interval: Optional[int] = Field(1800, description="表示重复消息检查的时间间隔，默认1800s")
    
    # 根据消息类型，以下字段只需要设置一个
    text: Optional[TextMessage] = Field(None, description="文本消息内容")
    image: Optional[ImageMessage] = Field(None, description="图片消息内容")
    voice: Optional[VoiceMessage] = Field(None, description="语音消息内容")
    video: Optional[VideoMessage] = Field(None, description="视频消息内容")
    file: Optional[FileMessage] = Field(None, description="文件消息内容")
    location: Optional[LocationMessage] = Field(None, description="位置消息内容")
    link: Optional[LinkMessage] = Field(None, description="链接消息内容")
    markdown: Optional[MarkdownMessage] = Field(None, description="markdown消息内容")
    miniprogram: Optional[MiniProgramMessage] = Field(None, description="小程序消息内容")
    news: Optional[NewsMessage] = Field(None, description="图文消息内容")
    template_card: Optional[TemplateCardMessage] = Field(None, description="模板卡片消息内容")