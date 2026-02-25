@echo off
REM 启动脚本 - Windows 版本
REM 使用 watchfiles 替代默认的文件监控，避免 Windows 上的重载问题

echo 正在启动 Feishu Print Backend...
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo 错误: 未找到虚拟环境，请先创建虚拟环境
    echo 运行: python -m venv venv
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 启动服务（使用 Python 脚本，更好的错误处理）
echo 使用 watchfiles 文件监控（Windows 优化）...
python run_server.py

pause

