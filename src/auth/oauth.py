import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建路由
router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2配置
OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")
OAUTH2_REDIRECT_URI = os.getenv("OAUTH2_REDIRECT_URI")

# 企业微信OAuth2配置
WECOM_OAUTH_URL = "https://open.weixin.qq.com/connect/oauth2/authorize"
WECOM_TOKEN_URL = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
WECOM_USER_INFO_URL = "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo"

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserInfo(BaseModel):
    userid: str
    name: Optional[str] = None
    avatar: Optional[str] = None
    department: Optional[list] = None

@router.get("/login")
async def login():
    """企业微信OAuth2登录"""
    # 构建OAuth2授权URL
    auth_url = f"{WECOM_OAUTH_URL}?appid={os.getenv('WECHAT_CORP_ID')}&redirect_uri={OAUTH2_REDIRECT_URI}&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect"
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def auth_callback(code: str, state: str):
    """OAuth2回调处理"""
    try:
        # 获取访问令牌
        token_response = requests.get(
            f"{WECOM_TOKEN_URL}?corpid={os.getenv('WECHAT_CORP_ID')}&corpsecret={os.getenv('WECHAT_SECRET')}"
        )
        token_data = token_response.json()
        
        if 'access_token' not in token_data:
            raise HTTPException(status_code=401, detail="获取访问令牌失败")
        
        access_token = token_data['access_token']
        
        # 获取用户信息
        user_info_response = requests.get(
            f"{WECOM_USER_INFO_URL}?access_token={access_token}&code={code}"
        )
        user_info = user_info_response.json()
        
        if 'UserId' not in user_info:
            raise HTTPException(status_code=401, detail="获取用户信息失败")
        
        # TODO: 在数据库中创建或更新用户信息
        # TODO: 生成会话令牌
        
        # 重定向到前端页面，带上会话令牌
        return {"message": "登录成功", "user_id": user_info['UserId']}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"认证过程中发生错误: {str(e)}")

@router.get("/user/me")
async def get_current_user():
    """获取当前登录用户信息"""
    # TODO: 从会话令牌中获取用户信息
    return {"message": "需要实现用户信息获取功能"}