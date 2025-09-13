#!/bin/bash

# 登攀引擎一键启动脚本
# Climber Engine One-Click Start Script

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 加载Trae环境变量
load_trae_env() {
    # 检查是否在Trae环境中
    local trae_node_path=""
    local uv_path=""
    
    # 尝试多个可能的Node.js路径
    if [ -n "$HOME" ] && [ -d "$HOME/.trae/sdks/versions/node/current" ]; then
        trae_node_path="$HOME/.trae/sdks/versions/node/current"
    elif [ -d "/Users/mac/.trae/sdks/versions/node/current" ]; then
        trae_node_path="/Users/mac/.trae/sdks/versions/node/current"
    fi
    
    # 尝试多个可能的uv路径
    if [ -n "$HOME" ] && [ -f "$HOME/.local/bin/uv" ]; then
        uv_path="$HOME/.local/bin"
    elif [ -f "/Users/mac/.local/bin/uv" ]; then
        uv_path="/Users/mac/.local/bin"
    fi
    
    # 构建PATH
    local new_paths=""
    if [ -n "$trae_node_path" ]; then
        new_paths="$trae_node_path"
        log_info "已加载Trae Node.js环境: $trae_node_path"
    fi
    
    if [ -n "$uv_path" ]; then
        if [ -n "$new_paths" ]; then
            new_paths="$new_paths:$uv_path"
        else
            new_paths="$uv_path"
        fi
        log_info "已加载uv环境: $uv_path"
    fi
    
    if [ -n "$new_paths" ]; then
        export PATH="$new_paths:$PATH"
    fi
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    # 先尝试加载Trae环境
    load_trae_env
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装，请先安装 Node.js"
        log_info "提示：如果您使用的是Trae IDE，请确保在Trae终端中运行此脚本"
        exit 1
    fi
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装，请先安装 Python3"
        exit 1
    fi
    
    # 检查 uv
    if ! command -v uv &> /dev/null; then
        log_warning "uv 未安装，正在安装..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
    fi
    
    log_success "依赖检查完成"
}

# 安装前端依赖
install_frontend_deps() {
    log_info "安装前端依赖..."
    if [ ! -d "node_modules" ]; then
        npm install
    else
        log_info "前端依赖已存在，跳过安装"
    fi
    log_success "前端依赖安装完成"
}

# 安装后端依赖
install_backend_deps() {
    log_info "安装后端依赖..."
    cd backend
    if [ ! -d ".venv" ]; then
        uv sync
    else
        log_info "后端依赖已存在，跳过安装"
    fi
    cd ..
    log_success "后端依赖安装完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    cd backend
    if [ ! -f "data/climber_engine.db" ]; then
        uv run python init_db.py
        log_success "数据库初始化完成"
    else
        log_info "数据库已存在，跳过初始化"
    fi
    cd ..
}

# 启动后端服务
start_backend() {
    log_info "启动后端服务..."
    cd backend
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    log_success "后端服务已启动 (PID: $BACKEND_PID)"
}

# 启动前端服务
start_frontend() {
    log_info "启动前端服务..."
    npm run dev &
    FRONTEND_PID=$!
    log_success "前端服务已启动 (PID: $FRONTEND_PID)"
}

# 等待服务启动
wait_for_services() {
    log_info "等待服务启动..."
    
    # 等待后端服务
    log_info "检查后端服务状态..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            log_success "后端服务已就绪"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "后端服务启动超时"
            exit 1
        fi
        sleep 2
    done
    
    # 等待前端服务
    log_info "检查前端服务状态..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            log_success "前端服务已就绪"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "前端服务启动超时"
            exit 1
        fi
        sleep 2
    done
}

# 显示启动信息
show_startup_info() {
    echo ""
    echo "======================================"
    echo -e "${GREEN}🚀 登攀引擎启动成功！${NC}"
    echo "======================================"
    echo ""
    echo -e "${BLUE}📱 前端应用:${NC} http://localhost:5173"
    echo -e "${BLUE}🔧 后端 API:${NC} http://localhost:8000"
    echo -e "${BLUE}📚 API 文档:${NC} http://localhost:8000/docs"
    echo -e "${BLUE}🎯 启动页面:${NC} http://localhost:5173"
    echo ""
    echo -e "${YELLOW}💡 提示:${NC}"
    echo "  - 按 Ctrl+C 停止所有服务"
    echo "  - 查看日志请检查终端输出"
    echo "  - 如需重启，请先停止当前服务"
    echo ""
}

# 清理函数
cleanup() {
    log_info "正在停止服务..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        log_info "后端服务已停止"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        log_info "前端服务已停止"
    fi
    log_success "所有服务已停止"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 主函数
main() {
    echo ""
    echo "======================================"
    echo -e "${BLUE}🏔️  登攀引擎启动脚本${NC}"
    echo -e "${BLUE}    Climber Engine Startup${NC}"
    echo "======================================"
    echo ""
    
    # 检查是否在正确的目录
    if [ ! -f "package.json" ] || [ ! -d "backend" ]; then
        log_error "请在项目根目录下运行此脚本"
        exit 1
    fi
    
    check_dependencies
    install_frontend_deps
    install_backend_deps
    init_database
    
    log_info "启动服务..."
    start_backend
    sleep 3  # 给后端一些启动时间
    start_frontend
    
    wait_for_services
    show_startup_info
    
    # 保持脚本运行
    log_info "服务正在运行中，按 Ctrl+C 停止..."
    while true; do
        sleep 1
    done
}

# 运行主函数
main "$@"