# -*- coding: utf-8 -*-
"""导演层（Director）：剧情吸引子 + 分支后继图（SUCCESSORS）+ 叙事压力。

- 主干 P1~P10 与《人物圣经》时间线一致；P10 之后进入分支层，收束到四结局之一。
- 自由度在过程：玩家自由行动，导演计算叙事压力，在合适时机把事件推到玩家面前。
- 分叉依据三轴（bond 羁绊 / obsession 执念 / worldly 现世），阈值见
  《设计文档/多结局分支设计.md》。SUCCESSORS 表保证：任何状态恰好一个可进入的后继，
  或到达吸收态结局——每条线必收束。
"""
from world.world import LOCATIONS
from agents import rule_engine
import re

# 吸引子前置条件表：phase → cond(world)
ATTRACTORS = {
    'P1':  lambda w: True,                                                              # 开场即入
    'P2':  lambda w: w.flags.get('met_miyuki') and not w.flags.get('snow_cleared'),
    'P3':  lambda w: w.flags.get('comforted') and w.day >= 3,
    'P4':  lambda w: w.flags.get('snowball_fight') and w.festival_countdown <= 0,
    'P5':  lambda w: w.flags.get('festival_done') and w.affection('shuuji', 'miyuki') >= 45 and w.location == 'oldhouse_in',
    'P6':  lambda w: w.flags.get('height_marked'),
    'P7':  lambda w: w.flags.get('left_town') or (w.phase == 'P7'),
    'P8':  lambda w: w.flags.get('reunion_done') and w.location in ('oldhouse_in', 'courtyard'),
    'P9':  lambda w: w.flags.get('daily_life') and w.location == 'oldhouse_in',
    'P10': lambda w: w.flags.get('height_remarked'),
    # ---------------- 分支层 ----------------
    'P11':      lambda w: w.flags.get('left_again'),                                    # 一年后的岔路（D0）
    'P12M':     lambda w: w.flags.get('chose_mountains') and w.axes['obsession'] >= 35,  # 入山线
    'P12B':     lambda w: w.flags.get('chose_return'),                                  # 归省线（默认路）
    'E_FAR':    lambda w: w.flags.get('happiness_asked'),                               # 原作向兜底
    'E_TOKYO':  lambda w: w.flags.get('stayed_tokyo'),                                  # 留京线（并入 END_FAR）
    'E_STAY':   lambda w: w.flags.get('chose_stay') and w.axes['bond'] >= 50,           # 留守线
    'E_SPRING': lambda w: w.flags.get('chose_spring') and w.axes['bond'] >= 50 and w.axes['obsession'] < 35,  # 真结局
    'P0':       lambda w: True,                                                         # 入山终幕
}

# 后继表：sid → 按序求值的候选后继（第一个 cond 通过者生效；空表 = 吸收态结局）
SUCCESSORS = {
    'P1': ['P2'], 'P2': ['P3'], 'P3': ['P4'], 'P4': ['P5'], 'P5': ['P6'],
    'P6': ['P7'], 'P7': ['P8'], 'P8': ['P9'], 'P9': ['P10'], 'P10': ['P11'],
    'P11': ['P12M', 'P12B', 'E_TOKYO'],
    'P12M': ['P0'],
    'P12B': ['E_STAY', 'E_SPRING', 'E_FAR'],
    'P0': [], 'E_STAY': [], 'E_SPRING': [], 'E_FAR': [], 'E_TOKYO': [],
}

# 展示用相序（引擎 HUD/存档兼容保留；推进一律走 SUCCESSORS）
PHASE_ORDER = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10',
               'P11', 'P12B', 'P12M', 'E_STAY', 'E_SPRING', 'E_FAR', 'E_TOKYO', 'P0']

# 吸收态：结局场景（进入后 flags['ending'] 置 END_*，导演不再推进）
ENDINGS = {'P0': 'END_SNOW', 'E_STAY': 'END_STAY', 'E_SPRING': 'END_SPRING',
           'E_FAR': 'END_FAR', 'E_TOKYO': 'END_FAR'}

ENDINGS_TITLE = {
    'END_SNOW': '白之彼方', 'END_STAY': '炉火与春讯',
    'END_SPRING': '等到花开', 'END_FAR': '两行足迹',
}
# 同一结局 ID 下按入场场景给的副标题（结局卡与提示用）
ENDING_SUBTITLE = {'E_TOKYO': '东来的雪'}

# 轴值门控条件（剧本选项 requires 字段用同一语法："axis:xxx>=n" / "axis:xxx<n" / "flag:name"）
THRESHOLDS = {'bond_stay': 50, 'obsession_mountain': 35, 'obsession_spring': 35}


def eval_cond(cond, w):
    """求值门控条件表达式：flag:xx / axis:k>=n / axis:k<n / default。"""
    if not cond or cond == 'default':
        return True
    if cond.startswith('flag:'):
        return bool(w.flags.get(cond[5:]))
    if cond.startswith('axis:'):
        expr = cond[5:]
        m = re.match(r'(\w+)\s*(>=|<=|<|>)\s*(\d+)', expr)
        if not m:
            return False
        key, op, num = m.group(1), m.group(2), int(m.group(3))
        v = w.axes.get(key, 0)
        return {'>=': v >= num, '<=': v <= num, '<': v < num, '>': v > num}[op]
    return False


class Director:
    def __init__(self, world):
        self.world = world
        self.pressure = {}   # phase -> 压力值
        # ---- C7 引导特征（玩家滞留/跑题行为采集）----
        self.idle_steps = 0        # 距上次剧情推进的幕间行动数
        self.location_stay = {}    # location -> 连续幕间行动次数
        self.mystery_probes = 0    # 谜团类交谈次数
        self.extra_present = []    # npc_redirect 一次性登台名单（frame 构建时并入）
        self.pending_force = None  # event_comes：仅差地点的待进入场景

    def on_interlude(self, action):
        """幕间行动计数（C7 行为特征采集）。"""
        self.idle_steps += 1
        loc = self.world.location
        self.location_stay[loc] = self.location_stay.get(loc, 0) + 1
        if action == 'wait':
            self.idle_steps += 1     # 干等更"拖"

    def note_mystery_probe(self):
        self.mystery_probes += 1

    def reset_progress(self):
        """进入新场景时清零引导特征。"""
        self.idle_steps = 0
        self.location_stay = {}
        self.mystery_probes = 0
        self.extra_present = []
        self.pending_force = None

    # ---------------- 后继求解：按序求值，返回全部可进入的候选
    def next_candidates(self, sid=None):
        sid = sid or self.world.phase
        return [s for s in SUCCESSORS.get(sid, []) if ATTRACTORS[s](self.world)]

    def route(self, sid=None):
        """确定性路由：当前状态的第一个可用后继；吸收态返回 None。"""
        cands = self.next_candidates(sid)
        return cands[0] if cands else None

    # ---------------- 叙事压力计算
    def compute_pressure(self):
        w = self.world
        self.pressure = {}
        for nxt in self.next_candidates():
            base = 50
            base += min(40, w.season_pressure)
            if nxt == 'P4':
                base += max(0, 20 - w.festival_countdown * 5)
            self.pressure[nxt] = base
        return self.pressure

    # ---------------- 是否应推进剧情
    def should_advance(self):
        self.compute_pressure()
        for nxt in self.next_candidates():
            if self.pressure.get(nxt, 0) >= 70:
                return nxt
        return None

    # ---------------- 场景描述（给 Agent 拼装用）
    def scene_desc(self):
        w = self.world
        loc = LOCATIONS[w.location]['name']
        tod = {'day': '白天', 'evening': '傍晚', 'night': '夜晚'}[w.time_slot]
        return f'{w.phase}阶段·第{w.day}天·{tod}·{loc}。雪一直下着。在场人物：{self.present_chars()}。'

    def present_chars(self):
        w = self.world
        chars = ['shuuji']
        if w.location in ('oldhouse_in', 'oldhouse_corridor', 'courtyard', 'oldhouse_front'):
            if w.flags.get('met_miyuki'):
                chars.append('miyuki')
        if w.location == 'toba_home':
            chars.append('toba')
        if w.phase == 'P1' and w.flags.get('relatives_meeting', True):
            chars += ['relative_man', 'relative_woman']
        # C7：npc_redirect 的一次性登台
        for c in self.extra_present:
            if c not in chars:
                chars.append(c)
        return chars

    # ---------------- 旁白选择
    def narrate(self, tag=None):
        return rule_engine.narrate(tag)
