@echo off
chcp 65001 >nul
title AI Studio Proxy API - 无头模式启动
cd /d "%~dp0"
echo ================================
echo   正在启动服务 (无头模式)...
echo ================================
echo.
poetry run python launch_camoufox.py --headless
pause
