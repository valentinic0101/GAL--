#!/bin/bash
# 音频录制守护进程 —— 录 Mureka 等网页播放的 BGM（经 BlackHole 虚拟声卡）
#
# 用途：ZCode 无法直接录音（macOS 对非终端进程静默拒绝麦克风权限，录到全是静音），
#       必须由 Terminal 启动本脚本（终端首次会弹权限框，允许一次即永久生效）。
#
# 用法：
#   1. 终端执行：bash game/tools/rec_audio_daemon.sh   （保持窗口开着）
#   2. ZCode 侧控制：echo "/tmp/xxx.wav" > /tmp/rec_start  开始录
#                    touch /tmp/rec_stop                    停止录
#   3. 录制前需把系统输出切到 BlackHole：SwitchAudioSource -t output -s "BlackHole 2ch"
#      录完切回音箱：                    SwitchAudioSource -t output -s "MacBook Air扬声器"
#
# 依赖：brew install ffmpeg switchaudio-osx && brew install --cask blackhole-2ch
echo "录音守护进程已启动 (pid $$)，等待指令..."
while true; do
  if [ -f /tmp/rec_start ]; then
    out=$(cat /tmp/rec_start); rm -f /tmp/rec_start
    echo ">> $(date +%H:%M:%S) 开始录音: $out"
    ffmpeg -y -f avfoundation -i ":0" -ac 2 -ar 48000 -c:a pcm_s16le "$out" >/dev/null 2>&1 &
    echo $! > /tmp/rec_pid; echo "$out" > /tmp/rec_last
  fi
  if [ -f /tmp/rec_stop ]; then
    rm -f /tmp/rec_stop
    pid=$(cat /tmp/rec_pid 2>/dev/null)
    [ -n "$pid" ] && kill -INT "$pid" 2>/dev/null && echo ">> $(date +%H:%M:%S) 停止录音"
    sleep 1
  fi
  sleep 0.5
done
