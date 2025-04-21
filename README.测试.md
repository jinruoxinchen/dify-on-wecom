# Dify-on-WeChat 测试指南

本文档提供了关于如何测试 Dify-on-WeChat 项目的详细指导，包括 Docker 部署测试和 API 端点测试。

## 先决条件

在开始测试之前，请确保您的系统上已安装以下工具：

- Docker (20.10.0+)
- Docker Compose (2.0.0+)
- curl
- jq (用于处理 JSON 数据)

## 测试脚本

本项目包含以下测试脚本：

1. `test_docker_deployment.sh` - Docker 部署测试脚本
2. `test_api_endpoints.sh` - API 端点测试脚本
3. `docker-compose-test.yml` - 测试专用的 Docker Compose 配置

## Docker 部署测试

Docker 部署测试脚本会检查各个服务的部署情况，包括：

- 后端服务
- 前端服务
- RabbitMQ 消息队列服务
- 个微服务

### 运行部署测试

```bash
./test_docker_deployment.sh
```

该脚本将执行以下步骤：

1. 检查必要条件 (Docker 和 Docker Compose)
2. 准备环境变量 (从 env.json 生成 .env 文件)
3. 检查 Docker 配置文件
4. 构建并启动服务
5. 检查服务状态
6. 测试基本连通性
7. 执行详细测试
8. 显示测试总结
9. 清理资源（可选）

### 测试环境选项

脚本支持测试不同的环境配置：

1. 开发环境 (docker-compose.dev.yml)
2. 生产环境 (docker-compose.prod.yml)
3. 所有服务 (docker-compose.yml)

## API 端点测试

API 端点测试脚本用于验证各个服务的 API 是否正常工作。

### 运行 API 端点测试

```bash
./test_api_endpoints.sh
```

该脚本支持测试以下端点：

1. 后端健康检查接口
2. 企业微信回调接口
3. RabbitMQ 管理界面
4. 前端静态资源
5. 个微服务接口

您可以选择测试单个端点或所有端点。

### 命令行参数

也可以直接通过命令行参数来测试特定端点：

```bash
./test_api_endpoints.sh 6  # 测试所有端点
```

## 使用测试专用 Docker Compose 配置

为了避免与正在运行的服务发生端口冲突，您可以使用测试专用的 Docker Compose 配置：

```bash
docker-compose -f docker-compose-test.yml up -d
```

该配置文件具有以下特点：

- 使用非标准端口以避免冲突
- 添加了健康检查
- 使用独立的网络和数据卷

## 测试最佳实践

1. **先测试开发环境**：在测试生产环境之前，先确保开发环境配置正确。
2. **逐步测试**：先测试基础设施（Docker、网络等），再测试各个服务的 API。
3. **查看日志**：如果测试失败，检查容器日志以获取更多信息。
4. **清理测试资源**：测试完成后记得清理测试资源，避免占用系统资源。

## 常见问题

### 端口冲突

如果遇到端口冲突，您可以：

1. 停止占用端口的进程
2. 修改 `docker-compose-test.yml` 中的端口映射
3. 使用 `docker-compose down` 停止所有服务后重试

### 环境变量问题

如果环境变量配置不正确，请检查：

1. `.env` 文件是否存在且包含所有必要的变量
2. 变量值是否正确（尤其是 API 密钥和 URL）

### 连接问题

如果服务无法相互连接：

1. 检查网络配置
2. 确保服务名称解析正确
3. 验证防火墙设置

## 其他测试方式

除了使用提供的测试脚本，您还可以：

1. 使用 Docker Desktop 监控容器状态
2. 使用 RabbitMQ 管理界面 (http://localhost:15672) 检查消息队列
3. 手动测试企业微信回调接口
4. 查看日志目录中的日志文件

## 总结

通过按照本指南进行测试，您可以确保 Dify-on-WeChat 项目的各个组件都正常工作。如果您在测试过程中遇到任何问题，请查阅项目文档或提交 issue。
