# -*- coding: utf-8 -*-
"""多结局收束测试：证明每条线都有归宿、没有未被收束的分支。

覆盖（对应《资料/02_设定与设计/多结局分支设计.md》第五节）：
  1. 图完备性：SUCCESSORS 覆盖全部场景；结局为吸收态；路由函数在全部
     「决策 flag × 轴边界值」组合下给出确定归宿（不可达的矛盾状态除外）。
  2. 实机全通路：SNOW / STAY / SPRING / FAR / TOKYO 五条路线离线通关，
     各自到达正确结局；SPRING 额外断言 accepted_sister 修复。
  3. 门控落空：执念/羁绊不足时，点击门槛选项 → 剧情化拒绝 + 回落 flag，绝不卡死。
  4. 结局后无悬挂：should_advance 恒 None、连续 advance 不报错。
  5. 离线打分器可用；存读档保留轴值。
运行：python3 tests/test_branching.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'server'))

import engine as engine_mod                                  # noqa: E402
from engine import Engine                                    # noqa: E402
from director.director import Director, SUCCESSORS, ENDINGS  # noqa: E402
from world.world import World                                # noqa: E402
from agents import score as axis_score                       # noqa: E402
from agents.llm import LLM                                   # noqa: E402
from scenes.script import SCENES                             # noqa: E402

# 回归测试全程离线（与 e2e 的 /api/mode llm:false 等价）：确定性、不耗 API 额度
LLM.enabled = False

FAILS = []


def check(name, cond, detail=''):
    if cond:
        print('  [pass] ' + name)
    else:
        FAILS.append(name)
        print('  [FAIL] ' + name + (' → ' + str(detail) if detail else ''))


ADJ = {
    'station': ['town_street', 'fields'], 'fields': ['station', 'oldhouse_front'],
    'town_street': ['station', 'toba_home', 'shrine_road'], 'toba_home': ['town_street'],
    'shrine_road': ['town_street', 'shrine'], 'shrine': ['shrine_road'],
    'oldhouse_front': ['fields', 'courtyard'], 'courtyard': ['oldhouse_front', 'oldhouse_in'],
    'oldhouse_in': ['courtyard', 'oldhouse_corridor'], 'oldhouse_corridor': ['oldhouse_in'],
    'mountains': [], 'blizzard': [],
}


def bfs_step(src, dst):
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


# ================================================================ 1. 图完备性
def test_graph():
    print('== 图完备性 ==')
    # 每个剧本场景都有后继表条目
    check('SUCCESSORS 覆盖全部场景', set(SUCCESSORS) >= set(SCENES),
          set(SCENES) - set(SUCCESSORS))
    # 吸收态 = 结局，且无后继
    for sid, succ in SUCCESSORS.items():
        if not succ:
            check('吸收态 %s 已映射结局 %s' % (sid, ENDINGS.get(sid)), sid in ENDINGS)
    # 结局场景都在剧本里
    check('结局场景均存在于剧本', all(s in SCENES for s in ENDINGS))
    # 每个 choice 节拍都有兜底无门控选项（保证任何轴值都有路可走）
    for sid, sc in SCENES.items():
        for b in sc['beats']:
            if b['type'] == 'choice':
                check('%s choice 有无门控兜底选项' % sid,
                      any(not o.get('requires') for o in b['options']))


def test_route_totality():
    print('== 路由穷举（决策 flag × 轴边界） ==')
    combos = 0
    for mountains in (0, 1):
        for ret in (0, 1):
            for tokyo in (0, 1):
                for stay in (0, 1):
                    for spring in (0, 1):
                        for bond in (0, 35, 49, 50, 100):
                            for obs in (0, 34, 35, 100):
                                w = World()
                                w.flags.update(chose_mountains=bool(mountains),
                                               chose_return=bool(ret),
                                               stayed_tokyo=bool(tokyo),
                                               happiness_asked=True,
                                               chose_stay=bool(stay),
                                               chose_spring=bool(spring))
                                w.axes = {'bond': bond, 'obsession': obs, 'worldly': 50}
                                d = Director(w)
                                # --- P11 视角（coherent 状态：三个决策 flag 互斥且由选择机制产生）
                                if mountains and not ret and not tokyo:
                                    r = d.route('P11')
                                    if obs >= 35:
                                        check('P11 入山 → P12M', r == 'P12M', r)
                                    combos += 1
                                elif ret and not mountains and not tokyo:
                                    check('P11 归去 → P12B', d.route('P11') == 'P12B')
                                    combos += 1
                                elif tokyo and not mountains and not ret:
                                    check('P11 留京 → E_TOKYO', d.route('P11') == 'E_TOKYO')
                                    combos += 1
                                # --- P12B 视角（幸福之问已问出）
                                if stay and spring:
                                    continue    # 矛盾状态，选择机制不会产生
                                if stay and not spring:
                                    expect = 'E_STAY' if bond >= 50 else 'E_FAR'
                                    check('P12B 留下 bond=%d → %s' % (bond, expect),
                                          d.route('P12B') == expect, d.route('P12B'))
                                    combos += 1
                                elif spring and not stay:
                                    expect = 'E_SPRING' if (bond >= 50 and obs < 35) else 'E_FAR'
                                    check('P12B 春天 bond=%d obs=%d → %s' % (bond, obs, expect),
                                          d.route('P12B') == expect, d.route('P12B'))
                                    combos += 1
                                else:
                                    check('P12B 兜底 → E_FAR', d.route('P12B') == 'E_FAR')
                                    combos += 1
    # P12M 恒达 P0；结局吸收
    w = World()
    w.flags['chose_mountains'] = True
    w.axes = {'bond': 50, 'obsession': 40, 'worldly': 10}
    d = Director(w)
    check('P12M → P0', d.route('P12M') == 'P0')
    for sid in ENDINGS:
        check('吸收态 %s 无后继' % sid, d.route(sid) is None)
    print('  （穷举 %d 个可达组合）' % combos)


# ================================================================ 2. 实机全通路
ROUTES = {
    # 入山线：狂泵执念，P11 选「先去群山」
    'SNOW': dict(
        choices={'P5': '父亲和母亲', 'P7': '追问', 'P11': '先去群山'},
        free=lambda ph: '父亲和母亲还在山里呼唤我',
        talk='父亲和母亲，还在那座深山里面。群山在呼唤。',
        want=lambda w: w.axes['obsession'] < 45,
        expect='END_SNOW'),
    # 真结局：泵羁绊、避开执念，P12B 选「春天再见」
    'SPRING': dict(
        choices={'P5': '岔开话题', 'P7': '放弃追问', 'P11': '回到雪国', 'P12B': '春天'},
        free=lambda ph: '姐姐，我很喜欢你' if ph != 'P12B' else '和你在一起，就是幸福',
        talk='姐姐，我很喜欢你，想和你一起堆雪人。',
        want=lambda w: w.axes['bond'] < 55,
        expect='END_SPRING'),
    # 留守线：同上，但 P12B 选「留在这里」
    'STAY': dict(
        choices={'P5': '岔开话题', 'P7': '放弃追问', 'P11': '回到雪国', 'P12B': '留在这里'},
        free=lambda ph: '姐姐，我很喜欢你' if ph != 'P12B' else '和你在一起，就是幸福',
        talk='姐姐，留下陪你清雪、打扑克、堆雪人。',
        want=lambda w: w.axes['bond'] < 55,
        expect='END_STAY'),
    # 原作向：不泵任何轴、沉默选项，走兜底
    'FAR': dict(
        choices={'P11': '回到雪国', 'P12B': '话终究没有说完整'},
        free=lambda ph: '……',
        talk=None,
        want=lambda w: False,
        expect='END_FAR'),
    # 留京线：泵现世，P11 选「留在东京」
    'TOKYO': dict(
        choices={'P5': '岔开话题', 'P11': '留在东京'},
        free=lambda ph: '东京的学校要开学了',
        talk='东京的学校，开学，考试，同学都在等我。',
        want=lambda w: w.axes['worldly'] < 40,
        expect='END_FAR'),
}


def pick_choice(engine, route):
    phase = engine.world.phase
    opts = (engine.last_frame.get('choices') or [])
    want_label = route['choices'].get(phase)
    if want_label:
        for i, o in enumerate(opts):
            if want_label in o['label']:
                return i
    return 0


def drive(route):
    """离线跑通一条完整路线，返回 (engine, steps)。"""
    e = Engine()
    e.new_game()
    steps = 0
    while steps < 1500:
        steps += 1
        f = e.last_frame
        kind = f['kind']
        if w_ended(e):
            return e, steps
        if kind == 'choice':
            e.submit_input(None, pick_choice(e, route))
        elif kind == 'free':
            e.submit_input(route['free'](e.world.phase), None)
        elif kind == 'interlude':
            if f['meta'].get('scene_offer'):
                e.enter_offered_scene()
                continue
            # 幕间策略：需要泵轴且深雪在场 → 交谈；否则挪向老屋 / 等待
            chars = e.director.present_chars()
            if route['talk'] and route['want'](e.world):
                e.interlude_act('talk', {'text': route['talk']})
            else:
                step = bfs_step(e.world.location, 'oldhouse_in')
                if step:
                    e.interlude_act('move', {'to': step})
                else:
                    e.interlude_act('wait', {})
        else:
            e.advance()
    raise AssertionError('1500 步内未达结局（route=%s）' % route['expect'])


def w_ended(e):
    return bool(e.world.flags.get('ending'))


def test_routes():
    print('== 实机全通路（五线） ==')
    for name, route in ROUTES.items():
        e, steps = drive(route)
        ending = e.world.flags.get('ending')
        check('%s → %s（%d 步）' % (name, route['expect'], steps),
              ending == route['expect'], '实际=%s' % ending)
        if name == 'SPRING':
            check('SPRING 修复 accepted_sister', e.world.flags.get('accepted_sister') is True)
        if name == 'SNOW':
            check('SNOW 走到 P0 终幕', e.world.flags.get('finale') is True)
        # 结局后无悬挂
        d = e.director
        check('%s 结局后 should_advance=None' % name, d.should_advance() is None)
        for _ in range(3):
            e.advance()
        e.interlude_act('wait', {})
        check('%s 结局后 advance/act 无异常' % name, True)


# ================================================================ 3. 门控落空
def test_gate_fail():
    print('== 门控落空（阈值不足 → 剧情化拒绝） ==')
    # P11 执念不足选「先去群山」
    e = Engine()
    e.new_game()
    e.enter_scene('P11')
    for _ in range(8):
        e.advance()          # 走到 choice（branch_text/旁白帧推进）
    assert e.last_frame['kind'] == 'choice', e.last_frame['kind']
    frames = e.submit_input(None, 0)  # 「先去群山」（执念不足）
    check('P11 门槛不足 → 落空旁白', any(
        f['kind'] == 'narration' and '资格' in (f.get('text') or '') for f in frames),
        [f.get('text', '')[:30] for f in frames])
    check('P11 落空 → chose_return', e.world.flags.get('chose_return') is True)
    check('P11 落空 → 未进山', e.world.flags.get('chose_mountains') is None)
    check('P11 落空后可继续推进', e.director.route() == 'P12B')

    # P12B 羁绊不足选「留在这里」
    e2 = Engine()
    e2.enter_scene('P12B')
    for _ in range(6):
        e2.advance()
    assert e2.last_frame['kind'] == 'free', e2.last_frame['kind']
    e2.submit_input('……', None)
    for _ in range(3):
        e2.advance()
    assert e2.last_frame['kind'] == 'choice', e2.last_frame['kind']
    e2.submit_input(None, 0)  # 「留在这里」 requires bond>=50，默认 20
    check('P12B 羁绊不足 → stay_promise_failed',
          e2.world.flags.get('stay_promise_failed') is True)
    # 回应独占一屏：落空旁白后需点击继续，尾随 effect（happiness_asked）才结算
    for _ in range(3):
        e2.advance()
    check('P12B 落空路由 → E_FAR', e2.director.route() == 'E_FAR')


# ================================================================ 4. 打分器与存档
def test_score_offline():
    print('== 离线打分器 ==')
    d = axis_score.score_axes('父亲和母亲在深山里呼唤我')
    check('执念词打分', d['obsession'] >= 6 and d['src'] == 'rules', d)
    d = axis_score.score_axes('姐姐我很喜欢你，想和你一起堆雪人')
    check('羁绊词打分', d['bond'] >= 6, d)
    d = axis_score.score_axes('东京的学校要开学了，考试很多')
    check('现世词打分', d['worldly'] >= 6, d)
    d = axis_score.score_axes('……')
    check('中性输入零分', d['bond'] == 0 and d['obsession'] == 0 and d['worldly'] == 0, d)


def test_save_load_axes():
    print('== 存读档保留轴值 ==')
    e = Engine()
    e.new_game()
    e.world.add_axis('bond', 25, 'test')
    e.world.add_axis('obsession', 30, 'test')
    e.save('branching_test')
    e2 = Engine()
    e2.load('branching_test')
    check('轴值往返', e2.world.axes == e.world.axes, (e2.world.axes, e.world.axes))
    os.remove(os.path.join(engine_mod.SAVE_DIR, 'branching_test.json'))


def test_branch_text():
    print('== 条件文本 ==')
    e = Engine()
    e.enter_scene('P12M')
    e.world.flags['parents_belief'] = True
    e.world.axes['obsession'] = 60
    got = []
    for _ in range(12):
        f = e.last_frame
        if f['kind'] == 'narration':
            got.append(f['text'])
        if f['kind'] == 'interlude':
            break
        e.advance()
    check('P12M 高执念显示「呼唤」变体', any('呼唤' in t for t in got))


if __name__ == '__main__':
    test_graph()
    test_route_totality()
    test_score_offline()
    test_save_load_axes()
    test_branch_text()
    test_gate_fail()
    test_routes()
    print()
    if FAILS:
        print('RESULT: %d FAILED → %s' % (len(FAILS), FAILS))
        sys.exit(1)
    print('RESULT: ALL BRANCHING TESTS PASSED')
