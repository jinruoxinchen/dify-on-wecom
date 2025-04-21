#!/bin/bash
# API端点测试脚本 - 用于测试Docker部署后API的可用性
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

# 测试后端健康检查接口
test_health_endpoint() {
  info "测试健康检查接口..."
  
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
  
  if [ "$response" -eq 200 ]; then
    success "健康检查接口返回状态码: $response ✓"
    return 0
  else
    error "健康检查接口返回状态码: $response ✗"
    return 1
  fi
}

# 测试微信回调接口
test_wecom_callback() {
  info "测试企业微信回调接口..."
  
  response=$(curl -s -o /dev/null -w "%{http_code}" -X GET "http://localhost:8000/wecom/callback?msg_signature=test&timestamp=123456789&nonce=test&echostr=test")
  
  if [ "$response" -eq 200 ] || [ "$response" -eq 403 ]; then
    success "企业微信回调接口返回状态码: $response ✓ (200或403都属正常响应)"
    return 0
  else
    error "企业微信回调接口返回状态码: $response ✗"
    return 1
  fi
}

# 测试RabbitMQ管理接口
test_rabbitmq_management() {
  info "测试RabbitMQ管理界面..."
  
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:15672)
  
  if [ "$response" -eq 200 ]; then
    success "RabbitMQ管理界面返回状态码: $response ✓"
    return 0
  else
    error "RabbitMQ管理界面返回状态码: $response ✗"
    return 1
  fi
}

# 测试前端静态资源
test_frontend() {
  info "测试前端静态资源..."
  
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80)
  
  if [ "$response" -eq 200 ]; then
    success "前端静态资源返回状态码: $response ✓"
    return 0
  else
    error "前端静态资源返回状态码: $response ✗"
    return 1
  fi
}

# 测试个微服务接口
test_gewechat() {
  info "测试个微服务接口..."
  
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080)
  
  if [ "$response" -eq 200 ]; then
    success "个微服务接口返回状态码: $response ✓"
    return 0
  else
    error "个微服务接口返回状态码: $response ✗"
    return 1
  fi
}

# 显示测试选项
show_test_options() {
  echo "请选择要测试的端点:"
  echo "1) 后端健康检查接口"
  echo "2) 企业微信回调接口"
  echo "3) RabbitMQ管理界面"
  echo "4) 前端静态资源"
  echo "5) 个微服务接口"
  echo "6) 测试所有端点"
  echo "0) 退出"
}

# 运行指定测试
run_test() {
  case $1 in
    1) test_health_endpoint ;;
    2) test_wecom_callback ;;
    3) test_rabbitmq_management ;;
    4) test_frontend ;;
    5) test_gewechat ;;
    6) 
      test_health_endpoint
      test_wecom_callback
      test_rabbitmq_management
      test_frontend
      test_gewechat
      ;;
    *) echo "无效选项" ;;
  esac
}

# 主函数
main() {
  echo "============================================"
  echo "       Dify-on-WeChat API端点测试工具       "
  echo "============================================"
  echo
  
  # 检查curl是否安装
  if ! command -v curl &> /dev/null; then
    error "curl未安装，请先安装curl"
    exit 1
  fi
  
  # 单次运行模式
  if [ $# -eq 1 ]; then
    run_test $1
    exit 0
  fi
  
  # 交互模式
  while true; do
    echo
    show_test_options
    read -p "请输入选项 [0-6]: " option
    
    if [ "$option" -eq 0 ]; then
      info "退出测试工具"
      break
    fi
    
    run_test $option
  done
}

# 执行主函数
if [ $# -eq 0 ]; then
  main
else
  main $1
fi
