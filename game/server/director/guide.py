# -*- coding: utf-8 -*-
"""C7：导演引导策略菜单——玩家滞留时选择一种 diegetic（世界内自洽）引导。

依据《资料/07_论文讲解/24_SENNA》：信息钩子 / NPC 影响 / 世界后果 / 时机调整 四类
diegetic 策略在不牺牲自主感与沉浸感的前提下维持叙事连贯；硬推（hard denial）
体验最差，只作最后降级。依据《资料/07_论文讲解/23_互动戏剧》：剧情推进只做有界介入。
"""
import settings
from director import gossip

# 信息钩子文案：下一场景的"钩子"写进世界（与 ATTRACTORS 前置条件对应）
HOOKS = {
    'P2': '檐廊外，雪把庭院铺得更厚了。铲子还靠在门边。',
    'P3': '天色暗得早。老屋的门虚掩着，屋里比早上更冷了。',
    'P4': '参道方向，隐约传来木鼓试音的声音——祭典快到了。',
    'P5': '炉火该添炭了。姐姐说，年末要替你量量身高。',
    'P6': '站房的钟指向中午——今天有班车。',
    'P8': '炉上坐着水，快开了。日子像雪一样，一层层过去。',
    'P9': '行李还没收拾，可归期就在明天。',
    'P10': '晨光落在门前，两个雪人的影子被拉得很长。',
    'P11': '日历撕到了寒假的第一页。',
    'P12B': '回东京的日子，就定在明天。',
}

# 仅差地点条件的吸引子（与 director.ATTRACTORS 的地点分支保持同步）：
# 其余条件满足而玩家滞留别处时，允许"事件上门"（时机调整型）。
FORCE_GATED = {
    'P5': lambda w: w.flags.get('festival_done') and w.affection('shuuji', 'miyuki') >= 45,
    'P9': lambda w: w.flags.get('daily_life'),
}


def guide(director):
    """返回 None 或 {'strategy', 'note', 'payload'}。只在滞留（idle_steps≥3）时触发。"""
    if not settings.GUIDE_V2:
        return None
    d, w = director, director.world
    nxt = d.route()
    if nxt is None and force_candidate(d) is None:
        return None            # 既无完整可进入后继，也无"仅差地点"的后继
    if d.idle_steps < 3:
        return None

    # ① NPC 影响型：谜团话头被反复试探时，深雪主动出现把话头带走
    #    （仅限她不会自动在场的地点：老屋区域 present_chars 本就包含她）
    if d.mystery_probes >= 2 and 'miyuki' not in d.present_chars() \
            and w.flags.get('met_miyuki') \
            and w.location in ('fields', 'station', 'town_street'):
        d.mystery_probes = 0
        return {'strategy': 'npc_redirect',
                'note': '身后传来踏雪声——她提着铲子站在这里，歪了歪头：「呐――小修，发什么呆呢？」',
                'payload': {'chars': ['miyuki']}}

    # ② 时机调整型：仅差地点的吸引子已就绪 → 事件上门
    force = force_candidate(d)
    if force:
        d.pending_force = force
        return {'strategy': 'event_comes',
                'note': '「呐――」她拍了拍身上的雪，「走吧，回老屋。有些事，想在那里跟你说。」',
                'payload': {}}
    # ③ 世界后果型：滞留较久 → 世界记住并回应（传闻余波 / 时间压力）
    if d.idle_steps >= 6:
        rumor = gossip.hot_rumor(w)
        if rumor:
            return {'strategy': 'world_consequence',
                    'note': '镇上有人在议论：「%s」' % rumor, 'payload': {}}
        return {'strategy': 'world_consequence',
                'note': '再待下去，冬天就要过去了一截。', 'payload': {}}

    # ④ 信息钩子型（默认）：把下一场景的钩子写进环境
    hook = HOOKS.get(nxt)
    if hook:
        return {'strategy': 'info_hook', 'note': hook, 'payload': {}}
    return None


def force_candidate(d):
    """返回"仅差地点"的可进入场景 ID，否则 None。"""
    w = d.world
    if w.phase not in ('P4', 'P8'):
        return None
    if w.location == 'oldhouse_in':
        return None
    for sid, cond in FORCE_GATED.items():
        if cond(w):
            return sid
    return None
