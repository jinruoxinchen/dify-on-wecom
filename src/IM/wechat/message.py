from typing import Dict, Optional
from fastapi import APIRouter, Request, HTTPException
from wechatpy.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureError
from wechatpy.messages import TextMessage
from wechatpy.replies import TextReply
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建路由
router = APIRouter(prefix="/wechat", tags=["wechat"])

# 初始化微信加密类
crypto = WeChatCrypto(
    token=os.getenv("WECHAT_PUBLIC_TOKEN"),
    encoding_aes_key=os.getenv("WECHAT_PUBLIC_ENCODING_AES_KEY"),
    app_id=os.getenv("WECHAT_PUBLIC_APP_ID")
)

@router.post("/callback")
async def handle_message(request: Request):
    """处理微信回调消息"""
    try:
        # 获取请求参数
        params = request.query_params
        msg_signature = params.get("msg_signature")
        timestamp = params.get("timestamp")
        nonce = params.get("nonce")
        
        # 获取请求体
        body = await request.body()
        xml_content = body.decode()
        
        # 解密消息
        decrypted_xml = crypto.decrypt_message(
            xml_content,
            msg_signature,
            timestamp,
            nonce
        )
        
        # 解析消息
        msg = TextMessage.from_xml(decrypted_xml)
        
        # TODO: 调用Dify API处理消息
        reply_content = f"收到消息：{msg.content}"
        
        # 构造回复
        reply = TextReply(
            message=msg,
            content=reply_content
        )
        
        # 加密回复
        encrypted_reply = crypto.encrypt_message(
            reply.render(),
            nonce,
            timestamp
        )
        
        return encrypted_reply
        
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
def verify_url(
    msg_signature: str,
    timestamp: str,
    nonce: str,
    echostr: str
) -> str:
    """验证URL有效性"""
    try:
        decrypted_echo = crypto.decrypt_message(
            echostr,
            msg_signature,
            timestamp,
            nonce
        )
        return decrypted_echo
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
