# -*- coding: utf-8 -*-
"""C4 正典检索注入 + C7 引导策略菜单 + C8 传闻强度回流 回归。

运行：python3 tests/test_canon_guide_gossip.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'server'))

from agents import canon, guardrails                                            # noqa: E402
from agents.llm import LLM                                                      # noqa: E402
from director import gossip, guide as guide_mod                                 # noqa: E402
from director.director import Director                                          # noqa: E402
from world.world import World                                                   # noqa: E402

LLM.enabled = False

PASS = FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print('  [pass]', name)
    else:
        FAIL += 1
        print('  [FAIL]', name, detail)


# ================================================================ C4 正典检索
def test_canon():
    print('== C4 正典检索 ==')
    check('语料库覆盖多数场景', len(canon.CANON) >= 12, len(canon.CANON))
    got = canon.retrieve_canon('P2', '我来清雪吧', 'miyuki')
    check('P2 检索出清雪相关正典',
          bool(got) and any(k in g for g in got for k in ('清雪', '清扫', '铲子')), got)
    # held-out：名场面不进检索库
    for scene, frag in (('P6', '写作深和雪'), ('P3', '你的姐姐啊'),
                        ('P7', '还是没有姐姐高'), ('P12B', '觉得现在幸福吗')):
        pool = [e['say'] for e in canon.CANON.get(scene, [])]
        check('held-out 不入库：%s' % frag, not any(frag in p for p in pool), pool[:5])
    # 注入台词全部能过护栏（示例合法）
    for scene in ('P1', 'P5', 'P8'):
        for line in canon.retrieve_canon(scene, '呐', 'miyuki'):
            check('示例过护栏：%s' % line[:12], not guardrails.check_miyuki(line, scene))


# ================================================================ C7 引导策略
def _director_with(phase='P3', **flags):
    w = World()
    w.phase = phase
    w.flags.update(met_miyuki=True, **flags)
    d = Director(w)
    return w, d


def test_guide():
    print('== C7 引导策略菜单 ==')
    # 信息钩子：滞留 ≥3 步且存在可进入后继
    w, d = _director_with('P3', snowball_fight=True)
    w.festival_countdown = 0
    d.idle_steps = 3
    g = guide_mod.guide(d)
    check('滞留 3 步 → 引导触发', g is not None)
    check('默认策略为 info_hook', g and g['strategy'] == 'info_hook', g and g['strategy'])
    # 未滞留不引导
    d2 = Director(w)
    d2.idle_steps = 1
    check('未滞留不引导', guide_mod.guide(d2) is None)
    # 谜团话头 → npc_redirect
    w3, d3 = _director_with('P3', comforted=True, snowball_fight=True)
    w3.festival_countdown = 0          # 让 P4 吸引子成立（route 非空）
    d3.idle_steps = 5
    d3.mystery_probes = 2
    w3.location = 'fields'             # 深雪不会自动在场的地点（NPC 影响型才有意义）
    g3 = guide_mod.guide(d3)
    check('谜团连问 → npc_redirect', g3 and g3['strategy'] == 'npc_redirect', g3 and g3['strategy'])
    # 世界后果型：滞留 ≥6 步
    d3.mystery_probes = 0
    d3.idle_steps = 7
    g3b = guide_mod.guide(d3)
    check('滞留 7 步 → 世界后果型', g3b and g3b['strategy'] == 'world_consequence',
          g3b and g3b['strategy'])
    # 时机调整型：P4 阶段、P5 仅差地点
    w4, d4 = _director_with('P4', festival_done=True)
    w4.miyuki_affection_extra = 45
    w4.location = 'town_street'
    d4.idle_steps = 4
    g4 = guide_mod.guide(d4)
    check('P5 仅差地点 → event_comes + pending_force',
          g4 and g4['strategy'] == 'event_comes' and d4.pending_force == 'P5',
          g4 and (g4['strategy'], d4.pending_force))


# ================================================================ C8 传闻强度
def test_gossip_strength():
    print('== C8 传闻强度与回流 ==')
    w = World()
    w.know('relative_man', 'girl_took_shuuji', '亲戚会议上，一个来历不明的女孩把修二牵出了庭院。')
    kn = w.knowledge['relative_man']['girl_took_shuuji']
    check('目击条目初始强度 1.2', abs(kn.strength - 1.2) < 1e-9, kn.strength)
    for _ in range(10):
        w.tick_rumors()
    check('10 日衰减后 < 0.5', kn.strength < 0.5, kn.strength)
    gossip.strengthen(w, 'relative_man', 0.1)
    check('引用升温封顶 2.0', kn.strength <= 2.0)
    # 沉寂传闻停传
    w2 = World()
    w2.day = 1
    w2.know('relative_man', 'r1', '某传闻。', source='heard')
    w2.knowledge['relative_man']['r1'].strength = 0.1
    items = gossip.run_daily_gossip(w2, seed=3)
    check('强度 <0.2 的传闻停传', all(i['key'] != 'r1' for i in items), items)
    # 回流接口
    w3 = World()
    w3.know('toba', 'r2', '老屋半夜有灯，你敢信？', source='heard')
    w3.knowledge['toba']['r2'].strength = 1.0
    check('rumors_for_prompt 过滤强度', gossip.rumors_for_prompt('toba', w3) != [])
    w3.knowledge['toba']['r2'].strength = 0.3
    check('低强度传闻不进 prompt', gossip.rumors_for_prompt('toba', w3) == [])
    check('hot_rumor 返回最热传闻', '老屋' in (gossip.hot_rumor(w3) or ''))


if __name__ == '__main__':
    test_canon()
    test_guide()
    test_gossip_strength()
    print('\nRESULT: %d passed, %d failed' % (PASS, FAIL))
    sys.exit(1 if FAIL else 0)
