import os
import time
import json
import logging
import requests
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class WeComClient:
    """企业微信API客户端
    
    该客户端负责与企业微信API进行通信，包括获取access_token、发送消息等功能
    """
    
    def __init__(self):
        """初始化企业微信客户端"""
        self.corp_id = os.getenv("WECHAT_CORP_ID")
        self.corp_secret = os.getenv("WECHAT_CORP_SECRET")
        self.agent_id = os.getenv("WECHAT_AGENT_ID")
        
        if not self.corp_id or not self.corp_secret or not self.agent_id:
            raise ValueError("WECHAT_CORP_ID、WECHAT_CORP_SECRET和WECHAT_AGENT_ID环境变量必须设置")
        
        self.access_token = None
        self.token_expires_at = 0
    
    def get_access_token(self) -> str:
        """获取企业微信API的access_token
        
        如果token已过期或不存在，则重新获取
        
        Returns:
            str: 有效的access_token
        """
        # 检查token是否存在且未过期
        current_time = time.time()
        if self.access_token and current_time < self.token_expires_at - 300:  # 提前5分钟刷新token
            return self.access_token
        
        # 获取新token
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corp_id}&corpsecret={self.corp_secret}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            result = response.json()
            
            if result.get("errcode") == 0:
                self.access_token = result.get("access_token")
                # 设置过期时间（企业微信的token有效期为7200秒）
                self.token_expires_at = current_time + 7200
                return self.access_token
            else:
                logger.error(f"获取access_token失败: {result}")
                raise Exception(f"获取access_token失败: {result.get('errmsg')}")
        except Exception as e:
            logger.error(f"获取access_token异常: {str(e)}")
            raise
    
    def send_text_message(self, user_ids: Union[str, List[str]], content: str, 
                          safe: int = 0) -> Dict[str, Any]:
        """发送文本消息
        
        Args:
            user_ids: 接收消息的用户ID，多个用户用'|'分隔，也可以是用户ID列表
            content: 消息内容
            safe: 是否为保密消息，0表示否，1表示是
            
        Returns:
            Dict: API的响应结果
        """
        # 获取access_token
        access_token = self.get_access_token()
        
        # 构建API URL
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        
        # 处理用户ID
        if isinstance(user_ids, list):
            user_ids = "|".join(user_ids)
        
        # 构建请求数据
        data = {
            "touser": user_ids,
            "msgtype": "text",
            "agentid": self.agent_id,
            "text": {
                "content": content
            },
            "safe": safe
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("errcode") == 0:
                logger.info(f"消息发送成功: {result}")
            else:
                logger.error(f"消息发送失败: {result}")
            
            return result
        except Exception as e:
            logger.error(f"发送消息异常: {str(e)}")
            raise
    
    def send_markdown_message(self, user_ids: Union[str, List[str]], content: str) -> Dict[str, Any]:
        """发送markdown消息
        
        Args:
            user_ids: 接收消息的用户ID，多个用户用'|'分隔，也可以是用户ID列表
            content: markdown格式的消息内容
            
        Returns:
            Dict: API的响应结果
        """
        # 获取access_token
        access_token = self.get_access_token()
        
        # 构建API URL
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        
        # 处理用户ID
        if isinstance(user_ids, list):
            user_ids = "|".join(user_ids)
        
        # 构建请求数据
        data = {
            "touser": user_ids,
            "msgtype": "markdown",
            "agentid": self.agent_id,
            "markdown": {
                "content": content
            }
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("errcode") == 0:
                logger.info(f"markdown消息发送成功: {result}")
            else:
                logger.error(f"markdown消息发送失败: {result}")
            
            return result
        except Exception as e:
            logger.error(f"发送markdown消息异常: {str(e)}")
            raise
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """获取企业微信用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 用户信息
        """
        # 获取access_token
        access_token = self.get_access_token()
        
        # 构建API URL
        url = f"https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={access_token}&userid={user_id}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            result = response.json()
            
            if result.get("errcode") == 0:
                logger.info(f"获取用户信息成功: {user_id}")
                return result
            else:
                logger.error(f"获取用户信息失败: {result}")
                return {"error": True, "message": result.get("errmsg")}
        except Exception as e:
            logger.error(f"获取用户信息异常: {str(e)}")
            raise
    
    def get_department_list(self, department_id: Optional[int] = None) -> Dict[str, Any]:
        """获取部门列表
        
        Args:
            department_id: 部门ID，如果不指定，则获取全量组织架构
            
        Returns:
            Dict: 部门列表信息
        """
        # 获取access_token
        access_token = self.get_access_token()
        
        # 构建API URL
        if department_id:
            url = f"https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token={access_token}&id={department_id}"
        else:
            url = f"https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token={access_token}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            result = response.json()
            
            if result.get("errcode") == 0:
                logger.info(f"获取部门列表成功")
                return result
            else:
                logger.error(f"获取部门列表失败: {result}")
                return {"error": True, "message": result.get("errmsg")}
        except Exception as e:
            logger.error(f"获取部门列表异常: {str(e)}")
            raise
    
    def get_department_users(self, department_id: int, fetch_child: int = 0) -> Dict[str, Any]:
        """获取部门成员
        
        Args:
            department_id: 部门ID
            fetch_child: 是否递归获取子部门下面的成员，0-不递归，1-递归
            
        Returns:
            Dict: 部门成员列表
        """
        # 获取access_token
        access_token = self.get_access_token()
        
        # 构建API URL
        url = f"https://qyapi.weixin.qq.com/cgi-bin/user/simplelist?access_token={access_token}&department_id={department_id}&fetch_child={fetch_child}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            result = response.json()
            
            if result.get("errcode") == 0:
                logger.info(f"获取部门成员成功: 部门ID {department_id}")
                return result
            else:
                logger.error(f"获取部门成员失败: {result}")
                return {"error": True, "message": result.get("errmsg")}
        except Exception as e:
            logger.error(f"获取部门成员异常: {str(e)}")
            raise