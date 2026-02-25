@echo off
REM 开发环境启动脚本 - 无自动重载（避免 Windows 重载问题）

echo 正在启动 Feishu Print Backend (开发模式 - 无自动重载)...
echo 提示: 修改代码后需要手动重启服务 (Ctrl+C 停止，然后重新运行此脚本)
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

REM 启动服务（不使用 reload，避免 Windows 重载问题）
uvicorn app.main:app --host 0.0.0.0 --port 8000

pause

