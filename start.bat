@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 登攀引擎一键启动脚本 (Windows)
REM Climber Engine One-Click Start Script (Windows)

REM 颜色定义
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 日志函数
set "log_info=echo %BLUE%[INFO]%NC%"
set "log_success=echo %GREEN%[SUCCESS]%NC%"
set "log_warning=echo %YELLOW%[WARNING]%NC%"
set "log_error=echo %RED%[ERROR]%NC%"

echo.
echo ======================================
echo %BLUE%🏔️  登攀引擎启动脚本%NC%
echo %BLUE%    Climber Engine Startup%NC%
echo ======================================
echo.

REM 检查是否在正确的目录
if not exist "package.json" (
    %log_error% 请在项目根目录下运行此脚本
    pause
    exit /b 1
)

if not exist "backend" (
    %log_error% 找不到 backend 目录，请确认在正确的项目目录下
    pause
    exit /b 1
)

%log_info% 检查系统依赖...

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    %log_error% Node.js 未安装，请先安装 Node.js
    pause
    exit /b 1
)

REM 检查 npm
npm --version >nul 2>&1
if errorlevel 1 (
    %log_error% npm 未安装，请先安装 npm
    pause
    exit /b 1
)

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    python3 --version >nul 2>&1
    if errorlevel 1 (
        %log_error% Python 未安装，请先安装 Python
        pause
        exit /b 1
    )
)

REM 检查 uv
uv --version >nul 2>&1
if errorlevel 1 (
    %log_warning% uv 未安装，请手动安装 uv 包管理器
    %log_info% 安装命令: pip install uv
    pause
    exit /b 1
)

%log_success% 依赖检查完成

%log_info% 安装前端依赖...
if not exist "node_modules" (
    npm install
    if errorlevel 1 (
        %log_error% 前端依赖安装失败
        pause
        exit /b 1
    )
) else (
    %log_info% 前端依赖已存在，跳过安装
)
%log_success% 前端依赖安装完成

%log_info% 安装后端依赖...
cd backend
if not exist ".venv" (
    uv sync
    if errorlevel 1 (
        %log_error% 后端依赖安装失败
        cd ..
        pause
        exit /b 1
    )
) else (
    %log_info% 后端依赖已存在，跳过安装
)
cd ..
%log_success% 后端依赖安装完成

%log_info% 初始化数据库...
cd backend
if not exist "data\climber_engine.db" (
    uv run python init_db.py
    if errorlevel 1 (
        %log_error% 数据库初始化失败
        cd ..
        pause
        exit /b 1
    )
    %log_success% 数据库初始化完成
) else (
    %log_info% 数据库已存在，跳过初始化
)
cd ..

%log_info% 启动服务...

REM 启动后端服务
%log_info% 启动后端服务...
start "Climber Engine Backend" cmd /k "cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM 等待后端启动
%log_info% 等待后端服务启动...
timeout /t 5 /nobreak >nul

REM 启动前端服务
%log_info% 启动前端服务...
start "Climber Engine Frontend" cmd /k "npm run dev"

REM 等待前端启动
%log_info% 等待前端服务启动...
timeout /t 5 /nobreak >nul

REM 等待服务完全启动
%log_info% 检查服务状态...
set /a "attempts=0"
:check_backend
set /a "attempts+=1"
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    if !attempts! lss 15 (
        timeout /t 2 /nobreak >nul
        goto check_backend
    ) else (
        %log_warning% 后端服务可能未完全启动，请检查后端窗口
    )
) else (
    %log_success% 后端服务已就绪
)

set /a "attempts=0"
:check_frontend
set /a "attempts+=1"
curl -s http://localhost:5173 >nul 2>&1
if errorlevel 1 (
    if !attempts! lss 15 (
        timeout /t 2 /nobreak >nul
        goto check_frontend
    ) else (
        %log_warning% 前端服务可能未完全启动，请检查前端窗口
    )
) else (
    %log_success% 前端服务已就绪
)

echo.
echo ======================================
echo %GREEN%🚀 登攀引擎启动成功！%NC%
echo ======================================
echo.
echo %BLUE%📱 前端应用:%NC% http://localhost:5173
echo %BLUE%🔧 后端 API:%NC% http://localhost:8000
echo %BLUE%📚 API 文档:%NC% http://localhost:8000/docs
echo %BLUE%🎯 启动页面:%NC% http://localhost:5173
echo.
echo %YELLOW%💡 提示:%NC%
echo   - 前后端服务已在新窗口中启动
echo   - 关闭对应窗口可停止服务
echo   - 如需重启，请先关闭所有服务窗口
echo.

REM 打开浏览器
%log_info% 正在打开浏览器...
start http://localhost:5173

echo %GREEN%✅ 启动完成！浏览器将自动打开启动页面%NC%
echo.
pause