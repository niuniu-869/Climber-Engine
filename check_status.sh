#!/bin/bash

# 登攀引擎状态检查脚本
# Climber Engine Status Check Script

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查函数
check_service() {
    local name="$1"
    local url="$2"
    local timeout="${3:-5}"
    
    echo -n "  检查 $name... "
    
    if curl -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 在线${NC}"
        return 0
    else
        echo -e "${RED}❌ 离线${NC}"
        return 1
    fi
}

check_port() {
    local port="$1"
    local name="$2"
    
    echo -n "  检查端口 $port ($name)... "
    
    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 已占用${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  空闲${NC}"
        return 1
    fi
}

check_dependency() {
    local cmd="$1"
    local name="$2"
    
    echo -n "  检查 $name... "
    
    if command -v "$cmd" > /dev/null 2>&1; then
        local version=$("$cmd" --version 2>/dev/null | head -n1 || echo "未知版本")
        echo -e "${GREEN}✅ 已安装${NC} ($version)"
        return 0
    else
        echo -e "${RED}❌ 未安装${NC}"
        return 1
    fi
}

echo ""
echo "======================================"
echo -e "${BLUE}🏔️  登攀引擎状态检查${NC}"
echo -e "${BLUE}    Climber Engine Status Check${NC}"
echo "======================================"
echo ""

# 检查系统依赖
echo -e "${BLUE}📋 系统依赖检查${NC}"
echo "--------------------------------------"
dep_errors=0

check_dependency "node" "Node.js" || ((dep_errors++))
check_dependency "npm" "npm" || ((dep_errors++))
check_dependency "python3" "Python3" || ((dep_errors++))
check_dependency "uv" "uv" || ((dep_errors++))
check_dependency "curl" "curl" || ((dep_errors++))

echo ""

# 检查端口占用
echo -e "${BLUE}🔌 端口占用检查${NC}"
echo "--------------------------------------"
port_errors=0

check_port "8000" "后端服务" || ((port_errors++))
check_port "5173" "前端服务" || ((port_errors++))

echo ""

# 检查服务状态
echo -e "${BLUE}🌐 服务状态检查${NC}"
echo "--------------------------------------"
service_errors=0

check_service "后端健康检查" "http://localhost:8000/health" || ((service_errors++))
check_service "后端 API 根路径" "http://localhost:8000/" || ((service_errors++))
check_service "MCP 能力接口" "http://localhost:8000/api/v1/mcp/capabilities" || ((service_errors++))
check_service "前端应用" "http://localhost:5173" || ((service_errors++))

echo ""

# 检查文件和目录
echo -e "${BLUE}📁 项目文件检查${NC}"
echo "--------------------------------------"
file_errors=0

files_to_check=(
    "package.json:前端配置文件"
    "backend/pyproject.toml:后端配置文件"
    "start.sh:启动脚本"
    "start.bat:Windows启动脚本"
    "STARTUP_GUIDE.md:启动指南"
    "backend/app/main.py:后端主文件"
    "src/App.tsx:前端主文件"
    "src/pages/Launch.tsx:启动页面"
)

for file_info in "${files_to_check[@]}"; do
    file_path="${file_info%%:*}"
    file_desc="${file_info##*:}"
    
    echo -n "  检查 $file_desc... "
    
    if [ -f "$file_path" ]; then
        echo -e "${GREEN}✅ 存在${NC}"
    else
        echo -e "${RED}❌ 缺失${NC} ($file_path)"
        ((file_errors++))
    fi
done

echo ""

# 检查数据库
echo -e "${BLUE}🗄️  数据库检查${NC}"
echo "--------------------------------------"
db_errors=0

echo -n "  检查数据库文件... "
if [ -f "backend/data/climber_engine.db" ]; then
    echo -e "${GREEN}✅ 存在${NC}"
else
    echo -e "${YELLOW}⚠️  不存在${NC} (首次运行时会自动创建)"
    ((db_errors++))
fi

echo -n "  检查数据目录... "
if [ -d "backend/data" ]; then
    echo -e "${GREEN}✅ 存在${NC}"
else
    echo -e "${YELLOW}⚠️  不存在${NC} (首次运行时会自动创建)"
fi

echo ""

# 总结
echo "======================================"
echo -e "${BLUE}📊 检查总结${NC}"
echo "======================================"

total_errors=$((dep_errors + service_errors + file_errors))

if [ $total_errors -eq 0 ]; then
    echo -e "${GREEN}🎉 所有检查通过！登攀引擎运行状态良好${NC}"
    echo ""
    echo "✅ 系统依赖: 完整"
    echo "✅ 服务状态: 正常"
    echo "✅ 项目文件: 完整"
    echo ""
    echo -e "${BLUE}🚀 可以正常使用以下功能:${NC}"
    echo "  - 启动页面: http://localhost:5173"
    echo "  - 前端应用: http://localhost:5173/home"
    echo "  - 后端 API: http://localhost:8000"
    echo "  - API 文档: http://localhost:8000/docs"
else
    echo -e "${YELLOW}⚠️  发现 $total_errors 个问题${NC}"
    echo ""
    
    if [ $dep_errors -gt 0 ]; then
        echo -e "${RED}❌ 系统依赖: $dep_errors 个问题${NC}"
        echo "   解决方案: 请安装缺失的依赖"
    else
        echo -e "${GREEN}✅ 系统依赖: 正常${NC}"
    fi
    
    if [ $service_errors -gt 0 ]; then
        echo -e "${RED}❌ 服务状态: $service_errors 个问题${NC}"
        echo "   解决方案: 运行 ./start.sh 启动服务"
    else
        echo -e "${GREEN}✅ 服务状态: 正常${NC}"
    fi
    
    if [ $file_errors -gt 0 ]; then
        echo -e "${RED}❌ 项目文件: $file_errors 个问题${NC}"
        echo "   解决方案: 检查项目完整性"
    else
        echo -e "${GREEN}✅ 项目文件: 完整${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}💡 建议操作:${NC}"
    
    if [ $dep_errors -gt 0 ]; then
        echo "  1. 安装缺失的系统依赖"
    fi
    
    if [ $service_errors -gt 0 ]; then
        echo "  2. 运行启动脚本: ./start.sh"
    fi
    
    if [ $file_errors -gt 0 ]; then
        echo "  3. 检查项目文件完整性"
    fi
fi

echo ""
echo -e "${BLUE}🔧 其他有用命令:${NC}"
echo "  - 启动服务: ./start.sh"
echo "  - 状态检查: ./check_status.sh"
echo "  - 创建快捷方式: ./create_desktop_shortcut.sh"
echo "  - 查看启动指南: cat STARTUP_GUIDE.md"
echo ""