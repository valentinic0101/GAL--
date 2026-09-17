@echo off
chcp 65001 >nul 2>&1
rem ============================================================
rem  深雪 ~miyuki~  停止游戏（Windows：双击本文件即可）
rem  作用：结束游戏服务进程，释放 8300 端口
rem ============================================================

cd /d "%~dp0"
set "PORT=8300"

echo ==============================================
echo    深雪 ~miyuki~  停止游戏服务
echo ==============================================
echo.

netstat -ano | findstr ":%PORT%" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
  echo （当前没有在运行的游戏服务，无需操作）
  echo.
  pause
  exit /b 0
)

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
  taskkill /F /PID %%p >nul 2>&1
)

timeout /t 1 /nobreak >nul
echo [OK] 游戏服务已停止，端口 %PORT% 已释放。
echo.
pause
