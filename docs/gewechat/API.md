# Gewechat API 参考文档

本文档提供了Gewechat服务集成的完整API参考。这些API允许您获取登录二维码、检查登录状态、保存配置信息以及发送消息。

## API 基础信息

- **基础URL**: `/api/gewechat`
- **Content-Type**: `application/json`
- **响应格式**: 所有API响应都使用JSON格式，并包含一个`success`字段表示请求是否成功

## API 端点

### 1. 获取登录二维码

获取用于微信扫码登录的二维码图像。

**请求**:
```
GET /api/gewechat/login/qrcode
```

**响应**:
```json
{
  "success": true,
  "qrcodeUrl": "data:image/png;base64,iVBOR...",
  "token": "abc123def456"
}
```

**字段说明**:
- `success`: 布尔值，表示请求是否成功
- `qrcodeUrl`: 字符串，Base64编码的二维码图像数据，可直接用于<img>标签的src属性
- `token`: 字符串，用于后续查询登录状态的令牌

**错误响应**:
```json
{
  "success": false,
  "message": "Failed to generate QR code"
}
```

### 2. 查询登录状态

使用之前获取的token查询登录状态。

**请求**:
```
GET /api/gewechat/login/status?token={token}
```

**参数**:
- `token`: 获取二维码时返回的token值

**响应**:
```json
{
  "success": true,
  "status": 2,
  "accountInfo": {
    "wxid": "wxid_abcdefg",
    "nickname": "用户昵称",
    "avatar": "头像URL"
  },
  "config": {
    "token": "wechat_access_token",
    "cookie": "wechat_cookie_string",
    "uid": "wechat_user_id",
    // 其他配置信息
  }
}
```

**字段说明**:
- `success`: 布尔值，表示请求是否成功
- `status`: 整数，表示登录状态
  - `0`: 未扫码
  - `1`: 已扫码，等待确认
  - `2`: 已确认，登录成功
  - `3`: 二维码已过期
- `accountInfo`: 对象，包含账号信息（仅在status=2时返回）
  - `wxid`: 微信ID
  - `nickname`: 微信昵称
  - `avatar`: 头像URL
- `config`: 对象，包含用于后续API调用的配置信息（仅在status=2时返回）

**错误响应**:
```json
{
  "success": false,
  "message": "Invalid token"
}
```

### 3. 保存配置信息

保存登录成功后获取的配置信息。

**请求**:
```
POST /api/gewechat/config/save
```

**请求体**:
```json
{
  "token": "wechat_access_token",
  "cookie": "wechat_cookie_string",
  "uid": "wechat_user_id",
  // 其他配置信息
}
```

**响应**:
```json
{
  "success": true,
  "message": "Configuration saved successfully",
  "config_path": "/path/to/config/file"
}
```

**字段说明**:
- `success`: 布尔值，表示请求是否成功
- `message`: 字符串，操作结果描述
- `config_path`: 字符串，配置文件保存的路径

**错误响应**:
```json
{
  "success": false,
  "message": "Configuration data is required"
}
```

### 4. 发送消息

向指定用户发送消息。

**请求**:
```
POST /api/gewechat/message/send
```

**请求体**:
```json
{
  "to_user": "wxid_abcdefg",
  "type": "text",
  "content": "你好，这是一条测试消息"
}
```

**字段说明**:
- `to_user`: 字符串，接收消息的用户ID
- `type`: 字符串，消息类型，支持的值:
  - `text`: 文本消息
  - `image`: 图片消息
  - `file`: 文件消息
- `content`: 字符串，消息内容。对于非文本消息，这应该是文件的URL或Base64编码

**响应**:
```json
{
  "success": true,
  "messageId": "msg123456"
}
```

**字段说明**:
- `success`: 布尔值，表示请求是否成功
- `messageId`: 字符串，已发送消息的ID

**错误响应**:
```json
{
  "success": false,
  "message": "Failed to send message: Invalid recipient"
}
```

## 状态码

系统使用标准HTTP状态码表示请求结果：

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未授权，需要登录
- `403 Forbidden`: 没有权限执行请求的操作
- `404 Not Found`: 请求的资源不存在
- `500 Internal Server Error`: 服务器内部错误

## 错误处理

所有API错误响应都使用以下格式：

```json
{
  "success": false,
  "message": "错误描述"
}
```

## 使用示例

### 获取登录二维码并完成登录流程

```javascript
// 1. 获取登录二维码
const getQrcode = async () => {
  const response = await fetch('/api/gewechat/login/qrcode');
  const data = await response.json();
  
  if (data.success) {
    // 显示二维码
    const qrcodeImg = document.getElementById('qrcode-img');
    qrcodeImg.src = data.qrcodeUrl;
    
    // 保存token用于轮询
    const token = data.token;
    
    // 开始轮询
    pollLoginStatus(token);
  }
}

// 2. 轮询登录状态
const pollLoginStatus = async (token) => {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/gewechat/login/status?token=${token}`);
    const data = await response.json();
    
    if (data.success) {
      // 根据状态更新UI
      switch (data.status) {
        case 0:  // 未扫码
          // 等待用户扫码
          break;
        case 1:  // 已扫码，等待确认
          // 更新UI提示用户确认
          break;
        case 2:  // 登录成功
          // 停止轮询
          clearInterval(interval);
          
          // 保存配置
          saveConfig(data.config);
          
          // 更新UI显示已登录
          displayUserInfo(data.accountInfo);
          break;
        case 3:  // 二维码已过期
          // 停止轮询
          clearInterval(interval);
          
          // 更新UI提示用户刷新二维码
          break;
      }
    }
  }, 2000);  // 每2秒检查一次
}

// 3. 保存配置
const saveConfig = async (config) => {
  const response = await fetch('/api/gewechat/config/save', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(config)
  });
  
  const data = await response.json();
  console.log('配置保存结果:', data);
}
```

## 安全注意事项

1. 请确保所有API请求都使用HTTPS以保护数据传输安全
2. 避免在客户端存储敏感配置信息，应该由服务端安全保存
3. 实现适当的访问控制，确保只有授权用户可以使用这些API
4. 定期轮换或刷新登录凭证，避免长期使用同一凭证
