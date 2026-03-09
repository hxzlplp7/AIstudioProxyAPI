@echo off
chcp 65001 >nul
title AI Studio Proxy API - 一键启动指南
cd /d "%~dp0"

echo =======================================
echo          AI Studio Proxy API          
echo             一键启动脚本             
echo =======================================
echo.

:: 0. 关闭残留进程和释放端口
echo [提示] 正在检查并关闭所有 Node.js 进程...
taskkill /F /IM node.exe >nul 2>&1
echo [OK] Node.js 进程已清理。

echo [提示] 正在检查并释放代理所需端口 (2048, 3120, 9222)...
for %%P in (2048 3120 9222) do (
    for /f "tokens=5" %%A in ('netstat -aon ^| findstr ":%%P " ^| findstr "LISTENING"') do (
        if "%%A" NEQ "" (
            taskkill /F /PID %%A >nul 2>&1
        )
    )
)
echo [OK] 端口清理完成。

:: 1. 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 并添加到环境变量。
    pause
    exit /b 1
)
echo [OK] Python 环境已就绪。

:: 2. 检查并处理配置文件 .env
if not exist .env (
    echo [提示] 未找到 .env 配置文件，正在从 .env.example 自动生成...
    copy .env.example .env >nul
    echo [提示] .env 文件创建完成，可后续根据需要自行修改。
) else (
    echo [OK] 配置文件 .env 存在。
)

:: 3. 检查 Poetry 环境
call poetry --version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未找到 Poetry，正在尝试通过 pip 自动安装...
    python -m pip install poetry
    if errorlevel 1 (
        echo [错误] Poetry 安装失败，请手动安装后重试。
        pause
        exit /b 1
    )
)
echo [OK] Poetry 依赖管理工具已就绪。

:: 4. 检查并安装项目依赖
echo [提示] 检查和同步项目依赖^(耗费时间视网络而定^)...
call poetry install
if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络或配置。
    pause
    exit /b 1
)
echo [OK] 项目依赖已就绪。

:: 4.5. 补充检查核心运行库 uvicorn
echo [提示] 正在检查附加核心运行库 uvicorn...
call poetry run python -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
    echo [警告] 缺少 uvicorn 模块，正在为您补充安装...
    call poetry add uvicorn
)

:: 5. 启动服务
echo.
echo =======================================
echo [提示] 正在使用无头模式^(Headless^)启动服务...
call poetry run python launch_camoufox.py --headless

pause
