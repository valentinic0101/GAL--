# -*- coding: utf-8 -*-
"""八卦传播引擎：每个游戏日结束时离线模拟一次。

依据《架构设计V1.md》§2.2：A 与 B 有社交接触时，A 以概率把信息传给 B，
概率与走样由性格过滤器决定，产物是「传闻条目」写入知识库。
传播的乐趣在于后果回流到玩家（NPC 台词引用传闻）。

C2：持有「老屋/遗产」类信念（洞察）的角色传播与扭曲概率提升——信念放大传播。
C8：传闻带强度（strength），每日 ×0.9 衰减；强度过低停传；
    LLM 可用时扭曲文案由小模型即时生成（失败回落固定模板）。
"""
import random

from agents.llm import LLM

# 性格过滤器：who -> (传播概率, 扭曲倾向描述)
PERSONALITY_FILTERS = {
    'relative_man':   dict(p=0.75, distort='push_away',   style='拐弯抹角、互相推诿'),
    'relative_woman': dict(p=0.70, distort='exaggerate',  style='欲言又止、添油加醋'),
    'toba':           dict(p=0.30, distort='none',        style='沉默寡言、原样转述'),
    'miyuki':         dict(p=0.05, distort='none',        style='几乎不与人往来'),
    'shuuji':         dict(p=0.20, distort='none',        style='寡言的少年'),
}

# 社交接触网：每日可能接触的边
CONTACT_EDGES = [
    ('relative_man', 'relative_woman', 0.8),
    ('relative_man', 'toba', 0.35),
    ('relative_woman', 'relative_man', 0.8),
    ('relative_woman', 'toba', 0.30),
    ('toba', 'relative_man', 0.35),
    ('toba', 'relative_woman', 0.30),
]

# 扭曲模板：distort 类型 -> 生成函数
DISTORTIONS = {
    'push_away': [
        '听说――老屋那边，怕是有点不干净。',
        '那孩子一个人守着空屋，真是不好办啊――',
        '遗产的事，怕是要出问题啊――',
    ],
    'exaggerate': [
        '听说了吗，老屋那边闹妖怪，还有个不知道哪来的丫头出入呢。',
        '那孩子怕是撞了什么不干净的东西，都不太对劲了。',
        '老屋的灯半夜会亮，你敢信？',
    ],
    'none': [],
}


def _belief_boost(world, char):
    """C2：角色是否持有「老屋/遗产/丫头」类信念（洞察）——是则放大传播。"""
    try:
        return any(('老屋' in m.content or '遗产' in m.content or '丫头' in m.content)
                   for m in world.memory[char].insights())
    except Exception:
        return False


def llm_distort(content, style):
    """C8：LLM 即时扭曲（保持事实不走样，只换口吻与添删细节）。失败抛异常由调用方回落。"""
    prompt = ('把下面这句话改写成「%s」口吻的转述。只输出改写后的一句话；'
              '可以添油加醋或拐弯抹角，但不得出现原句没有的新事实。原句：「%s」' % (style, content))
    out = LLM.chat('你是小镇闲话转述器。', prompt, temperature=0.8, max_tokens=60)
    return out.strip().splitlines()[0][:80]


def run_daily_gossip(world, seed=None, use_llm=False):
    """跑一遍当日的八卦模拟，返回新写入的传闻条目列表。"""
    new_items = []
    rnd = random.Random(seed if seed is not None else world.day * 131)
    for a, b, contact_p in CONTACT_EDGES:
        if rnd.random() > contact_p:
            continue
        fa = PERSONALITY_FILTERS[a]
        boost = _belief_boost(world, a)
        p = min(0.95, fa['p'] + (0.15 if boost else 0.0))
        for key, kn in list(world.knowledge[a].items()):
            if kn.hops >= 3:
                continue  # 三手以上无人再传
            if kn.strength < 0.2:
                continue  # C8：传闻已沉寂
            if rnd.random() > p:
                continue
            if world.knows(b, key) and world.knowledge[b][key].hops <= kn.hops:
                continue
            # 传播 + 可能走样（一手传播也可能经性格过滤器扭曲，
            # 如架构示例：亲戚电话串门把「雪衣少女」扭曲成「老屋不干净」）
            dist_p = 0.55 if kn.hops >= 1 else 0.35
            if boost:
                dist_p = min(0.9, dist_p + 0.2)
            content, distorted = kn.content, kn.distorted
            if fa['distort'] != 'none' and rnd.random() < dist_p:
                distorted = True
                content = None
                if use_llm and LLM.available and not LLM.rate_limited:
                    try:
                        content = llm_distort(kn.content, fa['style'])
                    except Exception:
                        content = None
                if not content:
                    content = rnd.choice(DISTORTIONS[fa['distort']])
            world.know(b, key, content, source='heard', hops=kn.hops + 1, distorted=distorted)
            new_items.append({'from': a, 'to': b, 'key': key, 'content': content,
                              'hops': kn.hops + 1, 'distorted': distorted})
            world.emit('gossip', {'from': a, 'to': b, 'key': key, 'content': content})
    return new_items


def rumor_hooks(char_id, world):
    """NPC 对话时引用的传闻（后果回流）。"""
    hooks = []
    for key, kn in world.knowledge[char_id].items():
        if kn.source == 'heard':
            hooks.append(kn.content)
    return hooks


def rumors_for_prompt(char_id, world):
    """C8：给 agent prompt 的「镇上最近流传」段（强度 ≥0.5 的听说条目）。"""
    return [kn.content for kn in world.knowledge[char_id].values()
            if kn.source == 'heard' and kn.strength >= 0.5]


def hot_rumor(world):
    """当前最热的传闻文本（无则 None）。"""
    best, best_s = None, 0.0
    for ks in world.knowledge.values():
        for kn in ks.values():
            if kn.source == 'heard' and kn.strength > best_s:
                best, best_s = kn.content, kn.strength
    return best


def strengthen(world, char_id, delta=0.1):
    """传闻被 NPC 引用后升温（C8 后果回流）。"""
    for kn in world.knowledge[char_id].values():
        if kn.source == 'heard':
            kn.strength = min(2.0, kn.strength + delta)
