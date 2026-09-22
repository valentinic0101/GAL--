# -*- coding: utf-8 -*-
"""记忆流与三因子检索（C1）+ 反思与信念沉淀（C2）。

依据《资料/07_论文讲解/01_Generative_Agents》：
- 每条经历成为记忆流中的一条自然语言记录（MemoryEntry）；
- 检索分 = recency(按游戏日指数衰减) + importance(1~10) + relevance(关键词重叠)；
- 重要经历累积超过阈值（REFLECT_THRESHOLD）触发反思，生成高层洞察写回记忆流——
  「事件 → 信念」的抽象，反过来影响台词与传播。
容量控制（MemGPT 式 pressure）：超过 MAX_ENTRIES 时最旧一批合并为摘要条目。
"""
import json
import math

import settings
from agents.llm import LLM

# ---------------------------------------------------------------- 词表
TIER_HIGH = ['父母', '父亲', '母亲', '遇难', '约定', '身高', '名字', '拉勾', '小指',
             '喜欢这雪', '欢迎回家', '幸福', '深雪', 'miyuki', '写作深和雪']
TIER_MID = ['骗子', '雪仗', '清雪', '哭', '拥抱', '祭典', '钟', '柱', '雪人',
            '樱花', '摇篮', '等', '回来']
TOPIC_WORDS = sorted(set(TIER_HIGH + TIER_MID + [
    '山', '雪', '东京', '学校', '念书', '亲戚', '鸟羽', '老屋', '庭院', '站台',
    '做饭', '扑克', '泡澡', '晚安', '堆雪人', '遗产', '丫头', '传闻']))


def rule_importance(content):
    """确定性重要度打分（写入时一次成本）：高锚词 6~8、中锚词 4、日常 2。"""
    n_high = sum(1 for w in TIER_HIGH if w in content)
    n_mid = sum(1 for w in TIER_MID if w in content)
    if n_high >= 2:
        return 8
    if n_high == 1:
        return 6
    if n_mid >= 1:
        return 4
    return 2


def llm_importance(content):
    """LLM 打 1~10 分（可选档，IMPORTANCE_LLM）；失败抛异常由调用方回落。"""
    system = ('你是文字游戏的记忆打分器。判断这条记忆对角色的重要程度（1=琐碎日常，'
              '10=人生大事）。只输出一个 1~10 的整数，不要其他文字。')
    out = LLM.chat(system, '记忆：「%s」' % content, temperature=0.1, max_tokens=8)
    return max(1, min(10, int(out.strip().strip('"') or 2)))


def extract_keywords(content):
    return [w for w in TOPIC_WORDS if w in content]


# ---------------------------------------------------------------- 记忆条目
class MemoryEntry:
    def __init__(self, content, kind='episode', day=1, importance=2,
                 source='experience', keywords=None):
        self.content = content
        self.kind = kind            # episode 经历 / rumor 传闻 / insight 洞察 / summary 摘要
        self.day = day
        self.importance = importance
        self.source = source        # experience / gossip / reflection
        self.keywords = keywords or []

    def to_dict(self):
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d):
        return MemoryEntry(d['content'], d.get('kind', 'episode'), d.get('day', 1),
                           d.get('importance', 2), d.get('source', 'experience'),
                           d.get('keywords'))


# ---------------------------------------------------------------- 记忆流
class MemoryStream:
    MAX_ENTRIES = 200
    COMPRESS_CHUNK = 50
    DECAY_PER_DAY = 0.15        # 等效 Smallville 0.995/游戏小时，按本作时间密度标定

    def __init__(self):
        self.entries = []

    def add(self, content, kind='episode', day=1, source='experience',
            importance=None, keywords=None):
        if not content:
            return None
        # 同日同文去重（P8 日常循环台词等）
        if self.entries and self.entries[-1].content == content and self.entries[-1].day == day:
            return None
        if importance is None:
            if settings.IMPORTANCE_LLM and LLM.available and not LLM.rate_limited \
                    and kind == 'episode':
                try:
                    importance = llm_importance(content)
                except Exception:
                    importance = None
            if importance is None:
                importance = rule_importance(content)
        if keywords is None:
            keywords = extract_keywords(content)
        e = MemoryEntry(content, kind, day, importance, source, keywords)
        self.entries.append(e)
        while len(self.entries) > self.MAX_ENTRIES:
            self._compress()
        return e

    def _compress(self):
        """容量压力：最旧一批合并为一条摘要（细节让位，要点与关键词保留）。"""
        chunk = self.entries[:self.COMPRESS_CHUNK]
        self.entries = self.entries[self.COMPRESS_CHUNK:]
        gist = '；'.join(e.content[:16] for e in chunk[:4])
        summary = MemoryEntry(
            content='（早期记忆摘要 第%d~%d天）%s……' % (chunk[0].day, chunk[-1].day, gist),
            kind='summary', day=chunk[-1].day,
            importance=min(8, max(e.importance for e in chunk)),
            source='summary',
            keywords=sorted({k for e in chunk for k in e.keywords})[:12])
        self.entries.insert(0, summary)

    def retrieve(self, query, now_day, k=6):
        """三因子检索：recency × importance × relevance。"""
        qkw = set(extract_keywords(query or ''))
        scored = []
        for e in self.entries:
            rec = math.exp(-self.DECAY_PER_DAY * max(0, now_day - e.day))
            ekw = set(e.keywords)
            rel = (len(qkw & ekw) / len(qkw | ekw)) if (qkw and ekw) else 0.0
            score = rec + e.importance / 10.0 + 1.5 * rel
            scored.append((score, e))
        scored.sort(key=lambda x: -x[0])
        return [e for _, e in scored[:k]]

    def latest(self, n=30):
        return self.entries[-n:]

    def insights(self):
        return [e for e in self.entries if e.kind == 'insight']

    def to_dict(self):
        return [e.to_dict() for e in self.entries]

    @classmethod
    def from_list(cls, lst):
        ms = cls()
        ms.entries = [MemoryEntry.from_dict(d) for d in (lst or [])]
        return ms


# ---------------------------------------------------------------- 反思（C2）
REFLECT_THRESHOLD = 40     # 重要度累积阈值；标定：P1~P3 深雪经历约每 2~3 场景触发一次

INSIGHT_PROMPT = (
    '只输出一行 JSON：{{"insights": ["关于他人或局势的高层判断1", "…"]}}。'
    '要求：至多 2 条；不复述事件本身；绝不说出你人设中不可能知道的信息；'
    '绝不触及「是否人类、从何而来、以何为生」等核心谜团。')


def offline_insights(char, world):
    """离线模板洞察（按 flag 组合），LLM 不可用时的兜底。"""
    f = world.flags
    out = []
    if char == 'miyuki':
        if f.get('likes_snow') and f.get('snowball_fight'):
            out.append('小修嘴上凶得很，其实一点都不讨厌这里——大概，也不讨厌我。')
        if f.get('height_marked') and f.get('left_town'):
            out.append('约定这种东西，对人类的孩子来说，是要用整整一年去遵守的。')
        if f.get('reunion_done'):
            out.append('这次回来，小修的眼睛里有了以前没有的东西——他不再是那个孩子了。')
    elif char in ('relative_man', 'relative_woman'):
        if f.get('met_miyuki') or f.get('comforted'):
            out.append('那孩子回老屋，怕不只是过寒假——遗产和老屋的事，没那么简单。')
        if f.get('left_town'):
            out.append('老屋那边有个来路不明的丫头，这事得跟其他人通个气。')
    elif char == 'toba':
        if f.get('met_miyuki'):
            out.append('老屋那边的事，瞒不了多久了。')
    return out[:2]


def reflect(char, world, memory):
    """生成 1~2 条洞察写回记忆流（importance=9，检索时恒靠前）。返回洞察列表。"""
    important = [m for m in memory.latest(30) if m.importance >= 5]
    insights = []
    if LLM.available and not LLM.rate_limited:
        try:
            from agents.personas import persona_card
            prompt = (persona_card(char)
                      + '\n\n【你最近的重要经历】\n'
                      + '\n'.join('- ' + m.content for m in important[:12])
                      + '\n\n' + INSIGHT_PROMPT)
            out = LLM.chat(prompt, '请反思并输出洞察。', temperature=0.5, max_tokens=200)
            obj = json.loads(out[out.find('{'):out.rfind('}') + 1])
            insights = [str(s) for s in obj.get('insights', [])][:2]
        except Exception:
            insights = []
    if not insights:
        insights = offline_insights(char, world)
    # 深雪的洞察必须过谜团锁（防"反思越界泄谜"）
    if char == 'miyuki':
        from agents import guardrails
        clean = []
        for s in insights:
            bad = any(k in i for i in guardrails.check_miyuki(s, world.phase)
                      for k in ('mystery', 'identity', 'name_leak', 'forbidden'))
            if not bad:
                clean.append(s)
        insights = clean
    for s in insights:
        memory.add(s, kind='insight', day=world.day, source='reflection',
                   importance=9, keywords=extract_keywords(s))
    return insights
