# -*- coding: utf-8 -*-
"""素材脚本的路径单一来源。

「AI 生图源文件」不随游戏本体分发——游戏运行时只认 assets/ 里已经接入的成品，
源文件属于项目资料。它放在项目根目录的 资料/03_美术/AI生图源文件/。
这条指向游戏目录树之外的依赖此前硬编码在两个脚本里（SRC = ../Gemini 绘图），
搬迁一次就要改多处；现在收敛到这里，也可以整体覆盖：

    GAL_ART_SRC=/path/to/生图源 python3 tools/integrate_art.py
"""
import os

GAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # game/
PROJECT = os.path.dirname(GAME)                                        # 项目根

# AI 生图源文件（不在 game/ 内）
ART_SRC = os.environ.get('GAL_ART_SRC') or os.path.join(
    PROJECT, '资料', '03_美术', 'AI生图源文件')

# 游戏内素材目录
ASSETS = os.path.join(GAME, 'assets')
BACKGROUNDS = os.path.join(ASSETS, 'backgrounds')
SPRITES = os.path.join(ASSETS, 'sprites')
CG = os.path.join(ASSETS, 'cg')
BGM = os.path.join(ASSETS, 'bgm')
WEB = os.path.join(GAME, 'web')


def require_art_src(src=None):
    """取生图源目录；不存在时给出可直接照做的提示，而不是让脚本崩在 FileNotFoundError。"""
    src = src or ART_SRC
    if not os.path.isdir(src):
        raise SystemExit(
            '找不到 AI 生图源目录：\n  %s\n'
            '请把源文件放回该位置，或设置 GAL_ART_SRC 指向它。' % src)
    return src
