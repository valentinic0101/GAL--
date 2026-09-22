# -*- coding: utf-8 -*-
"""分歧与结局场景数据：P11 岔路 / P12M 雪径 / P12B 幸福之问 / E_STAY / E_SPRING / E_FAR / E_TOKYO。

这些节点由 director 的 SUCCESSORS 表按三轴（bond/obsession/worldly）阈值挂到主干之后，
阈值与走向见 资料/02_设定与设计/多结局分支设计.md。
本模块从 trunk 取 SCENES 注册表并继续写入——import 本模块即完成注册。
"""
from .trunk import SCENES

# ================================================================ P11 一年后的岔路（D0）
SCENES['P11'] = {
    'title': 'P11 · 一年后的岔路',
    'location': 'station',
    'time': 'day',
    'bg': 'bg_station_day.png',
    'beats': [
        {'type': 'narration', 'text': '一年又过去了。期中与期末、东京的教室与宿舍，把日历撕得飞快。寒假的第一天，我提着行李，站上了上山站的站台。站台照旧空无一人。'},
        {'type': 'narration', 'text': '她没有来。也许正在老屋的炉边等着，也许正站在檐廊下听雪。这一次，没有人牵我的手——路，要自己选了。'},
        {'type': 'branch_text', 'cases': [
            {'cond': 'axis:obsession>=35',
             'text': '（行李的最底层，压着一张手绘的地图。山麓、搜救队当年走过的路线、父亲笔记里提到过的岔口……这一年里，我查过太多东西。）'},
            {'cond': 'default',
             'text': '（山在视野的尽头白着。我告诉自己，只是看看而已。）'},
        ]},
        {'type': 'choice', 'options': [
            {'label': '先去群山——去父亲和母亲所在的地方', 'intents': ['ask_parents'], 'requires': 'axis:obsession>=35',
             'flag': 'chose_mountains', 'axis': {'obsession': 5},
             'fail_flag': 'chose_return',
             'fail_text': '（脚迈向站台的另一头，却像陷进雪里一样沉。装备、体力、理由……都还没有准备好。我终于承认——现在的自己，还没有踏进那片白色的资格。）'},
            {'label': '回到雪国——回到姐姐身边', 'intents': ['promise_return'], 'flag': 'chose_return', 'axis': {'bond': 3}},
            {'label': '今年，就留在东京吧', 'intents': ['refuse'], 'requires': 'axis:worldly>=35',
             'flag': 'stayed_tokyo', 'axis': {'worldly': 3},
             'fail_flag': 'chose_return',
             'fail_text': '（话是这么说。可提笔写假期安排的时候，笔尖在「雪国」两个字上停了很久。等到回过神来，列车已经载着我，走在回去的路上。）'},
        ]},
        {'type': 'effect', 'flags': {'fork_done': True}},
    ],
}

# ================================================================ P12M 雪径（入山线）
SCENES['P12M'] = {
    'title': 'P12M · 雪径',
    'location': 'mountains',
    'time': 'evening',
    'bg': 'bg_mountain_path.png',
    'beats': [
        {'type': 'narration', 'text': '我没有先去老屋。把行李寄存在车站的柜子里，只背了一个轻包——地图、绳索、手电、三天的口粮。出发前给鸟羽老人挂了个电话，铃响到第七声，我挂断了。有些话一旦说出口，就会被人拦住。'},
        {'type': 'me', 'say': '……我出发了'},
        {'type': 'narration', 'text': '（对不起，姐姐。拉了勾的约定，我要先失约了。——等我把该接的人接回来，就回去向你赔罪。）'},
        {'type': 'narration', 'text': '山麓的雪没过膝盖。每一步都要先把腿从雪里拔出来。地图上的岔口和实地对不上——父亲笔记里的字迹，到这里就停了。'},
        {'type': 'narration', 'text': '不知走了多久。天色沉了下来，风从山脊上滚落，卷起地上的新雪。白色的飞沫遮住了视野。远处，有咏叹声一样的东西，混在风里。'},
        {'type': 'branch_text', 'cases': [
            {'cond': 'flag:parents_belief',
             'text': '（他们在呼唤。这一年里我终于敢承认——那不是幻听。是呼唤。）'},
            {'cond': 'default',
             'text': '（风里有声音。像呼唤，又只是风。）'},
        ]},
        {'type': 'narration', 'text': '雪原的深处，伫立着一个白色的身影。'},
        {'type': 'me', 'say': '――还有人？'},
        {'type': 'narration', 'text': '那身影转过来的弧度，那么缓慢，又那么熟悉。我的心跳漏了一拍——那张脸，我比任何人都要熟识。'},
        {'type': 'effect', 'location': 'blizzard', 'bg': 'bg_mountains_blizzard.png', 'axis': {'obsession': 5}},
    ],
}

# ================================================================ P12B 幸福之问（归省线·D1）
SCENES['P12B'] = {
    'title': 'P12B · 田间小路',
    'location': 'fields',
    'time': 'day',
    'bg': 'bg_mountains.png',
    'beats': [
        {'type': 'narration', 'text': '老屋的炉火、清雪、扑克、并肩而眠——几天的归省像一场太短的梦。回东京的日子又到了。深雪送我，走在这条田间小路上。雪把两边的田野盖成一片白，两行足迹在身后排开。'},
        {'type': 'line', 'who': 'miyuki', 'say': '今年，是小修自己回来的呢', 'expr': 'smile', 'action': '（她走在我旁边，脚步轻快。这话里有一点小小的得意）'},
        {'type': 'me', 'say': '……嗯。我自己回来的'},
        {'type': 'narration', 'text': '风从群山的方向吹过来。她忽然停下脚步，用漆黑的眼瞳望着我。'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修――', 'expr': 'smile', 'action': ''},
        {'type': 'line', 'who': 'miyuki', 'say': '觉得现在幸福吗……？', 'expr': 'normal', 'action': '（突如其来的提问。她安静地等着，不催促）'},
        {'type': 'free', 'prompt': '（原文里没能回答的那句话，由你来回答。说出真心话——它会决定故事的走向）', 'chips': ['和你在一起很幸福', '望着群山说不出话', '……']},
        {'type': 'choice', 'options': [
            {'label': '那就，留在这里——今年哪儿也不去了', 'intents': ['ask_stay'], 'requires': 'axis:bond>=50',
             'flag': 'chose_stay', 'axis': {'bond': 5}, 'fail_flag': 'stay_promise_failed',
             'fail_text': '「留下来」三个字在舌尖上化掉了，像雪落在手心。深雪轻轻摇头，笑容一如往常：「傻瓜。小修的教室在东京哦。……不过，谢谢你。」'},
            {'label': '春天，樱花开的时候，我再来见你', 'intents': ['promise_return'], 'requires': ['axis:bond>=50', 'axis:obsession<35'],
             'flag': 'chose_spring', 'axis': {'bond': 3}, 'fail_flag': 'spring_promise_failed',
             'fail_text': '「春天」两个字出口的时候，她的笑容淡了一瞬。她朝群山的方向望了一眼，什么也没说。而我，没能把「一定」说出口。'},
            {'label': '（话终究没有说完整）', 'intents': ['smalltalk'], 'flag': 'said_nothing'},
        ]},
        {'type': 'effect', 'flags': {'happiness_asked': True}, 'axis': {'bond': 1}},
    ],
}

# ================================================================ E_STAY 留守线（END_STAY）
SCENES['E_STAY'] = {
    'title': 'E · 炉火与春讯',
    'location': 'oldhouse_in',
    'time': 'evening',
    'bg': 'bg_oldhouse_room.png',
    'beats': [
        {'type': 'narration', 'text': '我在路口转过身，朝老屋走回去。深雪跟了上来，与我并肩。谁都没有说话，可脚步越来越快，最后几乎是小跑着，推开了那扇门。'},
        {'type': 'line', 'who': 'miyuki', 'say': '姐姐去添炭。小修去把烟囱上的雪拍一拍——今晚，要多煮一个人的饭了哦', 'expr': 'smile', 'action': ''},
        {'type': 'cg', 'img': 'cg_stay.png'},
        {'type': 'narration', 'text': '炉火重新旺了起来。窗外的雪声被隔得很远。晚饭是白粥和腌菜，热气把彼此的脸都熏得模糊。'},
        {'type': 'free', 'prompt': '（留下的第一个夜晚。你想对姐姐说什么？）', 'chips': ['姐姐，晚安', '春天来了会怎样？', '……']},
        {'type': 'narration', 'text': '夜里，我们隔着被炉说话，说到灯芯结花。她忽然安静了一会儿。'},
        {'type': 'line', 'who': 'miyuki', 'say': '呐，小修。春天来的时候……你还会在吗？', 'expr': 'normal', 'action': '（她问得很轻，像怕惊动什么）'},
        {'type': 'choice', 'options': [
            {'label': '在。哪儿都不去', 'flag': 'stay_confirmed', 'axis': {'bond': 3}},
            {'label': '……在。至少，到开学', 'axis': {'worldly': 2, 'bond': 1}},
        ]},
        {'type': 'narration', 'text': '我在雪国住了下来。清雪、泡澡、做饭、扑克——老屋的循环里，从此多出一个不会离开的位置。只是有时，镇上的人会在檐廊下多看我们两眼；只是偶尔，风从山那边吹过来的时候，她的笑容会停一下，像在听什么。'},
        {'type': 'narration', 'text': '亲戚那边总要有个说法，东京的学籍也是。……可那是春天以后的事了。今晚，先把饭煮上。'},
        {'type': 'narration', 'text': '雪一直下。春天，还没有来。'},
        {'type': 'effect', 'axis': {'bond': 2}},
    ],
}

# ================================================================ E_SPRING 真结局（END_SPRING）
SCENES['E_SPRING'] = {
    'title': 'E · 等到花开',
    'location': 'fields',
    'time': 'day',
    'bg': 'bg_fields_spring.png',
    'beats': [
        {'type': 'narration', 'text': '东京的春天来得很吵。开学、大扫除、粉笔灰。我把那个约定折好，放进内袋，等假期的列车。'},
        {'type': 'narration', 'text': '春假。我又一次踏上上山站。这一次，站台上吹的风是软的。雪水沿着铁轨的形状，淌成两条细细的溪流。'},
        {'type': 'narration', 'text': '田间小路卸下了它的白色。田埂露出黑土，水洼里晃着天光。路的尽头，老屋的院墙上探出一角粉色——'},
        {'type': 'me', 'say': '…………开了'},
        {'type': 'effect', 'location': 'courtyard', 'bg': 'bg_courtyard_spring.png'},
        {'type': 'cg', 'img': 'cg_spring.png'},
        {'type': 'narration', 'text': '樱花开了。那棵比我更老的老树，满枝都是浅色的花，开得没有一点犹豫。树下，站着一个比冬天里更明亮的身影。'},
        {'type': 'line', 'who': 'miyuki', 'say': '欢迎回来哦，小修', 'expr': 'spring',
         'action': '（她站在樱花树下。春装轻盈，发梢被春风轻轻掀起）',
         'cast': ['shuuji', 'miyuki']},
        {'type': 'me', 'say': '为什么……春天，你也在？'},
        {'type': 'line', 'who': 'miyuki', 'say': '因为约好了呀', 'expr': 'smile', 'action': '（她说得理所当然，像在说雪是白的）'},
        {'type': 'narration', 'text': '门口的两个雪人已经化得只剩矮矮的雪堆，可额头上的那一道，还看得出形状。我蹲下去，用指尖把齐刘海又描了一遍。'},
        {'type': 'narration', 'text': '「这样就好了。」——去年冬天，是我这样说的。今年，她替我说了。'},
        {'type': 'line', 'who': 'miyuki', 'say': '嗯。这样就好了', 'expr': 'smile', 'action': ''},
        {'type': 'effect', 'flags': {'accepted_sister': True}, 'axis': {'obsession': -10}},
        {'type': 'narration', 'text': '花瓣落进她的发间，分不清哪个是白，哪个是粉。群山还在视野的尽头白着——但今天的我，先看花。'},
    ],
}

# ================================================================ E_FAR 原作向（END_FAR）
SCENES['E_FAR'] = {
    'title': 'E · 两行足迹',
    'location': 'fields',
    'time': 'day',
    'bg': 'bg_mountains.png',
    'beats': [
        {'type': 'narration', 'text': '路口。一条路通向车站，一条路通回老屋。我朝车站的方向，迈开了脚步。'},
        {'type': 'line', 'who': 'miyuki', 'say': '我送你', 'expr': 'smile', 'action': '（她自然地走在我旁边，像第一次送站时那样）'},
        {'type': 'narration', 'text': '田间小路上，并排留下了两行黑色的足迹。雪还在下，把来路和去路都慢慢抹平。'},
        {'type': 'line', 'who': 'miyuki', 'say': '小修，不用回头也是知道的哦', 'expr': 'smile', 'action': '（她在站台上，像每一次那样朝我挥手）'},
        {'type': 'me', 'say': '嗯。……明年'},
        {'type': 'branch_text', 'cases': [
            {'cond': 'flag:spring_promise_failed',
             'text': '「春天」——这个约定，我没能守住。期末、亲戚、生活里连绵不断的琐事，把三月碾了过去。等我能再站上那座站台时，已经是冬天。她还是那样站在老屋门口，笑着说「欢迎回家」。好像迟到的从来不是我，只是雪。'},
            {'cond': 'flag:stay_promise_failed',
             'text': '「留下来」——我把这三个字咽了回去。东京的教室里，我偶尔会想起那天路口的炉火味。可想起归想起，列车依旧准点。'},
            {'cond': 'default',
             'text': '那句回答，我至今没能说完整。她大概早就习惯了——她等着的，从来都是一个会迟到的人。'},
        ]},
        {'type': 'cg', 'img': 'cg08.png'},
        {'type': 'cg', 'img': 'cg_far.png'},
        {'type': 'narration', 'text': '列车开动。她的身影越来越小，最后停在原地——朝着我看不见的、群山的方向。仿佛那里，有什么人在等待着她。'},
        {'type': 'narration', 'text': '而那句提问的答案，我把它和车票收在一起。总有一天，我会带着答案回来的。一定。'},
        {'type': 'effect', 'axis': {'bond': 1}},
    ],
}

# ================================================================ E_TOKYO 留京线（并入 END_FAR）
SCENES['E_TOKYO'] = {
    'title': 'E · 东来的雪',
    'location': 'town_street',
    'time': 'night',
    'bg': 'bg_tokyo.png',
    'beats': [
        {'type': 'narration', 'text': '「今年就留在东京吧」——说出这句话的时候，我听见自己的声音，平静得像在念别人的课程表。'},
        {'type': 'narration', 'text': '假期过去了。然后是下一个学期，下一个冬天。雪国的消息断了——没有地址，没有电话，只有一个我没能遵守的约定。'},
        {'type': 'narration', 'text': '唯一从那边寄来的东西，是一座停摆的挂钟。亲戚收拾老屋时寄来的，说「反正你也不回去」。指针停在四时四十九分。我把它挂在公寓的墙上。它不走，可我每天都会看它。'},
        {'type': 'narration', 'text': '有年冬天，东京下了很大的雪。站台人潮汹涌，我在人群里忽然停下脚步——因为有个撑伞的身影，侧脸白得像雪。我追了两步，又站住。不会是她。她在雪国。她一直都在雪国，等一个会迟到的人。'},
        {'type': 'me', 'say': '……明年。明年一定'},
        {'type': 'narration', 'text': '这句话，我对自己说了很多年。'},
    ],
}
