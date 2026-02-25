@echo off
echo ============================================================
echo 重启后端服务
echo ============================================================
echo.

echo 正在停止后端服务...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *run_server*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo 正在启动后端服务...
start "智能排版后端服务" cmd /k "cd /d %~dp0 && venv\Scripts\python.exe run_server.py"

echo.
echo ============================================================
echo ✓ 后端服务已重启
echo ============================================================
echo.
echo 服务地址: http://localhost:8000
echo 文档地址: http://localhost:8000/docs
echo.
pause
