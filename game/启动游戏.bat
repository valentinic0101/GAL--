@echo off
chcp 65001 >nul 2>&1
rem ============================================================
rem  深雪 ~miyuki~  一键启动（Windows：双击本文件即可）
rem  注意：本文件仅适用于 Windows。macOS 请双击「启动游戏.command」
rem  作用：检查依赖 - 启动游戏服务 - 自动打开浏览器
rem ============================================================

cd /d "%~dp0"

set "PORT=8300"
set "URL=http://127.0.0.1:%PORT%/"
set "HEALTH=%URL%api/health"
set "LOG=logs\server.log"
set /a N=0

echo ==============================================
echo    深雪 ~miyuki~
echo    雪国开放世界 GAL - 一键启动
echo ==============================================
echo.

rem ---------- 1. 已经在运行？直接开浏览器 ----------
curl -s -f -m 3 -o nul "%HEALTH%" 2>nul && (
  echo [OK] 游戏服务已经在运行，直接为你打开浏览器。
  echo.
  start "" "%URL%"
  echo   %URL%
  echo.
  pause
  exit /b 0
)

rem ---------- 2. 依赖检查 ----------
python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
  echo [..] 缺少运行依赖，正在安装 fastapi / uvicorn / pillow（仅需一次）
  echo.
  python -m pip install --disable-pip-version-check fastapi uvicorn pillow
  if errorlevel 1 (
    echo.
    echo [X] 依赖安装失败。请手动在命令行执行：
    echo      python -m pip install fastapi uvicorn pillow
    echo.
    pause
    exit /b 1
  )
  echo [OK] 依赖安装完成
  echo.
)

rem ---------- 3. 启动服务（独立最小化窗口） ----------
if not exist logs mkdir logs
echo [..] 正在启动游戏服务...
start "miyuki-server" /min cmd /c "python -m uvicorn server.app:app --host 127.0.0.1 --port %PORT% --log-level warning >> %LOG% 2>&1"

rem ---------- 4. 等待就绪（最多 40 秒） ----------
:wait
curl -s -f -m 2 -o nul "%HEALTH%" 2>nul && goto ready
set /a N+=1
if %N% GEQ 40 goto fail
timeout /t 1 /nobreak >nul
goto wait

:ready
echo [OK] 启动成功，正在打开浏览器...
echo.
start "" "%URL%"
echo   已为你打开浏览器：
echo     %URL%
echo.
echo   关闭游戏：双击同目录下的「停止游戏.bat」
echo   运行日志：%LOG%
echo.
pause
exit /b 0

:fail
echo [X] 启动超时。%LOG% 的最后 20 行：
echo ----------------------------------------------
if exist "%LOG%" powershell -NoProfile -Command "Get-Content -Tail 20 '%LOG%'"
echo ----------------------------------------------
echo.
pause
exit /b 1
