#!/bin/bash
# ============================================================
#  深雪 ~miyuki~  停止游戏（macOS：在访达里双击本文件即可）
#  作用：结束游戏服务进程，释放 8300 端口
# ============================================================

cd "$(dirname "$0")" || exit 1
PORT=8300

echo "=============================================="
echo "   深雪 ~miyuki~  停止游戏服务"
echo "=============================================="
echo

if ! lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "（当前没有在运行的游戏服务，无需操作）"
  echo
  exit 0
fi

pkill -f "uvicorn server.app:app"

# 等待端口释放（最多 10 秒）
for _ in $(seq 1 20); do
  if ! lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "✓ 游戏服务已停止，端口 ${PORT} 已释放。"
    echo
    exit 0
  fi
  sleep 0.5
done

echo "… 进程未正常退出，强制结束。"
pkill -9 -f "uvicorn server.app:app"
sleep 1
echo "✓ 已强制停止。"
echo
