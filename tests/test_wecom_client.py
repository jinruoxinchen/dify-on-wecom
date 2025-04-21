import os
import unittest
import time
from unittest import mock
from dotenv import load_dotenv

# 导入需要测试的模块
from src.wecom.client import WeComClient
from src.dify.client import DifyClient
from src.wecom.message_handler import WeComMessageHandler

# 加载环境变量
load_dotenv()

class TestWeComClient(unittest.TestCase):
    """测试企业微信客户端
    
    该测试类用于测试企业微信API的对接功能，包括获取access_token、发送消息等
    所有测试都通过环境变量获取必要的参数
    """
    
    def setUp(self):
        """测试前的准备工作
        
        检查必要的环境变量是否已设置
        """
        # 检查环境变量是否已设置
        required_env_vars = ["WECHAT_CORP_ID", "WECHAT_CORP_SECRET", "WECHAT_AGENT_ID"]
        for var in required_env_vars:
            self.assertIsNotNone(os.getenv(var), f"环境变量 {var} 未设置")
        
        # 初始化客户端
        self.client = WeComClient()
    
    def test_init(self):
        """测试客户端初始化
        
        验证客户端是否正确读取环境变量
        """
        self.assertEqual(self.client.corp_id, os.getenv("WECHAT_CORP_ID"))
        self.assertEqual(self.client.corp_secret, os.getenv("WECHAT_CORP_SECRET"))
        self.assertEqual(self.client.agent_id, os.getenv("WECHAT_AGENT_ID"))
        self.assertIsNone(self.client.access_token)
        self.assertEqual(self.client.token_expires_at, 0)
    
    @mock.patch('requests.get')
    def test_get_access_token(self, mock_get):
        """测试获取access_token
        
        模拟API响应，验证获取access_token的逻辑
        """
        # 模拟API响应
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "errcode": 0,
            "errmsg": "ok",
            "access_token": "mock_access_token",
            "expires_in": 7200
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 调用方法
        token = self.client.get_access_token()
        
        # 验证结果
        self.assertEqual(token, "mock_access_token")
        self.assertEqual(self.client.access_token, "mock_access_token")
        self.assertGreater(self.client.token_expires_at, time.time())
        
        # 验证API调用
        expected_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.client.corp_id}&corpsecret={self.client.corp_secret}"
        mock_get.assert_called_once_with(expected_url)
    
    @mock.patch('requests.post')
    def test_send_text_message(self, mock_post):
        """测试发送文本消息
        
        模拟API响应，验证发送文本消息的逻辑
        """
        # 设置access_token
        self.client.access_token = "mock_access_token"
        self.client.token_expires_at = time.time() + 3600  # 设置为1小时后过期
        
        # 模拟API响应
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "errcode": 0,
            "errmsg": "ok",
            "msgid": "mock_msgid"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 调用方法
        result = self.client.send_text_message("user1|user2", "测试消息")
        
        # 验证结果
        self.assertEqual(result["errcode"], 0)
        self.assertEqual(result["errmsg"], "ok")
        self.assertEqual(result["msgid"], "mock_msgid")
        
        # 验证API调用
        expected_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.client.access_token}"
        expected_data = {
            "touser": "user1|user2",
            "msgtype": "text",
            "agentid": self.client.agent_id,
            "text": {
                "content": "测试消息"
            },
            "safe": 0
        }
        mock_post.assert_called_once_with(expected_url, json=expected_data)


class TestDifyClient(unittest.TestCase):
    """测试Dify客户端
    
    该测试类用于测试Dify API的对接功能，包括发送消息、获取回复等
    所有测试都通过环境变量获取必要的参数
    """
    
    def setUp(self):
        """测试前的准备工作
        
        检查必要的环境变量是否已设置
        """
        # 检查环境变量是否已设置
        required_env_vars = ["DIFY_API_KEY", "DIFY_API_URL"]
        for var in required_env_vars:
            self.assertIsNotNone(os.getenv(var), f"环境变量 {var} 未设置")
        
        # 初始化客户端
        self.client = DifyClient()
    
    def test_init(self):
        """测试客户端初始化
        
        验证客户端是否正确读取环境变量
        """
        self.assertEqual(self.client.api_key, os.getenv("DIFY_API_KEY"))
        self.assertEqual(self.client.api_url, os.getenv("DIFY_API_URL"))
    
    @mock.patch('requests.post')
    def test_send_message(self, mock_post):
        """测试发送消息到Dify API
        
        模拟API响应，验证发送消息的逻辑
        """
        # 模拟API响应
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            "answer": "这是一个测试回复",
            "conversation_id": "mock_conversation_id"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 调用方法
        result = self.client.send_message("test_user", "测试消息")
        
        # 验证结果
        self.assertEqual(result["answer"], "这是一个测试回复")
        self.assertEqual(result["conversation_id"], "mock_conversation_id")
        
        # 验证API调用
        expected_headers = {
            'Authorization': f'Bearer {self.client.api_key}',
            'Content-Type': 'application/json'
        }
        expected_data = {
            'user_id': "test_user",
            'inputs': {
                'message': "测试消息"
            }
        }
        mock_post.assert_called_once_with(self.client.api_url, headers=expected_headers, json=expected_data)
    
    def test_get_reply(self):
        """测试从Dify API响应中提取回复内容
        
        验证提取回复内容的逻辑
        """
        # 测试正常响应
        response_data = {
            "answer": "这是一个测试回复",
            "conversation_id": "mock_conversation_id"
        }
        reply = self.client.get_reply(response_data)
        self.assertEqual(reply, "这是一个测试回复")
        
        # 测试错误响应
        error_response = {
            "error": True,
            "message": "API调用失败"
        }
        reply = self.client.get_reply(error_response)
        self.assertEqual(reply, "系统错误: API调用失败")


class TestWeComMessageHandler(unittest.TestCase):
    """测试企业微信消息处理器
    
    该测试类用于测试企业微信消息处理器的功能，包括处理各种类型的消息
    """
    
    def setUp(self):
        """测试前的准备工作
        
        初始化消息处理器和模拟对象
        """
        # 模拟WeComClient和DifyClient
        self.wecom_client = mock.Mock()
        self.dify_client = mock.Mock()
        
        # 初始化消息处理器
        self.handler = WeComMessageHandler(self.wecom_client, self.dify_client)
    
    @mock.patch('wechatpy.enterprise.replies.TextReply')
    async def test_handle_text_message(self, mock_text_reply):
        """测试处理文本消息
        
        验证文本消息处理逻辑
        """
        # 模拟TextMessage
        message = mock.Mock()
        message.source = "test_user"
        message.content = "测试消息"
        
        # 模拟DifyClient.send_message返回值
        self.dify_client.send_message.return_value = {"answer": "这是一个测试回复"}
        
        # 模拟DifyClient.get_reply返回值
        self.dify_client.get_reply.return_value = "这是一个测试回复"
        
        # 模拟TextReply
        mock_reply = mock.Mock()
        mock_text_reply.return_value = mock_reply
        
        # 调用方法
        result = await self.handler.handle_text_message(message)
        
        # 验证结果
        self.dify_client.send_message.assert_called_once_with("test_user", "测试消息")
        self.dify_client.get_reply.assert_called_once_with({"answer": "这是一个测试回复"})
        self.assertEqual(result, mock_reply)


if __name__ == "__main__":
    unittest.main()