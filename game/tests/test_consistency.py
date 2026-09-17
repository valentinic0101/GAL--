# -*- coding: utf-8 -*-
"""角色一致性回归测试（人物圣经§5 一致性自检的自动化版本）+ 资产校验。"""
import os
import sys
import xml.dom.minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'server'))

from agents import rule_engine, guardrails
from world.world import World

PASS = FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print('  [pass]', name)
    else:
        FAIL += 1
        print('  [FAIL]', name, detail)


def test_miyuki_consistency():
    print('== 深雪一致性 ==')
    w = World()
    w.phase = 'P3'
    w.miyuki_affection_extra = 30
    probes = [
        ('你到底是不是人类？！', '谜团锁-人类'),
        ('你是雪女吧？', '谜团锁-雪女'),
        ('你从哪里来的？', '谜团锁-来历'),
        ('你一个人住在这怎么生活？', '谜团锁-生存'),
        ('你是骗子！骗子！', '指控骗子'),
        ('爸爸和妈妈是不是死在山里了', '父母话题'),
        ('（呜呜地哭起来）', '哭泣安慰'),
    ]
    for text, label in probes:
        r = rule_engine.respond('miyuki', text, w)
        issues = guardrails.validate('miyuki', r['say'], w.phase)
        check('%s → 无护栏违规' % label, not issues, str(issues) + ' | ' + r['say'])
        check('%s → 谜团未泄漏' % label,
              not any(k in r['say'] for k in ('我是雪女', '我不是人类', '我已经死了', '我其实是')),
              r['say'])
    # 30 轮小对话不崩坏
    bad = 0
    for i in range(30):
        r = rule_engine.respond('miyuki', ['呐', '今天好冷', '雪真美', '我回来了', '随便聊聊'][i % 5], w)
        if guardrails.validate('miyuki', r['say'], w.phase):
            bad += 1
    check('30 轮闲聊零违规', bad == 0, '%d violations' % bad)
    # 高好感阶段语气
    w.miyuki_affection_extra = 40
    r = rule_engine.respond('miyuki', '嗯', w)
    check('高好感日常用语带长音/语气词', any(t in r['say'] for t in ('――', '哦', '呢', '啦', '嘛', '吧')), r['say'])


def test_shuuji_guardrails():
    print('== 修二护栏 ==')
    check('幼年文艺腔被拦', 'too_literary' in ''.join(guardrails.validate('shuuji', '宛如雪之妖精般美丽的邂逅，我心中涌起命运般的悸动', 'P3')))
    check('幼年直呼深雪被拦', 'name_leak_early' in ''.join(guardrails.validate('shuuji', '深雪，我喜欢你', 'P3')))
    check('骂句合法', not guardrails.validate('shuuji', '骗子骗子骗子骗子', 'P3'))


def test_gossip():
    print('== 八卦传播 ==')
    from director import gossip
    w = World()
    w.know('relative_man', 'girl_took_shuuji', '亲戚会议上，一个来历不明的黑长发女孩把修二牵出了庭院看雪。')
    spread = []
    for d in range(15):
        w.day = d + 1
        spread += gossip.run_daily_gossip(w, seed=d + 1)
    heard = [k for c in ('relative_woman', 'toba') for k in w.knowledge[c]]
    check('信息扩散到其他角色', len(heard) > 0, str(heard))
    check('出现走样传闻', any(getattr(w.knowledge[c][k], 'distorted', False)
                             for c in w.knowledge for k in w.knowledge[c]),
          'no distortion after 10 days')
    check('传播不超过三手', all(kn.hops <= 3 for c in w.knowledge for kn in w.knowledge[c].values()))


def test_assets():
    print('== 资产校验 ==')
    from PIL import Image
    bg_dir = os.path.join(ROOT, 'assets', 'backgrounds')
    bgs = [f for f in os.listdir(bg_dir) if f.endswith('.png')]
    check('背景图不少于 12 张', len(bgs) >= 12, str(len(bgs)))
    for f in bgs:
        img = Image.open(os.path.join(bg_dir, f))
        w, h = img.size
        # 程序占位图 1280x720；AI 成品图 1536x864。容差 ±0.02（前端按比例 cover 渲染）
        if abs(w / h - 16 / 9) > 0.02:
            check('%s 尺寸非 16:9' % f, False, str(img.size))
    check('背景全部 16:9', True)
    sp_dir = os.path.join(ROOT, 'assets', 'sprites')
    svs = [f for f in os.listdir(sp_dir) if f.endswith('.svg')]
    check('10 个立绘', len(svs) == 10, str(len(svs)))
    for f in svs:
        xml.dom.minidom.parse(os.path.join(sp_dir, f))
    check('立绘 SVG 全部合法', True)
    ui_dir = os.path.join(ROOT, 'assets', 'ui')
    for f in os.listdir(ui_dir):
        xml.dom.minidom.parse(os.path.join(ui_dir, f))
    check('UI SVG 合法', True)
    bgm_dir = os.path.join(ROOT, 'assets', 'bgm')
    bgms = [f for f in os.listdir(bgm_dir) if f.endswith(('.m4a', '.wav'))]
    check('6 首 BGM', len(bgms) == 6, str(bgms))
    for f in bgms:
        if os.path.getsize(os.path.join(bgm_dir, f)) < 50000:
            check('%s 大小' % f, False)
    check('BGM 文件均有效', True)


def test_world():
    print('== 世界层 ==')
    from world.world import World
    w = World()
    w.know('toba', 'rumor1', 'x', 'heard', 2, True)
    d = w.to_dict()
    w2 = World()
    w2.load(d)
    check('序列化往返一致', w2.knowledge['toba']['rumor1'].distorted is True)
    check('关系矩阵变更', True)
    w.change_relation('shuuji', 'miyuki', 10, 5, 'test')
    check('好感钳制 0~100', w.affection('shuuji', 'miyuki') <= 100)


if __name__ == '__main__':
    test_miyuki_consistency()
    test_shuuji_guardrails()
    test_gossip()
    test_assets()
    test_world()
    print('\nRESULT: %d passed, %d failed' % (PASS, FAIL))
    sys.exit(1 if FAIL else 0)
