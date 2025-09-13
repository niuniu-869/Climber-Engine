# 登攀引擎 (Climber Engine)

一个基于大模型的智能Agent平台，支持多种AI模型集成和工具调用。

## 🚀 快速启动

### 一键启动 (推荐)

**macOS / Linux:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

启动脚本会自动：
- ✅ 检查系统依赖
- 📦 安装前后端依赖
- 🗄️ 初始化数据库
- 🚀 启动前后端服务
- 🌐 打开启动页面

### 访问地址

- 🎯 **启动页面**: http://localhost:5173 (系统状态监控)
- 📱 **前端应用**: http://localhost:5173/home
- 🔧 **后端 API**: http://localhost:8000
- 📚 **API 文档**: http://localhost:8000/docs

> 💡 详细启动说明请查看 [STARTUP_GUIDE.md](./STARTUP_GUIDE.md)

## 项目概述

登攀引擎是一个现代化的全栈AI应用平台，旨在为开发者提供强大的Agent构建和管理能力。通过直观的界面和丰富的API，用户可以轻松创建、配置和部署各种类型的AI Agent。

### 核心特性

- 🤖 **多模型支持**: 集成OpenAI GPT、Anthropic Claude等主流大模型
- 🛠️ **工具生态**: 丰富的内置工具和自定义工具支持
- 💬 **对话管理**: 智能的多轮对话和上下文管理
- 📚 **知识库**: 向量化知识存储和智能检索
- 🔌 **MCP协议**: 支持Model Context Protocol标准
- 🎨 **现代界面**: 基于React和Tailwind CSS的响应式UI
- 🚀 **高性能**: 异步处理和优化的数据库设计

## 技术架构

### 前端技术栈
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **状态管理**: Zustand
- **路由**: React Router
- **图标**: Lucide React

### 后端技术栈
- **框架**: FastAPI
- **数据库**: SQLAlchemy + SQLite
- **AI集成**: OpenAI API, Anthropic API
- **异步处理**: asyncio + uvicorn
- **依赖管理**: uv

## 项目结构

```
Climber Engine/
├── src/                     # React前端应用
│   ├── components/          # 可复用组件
│   ├── pages/              # 页面组件
│   ├── hooks/              # 自定义Hooks
│   ├── lib/                # 工具库
│   └── assets/             # 静态资源
├── public/                 # 公共资源
├── backend/                # FastAPI后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模式
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── tests/              # 测试文件
│   └── pyproject.toml      # 后端依赖
├── package.json            # 前端依赖
└── README.md              # 项目说明
```

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.9+
- uv (Python包管理器)

### 1. 克隆项目

```bash
git clone https://github.com/your-org/climber-engine.git
cd climber-engine
```

### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 安装uv (如果未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
uv pip install -e .

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加你的API密钥

# 初始化数据库
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload
```

### 3. 前端设置

```bash
# 回到项目根目录
cd ..

# 安装前端依赖
npm install

# 启动前端开发服务器
npm run dev
```

### 4. 访问应用

- 前端应用: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 开发指南

### 环境配置

在 `backend/.env` 文件中配置必要的环境变量：

```env
# AI模型API密钥
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# 数据库配置
DATABASE_URL=sqlite:///./climber_engine.db

# 应用配置
SECRET_KEY=your_secret_key
DEBUG=true
```

### 代码规范

#### 前端
```bash
# 代码检查
npm run lint

# 类型检查
npm run check

# 构建
npm run build
```

#### 后端
```bash
# 代码格式化
black app tests
isort app tests

# 类型检查
mypy app

# 测试
pytest
```

### 添加新功能

1. **后端API开发**:
   - 在 `app/models/` 中定义数据模型
   - 在 `app/schemas/` 中创建Pydantic模式
   - 在 `app/services/` 中实现业务逻辑
   - 在 `app/api/v1/endpoints/` 中添加API端点

2. **前端组件开发**:
   - 在 `src/components/` 中创建可复用组件
   - 在 `src/pages/` 中添加页面组件
   - 在 `src/hooks/` 中实现自定义Hooks
   - 在 `src/lib/` 中添加工具函数

## 部署

### Docker部署

```bash
# 构建并启动服务
docker-compose up -d
```

### 手动部署

#### 后端部署
```bash
# 生产环境启动
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### 前端部署
```bash
# 构建生产版本
npm run build

# 部署到静态文件服务器
# 将 dist/ 目录内容部署到你的Web服务器
```

## API文档

详细的API文档可以通过以下方式访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

### 主要API端点

- `GET /api/v1/agents` - 获取Agent列表
- `POST /api/v1/agents` - 创建新Agent
- `GET /api/v1/conversations` - 获取对话列表
- `POST /api/v1/conversations/{id}/chat` - 发送消息
- `GET /api/v1/tools` - 获取工具列表
- `POST /api/v1/knowledge/search` - 搜索知识库

## 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

### 提交规范

请使用以下格式提交代码：

```
type(scope): description

[optional body]

[optional footer]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 支持与反馈

- 📧 邮箱: team@climber.ai
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-org/climber-engine/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/your-org/climber-engine/discussions)
- 📖 文档: [项目文档](https://docs.climber.ai)

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新详情。

---

**登攀引擎** - 让AI Agent开发变得简单而强大 🚀
