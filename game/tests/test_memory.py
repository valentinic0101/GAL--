# -*- coding: utf-8 -*-
"""C1 记忆流三因子检索 + C2 反思信念沉淀 回归。

运行：python3 tests/test_memory.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'server'))

from agents.memory import (MemoryStream, MemoryEntry, rule_importance,           # noqa: E402
                           extract_keywords, reflect, offline_insights, REFLECT_THRESHOLD)
from agents.llm import LLM                                                       # noqa: E402
from world.world import World                                                    # noqa: E402

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


def test_three_factor():
    print('== C1 三因子检索 ==')
    ms = MemoryStream()
    ms.add('他红着眼睛说喜欢这雪', day=1, importance=8)          # 高重要+久远
    ms.add('今天一起清了雪', day=2, importance=2)                # 低重要+新近
    ms.add('柱子上刻下了身高的约定', day=1, importance=8)         # 高重要+关键词命中
    ms.add('镇上的传闻在扩散', day=3, importance=2)
    hits = ms.retrieve('身高的约定还在吗', now_day=10, k=2)
    check('相关性优先命中', any('柱子' in e.content for e in hits), [e.content for e in hits])
    hits2 = ms.retrieve('随便聊聊', now_day=3, k=2)
    check('无查询词时按近因+重要排序（高重要记忆在前）',
          all(e.importance >= 8 for e in hits2), [(e.content, e.importance) for e in hits2])


def test_importance_and_keywords():
    print('== C1 重要度与关键词 ==')
    check('高锚词打 6+', rule_importance('和小修拉勾定了约定') >= 6)
    check('中锚词打 4', rule_importance('一起打了雪仗') >= 4)
    check('日常打 2', rule_importance('今天天气不错') == 2)
    check('关键词抽取', '雪' in extract_keywords('雪一直下') or '拉勾' in extract_keywords('拉勾了'))


def test_dedup_and_compress():
    print('== C1 去重与容量压缩 ==')
    ms = MemoryStream()
    ms.add('小修，晚安――', day=5)
    ms.add('小修，晚安――', day=5)
    check('同日同文去重', len(ms.entries) == 1)
    for i in range(220):
        ms.add('经历%d号：一些事情' % i, day=10 + i)
    check('容量硬上界 ≤ MAX_ENTRIES', len(ms.entries) <= MemoryStream.MAX_ENTRIES, len(ms.entries))
    check('压缩产生摘要条目', any(e.kind == 'summary' for e in ms.entries))


def test_hooks_via_engine():
    print('== C1 引擎写入钩子 ==')
    import engine as engine_mod
    from engine import Engine
    engine_mod.LLM.enabled = False
    e = Engine()
    e.new_game()
    for _ in range(80):
        if e.world.flags.get('ending') or e.world.flags.get('finale'):
            break
        f = e.last_frame
        if f['kind'] == 'choice':
            e.submit_input(None, 0)
        elif f['kind'] == 'free':
            e.submit_input('……', None)
        elif f['kind'] == 'interlude':
            if f['meta'].get('scene_offer'):
                e.enter_offered_scene()
            else:
                e.interlude_act('wait', {})
        else:
            e.advance()
    mems = e.world.memory['miyuki'].entries
    check('深雪记忆流非空', len(mems) > 0, len(mems))
    check('深雪记住了台词（含「说：」条目）', any('说：' in m.content for m in mems))
    # P1 结束后亲戚有目击知识 → 记忆镜像
    check('知识条目镜像进记忆流', any(m.kind in ('rumor', 'episode')
                                  for c in ('relative_man', 'toba')
                                  for m in e.world.memory[c].entries))
    # 存读档回环
    e.save('memory_test')
    e2 = Engine()
    e2.load('memory_test')
    check('记忆流存读档往返', len(e2.world.memory['miyuki'].entries) == len(mems))
    os.remove(os.path.join(engine_mod.SAVE_DIR, 'memory_test.json'))


def test_reflection():
    print('== C2 反思与信念 ==')
    w = World()
    w.flags.update(likes_snow=True, snowball_fight=True, met_miyuki=True)
    ms = w.memory['miyuki']
    ms.add('小修骂了我丑八怪', day=3, importance=6)
    ms.add('他说了「我喜欢这雪」', day=1, importance=8)
    insights = reflect('miyuki', w, ms)
    check('触发产出洞察', len(insights) > 0, insights)
    stored = ms.insights()
    check('洞察写回记忆流（importance=9）', any(e.importance == 9 for e in stored))
    # 亲戚信念
    rel = w.memory['relative_man']
    rel.add('亲戚会议上推诿抚养权', day=1, importance=6)
    ins2 = reflect('relative_man', w, rel)
    check('亲戚洞察含老屋/遗产执念', any(('老屋' in s or '遗产' in s or '丫头' in s) for s in ins2), ins2)
    # 谜团锁过滤：恶意洞察被丢弃
    w.phase = 'P3'
    ms2 = w.memory['miyuki']
    ms2.add('他问我从哪里来', day=3, importance=6)
    insights_bad = reflect('miyuki', w, ms2)
    check('洞察不泄谜团', all(not any(k in s for k in ('雪女', '人类', '我不是人'))
                           for s in insights_bad), insights_bad)
    # 能量槽触发逻辑（engine 侧）
    import engine as engine_mod
    from engine import Engine
    engine_mod.LLM.enabled = False
    e = Engine()
    e.new_game()
    e.world.reflect_points['miyuki'] = REFLECT_THRESHOLD
    e.enter_scene('P2')
    for _ in range(80):
        f = e.last_frame
        if f['kind'] in ('interlude',):
            break
        if f['kind'] == 'choice':
            e.submit_input(None, 0)
        elif f['kind'] == 'free':
            e.submit_input('……', None)
        else:
            e.advance()
    check('能量槽达阈值 → 场景结束触发反思',
          any(ev.kind == 'reflection' for ev in e.world.events) or e.world.reflect_points['miyuki'] == 0)


if __name__ == '__main__':
    test_three_factor()
    test_importance_and_keywords()
    test_dedup_and_compress()
    test_hooks_via_engine()
    test_reflection()
    print('\nRESULT: %d passed, %d failed' % (PASS, FAIL))
    sys.exit(1 if FAIL else 0)
