@echo off
chcp 65001 >nul
title AI Studio Proxy API
echo ================================
echo   AI Studio Proxy API 启动器
echo ================================
echo.

cd /d "%~dp0"

echo [1] 启动服务 (无头模式)
echo [2] 启动服务 (调试模式)
echo [3] 查询模型列表
echo [4] 测试聊天
echo [5] 打开 Web UI
echo [6] 退出
echo.

set /p choice=请选择 (1-6):

if "%choice%"=="1" goto headless
if "%choice%"=="2" goto debug
if "%choice%"=="3" goto models
if "%choice%"=="4" goto chat
if "%choice%"=="5" goto webui
if "%choice%"=="6" exit

:headless
echo.
echo 正在启动服务 (无头模式)...
poetry run python launch_camoufox.py --headless
goto end

:debug
echo.
echo 正在启动服务 (调试模式)...
poetry run python launch_camoufox.py
goto end

:models
curl -s http://127.0.0.1:2048/v1/models | python -m json.tool
pause
goto end

:chat
echo.
set /p prompt=请输入聊天内容:
curl -s -X POST "http://127.0.0.1:2048/v1/chat/completions" -H "Content-Type: application/json" -d "{\"model\":\"gemini-2.0-flash\",\"messages\":[{\"role\":\"user\",\"content\":\"%prompt%\"}],\"stream\":false}"
echo.
pause
goto end

:webui
start http://127.0.0.1:2048/
goto end

:end
