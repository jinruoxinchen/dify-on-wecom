#!/bin/bash
# Docker配置检查脚本
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

# 检查Docker配置文件
check_docker_files() {
  info "检查Docker配置文件..."
  
  # 主要的docker-compose.yml文件
  if [ ! -f docker-compose.yml ]; then
    error "找不到docker-compose.yml文件"
  else
    success "找到docker-compose.yml文件"
    check_compose_file "docker-compose.yml"
  fi
  
  # 开发环境配置
  if [ ! -f docker-compose.dev.yml ]; then
    warn "找不到docker-compose.dev.yml文件"
  else
    success "找到docker-compose.dev.yml文件"
    check_compose_file "docker-compose.dev.yml"
  fi
  
  # 生产环境配置
  if [ ! -f docker-compose.prod.yml ]; then
    warn "找不到docker-compose.prod.yml文件"
  else
    success "找到docker-compose.prod.yml文件"
    check_compose_file "docker-compose.prod.yml"
  fi
  
  # 测试环境配置
  if [ ! -f docker-compose-test.yml ]; then
    warn "找不到docker-compose-test.yml文件"
  else
    success "找到docker-compose-test.yml文件"
    check_compose_file "docker-compose-test.yml"
  fi
  
  # Dockerfile
  if [ ! -f docker/Dockerfile ]; then
    warn "找不到docker/Dockerfile文件"
  else
    success "找到docker/Dockerfile文件"
    check_dockerfile
  fi
  
  # nginx配置
  if [ ! -f docker/nginx.conf ]; then
    warn "找不到docker/nginx.conf文件"
  else
    success "找到docker/nginx.conf文件"
    check_nginx_conf
  fi
}

# 检查docker-compose配置文件
check_compose_file() {
  local file=$1
  info "验证 $file 文件的语法..."
  
  if $DOCKER_COMPOSE -f $file config > /dev/null 2>&1; then
    success "$file 配置有效"
    
    # 提取服务列表
    local services=$($DOCKER_COMPOSE -f $file config --services)
    info "$file 定义了以下服务:"
    for service in $services; do
      echo "  - $service"
    done
    
    # 检查环境变量
    if grep -q "\${.*}" $file; then
      warn "$file 使用了环境变量，确保在启动服务前设置这些变量"
      grep -o "\${[^}]*}" $file | sort | uniq | while read var; do
        echo "  - $var"
      done
    fi
    
    # 检查使用了哪些端口
    info "端口映射:"
    grep -A 3 "ports:" $file | grep -E "\"[0-9]+:" | sed 's/[^0-9]*\([0-9]\+\):.*/  - \1/g' | sort | uniq
    
    # 检查使用了哪些卷
    if grep -q "volumes:" $file; then
      info "使用了以下卷:"
      local volumes=$(grep -A 5 "volumes:" $file | grep -v "volumes:" | grep -v -- "--" | sed 's/^ *//g' | grep -v "^$")
      if [ ! -z "$volumes" ]; then
        echo "$volumes" | while read line; do
          echo "  - $line"
        done
      fi
    fi
    
  else
    error "$file 配置无效，请检查语法"
    $DOCKER_COMPOSE -f $file config
  fi
  
  echo
}

# 检查Dockerfile
check_dockerfile() {
  info "分析 Dockerfile 内容..."
  
  local base_image=$(grep "^FROM" docker/Dockerfile | head -1 | awk '{print $2}')
  info "基础镜像: $base_image"
  
  # 检查关键步骤
  if grep -q "COPY" docker/Dockerfile; then
    info "复制文件的步骤:"
    grep "COPY" docker/Dockerfile | while read line; do
      local src=$(echo $line | awk '{print $2}')
      local dst=$(echo $line | awk '{print $3}')
      echo "  - 从 $src 复制到 $dst"
      
      # 检查源文件/目录是否存在
      local src_path=$(echo $src | cut -d'/' -f1)
      if [ ! -e "$src_path" ]; then
        warn "  警告: 源文件/目录 '$src_path' 不存在!"
      fi
    done
  fi
  
  if grep -q "EXPOSE" docker/Dockerfile; then
    info "暴露的端口:"
    grep "EXPOSE" docker/Dockerfile | while read line; do
      local port=$(echo $line | awk '{print $2}')
      echo "  - $port"
    done
  fi
  
  if grep -q "ENTRYPOINT" docker/Dockerfile; then
    info "入口点命令:"
    grep "ENTRYPOINT" docker/Dockerfile | while read line; do
      echo "  - $line"
    done
  fi
  
  if grep -q "VOLUME" docker/Dockerfile; then
    info "定义的卷:"
    grep "VOLUME" docker/Dockerfile | while read line; do
      local volume=$(echo $line | awk '{print $2}')
      echo "  - $volume"
    done
  fi
  
  echo
}

# 检查nginx配置
check_nginx_conf() {
  info "分析 nginx.conf 内容..."
  
  # 检查监听端口
  if grep -q "listen" docker/nginx.conf; then
    info "监听的端口:"
    grep "listen" docker/nginx.conf | while read line; do
      local port=$(echo $line | awk '{print $2}' | sed 's/;//')
      echo "  - $port"
    done
  fi
  
  # 检查server_name
  if grep -q "server_name" docker/nginx.conf; then
    info "服务器名称:"
    grep "server_name" docker/nginx.conf | while read line; do
      local name=$(echo $line | awk '{print $2}' | sed 's/;//')
      echo "  - $name"
    done
  fi
  
  # 检查代理配置
  if grep -q "proxy_pass" docker/nginx.conf; then
    info "代理配置:"
    grep -A 1 "location" docker/nginx.conf | grep -B 1 "proxy_pass" | while read line; do
      if echo $line | grep -q "location"; then
        local path=$(echo $line | awk '{print $2}' | sed 's/;//')
        echo -n "  - 路径: $path"
      elif echo $line | grep -q "proxy_pass"; then
        local target=$(echo $line | awk '{print $2}' | sed 's/;//')
        echo " -> 目标: $target"
      fi
    done
  fi
  
  # 检查静态文件配置
  if grep -q "root" docker/nginx.conf; then
    info "静态文件配置:"
    grep -A 3 "location /" docker/nginx.conf | grep "root\|index" | while read line; do
      echo "  - $line"
    done
  fi
  
  echo
}

# 验证环境变量
check_env_variables() {
  info "检查环境变量配置..."
  
  if [ -f env.json ]; then
    success "找到env.json文件"
    
    # 需要jq工具来处理JSON
    if ! command -v jq &> /dev/null; then
      warn "未找到jq工具，无法解析env.json文件内容"
      echo "  建议安装jq: brew install jq"
    else
      info "env.json包含以下环境:"
      jq -r 'keys[]' env.json
      
      info "开发环境变量示例:"
      jq -r '.development | keys[]' env.json | head -5 | while read key; do
        echo "  - $key: $(jq -r --arg k "$key" '.development[$k]' env.json)"
      done
      
      info "测试环境变量示例:"
      jq -r '.test | keys[]' env.json | head -5 | while read key; do
        echo "  - $key: $(jq -r --arg k "$key" '.test[$k]' env.json)"
      done
      
      warn "确保在实际部署前修改env.json中的API密钥和其他敏感信息"
    fi
  else
    warn "找不到env.json文件"
  fi
  
  # 检查.env文件
  if [ -f .env ]; then
    success "找到.env文件，包含以下变量:"
    grep -v "^#" .env | grep -v "^$" | while read line; do
      local key=$(echo $line | cut -d'=' -f1)
      local value=$(echo $line | cut -d'=' -f2-)
      
      # 隐藏敏感信息
      if echo $key | grep -iq "key\|secret\|password\|token"; then
        echo "  - $key: ********"
      else
        echo "  - $key: $value"
      fi
    done
  else
    warn "找不到.env文件，Docker Compose可能无法使用环境变量"
  fi
}

# 检查项目结构
check_project_structure() {
  info "检查关键项目目录和文件..."
  
  # 后端目录
  if [ -d "src" ]; then
    success "找到src目录"
    local backend_files=$(find src -name "*.py" | wc -l)
    info "后端Python文件数量: $backend_files"
  else
    warn "找不到src目录"
  fi
  
  # 前端目录
  if [ -d "dist" ]; then
    success "找到dist目录"
    if [ -f "dist/index.html" ]; then
      success "找到dist/index.html文件"
    else
      warn "找不到dist/index.html文件，前端资源可能未构建"
    fi
  else
    warn "找不到dist目录，前端资源可能未构建"
  fi
  
  # 配置目录
  if [ -d "config" ]; then
    success "找到config目录"
  else
    warn "找不到config目录"
  fi
  
  # 日志目录
  if [ -d "logs" ]; then
    success "找到logs目录"
  else
    warn "找不到logs目录，将在部署时自动创建"
  fi
}

# 主函数
main() {
  echo "============================================"
  echo "       Dify-on-WeChat Docker配置检查       "
  echo "============================================"
  echo
  
  check_prerequisites
  check_docker_files
  check_env_variables
  check_project_structure
  
  echo
  echo "============================================"
  echo "             配置检查总结                  "
  echo "============================================"
  echo
  info "1. 在部署前，请确保:"
  echo "   - 已配置正确的环境变量（在env.json或.env文件中）"
  echo "   - 前端资源已构建（在dist目录中）"
  echo "   - 已创建必要的目录结构"
  echo
  info "2. 当前项目存在的问题:"
  echo "   - Dockerfile中引用的Java源文件不存在，需要修改或补充"
  echo "   - 如果使用企业微信，需确保企业微信相关配置正确"
  echo "   - 确保RabbitMQ的配置与实际需求匹配"
  echo
  info "3. 推荐的部署方法:"
  echo "   - 首先测试docker-compose-test.yml配置"
  echo "   - 解决任何配置问题后再使用生产环境配置"
  echo "   - 部署后使用test_api_endpoints.sh测试各个端点"
  echo
  
  success "配置检查完成！"
}

# 执行主函数
main
