#!/bin/bash

# 创建桌面快捷方式脚本
# Create Desktop Shortcut Script

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取当前脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="登攀引擎 (Climber Engine)"
SHORTCUT_NAME="Climber Engine"

echo -e "${BLUE}🏔️  登攀引擎桌面快捷方式创建工具${NC}"
echo "======================================"
echo ""

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo -e "${BLUE}[INFO]${NC} 检测到 macOS 系统"
    
    DESKTOP_PATH="$HOME/Desktop"
    SHORTCUT_PATH="$DESKTOP_PATH/$SHORTCUT_NAME.command"
    
    # 创建 .command 文件
    cat > "$SHORTCUT_PATH" << EOF
#!/bin/bash
# 登攀引擎启动快捷方式
cd "$SCRIPT_DIR"
./start.sh
EOF
    
    # 添加执行权限
    chmod +x "$SHORTCUT_PATH"
    
    echo -e "${GREEN}[SUCCESS]${NC} 桌面快捷方式已创建: $SHORTCUT_PATH"
    echo -e "${YELLOW}[提示]${NC} 双击桌面上的 '$SHORTCUT_NAME.command' 即可启动登攀引擎"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo -e "${BLUE}[INFO]${NC} 检测到 Linux 系统"
    
    DESKTOP_PATH="$HOME/Desktop"
    SHORTCUT_PATH="$DESKTOP_PATH/$SHORTCUT_NAME.desktop"
    
    # 创建 .desktop 文件
    cat > "$SHORTCUT_PATH" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$PROJECT_NAME
Comment=智能 AI 驱动的编程技能提升平台
Exec=gnome-terminal -- bash -c "cd '$SCRIPT_DIR' && ./start.sh; exec bash"
Icon=applications-development
Terminal=false
Categories=Development;IDE;
StartupNotify=true
EOF
    
    # 添加执行权限
    chmod +x "$SHORTCUT_PATH"
    
    echo -e "${GREEN}[SUCCESS]${NC} 桌面快捷方式已创建: $SHORTCUT_PATH"
    echo -e "${YELLOW}[提示]${NC} 双击桌面上的 '$SHORTCUT_NAME' 图标即可启动登攀引擎"
    
else
    echo -e "${RED}[ERROR]${NC} 不支持的操作系统: $OSTYPE"
    echo -e "${YELLOW}[提示]${NC} 请手动运行 ./start.sh 启动项目"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ 快捷方式创建完成！${NC}"
echo ""
echo "现在你可以："
echo "1. 双击桌面快捷方式启动登攀引擎"
echo "2. 或者在项目目录运行: ./start.sh"
echo "3. 或者在项目目录运行: $0"
echo ""
echo -e "${BLUE}📱 启动后访问: http://localhost:5173${NC}"
echo ""