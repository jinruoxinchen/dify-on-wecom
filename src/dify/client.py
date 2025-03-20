import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class DifyClient:
    """Dify API客户端
    
    该客户端负责与Dify API进行通信，发送用户消息并获取AI回复
    """
    
    def __init__(self):
        """初始化Dify客户端"""
        self.api_key = os.getenv("DIFY_API_KEY")
        self.api_url = os.getenv("DIFY_API_URL")
        
        if not self.api_key or not self.api_url:
            raise ValueError("DIFY_API_KEY和DIFY_API_URL环境变量必须设置")
    
    def send_message(self, user_id: str, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """发送消息到Dify API
        
        Args:
            user_id: 用户ID，用于标识用户
            message: 用户发送的消息内容
            conversation_id: 对话ID，用于关联多轮对话
            
        Returns:
            Dict: Dify API的响应结果
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'user_id': user_id,
            'inputs': {
                'message': message
            }
        }
        
        if conversation_id:
            payload['conversation_id'] = conversation_id
        
        try:
            # 确保 api_url 不为 None
            if not self.api_url:
                raise ValueError("DIFY_API_URL 不能为空")
                
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()  # 抛出HTTP错误
            
            return response.json()
        except requests.exceptions.RequestException as e:
            # 处理请求异常
            return {
                'error': True,
                'message': f"请求Dify API失败: {str(e)}"
            }
        except ValueError as e:
            # 处理 URL 为空的情况
            return {
                'error': True,
                'message': str(e)
            }
    
    def get_reply(self, response_data: Dict[str, Any]) -> str:
        """从Dify API响应中提取回复内容
        
        Args:
            response_data: Dify API的响应数据
            
        Returns:
            str: AI的回复内容
        """
        if 'error' in response_data and response_data['error']:
            return f"系统错误: {response_data.get('message', '未知错误')}"
        
        try:
            # 根据Dify API的响应格式提取回复内容
            return response_data.get('answer', '未获取到回复')
        except (KeyError, TypeError):
            return "解析回复失败，请稍后再试"