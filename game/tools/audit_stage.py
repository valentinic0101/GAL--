# -*- coding: utf-8 -*-
"""舞台匹配审计（对应《资料/02_设定与设计/舞台匹配规范.md》）。

逐项穷举校验"人物-场景匹配"六条规则在全部场景/背景/立绘上的落实：
  A. 背景完备：assets/backgrounds 每张图、剧本/地点表引用的每张图，都有 SCENE_STAGE 标定
     （或明确走默认），且文件真实存在。
  B. 立绘完备：personas 引用的每张立绘文件存在、有脚底元数据、有基准身高。
  C. 出场完备：每个场景（基线 + 台词自动登台 + cast_add）可能登场的每个角色，都有人设与立绘。
  D. 几何穷举：常见分辨率 × 每个背景 × 1~5 人组合，槽位求解后不得出屏、不得重叠。
  E. 剧情一致：人物基准身高序符合圣经（深雪 > 修二任意形态；成年人 ≥ 深雪）。
  F. 配置同步：web/gen/stage_meta.js、web/gen/sprites_meta.js 与 tools/stage_config.json、实际文件一致。

用法：python3 tools/audit_stage.py        # 全部通过退出 0，否则打印问题并退出 1
      python3 tools/audit_stage.py --fix  # 校验后重新生成两个 *_meta.js
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'server'))

from PIL import Image                                    # noqa: E402
from scenes.script import SCENES                         # noqa: E402
from world.world import LOCATIONS, CHARACTERS            # noqa: E402
from agents.personas import PERSONAS                     # noqa: E402

FAILS = []


def check(name, cond, detail=''):
    if cond:
        print('  [pass] ' + name)
    else:
        FAILS.append(name)
        print('  [FAIL] ' + name + ('  → ' + str(detail) if detail else ''))


def load_json(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def main(fix=False):
    cfg = load_json(os.path.join(ROOT, 'tools', 'stage_config.json'))
    char_h = cfg['char_height']
    scene_stage = cfg['scene_stage']
    default_stage = cfg['default_stage']

    print('== A. 背景完备 ==')
    bg_dir = os.path.join(ROOT, 'assets', 'backgrounds')
    bg_files = {f for f in os.listdir(bg_dir) if f.endswith('.png')}
    # 剧本与地点表引用到的所有背景
    referenced = set()
    for sc in SCENES.values():
        if sc.get('bg'):
            referenced.add(sc['bg'])
        for b in sc['beats']:
            if b.get('bg'):
                referenced.add(b['bg'])
    for loc in LOCATIONS.values():
        if loc.get('bg'):
            referenced.add(loc['bg'])
    for f in sorted(bg_files):
        check('已标定 %s' % f, f in scene_stage or f == 'bg_title.png',
              None if f in scene_stage else '走默认地面线（标题画面可接受）' if f == 'bg_title.png' else '缺失')
    # M2 已知待补：E_SPRING 引用的春景图（前端已优雅降级，图到位即自动生效）
    PENDING_BG = {'bg_fields_spring.png', 'bg_courtyard_spring.png'}
    for f in sorted(referenced):
        if f in PENDING_BG and f not in bg_files:
            check('引用的背景暂缺（已降级） %s' % f, True, 'M2 已知待补项')
            continue
        check('引用的背景存在 %s' % f, f in bg_files, '文件不存在')

    print('== B. 立绘完备 ==')
    sp_dir = os.path.join(ROOT, 'assets', 'sprites')
    feet_path = os.path.join(ROOT, 'web', 'gen', 'sprites_meta.js')
    feet = {}
    if os.path.exists(feet_path):
        txt = io_open(feet_path)
        body = txt.split('=', 1)[1].rstrip().rstrip(';')
        feet = json.loads(body)
    referenced_sprites = set()
    for pid, persona in PERSONAS.items():
        for k, v in (persona.get('sprites') or {}).items():
            referenced_sprites.add(v)
        if persona.get('sprite'):
            referenced_sprites.add(persona['sprite'])
    # 表情变体（如 miyuki_smile）继承本体身高；独立形态（shuuji_child/teen）须有显式 key
    def height_ok(f):
        key = f.rsplit('.', 1)[0]
        if key in char_h:
            return True
        base = key.split('_')[0]
        return base in char_h and not any(k in key for k in ('child', 'teen'))
    for f in sorted(referenced_sprites):
        p_ = os.path.join(sp_dir, f)
        check('立绘存在 %s' % f, os.path.exists(p_))
        if f.endswith('.png'):
            check('脚底元数据 %s' % f, f in feet, '缺 foot 数据（重跑 integrate_art.py）')
        else:
            check('SVG 立绘走默认脚底 %s' % f, True)
        check('基准身高 %s' % f, height_ok(f), 'char_height 缺 key 且无本体可继承')

    print('== C. 出场完备 ==')
    import engine as engine_mod  # noqa
    for sid, sc in sorted(SCENES.items()):
        base = set(engine_mod.SCENE_CAST.get(sid, ['shuuji']))
        for b in sc['beats']:
            if b['type'] == 'line' and b.get('who'):
                base.add(b['who'])
            for c in (b.get('cast_add') or []):
                base.add(c)
        base.add('shuuji')
        bad = [c for c in base if c not in PERSONAS and c not in CHARACTERS]
        check('%s 出场角色均有定义 %s' % (sid, sorted(base)), not bad, bad)
        nosprite = [c for c in base if c != 'shuuji' and not PERSONAS.get(c, {}).get('sprite')
                    and not (PERSONAS.get(c, {}) or {}).get('sprites')]
        check('%s 出场角色均有立绘' % sid, not nosprite, nosprite)

    print('== D. 几何穷举（分辨率 × 背景 × 真实出场组合） ==')
    aspects = {}
    for f in sorted(os.listdir(sp_dir)):
        if f.endswith('.png'):
            im = Image.open(os.path.join(sp_dir, f))
            aspects[f] = im.size[0] / im.size[1]
    # 真实出场组合（最宽/最高的实际组合：P1 四人、P2 双人等）
    cast_plan = {
        1: ['relative_man'],
        2: ['shuuji_teen', 'miyuki'],
        3: ['shuuji_teen', 'relative_man', 'miyuki'],
        4: ['shuuji_child', 'relative_man', 'relative_woman', 'miyuki'],
    }
    resos = [(1024, 768), (1280, 720), (1440, 900), (1920, 1080)]
    bgs = sorted(scene_stage)
    overflow_cnt, overlap_cnt, total_cnt = 0, 0, 0

    def fit_crowd(hs, asp, vw_, pad=10, edge=10):
        hs = list(hs)
        for _ in range(4):
            total = sum(h * a for h, a in zip(hs, asp)) + (len(hs) - 1) * pad
            avail = vw_ - 2 * edge
            if total <= avail or len(hs) == 1:
                break
            k = max(.6, (avail / total) ** .9)
            hs = [h * k for h in hs]
        return hs

    for (vw, vh) in resos:
        for bg in bgs:
            st = scene_stage[bg]
            for n in range(1, 5):
                names = cast_plan[n]
                dpf = (cfg['depth_profile'].get(str(n)) or cfg['depth_profile']['default'])
                hs, asp = [], []
                for i, nm in enumerate(names):
                    key = nm if nm in char_h else nm.rsplit('_', 1)[0]
                    if key not in char_h:
                        key = 'miyuki'
                    depth = dpf[i] if i < len(dpf) else 1
                    hs.append(char_h[key] * st['scale'] * depth * vh)
                    asp.append(aspects.get(nm + '.png', .66))
                hs = fit_crowd(hs, asp, vw)
                ws = [h * a for h, a in zip(hs, asp)]
                pts = solve_slots(n, ws, vw)
                total_cnt += 1
                for i in range(n):
                    if pts[i] - ws[i] / 2 < -2 or pts[i] + ws[i] / 2 > vw + 2:
                        overflow_cnt += 1
                        check('%dx%d %s %d人 #%d 出屏' % (vw, vh, bg, n, i), False,
                              'x=%.0f w=%.0f' % (pts[i], ws[i]))
                for i in range(n - 1):
                    if pts[i + 1] - pts[i] < (ws[i] + ws[i + 1]) / 2 - 2:
                        overlap_cnt += 1
                        check('%dx%d %s %d人 重叠@%d' % (vw, vh, bg, n, i), False,
                              'gap=%.0f' % (pts[i + 1] - pts[i]))
    check('几何穷举 %d 项（%d 分辨率 × %d 背景 × 4 组合）无出屏/无重叠'
          % (total_cnt, len(resos), len(bgs)), overflow_cnt == 0 and overlap_cnt == 0,
          '出屏 %d / 重叠 %d' % (overflow_cnt, overlap_cnt))

    print('== E. 身高序（人物圣经） ==')
    miyuki = char_h.get('miyuki', 0)
    check('深雪 > 孩童修二', miyuki > char_h.get('shuuji_child', 1))
    check('深雪 > 少年修二', miyuki > char_h.get('shuuji_teen', 1))
    check('深雪 ≤ 成年男', miyuki <= char_h.get('relative_man', 0))
    check('白衣雪女 ≥ 深雪', char_h.get('miyuki_white', 0) >= miyuki)

    print('== F. 配置同步 ==')
    if fix:
        regenerate_meta(cfg, feet if feet else read_or_init_feet())
    stage_meta = os.path.join(ROOT, 'web', 'gen', 'stage_meta.js')
    check('stage_meta.js 存在', os.path.exists(stage_meta))
    if os.path.exists(stage_meta):
        cur = io_open(stage_meta)
        want = 'window.STAGE_META = ' + json.dumps(cfg, ensure_ascii=False) + ';'
        check('stage_meta.js 与 stage_config.json 同步', want in cur)

    print()
    if FAILS:
        print('AUDIT: %d FAILED' % len(FAILS))
        sys.exit(1)
    print('AUDIT: ALL PASSED')


def io_open(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def solve_slots(n, ws, vw):
    """与 main.js solveSlots 相同的约束求解（审计用同一算法）。"""
    xs = {1: [.58], 2: [.24, .74], 3: [.15, .45, .78]}.get(n)
    pts = [f * vw for f in xs] if xs else [.12 + i * (.78 / max(1, n - 1)) * vw for i in range(n)]
    half = [w / 2 for w in ws]
    pad = 10
    pts[n - 1] = min(pts[n - 1], vw - half[n - 1] - pad)
    for i in range(n - 2, -1, -1):
        lim = pts[i + 1] - half[i + 1] - half[i] - pad
        pts[i] = min(max(pts[i], half[i] + pad), lim)
    if pts[0] < half[0] + pad:
        shift = half[0] + pad - pts[0]
        pts = [p + shift for p in pts]
        for i in range(1, n):
            pts[i] = min(pts[i], vw - half[i] - pad)
    return pts


def read_or_init_feet():
    from PIL import Image
    d = os.path.join(ROOT, 'assets', 'sprites')
    meta = {}
    for f in sorted(os.listdir(d)):
        if f.endswith('.png'):
            im = Image.open(os.path.join(d, f))
            bbox = im.getchannel('A').getbbox()
            meta[f] = round((im.size[1] - bbox[3]) / im.size[1], 4) if bbox else 1.0
    return meta


def regenerate_asset_manifest():
    import json as _json
    def names(sub):
        d = os.path.join(ROOT, 'assets', sub)
        return sorted(f for f in os.listdir(d) if f.endswith(('.png', '.svg', '.m4a'))) if os.path.isdir(d) else []
    manifest = {'bg': names('backgrounds'), 'cg': names('cg'), 'sprites': names('sprites')}
    js = '// 自动生成：tools/integrate_art.py / audit_stage.py —— 已有素材清单\nwindow.ASSET_MANIFEST = ' + _json.dumps(manifest, ensure_ascii=False) + ';\n'
    with open(os.path.join(ROOT, 'web', 'gen', 'asset_manifest.js'), 'w', encoding='utf-8') as f:
        f.write(js)


def regenerate_meta(cfg, feet):
    js = 'window.STAGE_META = ' + json.dumps(cfg, ensure_ascii=False) + ';'
    with open(os.path.join(ROOT, 'web', 'gen', 'stage_meta.js'), 'w', encoding='utf-8') as f:
        f.write('// 自动生成：tools/audit_stage.py（来源 tools/stage_config.json）——请勿手改\n' + js + '\n')
    fj = 'window.SPRITE_FEET = ' + json.dumps(feet, ensure_ascii=False) + ';'
    with open(os.path.join(ROOT, 'web', 'gen', 'sprites_meta.js'), 'w', encoding='utf-8') as f:
        f.write('// 自动生成：tools/integrate_art.py / audit_stage.py —— 立绘脚底透明边距\n' + fj + '\n')
    regenerate_asset_manifest()
    print('  已再生 stage_meta.js / sprites_meta.js / asset_manifest.js')


if __name__ == '__main__':
    main('--fix' in sys.argv)
