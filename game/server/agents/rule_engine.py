# -*- coding: utf-8 -*-
"""规则引擎（无 LLM 时的角色对演兜底）：意图分类 + 正典行为模式库。

来源：《人物设定与关系总览.md》§2 行为模式库 + §7 正典台词语料库。
输出统一结构：{'say', 'action', 'expr', 'effects'}。
"""
import random

# ---------------------------------------------------------------- 意图分类
INTENT_PATTERNS = [
    ('call_liar',      ['骗子', '骗人', '撒谎', '不可能', '我没有姐姐', '编的']),
    ('ask_identity',   ['你是谁', '你谁', '从哪', '来的人', '什么人', '为什么会在这', '为什么在这里', '你怎么会']),
    ('ask_mystery',    ['人类', '雪女', '妖怪', '幽灵', '鬼魂', '真实存在', '幻觉', '神仙', '魔物', '你到底是什么']),
    ('ask_parents',    ['父亲', '母亲', '爸爸', '妈妈', '父母', '遇难', '去世', '死了', '山里', '那一天']),
    ('cry',            ['呜', '哭', '呜呜', '呜咽', '泪']),
    ('refuse',         ['不要', '不去', '放开', '讨厌', '别碰', '放开我', '不去']),
    ('accept',         ['好', '嗯', '好吧', '知道了', '我来', '我来做', '走吧', '知道啊']),
    ('ask_name',       ['名字', '叫什么', '怎么称呼', '你是叫']),
    ('praise',         ['漂亮', '好看', '美丽', '像雪', '雪之妖精', '可爱', '温柔']),
    ('ask_play',       ['玩', '堆雪人', '打雪仗', '扑克', '游戏', '滑雪']),
    ('promise_return', ['回来', '还会', '约定', '明年', '拉勾', '一定']),
    ('farewell',       ['再见', '走了', '回去了', '告辞', '先走', ' bye', '拜拜']),
    ('apology',        ['抱歉', '对不起', '对不起啊', '抱歉啊', '是我不好', '没能']),
    ('ask_school',     ['念书', '学习', '上学', '功课', '学校', '升学']),
    ('ask_stay',       ['住这', '一直', '等', '一个人', '怎么办', '生活', '吃饭']),
    ('like_snow',      ['喜欢雪', '雪很', '爱雪', '雪好美', '好美']),
    ('smalltalk_hi',   ['你好', '嗨', '呐', '早', '晚上好', '在吗']),
    ('help_offer',     ['我来帮', '让我', '帮你', '我帮你']),
    ('ask_shrine',     ['祭典', '祭', '神社', '冬祭', '灯笼']),
    ('thanks',         ['谢谢', '多谢', '感激']),
]

MYSTERY_SOFT = ['人类', '雪女', '妖怪', '幽灵', '鬼魂', '幻觉', '到底是什么', '从哪来', '什么人']


def classify(text):
    """返回按命中长度排序的意图列表。"""
    hits = []
    for intent, pats in INTENT_PATTERNS:
        best = 0
        for p in pats:
            if p in text:
                best = max(best, len(p))
        if best:
            hits.append((best, intent))
    hits.sort(reverse=True)
    return [i for _, i in hits] or ['smalltalk']


# ---------------------------------------------------------------- 深雪行为模式库
def R(say, expr='normal', action='', effects=None):
    return {'say': say, 'expr': expr, 'action': action, 'effects': effects or {}}


# C2：信念句池——持有洞察（反思产物）时小概率替代日常闲聊，让信念"反过来影响行为"
BELIEF_LINES = [
    R('小修嘴上凶，心可不坏哦。嘿嘿――', 'smile', '（她像是看穿了什么，笑意盈盈）', {'affection': +1}),
    R('呐，小修。雪化了的时候，也要记得回来哦', 'normal', '（她轻声说着，像在确认什么）', {'affection': +1}),
]


def miyuki_respond(intents, text, world):
    phase = world.phase
    aff = world.affection('shuuji', 'miyuki')
    primary = intents[0]

    # —— 谜团锁（最高优先级，覆盖一切）
    if primary in ('ask_mystery', 'ask_identity'):
        return R('我会在那里，一直等啊。一直', 'normal', '（她微微睁大眼睛，随后一如往常地微笑）',
                 {'affection': 0, 'flag': 'touched_mystery'})

    if primary == 'call_liar':
        if phase in ('P1', 'P2', 'P3'):
            return R('我没有骗你', 'normal', '（平静地，气定神闲）', {'affection': 0})
        return R('都过了这么多年了，小修还记恨这个呀。嘿嘿――', 'smile', '（忍不住笑出来）', {'affection': +2})

    if primary == 'ask_parents':
        return R('呐――小修，我帮你量量身高吧', 'sad',
                 '（笑容消失，目光低垂，沉默片刻——随即瞬间恢复微笑，轻快地转移话题）',
                 {'affection': +1, 'flag': 'parents_topic'})

    if primary == 'cry':
        return R('不要哭了……男孩子可是不能哭的哦', 'normal',
                 '（她张开臂膀，环抱住你的头，手掌一下一下抚着你的背）', {'affection': +3, 'flag': 'comforted'})

    if primary == 'refuse':
        return R('我们走吧', 'smile', '（她并不生气，反而牵起你的手，稍稍用力地拽着）', {'affection': 0})

    if primary == 'accept':
        return R('很好……你做得很不错嘛', 'smile', '（在一旁看着你，露出饱含温暖的微笑）', {'affection': +2})

    if primary == 'ask_name':
        if phase in ('P1', 'P2', 'P3', 'P4', 'P5'):
            return R('小修的姐姐哦', 'smile', '（歪了歪头，仿佛这是天经地义的事）', {})
        return R('写作深和雪两个字，miyuki', 'smile', '（她凑近耳边，呢喃着）', {'affection': +1})

    if primary == 'praise':
        return R('嘿嘿――', 'smile', '（她有些得意地耸耸肩，白色的呼气溶化在空气里）', {'affection': +2})

    if primary == 'ask_play':
        return R('我们去外面玩吧', 'smile', '（她像肋下生出了双翅，在雪中张开双臂转了一圈）', {'affection': +2})

    if primary == 'promise_return':
        return R('那……我们拉勾', 'smile', '（她向你伸出了白皙的小拇指，目光凝视着你）',
                 {'affection': +3, 'flag': 'promise_made'})

    if primary == 'farewell':
        return R('没落下什么东西吧？', 'normal', '（她安静地微笑着，长发被寒风吹起）', {'affection': +1})

    if primary == 'apology':
        return R('小修，不要在意啦', 'smile', '（她摆了摆手，笑容一如往常）', {'affection': +2})

    if primary == 'ask_school':
        return R('不用担心念书的事啦', 'normal', '（她微微睁大眼睛，仿佛听说了不可思议的事）', {})

    if primary == 'ask_stay':
        return R('我会在那里，一直等啊。一直', 'normal', '（她望向庭院的雪，轻声说）', {})

    if primary == 'like_snow':
        return R('呐，你喜欢雪吗？', 'smile', '（她停下脚步，回过头来问你）', {'affection': +1})

    if primary == 'thanks':
        return R('多多小心啊', 'smile', '（她朝你挥了挥手）', {'affection': +1})

    if primary == 'help_offer':
        return R('给，这是你的', 'smile', '（她得意地把铲子递过来）', {})

    if primary == 'ask_shrine':
        return R('一起去吧。我们要是走散就坏了', 'normal', '（她用白皙而纤细的手牵着你）', {'affection': +1})

    # —— smalltalk：按阶段与好感的日常温柔；有洞察（C2 反思产物）时小概率说信念句
    try:
        _insights = world.memory['miyuki'].insights()
    except Exception:
        _insights = []
    if _insights and random.random() < 0.25:
        pick = dict(random.choice(BELIEF_LINES))
        pick['effects'] = {'affection': +1}
        return pick
    if aff >= 70:
        pool = [
            R('多吃多吃啊，小修――', 'smile'),
            R('小修，过来清雪啦――', 'smile'),
            R('小修？你先去泡澡吧――', 'normal'),
            R('小修，晚安――', 'smile'),
        ]
    elif aff >= 40:
        pool = [
            R('呐――外面还在下雪哦', 'normal'),
            R('因为――你看起来有点无聊哦', 'smile'),
            R('呼，好冷啊', 'smile', '（她有些开心地耸了耸肩膀）'),
            R('嘿嘿――', 'smile'),
        ]
    else:
        pool = [
            R('呐', 'normal', '（她凝视着你，仿佛已这样守望了你许多年）'),
            R('……哎？', 'surprise'),
            R('……嘛', 'normal'),
        ]
    pick = random.choice(pool)
    pick['effects'] = {'affection': +1}
    return pick


# ---------------------------------------------------------------- 其他 NPC
def toba_respond(intents, text, world):
    primary = intents[0]
    if primary == 'smalltalk_hi':
        return R('……来了啊。', 'normal', '（独眼老人朝你点了点头）', {})
    if primary in ('ask_shrine',):
        return R('……祭啊。今年的雪，深。', 'normal', '（他往炉子里添了根柴）', {})
    if '深雪' in text or '女孩' in text or '姐姐' in text:
        return R('……那孩子啊。', 'normal', '（他沉默地多看了你几眼）', {'flag': 'toba_noticed'})
    if '住' in text or '留' in text:
        return R('……炉边，暖。睡吧。', 'normal', '（他指了指被炉旁的旧被褥）', {})
    return R('……嗯。', 'normal', '（他久久地望着炉火）', {})


def relative_respond(intents, text, world, who='relative_man'):
    primary = intents[0]
    if who == 'relative_man':
        if primary == 'refuse' or '收养' in text or '抚养' in text:
            return R('麻烦呐――', 'normal', '（他推了推眼镜，视线游移开）', {})
        pool = [
            R('这么说――', 'normal', '（他双手在身前摊了摊）'),
            R('所以谁来――', 'normal', '（他看了看待在一旁的婶婶）'),
            R('真是不好办啊――', 'normal', '（他叹了口气，额角渗出一点汗）'),
        ]
    else:
        if primary == 'refuse' or '收养' in text or '抚养' in text:
            return R('虽然我不想直说――', 'normal', '（她用手掩着嘴，眼神游移）', {})
        pool = [
            R('正是因为你家――', 'normal', '（她欲言又止）'),
            R('可是――', 'normal', '（她轻轻叹了口气）'),
            R('真是不好办啊――', 'normal', '（她朝叔父那边看了一眼）'),
        ]
    return random.choice(pool)


NPC_RESPONDERS = {
    'toba': toba_respond,
    'relative_man': lambda i, t, w: relative_respond(i, t, w, 'relative_man'),
    'relative_woman': lambda i, t, w: relative_respond(i, t, w, 'relative_woman'),
}


def respond(char_id, text, world):
    intents = classify(text)
    if char_id == 'miyuki':
        return miyuki_respond(intents, text, world)
    fn = NPC_RESPONDERS.get(char_id)
    if fn:
        return fn(intents, text, world)
    return R('……', 'normal', '', {})


# ---------------------------------------------------------------- 旁白
NARRATOR_BANK = {
    'P1_intro': [
        '悲伤，犹如穿过蒙着水汽的窗玻璃照射进来的阳光，模糊而若有若无。',
        '走廊如同深海。尘埃的味道弥漫在空气中，陈年的木材颜色泛黄。',
        '雪花一片一片，从纯白无垠的天空中悠悠飘落。那里是无声的世界，空茫而没有尽头。',
    ],
    'P1_snow': [
        '好耀眼——纯白的色彩尽染了整个世界。可以说是一片白暗。',
        '太阳在厚重乌云的另一边微微晃动着，像是褪去了光彩，看起来十分清冷。',
        '雪之妖精——如果雪之妖精真的存在，那她的容貌一定与我眼前的这个女孩别无二致。',
    ],
    'P2_cry': [
        '过去，像这样在庭院中清雪的，总是我的父亲。晚餐的香气从厨房飘来。',
        '失去的家人，再不能回来。在那庭院中，在那客厅中，在那小小的被褥中。',
        '滚烫而酸楚的泪水流进口中，落到雪地上，留下星星点点的痕迹。',
    ],
    'P7_return': [
        '三年间毫无人烟的老屋，仿佛废墟一般荒凉。失去了主人的老屋，仿佛正渐渐地死去。',
        '她一直在等，我一直在逃，雪一直落在两人之间。',
        '有人还在等待着我，仍然让我感动不已。',
    ],
    'P0_climb': [
        '据说，群山有奇异的魔性。很久以前，这绵绵群山，并非人类所拥有的土地。',
        '深广的静寂，像是将一切都吞没了。无论是温度，光线，声音，时间。甚至是生命。',
        '我必须要前行。到父亲和母亲那里去。到二人等待着我的地方去。',
    ],
    'generic': [
        '雪，静静地落着。落在这座小镇，落在老屋，落在每一个人的肩上。',
        '这片土地上，时光仿佛停滞了。只有雪，还在无声地累积。',
        '群山在远处沉默着，仿佛怀着众多的谜，抗拒着人的接近。',
    ],
}


def narrate(tag=None):
    bank = NARRATOR_BANK.get(tag) or NARRATOR_BANK['generic']
    return random.choice(bank)
