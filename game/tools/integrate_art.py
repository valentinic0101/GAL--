# -*- coding: utf-8 -*-
"""素材接入管线（可重复执行，幂等）：

  python3 tools/integrate_art.py

扫描 AI 生图源文件（资料/03_美术/AI生图源文件/，位置见 tools/paths.py）并接入游戏：
  - bg_*.png          → 裁 16:9 → assets/backgrounds/（bg_fields_spring/bg_courtyard_spring
                         会同时把 E_SPRING 场景背景切换过去）
  - cg*.png / cg_*.png → 裁 16:9 → assets/cg/，并按 MAPPING 嵌入对应场景节拍
  - 立绘名（miyuki_* / shuuji_* / toba / relative_*）→ 抠图 → assets/sprites/，
    miyuki_spring 同时接入 personas（spring 表情）与 E_SPRING 场景立绘
"""
import io
import json
import os
import sys
from collections import deque

from PIL import Image, ImageFilter

import paths

ROOT = paths.GAME
SRC = paths.ART_SRC

# 剧本数据的分片（正典台词与场景节点）；script.py 只做汇总，不含节点数据
SCRIPT_PARTS = ('trunk.py', 'branches.py')

SPRITE_NAMES = {'miyuki_normal', 'miyuki_smile', 'miyuki_sad', 'miyuki_surprise', 'miyuki_white',
                'miyuki_spring', 'miyuki_hime', 'shuuji_child', 'shuuji_teen', 'toba',
                'relative_man', 'relative_woman'}

# CG → (场景, 嵌入锚点：在该唯一文本拍之前插入)
CG_MAPPING = {
    'cg04.png':      ('P5',  '今年到这里……吧'),
    'cg05.png':      ('P6',  '拉～勾！'),
    'cg06.png':      ('P7',  '欢迎回家哦，小修'),
    'cg07.png':      ('P10', '雪人留着齐刘海的头型。和姐姐的样貌一摸一样。'),
    'cg_snow.png':   ('P0',  '那白色的身影，伫立在雪原中。使得我毛骨悚然。'),
    'cg_stay.png':   ('E_STAY', '炉火重新旺了起来。窗外的雪声被隔得很远。'),
    'cg_spring.png': ('E_SPRING', '樱花开了。那棵比我更老的老树'),
    'cg_far.png':    ('E_FAR',  '列车开动。她的身影越来越小'),
    'cg08.png':      ('E_FAR',  '列车开动。她的身影越来越小'),
}

BG_SCENE_SWAP = {   # 新背景到达时顺带切换场景默认 bg
    'bg_fields_spring.png':   [('E_SPRING', 'bg_fields_spring.png')],
    'bg_courtyard_spring.png': [],
    'bg_mountain_path.png':   [('P12M', 'bg_mountain_path.png')],
    'bg_tokyo.png':           [('E_TOKYO', 'bg_tokyo.png')],
}


def crop169(im, top_bias=0.0):
    w, h = im.size
    th = int(w * 9 / 16)
    if th > h:                      # 高度不足 16:9 → 裁两侧
        tw = int(h * 16 / 9)
        left = (w - tw) // 2
        return im.crop((left, 0, left + tw, h))
    if th < h:
        top = max(0, int((h - th) / 2 - h * top_bias))
        return im.crop((0, top, w, top + th))
    return im


def integrate_background(name):
    im = Image.open(os.path.join(SRC, name)).convert('RGB')
    # 竖版图（如标题）居中裁；横版略偏上保留天空
    bias = 0.05 if im.size[0] > im.size[1] else 0.0
    crop169(im, bias).save(os.path.join(ROOT, 'assets', 'backgrounds', name), optimize=True)
    print('  bg 接入:', name)


def integrate_cg(name):
    im = Image.open(os.path.join(SRC, name)).convert('RGB')
    crop169(im, 0.03).save(os.path.join(ROOT, 'assets', 'cg', name), optimize=True)
    print('  cg 接入:', name)


def cutout(name, tol=18):
    # 优先 rembg AI 抠图（软 alpha + 边缘去污染，见 cutout_sprites.py）；
    # 本函数返回 kept 像素占比，kept<0.05 视为非纯底场景画，跳过接入。
    import cutout_sprites
    kept, _ = cutout_sprites.cutout_best(name)
    if kept < 0.05:
        return None
    return kept


def script_part(scene):
    """返回定义该场景的剧本分片路径。

    剧本数据按「主干 / 分支与结局」切成 server/scenes/trunk.py 与 branches.py
    （对外仍是同一个 SCENES，见 server/scenes/script.py），所以文本改写要先定位分片。
    """
    marker = "SCENES['%s']" % scene
    for name in SCRIPT_PARTS:
        p = os.path.join(ROOT, 'server', 'scenes', name)
        if marker in io.open(p, encoding='utf-8').read():
            return p
    raise SystemExit('剧本分片里找不到场景 %s（检查 tools/integrate_art.py 的 SCRIPT_PARTS）' % scene)


def patch_script(scene, anchor, cg_name=None, bg_name=None):
    """在场景的 anchor 文本拍前插入 cg 节拍 / 替换场景 bg。幂等。"""
    import re
    p = script_part(scene)
    s = io.open(p, encoding='utf-8').read()
    if cg_name:
        beat = "        {'type': 'cg', 'img': '%s'},\n" % cg_name
        if cg_name not in s:
            needle = "        {'type': 'narration', 'text': '%s'}" % anchor
            if needle not in s:      # anchor 可能是 line 拍
                needle = "        {'type': 'line', 'who': 'miyuki', 'say': '%s'" % anchor
            assert needle in s, 'anchor not found: ' + anchor[:20]
            s = s.replace(needle, beat + needle, 1)
            print('  cg 嵌入 %s: %s' % (scene, cg_name))
    for bg in ([bg_name] if bg_name else []):
        start = s.index("SCENES['%s'] = {" % scene)
        nxt = s.find("SCENES[", start + 10)
        end = nxt if nxt != -1 else len(s)      # 目标场景是文件中最后一个时取到结尾
        block = s[start:end]
        nb = re.sub(r"'bg': '[^']+'", "'bg': '%s'" % bg, block, count=1)
        if nb != block:
            s = s[:start] + nb + s[end:]
            print('  bg 切换 %s -> %s' % (scene, bg))
    io.open(p, 'w', encoding='utf-8').write(s)


def regenerate_asset_manifest():
    """再生 web/gen/asset_manifest.js（前端缺图优雅降级的依据）。"""
    def names(sub):
        d = os.path.join(ROOT, 'assets', sub)
        return sorted(f for f in os.listdir(d) if f.endswith(('.png', '.svg', '.m4a'))) if os.path.isdir(d) else []
    manifest = {'bg': names('backgrounds'), 'cg': names('cg'),
                'sprites': names('sprites')}
    js = '// 自动生成：tools/integrate_art.py / audit_stage.py —— 已有素材清单\nwindow.ASSET_MANIFEST = ' + \
        json.dumps(manifest, ensure_ascii=False) + ';\n'
    io.open(os.path.join(ROOT, 'web', 'gen', 'asset_manifest.js'), 'w', encoding='utf-8').write(js)
    print('  资源清单更新: bg %d / cg %d / sprites %d' % (len(manifest['bg']), len(manifest['cg']), len(manifest['sprites'])))


def regenerate_feet_meta():
    """重算所有立绘的脚底透明边距 → web/gen/sprites_meta.js（前端地面贴合用）。"""
    import json
    from PIL import Image as PImage
    d = os.path.join(ROOT, 'assets', 'sprites')
    meta = {}
    for f in sorted(os.listdir(d)):
        if not f.endswith('.png'):
            continue
        im = PImage.open(os.path.join(d, f))
        bbox = im.getchannel('A').getbbox()
        meta[f] = round((im.size[1] - bbox[3]) / im.size[1], 4) if bbox else 1.0
    js = '// 自动生成：tools/integrate_art.py —— 每张立绘脚底透明边距（占图高比例）\nwindow.SPRITE_FEET = ' + \
        json.dumps(meta, ensure_ascii=False) + ';\n'
    io.open(os.path.join(ROOT, 'web', 'gen', 'sprites_meta.js'), 'w', encoding='utf-8').write(js)
    print('  脚底元数据更新:', len(meta), '张')


def wire_personas_png():
    p = os.path.join(ROOT, 'server', 'agents', 'personas.py')
    s = io.open(p, encoding='utf-8').read()
    changed = False
    for n in SPRITE_NAMES - {'miyuki_white'}:
        if os.path.exists(os.path.join(ROOT, 'assets', 'sprites', n + '.png')) and ("'%s.svg'" % n) in s:
            s = s.replace("'%s.svg'" % n, "'%s.png'" % n)
            changed = True
    if changed:
        io.open(p, 'w', encoding='utf-8').write(s)
        print('  personas 已指向 png')


def main():
    files = set(os.listdir(paths.require_art_src(SRC)))
    acted = False
    # 1) 背景
    for f in sorted(files):
        if f.startswith('bg_') and f.endswith('.png'):
            dst = os.path.join(ROOT, 'assets', 'backgrounds', f)
            if not os.path.exists(dst) or os.path.getmtime(os.path.join(SRC, f)) > os.path.getmtime(dst):
                integrate_background(f)
                acted = True
                for scene, bg in BG_SCENE_SWAP.get(f, []):
                    patch_script(scene, None, bg_name=bg)
    # 2) CG
    for f in sorted(files):
        low = f.lower()
        if low.startswith('cg') and f.endswith('.png') and low in CG_MAPPING:
            dst = os.path.join(ROOT, 'assets', 'cg', f)
            if not os.path.exists(dst):
                integrate_cg(f)
                scene, anchor = CG_MAPPING[low]
                patch_script(scene, anchor, cg_name=f)
                acted = True
    # 3) 立绘
    for name in sorted(SPRITE_NAMES):
        src = os.path.join(SRC, name + '.png')
        if not os.path.exists(src):
            continue
        dst = os.path.join(ROOT, 'assets', 'sprites', name + '.png')
        if os.path.exists(dst) and os.path.getmtime(src) <= os.path.getmtime(dst):
            continue
        kept = cutout(name)
        if kept is None:
            print('  跳过(非纯底，需人工判断):', name)
            continue
        print('  立绘接入: %s（保留 %.1f%%）' % (name, kept * 100))
        acted = True
        if name == 'miyuki_spring':
            # personas 增加 spring 表情 + E_SPRING 场景使用春装
            p = os.path.join(ROOT, 'server', 'agents', 'personas.py')
            s = io.open(p, encoding='utf-8').read()
            if "'spring'" not in s:
                s = s.replace("'miyuki_surprise.png'", "'miyuki_surprise.png', 'spring': 'miyuki_spring.png'", 1)
                io.open(p, 'w', encoding='utf-8').write(s)
                print('  personas 增加 spring 表情')
            p2 = script_part('E_SPRING')
            s2 = io.open(p2, encoding='utf-8').read()
            old = "        {'type': 'line', 'who': 'miyuki', 'say': '欢迎回来哦，小修', 'expr': 'smile', 'action': '（她站在樱花树下。没有围着那条白围巾，发梢被春风轻轻掀起）'},"
            new = "        {'type': 'line', 'who': 'miyuki', 'say': '欢迎回来哦，小修', 'expr': 'spring', 'action': '（她站在樱花树下。春装轻盈，发梢被春风轻轻掀起）'},"
            if old in s2:
                s2 = s2.replace(old, new)
                io.open(p2, 'w', encoding='utf-8').write(s2)
                print('  E_SPRING 场景改用 spring 表情')
    # 4) 兜底：把已存在的 png 立绘映射进 personas（首轮回放）
    wire_personas_png()
    regenerate_feet_meta()
    regenerate_asset_manifest()
    if not acted:
        print('无新素材。')
    else:
        # 语法自检
        import py_compile
        for f in ('server/scenes/script.py', 'server/scenes/trunk.py',
                  'server/scenes/branches.py', 'server/agents/personas.py'):
            py_compile.compile(os.path.join(ROOT, f), doraise=True)
        print('接入完成，语法自检通过。')


if __name__ == '__main__':
    main()
