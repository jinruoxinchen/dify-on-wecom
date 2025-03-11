
# Dify-on-WeCom 项目跟踪

## 项目概况
基于微信企业号与Dify的智能客服系统，实现企业微信用户与AI客服的无缝交互。技术栈包含FastAPI后端+Vue3前端，当前处于核心功能开发阶段。

## 进度跟踪

### ✅ 已完成事项

- [x] [微信消息回调框架](src/wecom/message.py)

- [x] [配置管理前端](src/frontend/App.vue)

- [x] [FastAPI基础服务](src/main.py)

- [x] 依赖管理体系（Python/Node.js）

### ⏳ 待开发事项

#### 核心功能

- [ ] Dify API集成

  ```python:src/wecom/message.py:48-49
  # 替换占位代码（当前行48-49）
  # TODO: 调用Dify API处理消息
  reply_content = await dify_client.query(msg.content, user_id=msg.from_user)
  ```

#### 基础设施

- [ ] 消息队列实现  

  ```bash
  # 新建消息队列模块
  mkdir -p src/message_queue
  ```

- [ ] 部署配置  

  ```dockerfile:/Users/aaron/Documents/workspace/jinruoxinchen/dify-on-wecom/docker/Dockerfile
  # 需创建Dockerfile
  FROM python:3.9-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]
  ```

#### 辅助功能

- [ ] 知识库管理系统

  ```markdown
  - 前端组件: src/frontend/KnowledgeManagement.vue
  - 后端API: /api/knowledge/[create|update|delete]
  ```

#### 质量保障

- [ ] 测试套件  

  ```bash
  # 新建测试目录
  mkdir tests && touch tests/test_message.py
  ```

## 工程结构建议

```tree
dify-on-wecom/
├── docker/               # 部署配置
│   ├── Dockerfile
│   └── nginx.conf
└── src/
    ├── message_queue/    # 消息队列实现
    ├── knowledge/        # 知识库模块
    └── sso/             # SSO认证模块
```

## 优先级建议

1. **Dify集成** - 当前核心功能阻塞点
2. **消息队列** - 提升系统吞吐量
3. **知识管理** - 影响AI回复质量

