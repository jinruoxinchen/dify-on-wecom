#!/bin/bash
# 一键式测试脚本
# 作者：Cline
# 日期：2025-03-23

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 输出格式化信息
info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

section() {
  echo -e "\n${BLUE}[SECTION] $1${NC}"
  echo -e "${BLUE}$(printf '=%.0s' {1..50})${NC}\n"
}

# 项目根目录
ROOT_DIR="$(pwd)"

# 捕获Ctrl+C
trap ctrl_c INT
function ctrl_c() {
  echo
  warn "测试已中断，正在清理..."
  cleanup
  exit 1
}

# 清理函数
cleanup() {
  section "清理测试环境"
  
  info "停止所有Docker容器..."
  docker-compose -f docker-compose-python.yml down 2>/dev/null
  docker-compose -f docker-compose-test.yml down 2>/dev/null
  
  info "删除测试产生的临时文件..."
  rm -f .env.test 2>/dev/null
  
  info "清理完成"
}

# 检测必要工具
check_prerequisites() {
  section "检查必要工具"
  
  local missing_tools=0
  
  # 检查Docker
  if ! command -v docker &> /dev/null; then
    error "未安装Docker"
    missing_tools=1
  else
    info "Docker已安装: $(docker --version)"
  fi
  
  # 检查Docker Compose
  if ! command -v docker-compose &> /dev/null; then
    warn "未安装docker-compose命令，将尝试使用docker compose命令"
    if ! docker compose version &> /dev/null; then
      error "未安装Docker Compose"
      missing_tools=1
    else
      info "Docker Compose已安装: $(docker compose version --short)"
    fi
  else
    info "Docker Compose已安装: $(docker-compose --version)"
  fi
  
  # 检查curl
  if ! command -v curl &> /dev/null; then
    error "未安装curl"
    missing_tools=1
  else
    info "curl已安装: $(curl --version | head -n 1)"
  fi
  
  # 检查jq
  if ! command -v jq &> /dev/null; then
    warn "未安装jq - 部分JSON解析功能将不可用"
  else
    info "jq已安装: $(jq --version)"
  fi
  
  if [ $missing_tools -ne 0 ]; then
    error "缺少必要工具，请安装它们后再运行测试"
    exit 1
  fi
  
  info "所有必要工具已检查"
}

# 准备测试环境
prepare_environment() {
  section "准备测试环境"
  
  info "创建必要的目录结构..."
  mkdir -p logs/nginx
  mkdir -p dist
  
  if [ ! -f "dist/index.html" ]; then
    if [ -f "测试文件/index.html" ]; then
      info "复制测试用前端页面..."
      cp 测试文件/index.html dist/
    else
      warn "找不到测试用前端页面，可能会影响前端测试"
    fi
  fi
  
  info "创建测试用环境变量文件..."
  cat > .env.test << EOF
# 测试环境变量 - 由run_all_tests.sh生成
# 生成时间: $(date)
DIFY_API_KEY=test_dify_api_key
DIFY_API_URL=http://localhost:8001
WECHAT_TOKEN=test_wechat_token
WECHAT_ENCODING_AES_KEY=test_encoding_aes_key
WECHAT_CORP_ID=test_corp_id
WECHAT_CORP_SECRET=test_corp_secret
WECHAT_AGENT_ID=test_agent_id
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
ENVIRONMENT=test
EOF

  info "复制测试用requirements.txt..."
  if [ -f "requirements-test.txt" ]; then
    cp requirements-test.txt requirements.txt
  else
    warn "找不到requirements-test.txt，将使用项目现有的requirements.txt"
  fi
  
  info "测试环境准备完成"
}

# 运行配置检查
run_config_check() {
  section "运行Docker配置检查"
  
  if [ -f "./test_docker_config.sh" ]; then
    info "运行Docker配置检查脚本..."
    ./test_docker_config.sh
    
    if [ $? -ne 0 ]; then
      warn "Docker配置检查发现一些问题，但仍将继续测试"
    else
      info "Docker配置检查完成"
    fi
  else
    error "找不到test_docker_config.sh脚本"
    warn "跳过Docker配置检查"
  fi
}

# 构建并启动Python测试环境
build_and_start_env() {
  section "构建并启动Python测试环境"
  
  info "使用Python后端配置来测试部署..."
  
  # 使用.env.test环境变量文件
  info "使用临时生成的环境变量..."
  export $(cat .env.test | grep -v '#' | xargs)
  
  info "构建Docker镜像..."
  docker-compose -f docker-compose-python.yml build
  
  if [ $? -ne 0 ]; then
    error "构建失败，无法继续测试"
    exit 1
  fi
  
  info "启动Docker容器..."
  docker-compose -f docker-compose-python.yml up -d
  
  if [ $? -ne 0 ]; then
    error "启动容器失败，无法继续测试"
    exit 1
  fi
  
  info "等待服务启动 (30秒)..."
  sleep 30
}

# 测试API端点
test_api_endpoints() {
  section "测试API端点"
  
  if [ -f "./test_api_endpoints.sh" ]; then
    info "运行API端点测试脚本..."
    
    # 自动选择选项6 (测试所有端点)
    echo "6" | ./test_api_endpoints.sh
    
    if [ $? -ne 0 ]; then
      warn "API端点测试发现一些问题"
    else
      info "API端点测试完成"
    fi
  else
    warn "找不到test_api_endpoints.sh脚本，将使用内置测试"
    
    # 内置端点测试
    info "测试健康检查端点..."
    curl -s http://localhost:8001/health
    
    info "测试企业微信回调端点..."
    curl -s "http://localhost:8001/wecom/callback?msg_signature=test&timestamp=123456789&nonce=test&echostr=test"
  fi
}

# 检查服务状态
check_services() {
  section "检查服务状态"
  
  info "Docker容器状态:"
  docker-compose -f docker-compose-python.yml ps
  
  info "检查日志文件:"
  if [ -d "logs" ]; then
    ls -la logs
  else
    warn "找不到日志目录"
  fi
  
  info "后端服务日志摘要:"
  docker-compose -f docker-compose-python.yml logs backend --tail 20
}

# 报告测试结果
report_results() {
  section "测试结果汇总"
  
  info "环境信息:"
  echo "  - 操作系统: $(uname -s)"
  echo "  - Docker版本: $(docker --version)"
  
  info "服务状态:"
  local backend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health || echo "失败")
  local frontend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 || echo "失败")
  local rabbitmq_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:15673 || echo "失败")
  
  echo "  - 后端API: $backend_status"
  echo "  - 前端页面: $frontend_status"
  echo "  - RabbitMQ管理: $rabbitmq_status"
  
  info "测试链接:"
  echo "  - 后端Swagger文档: http://localhost:8001/docs"
  echo "  - 前端测试页面: http://localhost:8080"
  echo "  - RabbitMQ管理页面: http://localhost:15673 (guest/guest)"
  
  info "下一步:"
  echo "  1. 可以通过访问上述链接手动验证各个服务"
  echo "  2. 查看日志目录 (logs/) 了解更多详细信息"
  echo "  3. 使用 'docker-compose -f docker-compose-python.yml logs' 查看容器日志"
  echo "  4. 完成测试后使用 'docker-compose -f docker-compose-python.yml down' 停止服务"
}

# 主函数
main() {
  echo "=============================================="
  echo "     Dify-on-WeChat Docker部署一键式测试     "
  echo "=============================================="
  echo
  echo "此脚本将执行完整的测试流程，包括:"
  echo "  1. 检查必要工具"
  echo "  2. 准备测试环境"
  echo "  3. 检查Docker配置"
  echo "  4. 构建并启动测试服务"
  echo "  5. 测试API端点"
  echo "  6. 检查服务状态"
  echo "  7. 生成测试报告"
  echo
  read -p "按Enter键开始测试，Ctrl+C退出..." -r
  
  check_prerequisites
  prepare_environment
  run_config_check
  build_and_start_env
  test_api_endpoints
  check_services
  report_results
  
  echo
  echo "测试完成！测试环境仍在运行中。"
  read -p "是否要清理测试环境？ (y/n): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    cleanup
    info "测试环境已清理"
  else
    info "测试环境保持运行中，您可以继续手动测试"
    info "完成后使用 'docker-compose -f docker-compose-python.yml down' 停止服务"
  fi
}

# 执行主函数
main
