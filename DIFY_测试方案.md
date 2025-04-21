# Dify-on-WeChat 测试方案

## 测试脚本列表

我们为 Dify-on-WeChat 项目创建了以下测试脚本：

1. `test_docker_config.sh` - Docker 配置检查脚本
2. `test_env_vars.sh` - 环境变量测试与配置脚本
3. `test_api_endpoints.sh` - API 端点测试脚本
4. `test_docker_deployment.sh` - Docker 部署测试脚本（需修复）
5. `docker-compose-test.yml` - 测试专用的 Docker Compose 配置
6. `run_all_tests.sh` - 一键式测试脚本

## 新增的测试内容

为解决当前项目中的 Dockerfile 问题（缺少必要的 Java 源文件），我们创建了基于 Python 的替代测试方案：

1. `docker/Dockerfile.python` - 使用 Python 替代 Java 的 Dockerfile
2. `docker-compose-python.yml` - 使用 Python 后端的 Docker Compose 配置
3. `src/test_server.py` - 测试用 Python FastAPI 服务器
4. `requirements-test.txt` - Python 测试环境依赖
5. `测试文件/index.html` - 测试用前端页面

## 测试流程

### 方法一：一键式测试

最简单的测试方法是使用一键式测试脚本：

```bash
./run_all_tests.sh
```

此脚本会自动执行完整的测试流程，包括：
1. 检查必要工具
2. 准备测试环境
3. 检查 Docker 配置
4. 构建并启动测试服务
5. 测试 API 端点
6. 检查服务状态
7. 生成测试报告

### 方法二：逐步测试

如果您想详细了解每个测试步骤，可以按照以下步骤手动进行：

#### 步骤 1: 检查 Docker 配置

运行 Docker 配置检查脚本，确认项目的 Docker 配置是否正确：

```bash
./test_docker_config.sh
```

#### 步骤 2: 配置环境变量

使用环境变量测试与配置脚本来设置正确的环境变量：

```bash
./test_env_vars.sh
```

#### 步骤 3: 准备部署目录

创建必要的目录结构：

```bash
mkdir -p logs/nginx
mkdir -p dist
cp 测试文件/index.html dist/
```

#### 步骤 4: 使用 Python 配置启动服务

使用 Python 后端配置启动测试服务：

```bash
docker-compose -f docker-compose-python.yml up -d
```

#### 步骤 5: 测试 API 端点

使用 API 端点测试脚本检查各个服务的可用性：

```bash
./test_api_endpoints.sh
```

## 当前存在的问题与解决方案

### 1. Dockerfile 问题

**问题**：当前的 Dockerfile 假定存在 `src/wechat/pom.xml` 和 `src/wechat/src` 目录，但这些文件实际不存在。

**解决方案**：
- 我们提供了 `docker/Dockerfile.python` 和 `docker-compose-python.yml` 作为替代方案
- 使用 Python 实现了一个简易的测试服务器，可以完成基本的 API 功能

### 2. 前端资源缺失

**问题**：缺少前端构建资源（dist 目录）。

**解决方案**：
- 我们创建了 `测试文件/index.html` 作为测试用前端页面
- 测试脚本会自动将此页面复制到 dist 目录中

### 3. 环境变量默认值

**问题**：env.json 中使用了默认/测试值，这些在实际部署中需要替换。

**解决方案**：
- `run_all_tests.sh` 和 `test_env_vars.sh` 都会生成适合测试的环境变量文件
- 测试配置中添加了默认值，确保即使没有正确的环境变量也能进行测试

## 测试成功的标准

成功的测试应该满足以下条件：

1. Docker 容器能够成功构建和运行
2. 前端服务可访问（http://localhost:8080）
3. 后端 API 健康检查返回成功（http://localhost:8001/health）
4. 企业微信回调接口可访问（/wecom/callback）
5. RabbitMQ 管理界面可访问（http://localhost:15673）

## 高级测试

在基本测试完成后，可以进行以下高级测试：

1. **功能测试**：访问后端 Swagger 文档（http://localhost:8001/docs）并测试各 API 端点
2. **性能测试**：使用 Apache JMeter 或 wrk 等工具测试 API 性能
3. **故障恢复测试**：手动停止某个容器，检查系统是否能够恢复
4. **消息队列测试**：使用 RabbitMQ 管理界面发送测试消息

## 下一步开发建议

1. 完善 Java 后端实现，解决当前 Dockerfile 的问题
2. 添加更完整的前端 UI 和交互功能
3. 添加自动化集成测试
4. 实现企业微信集成的真实场景测试

## 总结

通过提供的测试脚本和工具，您可以全面测试 Dify-on-WeChat 项目的 Docker 部署情况，发现并解决潜在问题，确保系统在实际环境中的稳定运行。我们的 Python 测试方案提供了一个过渡性解决方案，让您可以在解决 Java 后端问题之前进行有效的部署测试。
