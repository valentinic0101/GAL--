#!/bin/bash
# ============================================================
#  深雪 ~miyuki~  一键启动（macOS：在访达里双击本文件即可）
#  作用：检查依赖 → 启动游戏服务 → 自动打开浏览器
#  重复双击不会起第二个实例；关掉本终端窗口游戏仍继续运行。
#  停止游戏请双击同目录下的「停止游戏.command」
# ============================================================

cd "$(dirname "$0")" || exit 1

PORT=8300
URL="http://127.0.0.1:${PORT}/"
HEALTH="${URL}api/health"
LOG="logs/server.log"

echo "=============================================="
echo "   深雪 ~miyuki~"
echo "   雪国开放世界 GAL · 一键启动"
echo "=============================================="
echo

# ---------- 1. 已经在运行？直接开浏览器 ----------
if curl -s -f -m 3 -o /dev/null "$HEALTH"; then
  echo "✓ 游戏服务已经在运行，直接为你打开浏览器。"
  echo
  open "$URL"
  echo "  ${URL}"
  echo
  exit 0
fi

# ---------- 2. 依赖检查 ----------
if ! python3 -c "import fastapi, uvicorn" >/dev/null 2>&1; then
  echo "… 缺少运行依赖，正在安装 fastapi / uvicorn / pillow（仅需一次）"
  echo
  if ! python3 -m pip install --quiet --disable-pip-version-check fastapi uvicorn pillow; then
    echo
    echo "✗ 依赖安装失败。请手动在终端执行："
    echo "     python3 -m pip install fastapi uvicorn pillow"
    echo
    read -n 1 -s -r -p "按任意键关闭本窗口…"
    exit 1
  fi
  echo "✓ 依赖安装完成"
  echo
fi

# ---------- 3. 检查端口是否被别的程序占用 ----------
if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "✗ 端口 ${PORT} 已被其它程序占用，无法启动。"
  echo
  echo "  占用情况："
  lsof -nP -iTCP:"$PORT" -sTCP:LISTEN | sed 's/^/    /'
  echo
  echo "  若是残留的本游戏进程，请先双击「停止游戏.command」再试。"
  echo
  read -n 1 -s -r -p "按任意键关闭本窗口…"
  exit 1
fi

# ---------- 4. 启动服务（后台，脱离终端） ----------
mkdir -p logs
echo "… 正在启动游戏服务…"

nohup python3 -m uvicorn server.app:app \
      --host 127.0.0.1 --port "$PORT" --log-level warning \
      >>"$LOG" 2>&1 &
SERVER_PID=$!

# ---------- 5. 等待就绪（最多 30 秒） ----------
for _ in $(seq 1 60); do
  if ! kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    break   # 进程已退出，失败
  fi
  if curl -s -f -m 2 -o /dev/null "$HEALTH"; then
    echo "✓ 启动成功（进程号 ${SERVER_PID}）"
    echo
    open "$URL"
    echo "  已为你打开浏览器："
    echo "    ${URL}"
    echo
    echo "  关闭游戏：双击同目录下的「停止游戏.command」"
    echo "  运行日志：${LOG}"
    echo
    echo "  （本窗口可以关掉，游戏不受影响）"
    exit 0
  fi
  sleep 0.5
done

# ---------- 6. 启动失败 ----------
echo "✗ 启动失败。${LOG} 的最后 25 行："
echo "----------------------------------------------"
tail -25 "$LOG" 2>/dev/null | sed 's/^/  /'
echo "----------------------------------------------"
echo
read -n 1 -s -r -p "按任意键关闭本窗口…"
exit 1
