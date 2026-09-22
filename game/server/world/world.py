# -*- coding: utf-8 -*-
"""雪国 GALGAME 引擎 —— 世界层。

事实库（不变量+动态状态）/ 场景图 / 每角色知识库 / 关系矩阵 / 事件总线。
设计依据：《架构设计V1.md》第二节。全部状态可序列化（事件溯源存档）。
"""
import time
import uuid
from collections import defaultdict

from agents.memory import MemoryStream

# ---------------------------------------------------------------- 不变量（物理常量）
INVARIANTS = {
    'snow_always': '雪始终在下，从未停歇。',
    'clock_stopped': '老屋的挂钟多年前就停摆，指针停在 4 时 49 分。',
    'station_empty': '上山站的站台永远空无一人，仿佛不属于现实。',
    'miyuki_taller': '深雪始终比修二高（初遇明显，三年后依旧「还是没有姐姐高」）。',
    'mountains_demonic': '群山是被神社供奉的灵山，古为异界，具有魔性，每年吞噬人命。',
    'old_house_dying': '父母死后老屋无人居住，仿佛正渐渐地死去。',
}

# ---------------------------------------------------------------- 场景图（地点邻接）
LOCATIONS = {
    'station':      {'name': '上山站',   'adjacent': ['town_street', 'fields'],       'bg': 'bg_station_day.png'},
    'fields':       {'name': '田间小路', 'adjacent': ['station', 'oldhouse_front'],   'bg': 'bg_mountains.png'},
    'town_street':  {'name': '小镇街道', 'adjacent': ['station', 'toba_home', 'shrine_road'], 'bg': 'bg_town_street.png'},
    'toba_home':    {'name': '鸟羽老人家', 'adjacent': ['town_street'],               'bg': 'bg_toba_home.png'},
    'shrine_road':  {'name': '冬祭参道', 'adjacent': ['town_street', 'shrine'],       'bg': 'bg_town_night_festival.png'},
    'shrine':       {'name': '神社',     'adjacent': ['shrine_road'],                 'bg': 'bg_shrine_night.png'},
    'oldhouse_front': {'name': '老屋门前', 'adjacent': ['fields', 'courtyard'],       'bg': 'bg_courtyard.png'},
    'courtyard':    {'name': '老屋庭院', 'adjacent': ['oldhouse_front', 'oldhouse_in'], 'bg': 'bg_courtyard.png'},
    'oldhouse_in':  {'name': '老屋·客厅', 'adjacent': ['courtyard', 'oldhouse_corridor'], 'bg': 'bg_oldhouse_room.png'},
    'oldhouse_corridor': {'name': '老屋·走廊', 'adjacent': ['oldhouse_in'],           'bg': 'bg_oldhouse_corridor.png'},
    'mountains':    {'name': '群山',     'adjacent': [],                             'bg': 'bg_mountains.png'},
    'blizzard':     {'name': '暴风雪山中', 'adjacent': [],                           'bg': 'bg_mountains_blizzard.png'},
}

CHARACTERS = ['shuuji', 'miyuki', 'toba', 'relative_man', 'relative_woman', 'father', 'mother', 'yukihime']

CHAR_NAME = {
    'shuuji': '修二', 'miyuki': '深雪', 'toba': '鸟羽老人',
    'relative_man': '叔父', 'relative_woman': '婶婶',
    'father': '父亲', 'mother': '母亲', 'yukihime': '？？？',
}


class Knowledge:
    """一条知识：谁知道、从谁听来、几手、是否走样、强度（C8 传闻热度）。"""

    def __init__(self, key, content, source='witness', hops=0, distorted=False, strength=1.0):
        self.key = key
        self.content = content
        self.source = source      # witness 亲眼 / heard 听说
        self.hops = hops          # 传播了几手
        self.distorted = distorted
        self.strength = strength  # 0~2：>1.3 沸扬 / <0.3 沉寂；每日 ×0.9 衰减

    def to_dict(self):
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d):
        return Knowledge(d['key'], d['content'], d['source'], d['hops'], d['distorted'],
                         d.get('strength', 1.0))


class Relation:
    """关系矩阵条目：好感/信任 0~100 + 变更日志。"""

    def __init__(self, a, b):
        self.a, self.b = a, b
        self.affection = 50
        self.trust = 50
        self.log = []

    def change(self, affection=0, trust=0, reason=''):
        self.affection = max(0, min(100, self.affection + affection))
        self.trust = max(0, min(100, self.trust + trust))
        if affection or trust or reason:
            self.log.append({'da': affection, 'dt': trust, 'reason': reason})

    def to_dict(self):
        return {'a': self.a, 'b': self.b, 'affection': self.affection,
                'trust': self.trust, 'log': self.log}


class WorldEvent:
    def __init__(self, kind, data):
        self.id = str(uuid.uuid4())
        self.t = time.time()
        self.kind = kind     # player_say / player_move / scene_line / plot_advance / gossip ...
        self.data = data

    def to_dict(self):
        return {'id': self.id, 't': self.t, 'kind': self.kind, 'data': self.data}


class World:
    """世界状态：事实库 + 知识库 + 关系矩阵 + 事件总线。"""

    def __init__(self):
        self.invariants = dict(INVARIANTS)
        self.day = 1                     # 游戏内天数
        self.phase = 'P1'                # 当前剧情阶段
        self.location = 'oldhouse_in'    # 玩家所在场景
        self.time_slot = 'day'           # day / evening / night
        self.season_pressure = 0         # 叙事压力（季节推进/冬祭倒计时）
        self.festival_countdown = 3      # 距冬祭天数
        self.flags = {}                  # 通用旗标
        self.knowledge = {c: {} for c in CHARACTERS}   # char -> {key: Knowledge}
        self.relations = {}
        for i, a in enumerate(CHARACTERS):
            for b in CHARACTERS[i + 1:]:
                r = Relation(a, b)
                self.relations[(a, b)] = r
        self.events = []                 # 事件溯源日志
        # 深雪好感单独常驻快捷读取
        self.miyuki_affection_extra = 0
        # 三轴（多结局分叉打分）：羁绊/执念/现世，见《资料/02_设定与设计/多结局分支设计.md》
        self.axes = {'bond': 20, 'obsession': 15, 'worldly': 15}
        # C1：每角色记忆流；C2：反思能量槽（重要度累积，达阈值触发反思）
        self.memory = {c: MemoryStream() for c in CHARACTERS}
        self.reflect_points = {c: 0.0 for c in CHARACTERS}

    # ---------------- 事件总线
    def emit(self, kind, data):
        ev = WorldEvent(kind, data)
        self.events.append(ev)
        return ev

    # ---------------- 知识
    def know(self, char, key, content, source='witness', hops=0, distorted=False):
        strength = 1.2 if source == 'witness' else 1.0    # C8：亲历比听说更有热度
        self.knowledge[char][key] = Knowledge(key, content, source, hops, distorted, strength)
        self.emit('knowledge', {'char': char, 'key': key})
        # C1：知识条目镜像进记忆流（rumor/episode）
        self.memory[char].add(content, kind='rumor' if source == 'heard' else 'episode',
                              day=self.day, source='gossip' if source == 'heard' else 'experience',
                              importance=4 if source == 'heard' else 6)

    def memory_retrieve(self, char, query, k=6):
        """C1 对外入口：返回该角色与 query 最相关的 k 条记忆文本。"""
        return [e.content for e in self.memory[char].retrieve(query, self.day, k)]

    def tick_rumors(self):
        """C8：每日传闻强度衰减（等待/过夜时调用）。"""
        for ks in self.knowledge.values():
            for kn in ks.values():
                kn.strength = max(0.0, kn.strength * 0.9)

    def knows(self, char, key):
        return key in self.knowledge[char]

    def knowledge_of(self, char):
        return {k: v.to_dict() for k, v in self.knowledge[char].items()}

    # ---------------- 关系
    def rel(self, a, b):
        key = (a, b) if (a, b) in self.relations else (b, a)
        return self.relations[key]

    def change_relation(self, a, b, affection=0, trust=0, reason=''):
        self.rel(a, b).change(affection, trust, reason)
        self.emit('relation', {'a': a, 'b': b, 'da': affection, 'dt': trust, 'reason': reason})

    def affection(self, a, b):
        base = self.rel(a, b).affection
        if {a, b} == {'shuuji', 'miyuki'}:
            return max(0, min(100, base + self.miyuki_affection_extra))
        return base

    # ---------------- 三轴（分叉打分）
    def add_axis(self, key, delta, reason=''):
        if key not in self.axes or not delta:
            return
        old = self.axes[key]
        self.axes[key] = max(0, min(100, old + delta))
        if self.axes[key] != old:
            self.emit('axis_change', {'axis': key, 'delta': delta,
                                      'value': self.axes[key], 'reason': reason})

    # ---------------- 序列化（存档=状态快照+事件日志）
    def to_dict(self):
        return {
            'day': self.day, 'phase': self.phase, 'location': self.location,
            'time_slot': self.time_slot, 'season_pressure': self.season_pressure,
            'festival_countdown': self.festival_countdown, 'flags': self.flags,
            'axes': self.axes,
            'knowledge': {c: {k: v.to_dict() for k, v in ks.items()} for c, ks in self.knowledge.items()},
            'relations': [r.to_dict() for r in self.relations.values()],
            'miyuki_affection_extra': self.miyuki_affection_extra,
            'memory': {c: ms.to_dict() for c, ms in self.memory.items()},
            'reflect_points': dict(self.reflect_points),
        }

    def load(self, d):
        self.day = d['day']; self.phase = d['phase']; self.location = d['location']
        self.time_slot = d['time_slot']; self.season_pressure = d['season_pressure']
        self.festival_countdown = d['festival_countdown']; self.flags = d.get('flags', {})
        self.knowledge = {c: {} for c in CHARACTERS}
        for c, ks in d['knowledge'].items():
            self.knowledge[c] = {k: Knowledge.from_dict(v) for k, v in ks.items()}
        for rd in d['relations']:
            r = self.relations[(rd['a'], rd['b'])]
            r.affection = rd['affection']; r.trust = rd['trust']; r.log = rd['log']
        self.miyuki_affection_extra = d.get('miyuki_affection_extra', 0)
        axes = d.get('axes') or {}
        self.axes = {'bond': axes.get('bond', 20),
                     'obsession': axes.get('obsession', 15),
                     'worldly': axes.get('worldly', 15)}   # 旧存档兼容默认值
        # C1/C2：记忆流与反思能量槽（旧存档缺省为空）
        self.memory = {c: MemoryStream.from_list((d.get('memory') or {}).get(c))
                       for c in CHARACTERS}
        rp = d.get('reflect_points') or {}
        self.reflect_points = {c: float(rp.get(c, 0.0)) for c in CHARACTERS}
