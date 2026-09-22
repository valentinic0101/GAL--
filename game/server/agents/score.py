# -*- coding: utf-8 -*-
"""三轴打分器：从修二（玩家）的自由输入中量化 心之去向 → 分叉依据。

- LLM 可用时：严格 JSON 输出三轴增量（每轴 -3..+3），失败立即回落。
- 离线/失败：关键词规则打分（确定性，供自动化测试与无网环境）。
设计依据：《资料/02_设定与设计/多结局分支设计.md》第二节。
"""
import json
import re

from agents.llm import LLM

AXES = ('bond', 'obsession', 'worldly')

# 关键词规则（离线兜底；同时是测试的确定性泵轴手段）
OBSESSION_WORDS = ['父亲', '母亲', '爸爸', '妈妈', '父母', '群山', '山里', '山中', '深山',
                   '遇难', '雪女', '妖怪', '幽灵', '谜', '真相', '呼唤', '山中异界', '白衣']
BOND_WORDS = ['姐姐', '喜欢', '一起', '留下', '陪你', '想你', '幸福', '约定', '回来',
              '深雪', '拉勾', '小指', '堆雪人', '扑克', '晚安', '做饭', '清雪', '温柔']
WORLDLY_WORDS = ['东京', '学校', '升学', '考试', '功课', '同学', '朋友', '将来', '工作',
                 '开学', '念书', '回去', '教室', '车站', '离开', '现实']


def rule_score(text):
    """确定性关键词打分：每命中一词 +2，单轴每次调用封顶 ±6。"""
    deltas = {'bond': 0, 'obsession': 0, 'worldly': 0}
    for axis, words in (('obsession', OBSESSION_WORDS), ('bond', BOND_WORDS),
                        ('worldly', WORLDLY_WORDS)):
        n = sum(1 for w in words if w in text)
        deltas[axis] = min(6, 2 * n)
    return deltas


def llm_score(text):
    """LLM 打分：三轴增量 JSON。失败抛异常由调用方回落。"""
    system = ('你是文字游戏的隐含打分器。玩家扮演少年修二。判断玩家的这句话让他的内心'
              '偏向哪个方向：bond=对姐姐深雪的依恋与羁绊；obsession=对遇难父母与魔性群山的执念；'
              'worldly=对东京学业与现实生活的牵挂。'
              '只输出一行 JSON：{"bond": 整数, "obsession": 整数, "worldly": 整数}，'
              '每个值在 -3 到 3 之间（0 表示无关）。不要输出任何其他文字。')
    out = LLM.chat(system, '玩家说：「%s」' % text, temperature=0.2, max_tokens=80)
    obj = json.loads(out[out.find('{'):out.rfind('}') + 1])
    deltas = {}
    for k in AXES:
        v = int(re.findall(r'-?\d+', str(obj.get(k, 0)))[0]) if obj.get(k) is not None else 0
        deltas[k] = max(-3, min(3, v))
    return deltas


def score_axes(text):
    """对外入口：优先 LLM，失败回落规则。返回 {'bond':d,'obsession':d,'worldly':d, 'src':..}"""
    text = (text or '').strip()
    if not text:
        return {'bond': 0, 'obsession': 0, 'worldly': 0, 'src': 'none'}
    if LLM.available and not LLM.rate_limited:
        try:
            d = llm_score(text)
            d['src'] = 'llm'
            return d
        except Exception:
            pass
    d = rule_score(text)
    d['src'] = 'rules'
    return d


# 打分反馈：修二的内心独白（把"这句话把我推向了哪里"可视化）
INNER_VOICE = {
    'bond': ['（……心里某处，已经被这个人的名字占满了。）',
             '（比起车站的方向，我更想看清她的侧脸。）',
             '（胸腔里那点温度，是雪压不住的。）'],
    'obsession': ['（风雪的深处，好像有什么在呼唤。父亲……母亲……）',
                  '（那片白，究竟是死者的国度，还是归处。）',
                  '（山不说话。可我总觉得，它在等我。）'],
    'worldly': ['（东京的教室、开学、考试……时间的流向和我拴在一起。）',
                '（我不能一辈子待在雪里。人，是要往前走的。）',
                '（故乡虽好，可我的未来不在雪里。）'],
    'neutral': ['（雪一直下。话落在雪上，没有声音。）',
                '（说了这句话，自己也没料到。）'],
}


def inner_voice(deltas, text=''):
    """按主导轴给一句内心独白；以输入文本哈希轮换，避免重复同一句。"""
    best, val = 'neutral', 0
    for k in AXES:
        if deltas.get(k, 0) > val:
            best, val = k, deltas[k]
    pool = INNER_VOICE[best]
    return pool[sum(map(ord, text or '')) % len(pool)]
