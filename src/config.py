import os
import json
import yaml
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()  # 保留.env文件支持

class Config:
    """配置管理类
    
    负责加载和管理应用配置，支持从环境变量和配置文件加载配置
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器"""
        if self._initialized:
            return
            
        # 获取当前环境
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # 初始化配置字典
        self.config = {}
        
        # 加载配置
        self._load_config()
        
        self._initialized = True
    
    def _load_config(self):
        """加载配置
        
        首先尝试从env.json加载配置，然后从环境变量加载配置，环境变量优先级高于配置文件
        """
        # 尝试从env.json加载配置
        try:
            json_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'env.json')
            if os.path.exists(json_config_path):
                with open(json_config_path, 'r', encoding='utf-8') as f:
                    json_config = json.load(f)
                    if self.environment in json_config:
                        env_config = json_config[self.environment]
                        for key, value in env_config.items():
                            # 只有在环境变量中没有设置时，才使用配置文件中的值
                            if os.getenv(key) is None:
                                os.environ[key] = str(value)
        except Exception as e:
            print(f"加载env.json配置文件失败: {str(e)}")
        
        # 加载企业微信专用配置
        wecom_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config/wecom.yml')
        if os.path.exists(wecom_config_path):
            try:
                with open(wecom_config_path, 'r', encoding='utf-8') as f:
                    wecom_config = yaml.safe_load(f)
                    # 获取根配置
                    wecom = wecom_config.get('wecom', {})
                    
                    # 读取配置并保持环境变量优先
                    self.config["WECHAT_CORP_ID"] = os.getenv("WECHAT_CORP_ID") or wecom.get('corp_id')
                    self.config["WECHAT_CORP_SECRET"] = os.getenv("WECHAT_CORP_SECRET") or wecom.get('corp_secret')
                    self.config["WECHAT_AGENT_ID"] = os.getenv("WECHAT_AGENT_ID") or wecom.get('agent_id')
                    
                    # 加密配置
                    encryption = wecom.get('encryption', {})
                    self.config["WECHAT_TOKEN"] = os.getenv("WECHAT_TOKEN") or encryption.get('token')
                    self.config["WECHAT_ENCODING_AES_KEY"] = os.getenv("WECHAT_ENCODING_AES_KEY") or encryption.get('aes_key')
                    
                    # Token管理配置
                    token_config = wecom.get('token', {})
                    self.config["TOKEN_REFRESH_INTERVAL"] = token_config.get('refresh_interval', 7000)
                    self.config["TOKEN_STORAGE_TYPE"] = token_config.get('storage_type', 'memory')
                    
            except Exception as e:
                print(f"加载企业微信配置文件失败: {str(e)}")
                # 回退到环境变量
                self.config["WECHAT_CORP_ID"] = os.getenv("WECHAT_CORP_ID")
                self.config["WECHAT_CORP_SECRET"] = os.getenv("WECHAT_CORP_SECRET")
                self.config["WECHAT_AGENT_ID"] = os.getenv("WECHAT_AGENT_ID")
                self.config["WECHAT_TOKEN"] = os.getenv("WECHAT_TOKEN")
                self.config["WECHAT_ENCODING_AES_KEY"] = os.getenv("WECHAT_ENCODING_AES_KEY")
        
        # Dify API配置
        self.config["DIFY_API_KEY"] = os.getenv("DIFY_API_KEY")
        self.config["DIFY_API_URL"] = os.getenv("DIFY_API_URL")
        
        # 个人微信配置
        self.config["WECHAT_PERSONAL_ENABLED"] = True
        self.config["WECHAT_PERSONAL_API_URL"] = "http://localhost:8080/wechat"
        
        # RabbitMQ配置
        self.config["RABBITMQ_HOST"] = os.getenv("RABBITMQ_HOST", "localhost")
        self.config["RABBITMQ_PORT"] = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.config["RABBITMQ_USERNAME"] = os.getenv("RABBITMQ_USERNAME", "guest")
        self.config["RABBITMQ_PASSWORD"] = os.getenv("RABBITMQ_PASSWORD", "guest")
        self.config["RABBITMQ_VHOST"] = os.getenv("RABBITMQ_VHOST", "/")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项
        
        Args:
            key: 配置项键名
            default: 默认值，当配置项不存在时返回
            
        Returns:
            Any: 配置项的值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项
        
        Args:
            key: 配置项键名
            value: 配置项的值
        """
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置项
        
        Returns:
            Dict[str, Any]: 所有配置项
        """
        return self.config.copy()

# 创建全局配置实例
config = Config()

def get_config(key: str, default: Any = None) -> Any:
    """获取配置项的快捷方法
    
    Args:
        key: 配置项键名
        default: 默认值，当配置项不存在时返回
        
    Returns:
        Any: 配置项的值
    """
    return config.get(key, default)
