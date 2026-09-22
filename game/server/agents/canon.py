# -*- coding: utf-8 -*-
"""正典台词检索（C4）：从剧本的 line 节拍自动构建 few-shot 语料。

- 语料单一来源 = scenes/script.py 汇总的 SCENES（节点数据分片在 trunk.py / branches.py，
  与剧本永远同步，无需手工维护）；
- HOLDOUT 保留名场面台词不进检索库，专供评测（C5）做 held-out 验证，防"背答案"；
- 意图匹配复用 rule_engine.classify，离线可用。
"""
from scenes.script import SCENES
from agents import rule_engine

# 保留台词（scene, say）：名字揭示 / 身份宣言 / 名场面——不进 few-shot
HOLDOUT = {
    ('P6', 'miyuki'),
    ('P6', '写作深和雪两个字，miyuki'),
    ('P3', '你的姐姐啊'),
    ('P1', '呐，你喜欢雪吗？'),
    ('P1', '……我喜欢这雪'),
    ('P7', '你长高了好多啊。但是，还是没有姐姐高'),
    ('P10', '会开花啊，开花时好漂亮的'),
    ('P12B', '觉得现在幸福吗……？'),
    ('E_SPRING', '因为约好了呀'),
}


def _build():
    corpus = {}
    for sid, sc in SCENES.items():
        entries = []
        for b in sc['beats']:
            if b.get('type') == 'line' and b.get('say'):
                say = b['say']
                if (sid, say) in HOLDOUT:
                    continue
                entries.append({'scene': sid, 'who': b.get('who'), 'say': say,
                                'intents': frozenset(rule_engine.classify(say))})
        if entries:
            corpus[sid] = entries
    return corpus


CANON = _build()
_GENERIC = [e for entries in CANON.values() for e in entries]


def retrieve_canon(scene_id, text, char_id=None, k=2):
    """按场景+意图+角色检索 k 条正典台词；无匹配返回空列表。"""
    intents = set(rule_engine.classify(text or ''))
    pool = list(CANON.get(scene_id, []))
    if len(pool) < 4:                       # 幕间等场景语料少：并入全局池
        pool = pool + [e for e in _GENERIC if e['scene'] != scene_id]

    def score(e):
        s = 0
        if e['scene'] == scene_id:
            s += 2
        if char_id and e['who'] == char_id:
            s += 1
        s += 2 * len(intents & set(e['intents']))
        return s

    ranked = sorted(pool, key=lambda e: (-score(e), len(e['say'])))
    return [e['say'] for e in ranked[:k] if score(e) > 0]
