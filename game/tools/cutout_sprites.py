# -*- coding: utf-8 -*-
"""立绘抠图：把 AI 生图源文件（资料/03_美术/AI生图源文件/）的浅灰实底立绘去底
→ game/assets/sprites/ 透明 PNG。

主算法：rembg(isnet-anime) 生成软 alpha → 轻微羽化 → 轮廓内色外扩（bleed/defringe，
把半透明边缘像素被背景污染的 RGB 替换成附近不透明像素的本色），消除白边与锯齿，
浅色衣物（披肩/围裙）不再被误抠。
兜底：无 rembg 时退回旧的"边框取色 + 洪泛填充"算法（tol=18，边缘质量较差）。

用法：
  # 项目内已不再保留 .venv（占 495MB，2026-09-17 移出以减少仓库体积）。
  # 依赖清单见 tools/requirements.txt；重建后把下面路径换回 .venv/bin/python 即可。
  "$ARCH/tools_venv_495M/bin/python" tools/cutout_sprites.py            # 全部立绘
  "$ARCH/tools_venv_495M/bin/python" tools/cutout_sprites.py miyuki_smile toba

  其中 $ARCH 为移出归档目录（见归档目录内的 README.md）。
  若用系统 python3 直接运行，会因缺少 rembg 而自动退回旧的洪泛算法（边缘质量较差）。

源目录位置由 tools/paths.py 统一给出（可用 GAL_ART_SRC 环境变量覆盖）。
"""
import os
import sys
from collections import deque

from PIL import Image, ImageFilter

import paths

ROOT = paths.GAME
SRC = paths.ART_SRC
DST = paths.SPRITES

SPRITES = ['miyuki_normal', 'miyuki_smile', 'miyuki_sad', 'miyuki_surprise', 'miyuki_white',
           'miyuki_spring', 'miyuki_hime', 'shuuji_child', 'shuuji_teen', 'toba',
           'relative_man', 'relative_woman']

BLEED_PX = 4        # 边缘色外扩距离（px）
SEED_ALPHA = 250    # alpha 达到该值视为可信的"本色"种子


def cutout_rembg(name, session):
    """rembg 软 alpha + bleed 去污染。返回前景像素占比。"""
    import numpy as np
    from rembg import remove
    im = Image.open(os.path.join(SRC, name + '.png')).convert('RGB')
    out = remove(im, session=session)
    a = np.array(out)
    al = np.array(Image.frombytes('L', im.size, a[..., 3].tobytes())
                  .filter(ImageFilter.GaussianBlur(0.6)))

    # bleed：从 alpha 可信的像素出发，把本色向外扩几像素，覆盖被背景色污染的边缘 RGB
    rgb = a[..., :3].copy()
    h, w = al.shape
    seed = al >= SEED_ALPHA
    dist = np.full((h, w), -1, np.int16)
    dist[seed] = 0
    q = deque(zip(*np.where(seed)))
    while q:
        y, x = q.popleft()
        if dist[y, x] >= BLEED_PX:
            continue
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and dist[ny, nx] < 0:
                dist[ny, nx] = dist[y, x] + 1
                rgb[ny, nx] = rgb[y, x]
                q.append((ny, nx))

    res = Image.fromarray(np.dstack([rgb, al]))
    res.save(os.path.join(DST, name + '.png'), optimize=True)
    return float((al > 128).mean())


def cutout_floodfill(name, tol=18):
    """旧兜底算法：边框取色 → 洪泛填充 → 二值 mask 收缩 + 羽化。"""
    im = Image.open(os.path.join(SRC, name + '.png')).convert('RGB')
    w, h = im.size
    px = im.load()

    border = []
    for x in range(0, w, max(1, w // 100)):
        border += [px[x, 0], px[x, h - 1]]
    for y in range(0, h, max(1, h // 100)):
        border += [px[0, y], px[w - 1, y]]
    border.sort()
    bg = border[len(border) // 2]
    tol2 = tol * tol * 3

    bg_mask = bytearray(w * h)
    q = deque()
    for x in range(w):
        q.append((x, 0)); q.append((x, h - 1))
    for y in range(h):
        q.append((0, y)); q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        i = y * w + x
        if bg_mask[i]:
            continue
        p = px[x, y]
        if (p[0] - bg[0]) ** 2 + (p[1] - bg[1]) ** 2 + (p[2] - bg[2]) ** 2 > tol2:
            continue
        bg_mask[i] = 1
        if x > 0: q.append((x - 1, y))
        if x < w - 1: q.append((x + 1, y))
        if y > 0: q.append((x, y - 1))
        if y < h - 1: q.append((x, y + 1))

    alpha = Image.frombytes('L', (w, h), bytes(255 - b * 255 for b in bg_mask))
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
    out = im.convert('RGBA')
    out.putalpha(alpha)
    out.save(os.path.join(DST, name + '.png'), optimize=True)
    return sum(1 for b in bg_mask if not b) / (w * h)


def cutout_best(name):
    """优先 rembg，不可用时退回洪泛填充。"""
    try:
        import numpy as np  # noqa: F401  延迟导入，缺 numpy 时走兜底
        import rembg  # noqa: F401
    except ImportError:
        print('  [警告] 未安装 rembg，%s 使用旧洪泛算法（边缘质量较差）' % name)
        return cutout_floodfill(name), False
    global _SESSION
    try:
        if '_SESSION' not in globals():
            _SESSION = new_session('isnet-anime')   # 首次运行会下载模型(~176MB)
        return cutout_rembg(name, _SESSION), True
    except Exception as e:
        print('  [警告] rembg 失败(%s)，%s 使用旧洪泛算法' % (e, name))
        return cutout_floodfill(name), False


_SESSION = None


def main():
    args = sys.argv[1:]
    names = [a for a in args if not a.startswith('-')] or SPRITES
    paths.require_art_src(SRC)
    os.makedirs(DST, exist_ok=True)
    for name in names:
        src_path = os.path.join(SRC, name + '.png')
        if not os.path.exists(src_path):
            print('skip (未生成):', name)
            continue
        kept, used_ai = cutout_best(name)
        tag = 'AI' if used_ai else '洪泛'
        print('cutout[%s] %-18s 前景 %.1f%%' % (tag, name, kept * 100))


if __name__ == '__main__':
    main()
