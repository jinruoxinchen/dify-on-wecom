#!/bin/bash
# 环境变量测试与配置脚本
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

# 检查配置文件
check_config_files() {
  info "检查配置文件..."
  
  if [ -f env.json ]; then
    success "找到env.json文件"
    
    # 需要jq工具来处理JSON
    if ! command -v jq &> /dev/null; then
      error "未找到jq工具，请先安装jq"
      echo "    Mac: brew install jq"
      echo "    Ubuntu/Debian: apt-get install jq"
      exit 1
    fi
    
    # 检查env.json中的环境
    local environments=$(jq -r 'keys[]' env.json)
    info "env.json中包含以下环境:"
    for env in $environments; do
      echo "  - $env"
    done
  else
    error "找不到env.json文件，无法继续"
    exit 1
  fi
  
  if [ -f .env ]; then
    success "找到.env文件"
  else
    warn "未找到.env文件，将尝试创建"
  fi
}

# 创建或更新.env文件
create_env_file() {
  local selected_env=$1
  
  info "从env.json生成.env文件..."
  echo "# Dify-on-WeChat 环境变量 - 通过test_env_vars.sh生成" > .env
  echo "# 环境: $selected_env" >> .env
  echo "# 生成时间: $(date)" >> .env
  echo "" >> .env
  
  jq -r --arg ENV "$selected_env" '.[$ENV] | to_entries | .[] | "\(.key)=\(.value)"' env.json >> .env
  
  # 添加环境类型标识
  echo "" >> .env
  echo "ENVIRONMENT=$selected_env # development test production" >> .env
  
  success ".env文件已创建/更新"
}

# 测试环境变量是否被正确加载
test_env_vars() {
  info "测试环境变量配置..."
  
  # Docker Compose可以读取.env文件
  if ! command -v docker-compose &> /dev/null; then
    warn "找不到docker-compose命令，将尝试使用docker compose命令"
    DOCKER_COMPOSE="docker compose"
  else
    DOCKER_COMPOSE="docker-compose"
  fi
  
  info "测试Docker Compose环境变量:"
  
  # 检查.env文件内容
  local key_vars=("DIFY_API_KEY" "WECHAT_TOKEN" "WECHAT_ENCODING_AES_KEY")
  for var in "${key_vars[@]}"; do
    if grep -q "^$var=" .env; then
      local value=$(grep "^$var=" .env | cut -d '=' -f 2)
      if [[ "$value" == "your_"* ]] || [[ "$value" == "test_"* ]] || [[ "$value" == "prod_"* ]]; then
        warn "警告: $var 使用了测试/默认值: $value"
      else
        success "$var 已配置"
      fi
    else
      error "错误: $var 未在.env中设置"
    fi
  done
  
  # 测试Docker Compose能否解析环境变量
  $DOCKER_COMPOSE config >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    success "Docker Compose能正确加载环境变量"
  else
    error "Docker Compose无法加载环境变量，请检查.env文件格式"
    $DOCKER_COMPOSE config
  fi
}

# 检查密钥是否有效
check_api_keys() {
  info "检查API密钥有效性..."
  
  # 检查Dify API Key
  local dify_api_key=$(grep "^DIFY_API_KEY=" .env | cut -d '=' -f 2)
  local dify_api_url=$(grep "^DIFY_API_URL=" .env | cut -d '=' -f 2)
  
  if [[ "$dify_api_key" == "your_"* ]] || [[ "$dify_api_key" == "test_"* ]] || [[ "$dify_api_key" == "prod_"* ]]; then
    warn "Dify API Key似乎是默认值，请更新为实际密钥"
  else
    info "Dify API Key格式看起来有效"
  fi
  
  # 检查企业微信配置
  local wechat_token=$(grep "^WECHAT_TOKEN=" .env | cut -d '=' -f 2)
  local wechat_encoding_aes_key=$(grep "^WECHAT_ENCODING_AES_KEY=" .env | cut -d '=' -f 2)
  local wechat_corp_id=$(grep "^WECHAT_CORP_ID=" .env | cut -d '=' -f 2)
  
  if [[ "$wechat_token" == "your_"* ]] || [[ "$wechat_encoding_aes_key" == "your_"* ]] || [[ "$wechat_corp_id" == "your_"* ]]; then
    warn "企业微信配置看起来使用了默认值，请更新为实际值"
  else
    info "企业微信配置格式看起来有效"
  fi
}

# 建议下一步操作
suggest_next_steps() {
  info "配置完成，建议的下一步操作:"
  echo "  1. 检查前端资源是否已构建到dist目录"
  echo "  2. 尝试使用以下命令启动测试环境:"
  echo "     $ docker-compose -f docker-compose-test.yml up -d"
  echo "  3. 使用API端点测试工具检查服务是否正常:"
  echo "     $ ./test_api_endpoints.sh"
  echo "  4. 解决任何配置或服务问题"
  echo "  5. 准备就绪后，使用生产配置部署:"
  echo "     $ docker-compose -f docker-compose.prod.yml up -d"
}

# 主函数
main() {
  echo "============================================"
  echo "    Dify-on-WeChat 环境变量测试与配置      "
  echo "============================================"
  echo
  
  check_config_files
  
  echo
  echo "请选择要使用的环境配置:"
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
  
  echo
  info "使用 $ENV 环境配置"
  create_env_file $ENV
  
  echo
  test_env_vars
  
  echo
  check_api_keys
  
  echo
  suggest_next_steps
}

# 执行主函数
main
