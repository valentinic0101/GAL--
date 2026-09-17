# -*- coding: utf-8 -*-
"""端到端自动通关测试：模拟玩家从 P1 走到分支层，直至到达任一结局。

结局由三轴与选择决定（见《设计文档/多结局分支设计.md》）：
END_SNOW 白之彼方 / END_STAY 炉火与春讯 / END_SPRING 等到花开 / END_FAR 两行足迹。
穷举式路由验证在 tests/test_branching.py。"""
import json
import sys
import urllib.request

BASE = 'http://127.0.0.1:8300'

# 绕过系统代理（macOS urllib 会读系统代理，localhost 被代理拦截会 502）
urllib.request.install_opener(
    urllib.request.build_opener(urllib.request.ProxyHandler({})))


def call(path, body=None, get=None):
    if get is None:
        get = path.rstrip('/') in ('/api/state', '/api/locations', '/api/backlog',
                                   '/api/world', '/api/saves', '/api/personas', '/api/health')
    if get:
        req = urllib.request.Request(BASE + path)
    else:
        req = urllib.request.Request(BASE + path,
                                     data=json.dumps(body or {}).encode(),
                                     headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def last(frames):
    return frames[-1] if frames else {}


# 场景图（与 server/world/world.py 保持一致），用于测试机器人寻路
ADJ = {
    'station': ['town_street', 'fields'], 'fields': ['station', 'oldhouse_front'],
    'town_street': ['station', 'toba_home', 'shrine_road'], 'toba_home': ['town_street'],
    'shrine_road': ['town_street', 'shrine'], 'shrine': ['shrine_road'],
    'oldhouse_front': ['fields', 'courtyard'], 'courtyard': ['oldhouse_front', 'oldhouse_in'],
    'oldhouse_in': ['courtyard', 'oldhouse_corridor'], 'oldhouse_corridor': ['oldhouse_in'],
    'mountains': [], 'blizzard': [],
}


def next_step_toward(src, dst):
    """BFS 返回从 src 到 dst 的第一步；同点返回 None。"""
    if src == dst:
        return None
    from collections import deque
    q = deque([(src, None)])
    seen = {src}
    while q:
        cur, first = q.popleft()
        for nb in ADJ.get(cur, []):
            if nb in seen:
                continue
            step = nb if first is None else first
            if nb == dst:
                return step
            seen.add(nb)
            q.append((nb, step))
    return None


def play():
    seen_phases = []
    # 回归模式：关闭真实 LLM 调用（规则引擎兜底），避免 API 消耗与超时；结束后恢复
    call('/api/mode', {'llm': False})
    try:
        _play(seen_phases)
    finally:
        call('/api/mode', {'llm': True})


def _play(seen_phases):
    r = call('/api/new', {})
    f = last(r['frames'])
    assert f['kind'] in ('scene_title', 'narration'), f
    print('[ok] new game, first frame:', f['kind'])

    steps = 0
    free_texts = iter(['你放……放开我', '我喜欢这雪', '呜呜……', '骗子骗子骗子',
                       '姐姐，来陪我打扑克――', '我喜欢这雪', '……你要怎么办？',
                       '姐姐也是啊', '再见', '修二你在哪里'])
    ended = set()
    while steps < 900:
        steps += 1
        f = call('/api/state') or {}
        meta = f.get('meta') or {}
        kind = f.get('kind')
        if meta.get('phase') not in seen_phases:
            seen_phases.append(meta.get('phase'))
        if kind == 'choice':
            # 决策/普通选项：轮换点击（选项节拍不可被自由输入跳过，见 submit_input）
            opts = f.get('choices') or []
            idx = steps % max(1, len(opts))
            r = call('/api/input', {'choice_index': idx})
            f = last(r['frames'])
        elif kind == 'free':
            try:
                t = next(free_texts)
            except StopIteration:
                t = '……'
            r = call('/api/input', {'text': t})
            f = last(r['frames'])
        elif kind == 'interlude':
            offer = (f.get('meta') or {}).get('scene_offer')
            if offer:
                r = call('/api/act', {'action': 'enter_scene'})
                f = last(r['frames'])
                print('[scene]', offer)
            else:
                # 幕间：优先走向老屋（多数剧情吸引子的地点条件），途中交谈+等待推进时间
                loc = call('/api/locations')
                target = 'oldhouse_in' if loc['current'] != 'oldhouse_in' else None
                mv = next_step_toward(loc['current'], target) if target else None
                if mv:
                    r = call('/api/act', {'action': 'move', 'to': mv})
                    f = last(r['frames'])
                else:
                    r = call('/api/act', {'action': 'talk', 'text': '呐，你喜欢雪吗？'})
                    f = last(r['frames'])
                r = call('/api/act', {'action': 'wait'})
                f = last(r['frames'])
        else:
            r = call('/api/advance')
            f = last(r['frames'])
        if f.get('kind') == 'error':
            print('[warn] error frame:', f.get('note'))
        # 终点判定：进入任一结局（吸收态 flag ending=END_*）
        w = call('/api/world')
        if w.get('flags', {}).get('ending'):
            print('[ok] reached ending:', w['flags']['ending'])
            break
    print('phases reached:', seen_phases)
    w = call('/api/world')
    print('final world:', json.dumps({k: w[k] for k in ('day', 'phase', 'location', 'affection')}, ensure_ascii=False))
    print('flags:', w['flags'])
    assert w['flags'].get('ending'), '未到达任何结局'
    # 存读档
    call('/api/save/1', {})
    r = call('/api/load/1', {})
    assert 'frames' in r
    print('[ok] save/load roundtrip')
    # 日志
    b = call('/api/backlog')
    print('[ok] backlog entries:', len(b['history']))
    print('E2E PASSED in', steps, 'steps')


if __name__ == '__main__':
    play()
