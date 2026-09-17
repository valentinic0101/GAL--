# -*- coding: utf-8 -*-
"""带完整轨迹采集的自动通关：把 P1→P0 全程录成 JSON，供 playthrough.html 展示。

离线模式（规则引擎）保证确定性与速度；记录每一次 API 调用的帧、
每条台词/旁白/选项/幕间行动、阶段转换、世界快照（旗标/好感/传闻）。
输出：game/web/playthrough_data.json
"""
import json
import os
import time
import urllib.request

BASE = 'http://127.0.0.1:8300'
GETS = ('/api/state', '/api/world', '/api/backlog', '/api/saves', '/api/locations', '/api/health')
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'web', 'playthrough_data.json')

ADJ = {
    'station': ['town_street', 'fields'], 'fields': ['station', 'oldhouse_front'],
    'town_street': ['station', 'toba_home', 'shrine_road'], 'toba_home': ['town_street'],
    'shrine_road': ['town_street', 'shrine'], 'shrine': ['shrine_road'],
    'oldhouse_front': ['fields', 'courtyard'], 'courtyard': ['oldhouse_front', 'oldhouse_in'],
    'oldhouse_in': ['courtyard', 'oldhouse_corridor'], 'oldhouse_corridor': ['oldhouse_in'],
}


def next_step_toward(src, dst):
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


def call(path, body=None):
    if body is None and path in GETS:
        req = urllib.request.Request(BASE + path)
    else:
        req = urllib.request.Request(BASE + path,
                                     data=json.dumps(body or {}).encode(),
                                     headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def world_snap():
    w = call('/api/world')
    rumors = []
    for c, ks in (w.get('knowledge') or {}).items():
        for k, v in ks.items():
            if v.get('source') == 'heard':
                rumors.append({'who': c, 'content': v['content'], 'hops': v.get('hops', 0),
                               'distorted': v.get('distorted', False)})
    return {'day': w['day'], 'phase': w['phase'], 'location': w['location'],
            'affection': w['affection'], 'countdown': w['countdown'],
            'flags': sorted(w['flags'].keys()), 'rumors': rumors}


FREE_TEXTS = ['你放……放开我', '我喜欢这雪', '呜呜……', '骗子骗子骗子',
              '姐姐，来陪我打扑克――', '我喜欢这雪', '……你要怎么办？',
              '姐姐也是啊', '再见', '修二你在哪里']


def main():
    t_start = time.time()
    entries = []
    step = [0]

    def log(t, **kw):
        kw['t'] = step[0]
        kw['type'] = t
        entries.append(kw)

    def frames_log(frames, api):
        """把一次响应的帧记录进日志。"""
        for f in frames:
            k = f.get('kind')
            if k in ('narration', 'line', 'me'):
                log('beat', kind=k, name=f.get('name'), text=f.get('text'),
                    action=f.get('action') or None, src=f.get('src'),
                    who=f.get('who'), bg=f.get('bg'))
            elif k == 'scene_title':
                log('scene_title', title=f.get('note'), bg=f.get('bg'))
            elif k == 'choice':
                log('choice_prompt', options=[o['label'] for o in (f.get('choices') or [])])
            elif k == 'free':
                log('free_prompt', hint=f.get('note'))
            elif k == 'interlude':
                m = f.get('meta') or {}
                log('interlude', note=f.get('note'), bg=f.get('bg'),
                    offer=m.get('scene_offer'), offer_title=m.get('scene_offer_title'))

    # ---------- 开始（离线模式） ----------
    call('/api/mode', {'llm': False})
    log('run_begin', note='离线回归模式（规则引擎应答，确定性轨迹）')
    r = call('/api/new', {})
    frames_log(r['frames'], '/api/new')
    prev_snap = world_snap()
    log('world', snap=prev_snap)
    seen_phases = ['P1']

    free_iter = iter(FREE_TEXTS)
    steps = 0
    finished = False
    while steps < 900:
        steps += 1
        step[0] += 1
        f = call('/api/state')
        kind = f.get('kind')
        if kind in ('choice', 'free'):
            try:
                txt = next(free_iter)
            except StopIteration:
                txt = '……'
            log('input', mode='free_text' if kind == 'free' else 'choice_text', text=txt)
            r = call('/api/input', {'text': txt})
            frames_log(r['frames'], '/api/input')
        elif kind == 'interlude':
            offer = (f.get('meta') or {}).get('scene_offer')
            if offer:
                log('scene_enter', phase=offer, title=(f.get('meta') or {}).get('scene_offer_title'))
                r = call('/api/act', {'action': 'enter_scene'})
                frames_log(r['frames'], '/api/act.enter_scene')
                if offer not in seen_phases:
                    seen_phases.append(offer)
                snap = world_snap()
                if snap != prev_snap:
                    log('world', snap=snap)
                    prev_snap = snap
                continue
            loc = call('/api/locations')
            target = 'oldhouse_in' if loc['current'] != 'oldhouse_in' else None
            mv = next_step_toward(loc['current'], target) if target else None
            if mv:
                log('action_move', to=mv, from_loc=loc['current_name'])
                r = call('/api/act', {'action': 'move', 'to': mv})
                frames_log(r['frames'], '/api/act.move')
            else:
                txt = '呐，你喜欢雪吗？'
                log('input', mode='talk', text=txt)
                r = call('/api/act', {'action': 'talk', 'text': txt})
                frames_log(r['frames'], '/api/act.talk')
            step[0] += 1
            log('action_wait')
            r = call('/api/act', {'action': 'wait'})
            frames_log(r['frames'], '/api/act.wait')
            snap = world_snap()
            if snap != prev_snap:
                log('world', snap=snap, note='（过夜后的世界状态：天数/旗标/传闻）')
                prev_snap = snap
        else:
            r = call('/api/advance', {})
            frames_log(r['frames'], '/api/advance')
        w = call('/api/world')
        if w['flags'].get('finale'):
            log('finale', note='P0 终幕完成：修二在暴风雪中走向群山深处。')
            finished = True
            break

    # ---------- 存读档验证 ----------
    call('/api/save/1', {})
    log('save', slot='1')
    r = call('/api/load/1', {})
    frames_log(r['frames'], '/api/load')
    log('load', slot='1')

    final = world_snap()
    dur = time.time() - t_start
    data = {
        'meta': {
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'mode': 'offline (rules engine)',
            'llm': call('/api/health').get('model'),
            'api_calls': steps,
            'entries': len(entries),
            'phases': seen_phases,
            'duration_sec': round(dur, 1),
            'final': final,
            'finished': finished,
        },
        'entries': entries,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print('captured', len(entries), 'entries,', steps, 'api calls,', round(dur, 1), 's ->', OUT)
    print('phases:', ' → '.join(seen_phases))
    print('final:', json.dumps({k: final[k] for k in ('day', 'phase', 'affection')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
