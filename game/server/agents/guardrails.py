# -*- coding: utf-8 -*-
"""护栏层：风格校验器 + 谜团锁校验 + 阶段硬锁（C3）+ 违规解释（C4）。

依据《人物设定与关系总览.md》§5（双 AI 对演规范）实现为硬规则：
- 深雪：称谓白名单、语气词表、禁忌词黑名单、句长上限；
- 阶段硬锁（C3）：P1/P2 禁身份宣言、P1~P5 禁名字泄漏、雪女只许唤名；
- 谜团锁：输出不得触及四个核心问题且超出四种合法回应。
explain() 把违规翻成人话，供反馈式重试（C4）使用。
"""
import os
import re

import settings

# ---------------------------------------------------------------- 深雪校验
MIYUKI_FORBIDDEN = [
    '总的来说', '我理解你的感受', '作为AI', '作为一个', '抱歉，我', '无法回答',
    '其实我是', '我的身世', '我是雪女', '我是幽灵', '我不是人类', '我已经死了',
    '你烦什么约', '你怎么才来', '你迟到了', '责怪', '讲道理', '听我说来',
    '现代', '网络', '手机信号', '逻辑上', '从理论上',
]
MIYUKI_TONE = ['哦', '呢', '啦', '嘛', '吧', '――', '〜', '~', '？', '！', '。']
ADDRESS_OK = ['小修', '姐姐']
# 谜团关键词（触及即需检查是否为四种合法回应之一）
MYSTERY_KEYS = ['人类', '雪女', '幽灵', '妖怪', '身份', '从哪', '来历', '身世', '户籍',
                '父母是谁', '吃什么', '怎么活', '三年', '等的是谁', '山上等你']
MYSTERY_LEGAL = ['我会在那里，一直等啊。一直', '……哎？', '……', '（一如往常的微笑）',
                 '（睁大眼睛）', '（沉默片刻）']

# ---------------------------------------------------------------- 阶段硬锁（C3）
STAGES_EARLY = ('P1', 'P2')                            # 身份宣言禁发期（P3 才有「你的姐姐啊」）
STAGES_BEFORE_NAME = ('P1', 'P2', 'P3', 'P4', 'P5')    # 名字禁提期（P6 才揭示）
IDENTITY_DECLARATIONS = ['我是你的姐姐', '你的姐姐', '我就是姐姐', '我是姐姐',
                         '我是你的亲姐姐', '姐姐呀']
# 变体句式（真机冒烟抓到「我是小修的姐姐啊」绕过字面黑名单）：我是 + 0~3 字 + 姐姐
IDENTITY_RE = re.compile(r'我是.{0,3}姐姐|我就是姐姐|是你的姐姐')
NAME_TOKENS = ['深雪', 'みゆき', 'miyuki', '写作深和雪']

# 正典台词白名单：{台词: 允许阶段列表或 None(全阶段)}。阶段硬锁不受白名单豁免。
CANON_WHITELIST = {
    '我没有骗你': None, '我都说了这不是骗你': None,
    '我会在那里，一直等啊。一直': None,
    '不要哭了……男孩子可是不能哭的哦': None,
    '呐': None, '……哎？': None, '……嘛': None, '嘿嘿――': None,
    '给，这是你的': None, '用这个清雪': None, '我们走吧': None,
    '欢迎回来哦': None, '以牙还牙！': None, '不要紧――': None,
    '拉～勾！': None, '那就这么约定了哦': None,
    '不用担心念书的事啦': None, '多多小心啊': None, '保重身体哦，小修': None,
    '今年也快到头了': None, '外面――下雪了吗': None,
    '雪人好像脏了': None, '……哎': None, '会开花啊，开花时好漂亮的': None,
    '？': None, '很好……你做得很不错嘛': None, '没落下什么东西吧？': None,
    # ---- 阶段限定台词：出了允许阶段不再豁免（阶段锁照拦） ----
    '你的姐姐啊': ['P3', 'P7'],
    '写作深和雪两个字，miyuki': ['P6'],
    'miyuki': ['P6'],
}


def check_miyuki(text, stage=None):
    issues = []
    # ---- 1) 阶段硬锁（最高优先级；白名单不豁免） ----
    if settings.STAGE_GUARD:
        if stage in STAGES_EARLY and (
                any(wd in text for wd in IDENTITY_DECLARATIONS) or IDENTITY_RE.search(text)):
            issues.append('identity_declaration_early')
        if stage in STAGES_BEFORE_NAME and any(t in text for t in NAME_TOKENS):
            issues.append('name_leak_early')
    # ---- 2) 白名单：跳过风格检查（但阶段锁已先行判定） ----
    if text in CANON_WHITELIST:
        allowed = CANON_WHITELIST[text]
        if allowed is None or stage in allowed:
            return issues
    # ---- 3) 风格检查 ----
    if '小修' not in text and len(text) > 18:
        issues.append('missing_address')
    for w in MIYUKI_FORBIDDEN:
        if w in text:
            issues.append('forbidden:%s' % w)
    # 句长上限（旁白外台词）
    for seg in re.split(r'[。！？\n]', text):
        seg = seg.strip()
        if len(seg) > 42:
            issues.append('too_long_segment')
            break
    if len(text) >= 8 and not any(t in text for t in MIYUKI_TONE):
        issues.append('missing_tone')
    # ---- 4) 谜团锁 ----
    if any(k in text for k in MYSTERY_KEYS):
        if not any(l in text for l in MYSTERY_LEGAL) and '等啊' not in text:
            issues.append('mystery_leak')
    return issues


# ---------------------------------------------------------------- 修二校验
SHUUJI_FORBIDDEN_LITERARY = [
    '宛如', '仿佛', '恍若', '宛若', '犹如', '恰似', '我心潮澎湃', '命运的',
    '总的来说', '我理解', '对不起我不能', '我爱你', '我喜欢你', '想念你', '寂寞',
]
SHUUJI_NAME_FORBIDDEN = ['深雪']


def check_shuuji(text, stage):
    issues = []
    for w in SHUUJI_FORBIDDEN_LITERARY:
        if w in text:
            issues.append('too_literary:%s' % w)
            break
    if stage in ('P1', 'P2', 'P3', 'P4', 'P5', 'P6'):
        for w in SHUUJI_NAME_FORBIDDEN:
            if w in text:
                issues.append('name_leak_early')
        # 幼年不接受姐姐设定
        if '姐姐' in text and '骗子' not in text and '没有' in text:
            pass  # 「我根本没有姐姐」合法
    if stage in ('P1', 'P2', 'P3'):
        if any(w in text for w in ['我知道你的感受', '或许吧', '确实']):
            issues.append('vocab_over_age')
    return issues


# ---------------------------------------------------------------- 雪女校验（幻影只唤名）
def check_yukihime(text):
    t = text.replace('―', '').replace('－', '').replace('—', '').strip()
    if t in ('修二', ''):
        return []
    return ['yukihime_speech_rule']


# ---------------------------------------------------------------- 通用校验管道
def validate(char_id, text, stage=None):
    if char_id == 'miyuki':
        return check_miyuki(text, stage)
    if char_id == 'shuuji':
        return check_shuuji(text, stage)
    if char_id == 'yukihime':
        return check_yukihime(text)
    if char_id == 'toba':
        return [] if len(text) <= 60 else ['too_long_toba']
    if char_id in ('relative_man', 'relative_woman'):
        return [] if len(text) <= 120 else ['too_long_relative']
    return []


def is_acceptable(char_id, text, stage=None):
    return len(validate(char_id, text, stage)) == 0


# ---------------------------------------------------------------- 违规解释（C4 反馈式重试用）
ISSUE_EXPLAIN = {
    'missing_address': '台词未称呼对方「小修」',
    'forbidden': '使用了禁忌或出戏的表达',
    'too_long_segment': '单句超过 42 字，请拆成短句',
    'missing_tone': '缺少句尾语气词（哦/呢/啦/嘛/吧/――）',
    'mystery_leak': '触及了核心谜团却未用四种合法回应之一'
                    '（睁大眼睛真心不解/沉默片刻/一如往常的微笑/「我会在那里，一直等啊。一直」）',
    'identity_declaration_early': '本阶段你还不能说出「我是你的姐姐」这类身份宣言（剧情尚未到）',
    'name_leak_early': '本阶段你还不能说出自己的名字「深雪/miyuki」（剧情尚未到）',
    'yukihime_speech_rule': '幻影形态不对话，只唤一声「修二――――」',
    'too_long_toba': '鸟羽老人台词过长（至多两句短句）',
    'too_long_relative': '亲戚台词过长',
    'too_literary': '台词太文艺——抒情只能交给旁白，台词必须口语短句',
    'name_leak_early_shuuji': '本阶段修二还不知道对方的名字',
    'vocab_over_age': '用词超出当前年龄段的词汇量',
}


def explain(char_id, text, stage=None):
    """把违规编号翻成人话，供反馈式重试（C4）把原因喂回模型。"""
    out = []
    for i in validate(char_id, text, stage):
        if ':' in i:
            head, _, detail = i.partition(':')
            out.append('%s（%s）' % (ISSUE_EXPLAIN.get(head, i), detail))
        else:
            out.append(ISSUE_EXPLAIN.get(i, i))
    return out
