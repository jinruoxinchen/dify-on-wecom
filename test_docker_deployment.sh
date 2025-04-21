#!/bin/bash
# 测试Docker部署脚本
# 作者：Cline
# 日期：2025-03-23

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
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

success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 检查Docker和Docker Compose是否安装
check_prerequisites() {
  info "检查必要条件..."
  
  if ! command -v docker &> /dev/null; then
    error "Docker未安装，请先安装Docker"
    exit 1
  fi
  
  if ! command -v docker-compose &> /dev/null; then
    warn "Docker Compose未安装，将尝试使用docker compose命令"
    DOCKER_COMPOSE="docker compose"
  else
    DOCKER_COMPOSE="docker-compose"
  fi
  
  success "检查完成，继续进行测试"
}

# 准备环境变量
prepare_env() {
  info "准备环境变量..."
  
  if [ ! -f .env ]; then
    warn ".env文件不存在，从env.json创建"
    
    if [ ! -f env.json ]; then
      error "env.json不存在，无法创建环境变量文件"
      exit 1
    fi
    
    # 选择环境
    echo "请选择测试环境:"
    echo "1) 开发环境 (development)"
    echo "2) 测试环境 (test)"
    echo "3) 生产环境 (production)"
    read -p "请输入选项 [1-3]: " env_option
    
    case $env_option in
      1) ENV="development" ;;
      2) ENV="test" ;;
      3) ENV="production" ;;
      *) ENV="development"; warn "无效选项，使用默认开发环境" ;;
    esac
    
    info "使用 $ENV 环境配置"
    
    # 需要jq工具来处理JSON，如果不存在则提示安装
    if ! command -v jq &> /dev/null; then
      error "未找到jq工具，请先安装: brew install jq"
      exit 1
    fi
    
    # 从env.json生成.env文件
    echo "# 自动生成的环境变量文件 - $(date)" > .env
    jq -r --arg ENV "$ENV" '.[$ENV] | to_entries | .[] | "\(.key)=\(.value)"' env.json >> .env
    
    success "环境变量文件创建成功"
  else
    info "使用现有的.env文件"
  fi
}

# 检查Docker配置文件
check_docker_files() {
  info "检查Docker配置文件..."
  
  if [ ! -f docker-compose.yml ]; then
    error "找不到docker-compose.yml文件"
    exit 1
  fi
  
  if [ ! -f docker/Dockerfile ]; then
    error "找不到Dockerfile文件"
    exit 1
  fi
  
  success "Docker配置文件检查完成"
}

# 构建并启动开发环境
start_dev_environment() {
  info "构建并启动开发环境..."
  
  $DOCKER_COMPOSE -f docker-compose.dev.yml build
  if [ $? -ne 0 ]; then
    error "构建开发环境失败"
    exit 1
  fi
  
  $DOCKER_COMPOSE -f docker-compose.dev.yml up -d
  if [ $? -ne 0 ]; then
    error "启动开发环境失败"
    exit 1
  fi
  
  success "开发环境启动成功"
}

# 构建并启动生产环境
start_prod_environment() {
  info "构建并启动生产环境..."
  
  $DOCKER_COMPOSE -f docker-compose.prod.yml build
  if [ $? -ne 0 ]; then
    error "构建生产环境失败"
    exit 1
  fi
  
  $DOCKER_COMPOSE -f docker-compose.prod.yml up -d
  if [ $? -ne 0 ]; then
    error "启动生产环境失败"
    exit 1
  fi
  
  success "生产环境启动成功"
}

# 构建并启动全部服务
start_all_services() {
  info "构建并启动所有服务..."
  
  $DOCKER_COMPOSE build
  if [ $? -ne 0 ]; then
    error "构建服务失败"
    exit 1
  fi
  
  $DOCKER_COMPOSE up -d
  if [ $? -ne 0 ]; then
    error "启动服务失败"
    exit 1
  fi
  
  success "所有服务启动成功"
}

# 检查服务状态
check_services() {
  info "检查服务状态..."
  
  $DOCKER_COMPOSE ps
  
  # 检查容器是否都处于运行状态
  running_containers=$($DOCKER_COMPOSE ps --services --filter "status=running" | wc -l)
  total_containers=$($DOCKER_COMPOSE ps --services | wc -l)
  
  if [ "$running_containers" -eq "$total_containers" ]; then
    success "所有 $total_containers 个服务都在正常运行"
  else
    error "有服务未正常运行，运行: $running_containers/$total_containers"
    warn "请使用 'docker-compose logs' 查看详细日志"
    exit 1
  fi
}

# 测试基本连通性
test_connectivity() {
  info "测试基本连通性..."
  
  # 测试前端服务
  if curl -s http://localhost:80 > /dev/null; then
    success "前端服务访问正常"
  else
    warn "前端服务无法访问"
  fi
  
  # 测试后端服务
  if curl -s http://localhost:8000/health > /dev/null; then
    success "后端服务健康检查正常"
  else
    warn "后端服务健康检查失败"
  fi
  
  # 测试RabbitMQ服务
  if curl -s http://localhost:15672 > /dev/null; then
    success "RabbitMQ管理界面访问正常"
  else
    warn "RabbitMQ管理界面无法访问"
  fi
  
  # 测试个微服务
  if curl -s http://localhost:8080 > /dev/null; then
    success "个微服务访问正常"
  else
    warn "个微服务无法访问"
  fi
}

# 执行详细测试
run_detailed_tests() {
  info "执行详细测试..."
  
  # 检查日志目录是否创建
  if [ -d "logs" ]; then
    success "日志目录创建成功"
  else
    warn "日志目录未创建"
  fi
  
  # 检查Docker网络
  if docker network ls | grep -q "app-network"; then
    success "Docker网络创建成功"
  else
    warn "Docker网络未创建"
  fi
  
  # 检查数据卷
  if docker volume ls | grep -q "rabbitmq-data"; then
    success "RabbitMQ数据卷创建成功"
  else
    warn "RabbitMQ数据卷未创建"
  fi
  
  info "详细测试完成"
}

# 清理资源
cleanup() {
  info "清理资源..."
  
  read -p "是否停止并移除所有容器？(y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    $DOCKER_COMPOSE down
    success "所有容器已停止并移除"
  else
    info "跳过清理步骤，容器继续运行"
  fi
}

# 显示测试总结
show_summary() {
  info "============== 测试总结 =============="
  $DOCKER_COMPOSE ps
  echo
  info "前端访问地址: http://localhost:80"
  info "后端API地址: http://localhost:8000"
  info "RabbitMQ管理界面: http://localhost:15672 (用户名/密码: guest/guest)"
  info "个微服务地址: http://localhost:8080"
  echo
  info "测试完成！感谢使用Docker部署测试脚本"
}

# 主函数
main() {
  echo "============================================"
  echo "         Dify-on-WeChat Docker部署测试      "
  echo "============================================"
  echo
  
  check_prerequisites
  prepare_env
  check_docker_files
  
  echo
  echo "请选择测试类型:"
  echo "1) 测试开发环境 (docker-compose.dev.yml)"
  echo "2) 测试生产环境 (docker-compose.prod.yml)"
  echo "3) 测试所有服务 (docker-compose.yml)"
  read -p "请输入选项 [1-3]: " test_option
  
  case $test_option in
    1) start_dev_environment ;;
    2) start_prod_environment ;;
    3) start_all_services ;;
    *) start_all_services; warn "无效选项，默认测试所有服务" ;;
  esac
  
  sleep 5 # 等待服务启动
  
  check_services
  test_connectivity
  run_detailed_tests
  show_summary
  cleanup
}

# 执行主函数
main
