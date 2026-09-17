#!/bin/bash
# 麦克风录音守护进程 —— 扬声器播放 + 麦克风采集
#
# 用途：平台禁止下载时，用真实硬件设备采集（绕开 BlackHole 虚拟声卡的时钟漂移丢样本问题）。
#       必须经 Terminal 启动（macOS 对非终端进程静默拒绝麦克风权限，会录到全静音）。
#
# 用法：
#   bash game/tools/rec_mic_daemon.sh [设备索引]
#     设备索引：1 = 内置麦克风（默认）；0 = BlackHole 2ch；其他值见 ffmpeg 设备列表
#   然后由 ZCode 侧控制：echo "/tmp/xxx.wav" > /tmp/rec_start  开始 / touch /tmp/rec_stop  停止
#
# 录音前准备：
#   - 系统输出保持「MacBook Air扬声器」（让喇叭发声、麦克风采集）
#   - 环境安静、不要有人说话；播放期间不要运行重负载程序
#   - 音量开到 70~90%（太大喇叭会失真，太小信噪比差）
#
# 质量预期：受限于喇叭频响（约 150Hz 以下放不出）+ 房间反射 + 麦克风底噪，
#           成品必然不如原文件；建议优先尝试电气回路（音频线接线路输入）替代声学回路。
#
# 验收：录完必须用「突变检测」体检（见《BGM需求文档.md》4.3 节），要求 突变 >0.2×峰值 为 0 处。
DEV="${1:-1}"
echo "麦克风录音守护进程已启动 (pid $$)，设备索引 $DEV，等待指令..."
while true; do
  if [ -f /tmp/rec_start ]; then
    out=$(cat /tmp/rec_start); rm -f /tmp/rec_start
    echo ">> $(date +%H:%M:%S) 开始录音: $out"
    ffmpeg -y -f avfoundation -i ":$DEV" -ar 48000 -c:a pcm_s16le "$out" >/dev/null 2>&1 &
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
