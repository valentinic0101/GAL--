# -*- coding: utf-8 -*-
"""引擎的静态配置表（纯数据，无逻辑）。

阶段提示、BGM 映射、场景转场、在场演员、幕间自由行动候选词——
这些是「内容侧调参」的地方，改它们不需要碰 core.py 的运行时逻辑。
"""
# 阶段约束：随场景注入 Agent prompt，防止 LLM 泄漏后设（如 P1 就说「你的姐姐啊」）
STAGE_NOTES = {
    'P1': '你与修二今日初遇。他还不知道你的存在，你尚未说过「我是你的姐姐」这样的身份宣言——此刻只是以自来熟的、姐姐般的姿态待他，叫他「小修」。',
    'P2': '初遇次日。你尚未对他说过「我是你的姐姐」这样的身份宣言，只以温柔姐姐的姿态照顾他。',
    'P3': '本场景中你自然地说出「你的姐姐啊」——这是修二第一次听到。',
    'P6': '他仍不知你的名字；名字只在你送站的列车发车前才低语告知。',
    'P11': '深雪不在场。她在老屋等你，不知道你此刻站在站台上想什么。',
    'P12M': '深雪不在场。这是修二独自行走在雪径上的场景。不要让任何角色出现或说话。',
    'P12B': '归省最后一天，她送你走田间小路。「觉得现在幸福吗」是她鼓起勇气问出的话，她只会安静地听，不追问。',
    'E_STAY': '修二留在了雪国。不解释你为何能独自留在老屋、不提春天之后的事；风从山那边吹来时你可以怔一下，但不说破。',
    'E_SPRING': '春天，樱花开了，你在樱花树下。绝不解释为何冬天之外你也能现身——被问到只以「因为约好了呀」带过。谜团一个都不揭。',
    'E_FAR': '怅然的送别。你照常微笑，不挽留、不追问。',
    'E_TOKYO': '深雪不在场。这是修二独自在东京的独白场景。不要让任何角色出现或说话。',
}

# BGM 映射：场景优先，幕间按地点
SCENE_BGM = {
    'P1': 'bgm_main', 'P2': 'bgm_sad', 'P3': 'bgm_daily', 'P4': 'bgm_festival',
    'P5': 'bgm_main', 'P6': 'bgm_sad', 'P7': 'bgm_main', 'P8': 'bgm_daily',
    'P9': 'bgm_main', 'P10': 'bgm_sad', 'P0': 'bgm_blizzard',
    'P11': 'bgm_sad', 'P12M': 'bgm_blizzard', 'P12B': 'bgm_main',
    'E_STAY': 'bgm_daily', 'E_SPRING': 'bgm_main', 'E_FAR': 'bgm_sad', 'E_TOKYO': 'bgm_sad',
}
LOC_BGM = {
    'oldhouse_in': 'bgm_daily', 'oldhouse_corridor': 'bgm_daily',
    'courtyard': 'bgm_daily', 'oldhouse_front': 'bgm_daily',
    'station': 'bgm_main', 'fields': 'bgm_main', 'town_street': 'bgm_daily',
    'toba_home': 'bgm_daily', 'shrine_road': 'bgm_festival', 'shrine': 'bgm_festival',
    'mountains': 'bgm_blizzard', 'blizzard': 'bgm_blizzard',
}

# 阶段转换时的世界时间推进
TRANSITIONS = {
    'P1':  dict(day=1, countdown=None),
    'P2':  dict(day=2, countdown=None),
    'P3':  dict(day=3, countdown=2),
    'P4':  dict(day=4, countdown=0),
    'P5':  dict(day=5, countdown=None),
    'P6':  dict(day=6, countdown=None),
    'P7':  dict(day=1000, countdown=None),   # 三年后
    'P8':  dict(day=1001, countdown=None),
    'P9':  dict(day=1003, countdown=None),
    'P10': dict(day=1004, countdown=None),
    'P0':  dict(day=2000, countdown=None),
    'P11': dict(day=1400, countdown=None),   # 一年后
    'P12B': dict(day=1403, countdown=None),
    'P12M': dict(day=1401, countdown=None),
    'E_STAY': dict(day=1404, countdown=None),
    'E_SPRING': dict(day=1500, countdown=None),   # 春假
    'E_FAR': dict(day=1404, countdown=None),
    'E_TOKYO': dict(day=1700, countdown=None),    # 数年后
}

# 各阶段的在场角色与初始场景
# 场景开场在场基线；中途登场者由台词自动上台（详见 frame/present 管理）
SCENE_CAST = {
    'P1': ['shuuji', 'relative_man', 'relative_woman'],
    'P2': ['shuuji', 'miyuki'],
    'P3': ['shuuji'],
    'P4': ['shuuji', 'miyuki'],
    'P5': ['shuuji', 'miyuki'],
    'P6': ['shuuji', 'miyuki'],
    'P7': ['shuuji'],
    'P8': ['shuuji', 'miyuki'],
    'P9': ['shuuji', 'miyuki'],
    'P10': ['shuuji', 'miyuki'],
    'P0': ['shuuji'],
    'P11': ['shuuji'],
    'P12M': ['shuuji'],
    'P12B': ['shuuji', 'miyuki'],
    'E_STAY': ['shuuji', 'miyuki'],
    'E_SPRING': ['shuuji'],
    'E_FAR': ['shuuji', 'miyuki'],
    'E_TOKYO': ['shuuji'],
}


INTERLUDE_CHIPS = {
    'P1':  ['呐，你喜欢雪吗？', '你叫什么名字？', '……'],
    'P2':  ['谢谢你陪着我', '我好想爸爸妈妈……', '……'],
    'P3':  ['你到底为什么在这里？', '刚才……对不起', '……'],
    'P4':  ['祭典真热闹啊', '背着我累不累？', '……'],
    'P5':  ['明年也要量身高哦', '学校里的事情……', '……'],
    'P6':  ['深雪是什么意思？', '东京的事……说说嘛', '……'],
    'P7':  ['这三年你都在哪里？', '终于见到你了……', '……'],
    'P8':  ['来陪我打扑克吧', '一起去堆雪人嘛', '……'],
    'P9':  ['没能每年回来，抱歉', '明年我一定回来', '……'],
    'E_STAY':  ['姐姐，晚安', '春天来了会怎样？', '……'],
    'E_SPRING': ['樱花真好看', '以后一起看花吧', '……'],
    'E_FAR':   ['明年见', '保重身体', '……'],
}
