import os
import json
import requests
from dotenv import load_dotenv
from src.dify.client import DifyClient

# 加载环境变量
load_dotenv()

def test_dify_client():
    """测试Dify客户端是否能正常工作"""
    print("\n===== 测试Dify客户端 =====")
    
    # 检查环境变量
    api_key = os.getenv("DIFY_API_KEY")
    api_url = os.getenv("DIFY_API_URL")
    
    if not api_key or not api_url:
        print("❌ 错误: 环境变量DIFY_API_KEY或DIFY_API_URL未设置")
        print("请复制.env.example为.env并填写正确的配置")
        return False
    
    print(f"✓ 环境变量检查通过")
    print(f"  API URL: {api_url}")
    
    try:
        # 初始化客户端
        client = DifyClient()
        print(f"✓ Dify客户端初始化成功")
        
        # 发送测试消息
        test_user_id = "test_user_001"
        test_message = "你好，这是一条测试消息"
        
        print(f"正在发送测试消息: '{test_message}'")
        response = client.send_message(user_id=test_user_id, message=test_message)
        
        # 检查响应
        if 'error' in response and response['error']:
            print(f"❌ 发送消息失败: {response.get('message')}")
            return False
        
        # 获取回复
        reply = client.get_reply(response)
        print(f"✓ 收到Dify回复: '{reply}'")
        
        return True
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {str(e)}")
        return False

def test_wecom_callback():
    """测试企业微信回调接口"""
    print("\n===== 测试企业微信回调接口 =====")
    
    # 检查环境变量
    token = os.getenv("WECHAT_TOKEN")
    aes_key = os.getenv("WECHAT_ENCODING_AES_KEY")
    corp_id = os.getenv("WECHAT_CORP_ID")
    
    if not token or not aes_key or not corp_id:
        print("❌ 错误: 企业微信相关环境变量未设置")
        print("请复制.env.example为.env并填写正确的配置")
        return False
    
    print(f"✓ 企业微信环境变量检查通过")
    
    # 获取服务器地址
    port = os.getenv("PORT", "8000")
    callback_url = f"http://localhost:{port}/wecom/callback"
    print(f"企业微信回调URL: {callback_url}")
    
    print("\n配置说明:")
    print("1. 确保服务已启动 (python -m src.main)")
    print("2. 如果在本地测试，需要使用内网穿透工具(如ngrok)将本地服务暴露到公网")
    print("3. 在企业微信管理后台配置接收消息的URL为上述地址")
    print("4. 在企业微信客户端向应用发送消息，检查是否收到回复")
    
    return True

def main():
    print("\n🚀 Dify-on-WeCom 集成测试工具")
    print("===============================\n")
    
    # 测试Dify客户端
    dify_success = test_dify_client()
    
    # 测试企业微信回调
    wecom_success = test_wecom_callback()
    
    # 总结
    print("\n===== 测试结果汇总 =====")
    print(f"Dify客户端测试: {'✓ 通过' if dify_success else '❌ 失败'}")
    print(f"企业微信配置检查: {'✓ 通过' if wecom_success else '❌ 失败'}")
    
    if dify_success and wecom_success:
        print("\n🎉 基础配置检查通过! 请按照上述说明完成企业微信回调配置，然后进行实际消息测试。")
    else:
        print("\n❌ 测试未通过，请检查上述错误信息并修复问题。")

if __name__ == "__main__":
    main()