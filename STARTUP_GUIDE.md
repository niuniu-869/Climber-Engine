# 登攀引擎启动指南

## 🚀 一键启动

登攀引擎提供了便捷的一键启动脚本，支持 macOS/Linux 和 Windows 系统。

### macOS / Linux 用户

```bash
# 在项目根目录下运行
./start.sh
```

### Windows 用户

```cmd
# 在项目根目录下运行
start.bat
```

## 📋 系统要求

### 必需依赖
- **Node.js** (v16+)
- **npm** (v8+)
- **Python** (v3.9+)
- **uv** (Python 包管理器)

### 安装 uv (如果未安装)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```cmd
pip install uv
```

## 🎯 启动流程

启动脚本会自动执行以下步骤：

1. ✅ **依赖检查** - 验证系统环境
2. 📦 **安装依赖** - 自动安装前后端依赖
3. 🗄️ **初始化数据库** - 创建必要的数据表
4. 🔧 **启动后端** - 启动 FastAPI 服务器 (端口 8000)
5. 📱 **启动前端** - 启动 React 开发服务器 (端口 5173)
6. 🌐 **打开浏览器** - 自动打开启动页面

## 🌐 服务地址

启动成功后，可以访问以下地址：

| 服务 | 地址 | 描述 |
|------|------|------|
| 🎯 **启动页面** | http://localhost:5173 | 系统状态监控和快速导航 |
| 📱 **前端应用** | http://localhost:5173/home | 主要用户界面 |
| 🔧 **后端 API** | http://localhost:8000 | RESTful API 服务 |
| 📚 **API 文档** | http://localhost:8000/docs | Swagger 接口文档 |
| 🔍 **MCP 服务** | http://localhost:8000/api/v1/mcp | AI 工具调用接口 |

## 🛠️ 手动启动 (开发模式)

如果需要分别启动前后端服务进行开发：

### 启动后端
```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 启动前端
```bash
# 在项目根目录
npm run dev
```

## 🔧 故障排除

### 常见问题

**1. 端口被占用**
```bash
# 查看端口占用
lsof -i :8000  # 后端端口
lsof -i :5173  # 前端端口

# 杀死占用进程
kill -9 <PID>
```

**2. 依赖安装失败**
```bash
# 清理缓存重新安装
npm cache clean --force
npm install

# 后端依赖
cd backend
uv cache clean
uv sync
```

**3. 数据库初始化失败**
```bash
# 删除数据库文件重新初始化
rm backend/data/climber_engine.db
cd backend
uv run python init_db.py
```

**4. Python 环境问题**
```bash
# 确保使用正确的 Python 版本
python3 --version

# 如果 uv 未找到，添加到 PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

### 日志查看

- **后端日志**: 查看后端终端窗口输出
- **前端日志**: 查看前端终端窗口输出
- **浏览器控制台**: F12 打开开发者工具查看前端错误

## 🛑 停止服务

### 使用启动脚本
- **macOS/Linux**: 在启动脚本终端按 `Ctrl+C`
- **Windows**: 关闭对应的命令行窗口

### 手动停止
```bash
# 查找并停止进程
ps aux | grep uvicorn
ps aux | grep vite
kill <PID>
```

## 🎨 启动页面功能

启动页面提供以下功能：

- 🔍 **实时服务监控** - 显示前后端服务状态
- 🚀 **快速导航** - 一键访问各个服务
- 📊 **系统状态** - 整体健康状况检查
- 🔄 **状态刷新** - 手动刷新服务状态
- 📱 **响应式设计** - 支持各种屏幕尺寸

## 📞 技术支持

如果遇到问题，请：

1. 查看本指南的故障排除部分
2. 检查终端输出的错误信息
3. 确认系统环境符合要求
4. 查看项目 GitHub Issues

---

**登攀引擎团队** 🏔️

*让 AI 驱动你的编程技能提升之旅*