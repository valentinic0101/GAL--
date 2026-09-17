# -*- coding: utf-8 -*-
"""监督会话专用测试驱动器：按《全分叉树_评审确认版》驱动剧情 + 采集场景帧。

用法（子命令式，便于配合浏览器截图分步执行）：
  python3 tester_drive.py new                     # 新游戏（LLM 保持开启，真实玩法）
  python3 tester_drive.py walk_p11                # 从头玩到 P10 结束幕间，泵羁绊，存档 t1
  python3 tester_drive.py load t1                 # 读档
  python3 tester_drive.py pump obsession 36       # 幕间对话泵轴到目标值
  python3 tester_drive.py enter                   # 进入 director 提供的场景
  python3 tester_drive.py pick 0                  # 在选项节拍点第 0 项
  python3 tester_drive.py say 文本                 # 自由输入
  python3 tester_drive.py run_choice SEQ          # 沿既定脚本推进场景（遇 choice 按 SCENE_PICKS）
  python3 tester_drive.py until interlude|ending|choice|scene_end
  python3 tester_drive.py state                   # 打印当前帧摘要
  python3 tester_drive.py dump 名字                # 当前帧存 /tmp/gal_frames/名字.json
"""
import json
import os
import sys
import urllib.request

BASE = 'http://127.0.0.1:8300'
DUMP = '/tmp/gal_frames'
os.makedirs(DUMP, exist_ok=True)

urllib.request.install_opener(
    urllib.request.build_opener(urllib.request.ProxyHandler({})))


def call(path, body=None, get=None):
    if get is None:
        get = path.rstrip('/') in ('/api/state', '/api/locations', '/api/backlog',
                                   '/api/world', '/api/saves', '/api/health')
    if get:
        req = urllib.request.Request(BASE + path)
    else:
        req = urllib.request.Request(BASE + path,
                                     data=json.dumps(body or {}).encode(),
                                     headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())


def last(frames):
    return frames[-1] if frames else {}


def brief(f):
    meta = f.get('meta') or {}
    who = f.get('who') or ''
    txt = (f.get('text') or (f.get('note') if f.get('kind') == 'interlude' else '')) or ''
    ch = ','.join((c.get('label') or '') for c in (f.get('choices') or []))
    return '[%s|%s|%s] %s%s' % (f.get('kind'), meta.get('phase'), meta.get('day'), txt[:52],
                                (' 「' + ch + '」') if ch else '')


def step_once(picks=None):
    """推进一步：按帧类型自动处理；picks = {scene: [按序点的选项下标]}。返回 (frame, action_desc)。"""
    f = call('/api/state')
    kind = f.get('kind')
    meta = f.get('meta') or {}
    if kind == 'choice':
        opts = f.get('choices') or []
        seq = picks or {}
        lst = seq.get(meta.get('phase'))
        idx = 0
        if lst:
            i = meta.get('choice_seq') if meta.get('choice_seq') is not None else None
            # 场景内第几个 choice：用已记录的计数器
            idx = lst[min(COUNTER['c'], len(lst) - 1)]
        COUNTER['c'] += 1
        r = call('/api/input', {'choice_index': idx})
        return last(r['frames']), 'choice %d' % idx
    if kind == 'free':
        r = call('/api/input', {'text': FREE_NEXT[0] if FREE_NEXT else '……'})
        if FREE_NEXT:
            FREE_NEXT.pop(0)
        return last(r['frames']), 'free'
    if kind == 'interlude':
        offer = (f.get('meta') or {}).get('scene_offer')
        if offer:
            r = call('/api/act', {'action': 'enter_scene'})
            return last(r['frames']), 'enter ' + str(offer)
        return None, 'interlude-idle'   # 由调用方决定泵轴/等待
    r = call('/api/advance')
    return last(r['frames']), 'advance'


COUNTER = {'c': 0}
FREE_NEXT = []

# 主干正典选项表（羁绊最大化 + P5 提父母铺入山线执念）
SCENE_PICKS = {
    'P1': [0],        # 喜欢这雪 bond+2
    'P2': [0],        # 任由她抱着 bond+3
    'P3': [0, 1],     # 你是谁 / 愣在原地 bond+1
    'P4': [1],        # 默默让她牵 bond+2
    'P5': [1],        # 岔开话题（保住低执念，春天线可达）
    'P6': [1, 0, 0],  # ……嗯 / 你要怎么办 / 问名字 → bond+2×3
    'P7': [1],        # 接纳安心 bond+3
    'P9': [0],        # 道歉 bond+2
    'P10': [0],       # 姐姐也是 bond+2
    'P12B': [0],      # 默认：留在这里（路线可覆盖）
}
FREE_TEXTS = {
    'P1': ['你放……放开我……你是谁啊'],
    'P8': ['姐姐，来陪我打扑克――'],
    'P12B': ['和你在一起，很幸福。'],
    'E_STAY': ['姐姐，晚安。'],
}
BOND_WORDS = ['姐姐，我最喜欢你了', '我想和你一起堆雪人', '约定好了哦，拉勾',
              '姐姐做的饭最好吃了', '晚安，姐姐', '我想留在你身边']
OBSESSION_WORDS = ['父亲和母亲还在山里', '我想去群山找他们', '雪女的传说是什么',
                   '山里好像有呼唤我的声音', '那片白色的深处是异界吗']
WORLDLY_WORDS = ['东京的学校还有课', '升学考试快到了', '宿舍的同学在等我',
                 '功课还没做完呢', '开学就要迟到了']


def axes():
    f = call('/api/state')
    meta = f.get('meta') or {}
    return meta.get('axes') or {}, meta.get('affection')


def pump(axis_word, target, max_talks=40):
    """幕间对话泵轴：对在场者连续说话。"""
    pools = {'bond': BOND_WORDS, 'obsession': OBSESSION_WORDS, 'worldly': WORLDLY_WORDS}
    words = pools[axis_word]
    i = 0
    for k in range(max_talks):
        ax, aff = axes()
        if ax.get(axis_word, 0) >= target:
            return True, k
        r = call('/api/act', {'action': 'talk', 'text': words[i % len(words)]})
        i += 1
        f = last(r.get('frames') or [])
        if f.get('kind') == 'error' or '没有可以说话的人' in (f.get('note') or ''):
            return False, k
    ax, _ = axes()
    return ax.get(axis_word, 0) >= target, max_talks


def interlude_hold(pump_aff_under=45):
    """幕间待命：无 offer 时——优先泵好感（P5 门槛）→ 走向老屋 → 等待。"""
    ax, aff = axes()
    if aff is not None and aff < pump_aff_under:
        call('/api/act', {'action': 'talk', 'text': '姐姐，谢谢你一直陪着我'})
        return 'talk-aff'
    loc = call('/api/locations').get('current')
    ADJ = {'station': ['town_street', 'fields'], 'fields': ['station', 'oldhouse_front'],
           'town_street': ['station', 'toba_home', 'shrine_road'], 'toba_home': ['town_street'],
           'shrine_road': ['town_street', 'shrine'], 'shrine': ['shrine_road'],
           'oldhouse_front': ['fields', 'courtyard'], 'courtyard': ['oldhouse_front', 'oldhouse_in'],
           'oldhouse_in': ['courtyard', 'oldhouse_corridor']}
    if loc != 'oldhouse_in' and loc in ADJ:
        # BFS 一步
        from collections import deque
        q = deque([(loc, None)])
        seen = {loc}
        mv = None
        while q:
            cur, first = q.popleft()
            if cur == 'oldhouse_in':
                mv = first
                break
            for nb in ADJ.get(cur, []):
                if nb in seen:
                    continue
                seen.add(nb)
                q.append((nb, first or nb))
        if mv:
            call('/api/act', {'action': 'move', 'to': mv})
            return 'move ' + mv
    call('/api/act', {'action': 'wait'})
    return 'wait'


def cmd_walk_p11():
    """从头玩到 P10 结束的幕间：主干选项按 SCENE_PICKS，泵好感过 P5 门槛，泵 bond≥52，存档 t1。"""
    call('/api/new', {})
    steps = 0
    seen = set()
    while steps < 900:
        steps += 1
        f = call('/api/state')
        meta = f.get('meta') or {}
        ph = meta.get('phase')
        if ph not in seen:
            seen.add(ph)
            print('SCENE', ph, brief(f))
        kind = f.get('kind')
        if kind == 'interlude':
            offer = (meta.get('scene_offer'))
            # P9 结束后的幕间（下一步是 P10，深雪在场）：三套泵轴存档
            if offer == 'P10' and ph == 'P9':
                ok, n = pump('bond', 52)
                ax, aff = axes()
                print('PUMP bond ok=%s talks=%d axes=%s' % (ok, n, ax))
                call('/api/save/t1', {})
                print('SAVED t1 (bond线)')
                ok, n = pump('obsession', 36)
                ax, _ = axes()
                print('PUMP obsession ok=%s talks=%d axes=%s' % (ok, n, ax))
                call('/api/save/t1m', {})
                print('SAVED t1m (入山线)')
                ok, n = pump('worldly', 36)
                ax, _ = axes()
                print('PUMP worldly ok=%s talks=%d axes=%s' % (ok, n, ax))
                call('/api/save/t1w', {})
                print('SAVED t1w (留京线)')
                r = call('/api/act', {'action': 'enter_scene'})
                print('  enter P10 |', brief(last(r['frames'])))
                continue
            if offer == 'P11':
                # P10 结束后的幕间（无人可谈）：存基线后停
                call('/api/save/t0', {})
                print('SAVED t0 |', brief(call('/api/state')))
                ax, aff = axes()
                print('FINAL axes:', ax, 'aff:', aff)
                return
            if offer:
                r = call('/api/act', {'action': 'enter_scene'})
                print('  enter', offer, '|', brief(last(r['frames'])))
                continue
            interlude_hold()
            continue
        COUNTER['c'] = 0
        FREE_NEXT.clear()
        FREE_NEXT.extend(FREE_TEXTS.get(ph, []))
        # 每个场景用独立 picks
        f2, act = step_once({k: v for k, v in SCENE_PICKS.items() if k == ph})
        if act == 'interlude-idle':
            interlude_hold()
            continue
    print('WALK TIMEOUT')


def cmd_until(target, picks_scene=None):
    """推进直到目标：interlude / ending / choice / scene(PH) 变化。"""
    steps = 0
    while steps < 400:
        steps += 1
        f = call('/api/state')
        kind = f.get('kind')
        meta = f.get('meta') or {}
        if target == 'interlude' and kind == 'interlude':
            print('REACH interlude |', brief(f))
            return
        if target == 'ending' and (meta.get('ending') or kind == 'ending_card'):
            print('REACH ending |', brief(f))
            return
        if target == 'choice' and kind == 'choice':
            print('REACH choice |', brief(f))
            return
        if target.startswith('scene:') and meta.get('phase') == target.split(':')[1]:
            print('REACH scene |', brief(f))
            return
        if target.startswith('bg:') and f.get('bg') == target.split(':', 1)[1]:
            print('REACH bg |', brief(f))
            return
        if target.startswith('kind:') and kind == target.split(':', 1)[1]:
            print('REACH kind |', brief(f))
            return
        ph = meta.get('phase')
        if kind == 'choice':
            picks = {picks_scene: SCENE_PICKS.get(picks_scene, [0])} if picks_scene else {}
            COUNTER['c'] = 0
            FREE_NEXT.clear()
            FREE_NEXT.extend(FREE_TEXTS.get(ph, []))
            f2, act = step_once(picks)
            print(' ', act, '|', brief(f2))
            continue
        if kind == 'free':
            r = call('/api/input', {'text': (FREE_TEXTS.get(ph) or ['……'])[0]})
            print('  free |', brief(last(r['frames'])))
            continue
        if kind == 'interlude':
            offer = meta.get('scene_offer')
            if offer:
                r = call('/api/act', {'action': 'enter_scene'})
                print('  enter', offer, '|', brief(last(r['frames'])))
            else:
                interlude_hold()
                print('  idle')
            continue
        r = call('/api/advance')
        print('  adv |', brief(last(r['frames'])))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'state'
    if cmd == 'new':
        r = call('/api/new', {})
        print('NEW |', brief(last(r['frames'])))
    elif cmd == 'walk_p11':
        cmd_walk_p11()
    elif cmd == 'load':
        r = call('/api/load/' + sys.argv[2], {})
        print('LOAD |', brief(last(r['frames'])))
    elif cmd == 'pump':
        ok, n = pump(sys.argv[2], int(sys.argv[3]))
        ax, aff = axes()
        print('PUMP %s→%s ok=%s talks=%d axes=%s aff=%s' % (sys.argv[2], sys.argv[3], ok, n, ax, aff))
    elif cmd == 'enter':
        r = call('/api/act', {'action': 'enter_scene'})
        print('ENTER |', brief(last(r['frames'])))
    elif cmd == 'pick':
        r = call('/api/input', {'choice_index': int(sys.argv[2])})
        print('PICK |', brief(last(r['frames'])))
    elif cmd == 'say':
        r = call('/api/input', {'text': sys.argv[2]})
        print('SAY |', brief(last(r['frames'])))
    elif cmd == 'until':
        cmd_until(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == 'state':
        f = call('/api/state')
        ax, aff = axes()
        print(brief(f))
        print('axes:', ax, 'aff:', aff, '| offer:', (f.get('meta') or {}).get('scene_offer'),
              '| ending:', (f.get('meta') or {}).get('ending'))
    elif cmd == 'dump':
        f = call('/api/state')
        with open(os.path.join(DUMP, sys.argv[2] + '.json'), 'w', encoding='utf-8') as fp:
            json.dump(f, fp, ensure_ascii=False)
        print('DUMP', sys.argv[2], '|', brief(f))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
