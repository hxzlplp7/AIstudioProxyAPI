@echo off
chcp 65001 >nul
title AI Studio Proxy API - 测试环境
cd /d "%~dp0"
echo ================================
echo   正在检查 Poetry 环境信息...
echo ================================
echo.
call poetry env info
pause
