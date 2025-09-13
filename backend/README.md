# 登攀引擎后端

基于 FastAPI 的智能 Agent 平台后端服务。

## 功能特性

- 🤖 **智能 Agent 管理** - 创建、配置和管理多种类型的 AI Agent
- 💬 **对话系统** - 支持多轮对话和上下文管理
- 🛠️ **工具集成** - 集成各种外部工具和 API
- 📚 **知识库** - 向量化知识存储和检索
- 🔌 **MCP 协议** - 支持 Model Context Protocol
- 🚀 **高性能** - 异步处理和数据库优化
- 📊 **监控日志** - 完整的日志记录和性能监控

## 技术栈

- **框架**: FastAPI 0.104+
- **数据库**: SQLAlchemy 2.0 + SQLite
- **AI 模型**: OpenAI GPT / Anthropic Claude
- **异步**: asyncio + uvicorn
- **依赖管理**: uv
- **代码质量**: Black + isort + mypy + pytest

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── core/                # 核心配置
│   │   ├── config.py        # 应用配置
│   │   ├── database.py      # 数据库配置
│   │   └── security.py      # 安全配置
│   ├── models/              # 数据模型
│   │   ├── agent.py         # Agent 模型
│   │   ├── conversation.py  # 对话模型
│   │   ├── tool.py          # 工具模型
│   │   └── knowledge.py     # 知识库模型
│   ├── schemas/             # Pydantic 模式
│   │   ├── agent.py
│   │   ├── conversation.py
│   │   ├── tool.py
│   │   └── knowledge.py
│   ├── api/                 # API 路由
│   │   └── v1/
│   │       ├── router.py    # 主路由
│   │       └── endpoints/   # 端点实现
│   ├── services/            # 业务逻辑
│   │   ├── agent_service.py
│   │   ├── conversation_service.py
│   │   ├── tool_service.py
│   │   └── knowledge_service.py
│   └── utils/               # 工具函数
│       ├── logger.py        # 日志工具
│       ├── ai_client.py     # AI 客户端
│       └── mcp_client.py    # MCP 客户端
├── tests/                   # 测试文件
├── alembic/                 # 数据库迁移
├── pyproject.toml           # 项目配置
└── README.md
```

## 快速开始

### 1. 环境准备

确保已安装 Python 3.9+ 和 uv：

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证安装
uv --version
```

### 2. 安装依赖

```bash
# 进入后端目录
cd backend

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安装项目依赖
uv pip install -e .

# 安装开发依赖
uv pip install -e ".[dev]"
```

### 3. 环境配置

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的环境变量：

```env
# 数据库
DATABASE_URL=sqlite:///./climber_engine.db

# AI 模型 API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# 应用配置
SECRET_KEY=your_secret_key_here
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. 数据库初始化

```bash
# 初始化 Alembic
alembic init alembic

# 生成迁移文件
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 5. 启动服务

```bash
# 开发模式启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Python 直接运行
python -m app.main
```

服务启动后，访问：

- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- API 根路径: http://localhost:8000/api/v1

## 开发指南

### 代码规范

项目使用以下工具确保代码质量：

```bash
# 代码格式化
black app tests
isort app tests

# 类型检查
mypy app

# 代码检查
flake8 app tests

# 运行所有检查
pre-commit run --all-files
```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_agents.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### API 开发

1. **添加新模型**：在 `app/models/` 中定义 SQLAlchemy 模型
2. **创建 Schema**：在 `app/schemas/` 中定义 Pydantic 模式
3. **实现服务**：在 `app/services/` 中编写业务逻辑
4. **添加端点**：在 `app/api/v1/endpoints/` 中创建 API 端点
5. **注册路由**：在 `app/api/v1/router.py` 中注册新路由

### 数据库迁移

```bash
# 生成新的迁移文件
alembic revision --autogenerate -m "描述变更内容"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t climber-engine-backend .

# 运行容器
docker run -p 8000:8000 -e DATABASE_URL=sqlite:///./data/climber_engine.db climber-engine-backend
```

### 生产环境

```bash
# 使用 gunicorn 部署
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API 文档

### 核心端点

- `GET /api/v1/agents` - 获取 Agent 列表
- `POST /api/v1/agents` - 创建新 Agent
- `GET /api/v1/conversations` - 获取对话列表
- `POST /api/v1/conversations/{id}/chat` - 发送消息
- `GET /api/v1/tools` - 获取工具列表
- `POST /api/v1/tools/{id}/execute` - 执行工具
- `GET /api/v1/knowledge` - 获取知识库列表
- `POST /api/v1/knowledge/search` - 搜索知识库

详细的 API 文档请访问 `/docs` 端点查看 Swagger UI。

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 支持

如有问题或建议，请：

- 提交 [Issue](https://github.com/climber-team/climber-engine/issues)
- 发送邮件至 team@climber.ai
- 查看 [文档](https://docs.climber.ai)