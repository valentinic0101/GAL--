# -*- coding: utf-8 -*-
"""游戏运行时引擎：场景推进 + 幕间自由行动 + 导演调度 + 事件溯源存档。"""
import json
import os
import time
import uuid

from world.world import World, LOCATIONS, CHAR_NAME
from director.director import Director, PHASE_ORDER, ENDINGS, ENDINGS_TITLE, ENDING_SUBTITLE, eval_cond
from agents import score as axis_score
from director import gossip
from agents import rule_engine
from agents.llm import LLM, assemble_prompt
from agents.personas import PERSONAS, persona_card
from agents import guardrails
from agents import canon as canon_mod
from agents import memory as memory_mod
from director import guide as guide_mod
import settings
from scenes.script import SCENES

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'saves')
os.makedirs(SAVE_DIR, exist_ok=True)
LOG_PATH = os.path.join(os.path.dirname(SAVE_DIR), 'logs', 'engine.log')


def log(msg):
    """引擎事件日志（LLM 异常/护栏拦截/引导策略），排障不再靠盲测。"""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write('%s %s\n' % (time.strftime('%m-%d %H:%M:%S'), msg))
    except OSError:
        pass

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

class Engine:
    def __init__(self):
        self.world = World()
        self.director = Director(self.world)
        self.session = str(uuid.uuid4())[:8]
        self.mode = 'scene'          # scene / interlude
        self.scene_id = None
        self.beat_idx = 0
        self.history = []            # 展示日志（前端 backlog）
        self.pending_choices = None
        self.last_frame = None
        self.present = []            # 当前在台角色（有序：shuuji 恒第一）
        self._remembered = set()     # 本场景被写入过记忆的角色（C2 反思候选）

    # ---------------------------------------------------------------- 帧构造
    def sprite_of(self, char_id, expr=None):
        p = PERSONAS.get(char_id, {})
        sprites = p.get('sprites') or {}
        if char_id == 'shuuji':
            key = 'teen' if self.world.phase in ('P7', 'P8', 'P9', 'P10', 'P0', 'P11', 'P12M', 'P12B', 'E_STAY', 'E_SPRING', 'E_FAR', 'E_TOKYO') else 'child'
            return sprites.get(key)
        if expr and expr in sprites:
            return sprites[expr]
        return p.get('sprite')

# 幕间「交谈」话题建议：按场景定制（自由输入会被打分累积三轴——话题即去向）


    def frame(self, kind, text='', who=None, expr=None, action='', choices=None, bg=None, note='', chips=None):
        w = self.world
        sprites = []
        cast = list(self.present) if self.mode == 'scene' else self.director.present_chars()
        for c in cast:
            sp = self.sprite_of(c, expr if c == who else None)
            if sp:
                sprites.append({'id': c, 'name': CHAR_NAME.get(c), 'sprite': sp,
                                'side': 'left' if c == 'shuuji' else ('right' if c == 'miyuki' else 'far'),
                                'speaking': bool(who and c == who)})
        cur_bg = bg or w.flags.get('_bg_override') or (LOCATIONS.get(w.location, {}).get('bg'))
        chips_now = None
        if kind == 'interlude':
            others = [c for c in self.director.present_chars() if c != 'shuuji']
            chips_now = INTERLUDE_CHIPS.get(self.world.phase) if others else []
        f = {
            'kind': kind,
            'name': CHAR_NAME.get(who) if who else None,
            'who': who,
            'text': text,
            'action': action,
            'choices': choices,
            'chips': chips if kind == 'free' else chips_now,
            'bg': cur_bg,
            'sprites': sprites,
            'note': note,
            'src': None,
            'meta': {
                'phase': w.phase, 'day': w.day,
                'location': LOCATIONS.get(w.location, {}).get('name', w.location),
                'time': w.time_slot, 'affection': w.affection('shuuji', 'miyuki'),
                'countdown': w.festival_countdown,
                'mode': self.mode,
                'axes': dict(w.axes),
                'ending': self._ending_card(),
                'scene_title': SCENES.get(self.scene_id, {}).get('title', '') if self.scene_id else '',
                'llm': LLM.available,
                'bgm': (SCENE_BGM.get(self.scene_id) if self.mode == 'scene'
                        else LOC_BGM.get(w.location, 'bgm_daily')),
            },
        }
        self.last_frame = f
        if kind in ('narration', 'line', 'me'):
            self.history.append({'name': f['name'] or '旁白', 'text': text, 'action': action})
        return f

    # ---------------------------------------------------------------- 新游戏
    def new_game(self):
        self.world = World()
        self.director = Director(self.world)
        self.history = []
        self.world.emit('game_start', {})
        return self.enter_scene('P1')

    def enter_scene(self, scene_id):
        self.scene_id = scene_id
        self.beat_idx = 0
        self.mode = 'scene'
        self.pending_choices = None      # 丢弃旧会话的待输入状态，防止 advance 卡死
        sc = SCENES[scene_id]
        self.world.phase = scene_id
        self.director.reset_progress()      # C7：引导特征清零
        self._remembered = set()            # C2：本场景记忆写入者清零
        # 场景声明的 location/time 同步进世界层（修复：结局卡/HUD 地点回落到旧地点）
        if sc.get('location'):
            self.world.location = sc['location']
        if sc.get('time'):
            self.world.time_slot = sc['time']
        self.present = list(SCENE_CAST.get(scene_id, ['shuuji']))
        if 'shuuji' not in self.present:
            self.present.insert(0, 'shuuji')
        # 场景声明的背景在入场即生效（效果节拍仍可中途切换；scene_end 会清除）
        if sc.get('bg'):
            self.world.flags['_bg_override'] = sc['bg']
        self.world.emit('scene_enter', {'scene': scene_id})
        f = self.frame('scene_title', '', note=sc['title'])
        return [f, self.step()]

    # ---------------------------------------------------------------- 场景推进
    def step(self):
        sc = SCENES[self.scene_id]
        while self.beat_idx < len(sc['beats']):
            beat = sc['beats'][self.beat_idx]
            t = beat['type']
            # beat 级 cast：立绘按拍入场/退场（如 P7 重逢前深雪不在站台）
            if beat.get('cast') is not None:
                self.present = list(dict.fromkeys(beat['cast']))
                if 'shuuji' not in self.present:
                    self.present.insert(0, 'shuuji')
            if t == 'narration':
                self.beat_idx += 1
                return self.frame('narration', beat['text'])
            if t == 'line':
                self.beat_idx += 1
                self._join_stage(beat['who'])
                self._remember_beat(beat)          # C1：台词写入在场角色记忆流
                return self.frame('line', beat['say'], beat['who'], beat.get('expr'), beat.get('action', ''))
            if t == 'me':
                self.beat_idx += 1
                for c in self.present:             # C1：正典台词也被他人记住
                    if c != 'shuuji':
                        self._remember(c, '修二说：%s' % beat['say'])
                return self.frame('me', beat['say'], 'shuuji')
            if t == 'choice':
                # 选项全部可见；阈值在提交时判定，不够格的选项会被剧情化拒绝（fail_text）
                self.pending_choices = beat
                return self.frame('choice', '', choices=beat['options'])
            if t == 'branch_text':
                self.beat_idx += 1
                for case in beat['cases']:
                    if eval_cond(case.get('cond', 'default'), self.world):
                        return self.frame('narration', case['text'])
            if t == 'free':
                self.pending_choices = {'free': True, 'prompt': beat.get('prompt', '你想说什么？')}
                return self.frame('free', '', choices=None, note=beat.get('prompt', ''), chips=beat.get('chips'))
            if t == 'cg':
                self.beat_idx += 1
                cg_path = os.path.join(os.path.dirname(SAVE_DIR), 'assets', 'cg', beat['img'])
                if not os.path.exists(cg_path):
                    continue      # 素材未生成：优雅跳过（图到位即自动生效）
                f = self.frame('cg', beat.get('caption', ''))
                f['meta']['cg'] = beat['img']
                return f
            if t == 'effect':
                self.apply_effect(beat)
                self.beat_idx += 1
                continue
        # 场景结束
        return self.end_scene()

    def _join_stage(self, char_id):
        """角色登台：有立绘/人设的角色因台词或 cast_add 出现在场上。"""
        if char_id and char_id != 'shuuji' and char_id not in self.present \
                and (char_id in PERSONAS or char_id in CHAR_NAME):
            self.present.append(char_id)

    def _ending_card(self):
        eid = self.world.flags.get('ending')
        if not eid:
            return None
        return {'id': eid, 'title': ENDINGS_TITLE.get(eid, eid),
                'subtitle': ENDING_SUBTITLE.get(getattr(self, 'last_ending_scene', ''))}

    def _apply_axes(self, opt, label=''):
        for k, v in (opt.get('axis') or {}).items():
            self.world.add_axis(k, v, (label or opt.get('label', ''))[:24])

    def _score_frame(self, text):
        """自由输入打分：应用三轴增量，有偏移则返回内心独白帧。"""
        d = axis_score.score_axes(text)
        applied = False
        for k in axis_score.AXES:
            if d.get(k):
                self.world.add_axis(k, d[k], '自由输入')
                applied = True
        if not applied:
            return None
        return self.frame('narration', axis_score.inner_voice(d, text))

    # ---------------------------------------------------------------- 记忆流（C1）/ 反思（C2）
    def _remember(self, char_id, content, kind='episode', importance=None):
        """写入角色记忆流并累积反思能量。"""
        if not settings.MEMORY_ON or char_id not in self.world.memory:
            return
        e = self.world.memory[char_id].add(content, kind=kind, day=self.world.day,
                                           importance=importance)
        if e is not None:
            self._remembered.add(char_id)
            self.world.reflect_points[char_id] = \
                self.world.reflect_points.get(char_id, 0.0) + e.importance

    def _remember_beat(self, beat):
        """场景台词节拍 → 在场角色的记忆流（说话者自传式，他人旁听式）。"""
        speaker = beat['who']
        name = CHAR_NAME.get(speaker, speaker)
        for c in self.present:
            if c != speaker:
                self._remember(c, '%s说：%s' % (name, beat['say']))
        self._remember(speaker, '我说：%s' % beat['say'])

    def _maybe_reflect(self):
        """C2：场景结束时检查反思能量槽，达阈值则生成洞察写回记忆流。"""
        if not settings.REFLECT_ON:
            return
        w = self.world
        # 候选 = 本场景被写入过记忆的角色 ∪ 有知识条目的镇民（退场者不漏）
        cands = set(getattr(self, '_remembered', set())) | \
            {c for c in ('relative_man', 'relative_woman', 'toba') if w.knowledge.get(c)}
        for char in sorted(cands):
            if char not in w.memory:
                continue
            if w.reflect_points.get(char, 0.0) >= memory_mod.REFLECT_THRESHOLD:
                w.reflect_points[char] = 0.0
                insights = memory_mod.reflect(char, w, w.memory[char])
                if insights:
                    w.emit('reflection', {'char': char, 'insights': insights})
                    log('反思（%s）：%s' % (CHAR_NAME.get(char, char), '／'.join(insights)))

    def apply_effect(self, beat):
        w = self.world
        if 'flags' in beat:
            w.flags.update(beat['flags'])
        if beat.get('affection'):
            w.miyuki_affection_extra += beat['affection']
            w.change_relation('shuuji', 'miyuki', beat['affection'], 0, 'scene effect')
        if 'location' in beat:
            w.location = beat['location']
            w.emit('player_move', {'to': beat['location']})
        if 'time' in beat:
            w.time_slot = beat['time']
        if 'bg' in beat:
            w.flags['_bg_override'] = beat['bg']
        if beat.get('daily_inc'):
            w.flags['daily_life_count'] = w.flags.get('daily_life_count', 0) + 1
        for k, v in (beat.get('axis') or {}).items():
            w.add_axis(k, v, 'scene:' + str(self.scene_id))
        for c in (beat.get('cast_add') or []):
            self._join_stage(c)
        for c in (beat.get('cast_remove') or []):
            if c in self.present:
                self.present.remove(c)

    def end_scene(self):
        w = self.world
        sid = self.scene_id
        w.emit('scene_end', {'scene': sid})
        # 知识目击（事件 → 目击者知识库，供八卦传播）
        self._witness(sid)
        self._maybe_reflect()      # C2：重要经历累积 → 反思 → 洞察
        trans = TRANSITIONS.get(sid, {})
        if trans.get('day') is not None and trans['day'] > w.day:
            skipped = trans['day'] - w.day
            w.day = trans['day']
        if trans.get('countdown') is not None:
            w.festival_countdown = trans['countdown']
        # 场景结束 → 幕间；后续由 director 按分支图路由
        self.mode = 'interlude'
        self.scene_id = None
        # 结局场景保留最后一幕的背景（结局卡与终幕一致）；普通场景清除，回落地点默认图
        if sid not in ENDINGS:
            w.flags.pop('_bg_override', None)
        if sid == 'P6':
            w.flags['time_skip'] = True
        # 结局吸收态：终幕场景进入后导演不再推进
        ending_id = ENDINGS.get(sid)
        if ending_id:
            w.flags['ending'] = ending_id
            self.last_ending_scene = sid
            w.emit('ending_reached', {'ending': ending_id, 'axes': dict(w.axes)})
        nxt = self.director.route()
        hint = self._interlude_hint(nxt)
        f = self.frame('interlude', '', note=hint)
        return f

    def _witness(self, sid):
        w = self.world
        if sid == 'P1':
            for r in ('relative_man', 'relative_woman'):
                w.know(r, 'girl_took_shuuji', '亲戚会议上，一个来历不明的黑长发女孩把修二牵出了庭院看雪。')
        elif sid == 'P2':
            w.know('shuuji', 'miyuki_comforted', '清雪时我哭了，她抱住了我，说「想哭就哭出来吧」。')
        elif sid == 'P3':
            w.know('shuuji', 'miyuki_claims_sister', '她自称是我的姐姐，还在雪仗里把我打得落花流水。')
        elif sid == 'P7':
            w.know('shuuji', 'miyuki_waited_3y', '三年过去，她仍守在老屋里等着我。')
        elif sid == 'P10':
            w.know('shuuji', 'leaving_again', '我又一次离开了雪国。她在站台上朝我挥手。')

    def _interlude_hint(self, nxt):
        w = self.world
        if w.flags.get('ending'):
            t = ENDINGS_TITLE.get(w.flags['ending'], w.flags['ending'])
            sub = ENDING_SUBTITLE.get(getattr(self, 'last_ending_scene', ''))
            if sub:
                t += ' · ' + sub
            return '【结局达成 · ' + t + '】雪还在下。你可以在回忆里继续漫步，也可以随时开始新的故事。'
        if nxt == 'P7':
            return '三年后——你再次踏上了归乡的列车。（剧情将自动推进）'
        if nxt == 'P4' and w.festival_countdown <= 0:
            return '祭典之夜临近了。镇上灯火渐次亮起……（前往参道即可遇上祭典）'
        if nxt == 'P11':
            return '又一次离别。站台上今天没有别人——路，要自己选了。（你说的每一句话，都在决定故事的去向）'
        if nxt is None:
            return '雪还在下。你可以继续在雪国漫步。'
        return '雪还在下。你可以四处走走、找人说话，或等待时间流逝。（「等待/过夜」推进时间）'

    # ---------------------------------------------------------------- 幕间自由行动
    def interlude_act(self, action, payload=None):
        payload = payload or {}
        w = self.world
        w.season_pressure = min(60, w.season_pressure + 6)
        # C7：一次性登台名单先清空，再采集行为特征、求解引导策略
        self.director.extra_present = []
        self.director.on_interlude(action)
        guide = guide_mod.guide(self.director) if settings.GUIDE_V2 else None
        if guide and guide['strategy'] == 'npc_redirect':
            self.director.extra_present = list(guide['payload'].get('chars') or ['miyuki'])
        if action == 'move':
            to = payload.get('to')
            loc = LOCATIONS.get(w.location, {})
            if to not in loc.get('adjacent', []):
                return self._after_interlude(self.frame('interlude', '', note='那里太远了，一次走不到。'))
            w.location = to
            w.emit('player_move', {'to': to})
            note = LOCATIONS[to]['name'] + '。' + rule_engine.narrate()
            if guide:
                note = guide['note']
            # 特殊地点触发
            if to == 'shrine_road' and w.flags.get('accepted_sister') is False and w.festival_countdown <= 0 and w.phase == 'P3':
                pass
            return self._after_interlude(self.frame('interlude', '', note=note))
        if action == 'talk':
            text = (payload.get('text') or '').strip()
            if not text:
                return self._after_interlude(self.frame('interlude', '', note='你想说什么？'))
            chars = self.director.present_chars()
            target = 'miyuki' if 'miyuki' in chars else (chars[1] if len(chars) > 1 else None)
            if target is None:
                return self._after_interlude(self.frame('interlude', '', note='这里没有可以说话的人。只有雪落在肩上的声音。'))
            w.emit('player_say', {'to': target, 'text': text})
            self._remember(target, '修二说：%s' % text)      # C1：玩家的话进入对方记忆
            its = rule_engine.classify(text)
            if its and its[0] in ('ask_mystery', 'ask_identity'):
                self.director.note_mystery_probe()           # C7：谜团话头计数
            resp = self._agentRespond(target, text)
            f = self.frame('line', resp['say'], target, resp.get('expr'), resp.get('action', ''))
            f['src'] = resp.get('src')
            self.history.append({'name': '修二', 'text': text, 'action': ''})
            frames = [f]
            voice = self._score_frame(text)
            if voice:
                frames.append(voice)
            frames[-1] = self._after_interlude(frames[-1])
            return frames if len(frames) > 1 else frames[0]
        if action == 'wait':
            w.day += 1
            w.season_pressure += 10
            if w.festival_countdown > 0:
                w.festival_countdown -= 1
            w.time_slot = 'day'
            if settings.RUMOR_STRENGTH:
                w.tick_rumors()      # C8：传闻热度每日衰减
            new_rumors = gossip.run_daily_gossip(
                w, use_llm=bool(settings.RUMOR_STRENGTH and LLM.available and not LLM.rate_limited))
            w.emit('day_end', {'day': w.day, 'rumors': len(new_rumors)})
            rumor_note = ''
            if new_rumors:
                rumor_note = '（镇子上，有人在传：「%s」）' % new_rumors[0]['content']
            note = f'第 {w.day} 天。雪又积了一层。{rule_engine.narrate()}{rumor_note}'
            if guide:
                note = guide['note'] + rumor_note
            return self._after_interlude(self.frame('interlude', '', note=note))
        if action == 'state':
            return self._after_interlude(self.frame('interlude', '', note='（当前：{}）'.format(LOCATIONS[w.location]['name'])))
        return self._after_interlude(self.frame('interlude', '', note='……'))

    def _after_interlude(self, f):
        """幕间行动后：检查导演是否要推进剧情。"""
        w = self.world
        nxt = self.director.should_advance()
        if nxt is None and getattr(self.director, 'pending_force', None):
            # C7 时机调整型：仅差地点的吸引子已就绪，给出"事件上门"入口
            f['meta']['scene_offer'] = self.director.pending_force
            f['meta']['scene_offer_title'] = SCENES[self.director.pending_force]['title']
            return f
        if nxt is None and w.phase == 'P6' and w.flags.get('time_skip'):
            # 三年跳跃后自动进入 P7
            nxt = 'P7'
        if nxt:
            f['meta']['scene_offer'] = nxt
            f['meta']['scene_offer_title'] = SCENES[nxt]['title']
        return f

    # ---------------------------------------------------------------- 玩家输入（场景内）
    def submit_input(self, text=None, choice_index=None):
        """choice/free beat 的输入。返回帧列表。

        决策节拍（选项带 flag，如 P11/P12B 的分叉选择）不可被自由输入跳过：
        输入若命中某选项的 intents 则视同选择该选项；否则只做角色对演，选择仍待玩家按下。
        """
        frames = []
        beat = self.pending_choices
        if beat is None:
            return [self.frame('error', '', note='当前没有待选择的输入。')]
        is_free = beat.get('free')
        w = self.world

        # 1) 自由输入（free beat，或选择节拍里玩家打字）
        if is_free or (text not in (None, '') and choice_index is None):
            text = (text or '').strip() or '……'
            if not is_free and beat.get('options'):
                intents = rule_engine.classify(text)
                matched = None
                for o in beat['options']:
                    if o.get('intents') and set(intents) & set(o['intents']):
                        matched = o
                        break
                frames.append(self.frame('me', text, 'shuuji'))
                w.emit('player_say', {'scene': self.scene_id, 'text': text})
                for c in self.present:                 # C1：玩家的话进入在场角色记忆
                    if c != 'shuuji':
                        self._remember(c, '修二说：%s' % text)
                if matched:
                    # 视同选择了该选项（门控/轴/flag 全流程生效）
                    voice = self._score_frame(text)
                    if voice:
                        frames.append(voice)
                    resp = self._agentRespond('miyuki', text)
                    lf = self.frame('line', resp['say'], 'miyuki', resp.get('expr'), resp.get('action', ''))
                    lf['src'] = resp.get('src')
                    frames.append(lf)
                    return self._resolve_choice(beat, matched, frames)
                if any(o.get('flag') for o in beat['options']):
                    # 决策节拍：对演归对演，分叉必须由玩家明确选择
                    voice = self._score_frame(text)
                    if voice:
                        frames.append(voice)
                    resp = self._agentRespond('miyuki', text)
                    lf = self.frame('line', resp['say'], 'miyuki', resp.get('expr'), resp.get('action', ''))
                    lf['src'] = resp.get('src')
                    frames.append(lf)
                    frames.append(self.frame('narration', '（心意已经传达到了。但脚下的路，还是要自己选的。）'))
                    frames.append(self.frame('choice', '', choices=beat['options']))
                    return frames
            # free beat 或无 flag 的普通选择节拍：吸收意图继续（原行为）
            intents = rule_engine.classify(text)
            label = text
            frames.append(self.frame('me', label, 'shuuji'))
            w.emit('player_say', {'scene': self.scene_id, 'text': label})
            for c in self.present:                     # C1：玩家的话进入在场角色记忆
                if c != 'shuuji':
                    self._remember(c, '修二说：%s' % label)
            voice = self._score_frame(label)
            if voice:
                frames.append(voice)
            resp = self._agentRespond('miyuki', label)
            lf = self.frame('line', resp['say'], 'miyuki', resp.get('expr'), resp.get('action', ''))
            lf['src'] = resp.get('src')
            frames.append(lf)
            self.pending_choices = None
            self.beat_idx += 1
            # 回应独占一屏：她的回应不被下一拍覆盖；下一次 advance 才继续剧情
            return frames

        # 2) 点击选项
        if choice_index is not None:
            opts = beat.get('options') or []
            if choice_index >= len(opts):
                return [self.frame('error', '', note='没有这个选项。')]
            opt = opts[choice_index]
            frames.append(self.frame('me', opt.get('label') or '……', 'shuuji'))
            w.emit('player_say', {'scene': self.scene_id, 'text': opt.get('label') or ''})
            for c in self.present:                     # C1：正典选项也被在场角色记住
                if c != 'shuuji':
                    self._remember(c, '修二说：%s' % (opt.get('label') or '……'))
            return self._resolve_choice(beat, opt, frames)
        return [self.frame('error', '', note='输入为空。')]

    def _resolve_choice(self, beat, opt, frames):
        """结算一个选项：门控落空 → 剧情化拒绝并回落；正常 → 效果结算并推进。"""
        w = self.world
        req = opt.get('requires')
        conds = req if isinstance(req, list) else ([req] if req else [])
        if conds and not all(eval_cond(c, w) for c in conds):
            frames.append(self.frame('narration', opt.get('fail_text') or '（话没能说完整。）'))
            if opt.get('fail_flag'):
                w.flags[opt['fail_flag']] = True
            if opt.get('fallback_flag'):
                w.flags[opt['fallback_flag']] = True
            self.pending_choices = None
            self.beat_idx += 1
            # 回应独占一屏：她的回应不被下一拍覆盖；下一次 advance 才继续剧情
            return frames
        if opt.get('affection'):
            w.miyuki_affection_extra += opt['affection']
            w.change_relation('shuuji', 'miyuki', opt['affection'], 0, opt.get('label', ''))
        if opt.get('flag'):
            w.flags[opt['flag']] = True
        self._apply_axes(opt, opt.get('label', ''))
        self.pending_choices = None
        self.beat_idx += 1
        frames.append(self.step())
        return frames

    # ---------------------------------------------------------------- Agent 应答（LLM 优先，规则兜底）
    def _agentRespond(self, char_id, text):
        w = self.world
        if LLM.available:
            persona = persona_card(char_id)
            kb_entries = list(w.knowledge[char_id].values())
            kb = [v.content for v in kb_entries][:8]
            scene = self.director.scene_desc()
            canon = (canon_mod.retrieve_canon(w.phase, text, char_id)
                     if settings.CANON_INJECT else None)
            # C8：传闻回流（仅镇民角色；深雪几乎不与人往来，不引用镇上闲话）
            rumors = (gossip.rumors_for_prompt(char_id, w)
                      if (settings.RUMOR_STRENGTH and char_id in ('toba', 'relative_man', 'relative_woman'))
                      else None)
            last_say, last_issues = None, None
            for attempt in range(2):
                try:
                    memories = self._memories_for(char_id, text)   # C1：三因子检索（或旧行为回落）
                    prompt = assemble_prompt(persona, w, char_id, memories, scene, kb,
                                             canon=canon, rumors=rumors)
                    if STAGE_NOTES.get(w.phase):
                        prompt += '\n\n【阶段约束（最高优先级，覆盖上述一切暗示）】\n' + STAGE_NOTES[w.phase]
                    if last_issues and settings.FEEDBACK_RETRY:
                        prompt += ('\n\n【上一次回应未通过设定校验，必须修正】\n'
                                   '上次回应：「%s」\n问题：\n- %s\n'
                                   '请重新输出（保持一行 JSON 格式），不要重蹈以上问题。'
                                   % (last_say, '\n- '.join(last_issues)))
                    out = LLM.chat(prompt, '玩家（修二）说：「%s」\n请以角色身份回应。' % text,
                                   temperature=0.7 if attempt == 0 else 0.4)
                    obj = json.loads(out[out.find('{'):out.rfind('}') + 1])
                    say = obj.get('say', out)
                    issues = guardrails.explain(char_id, say, w.phase)
                    if not issues:
                        self._remember(char_id, '我说：%s' % say)   # C1：自传式记忆
                        if rumors and obj.get('heard'):
                            gossip.strengthen(w, char_id)          # C8：引用传闻 → 热度上升
                            w.emit('rumor_referenced', {'char': char_id})
                        return {'say': say, 'expr': obj.get('expression', 'normal'),
                                'action': obj.get('action', ''), 'effects': {}, 'src': 'llm'}
                    last_say, last_issues = say, issues
                    w.emit('llm_retry', {'char': char_id, 'issues': issues,
                                         'attempt': attempt + 1})
                except Exception as e:
                    log('LLM 调用失败（%s 第%d次）：%s' % (char_id, attempt + 1, e))
                    break   # 网络/超时/限流等异常：重试只会让玩家等更久，立即回落规则引擎
            if last_issues:
                log('护栏拦截（%s）：%s ｜ 「%s」' % (char_id, '；'.join(last_issues), last_say))
        resp = rule_engine.respond(char_id, text, w)
        resp['src'] = 'rules'
        # 规则兜底输出也过一遍护栏（防御性；违规替换为安全句）
        if guardrails.validate(char_id, resp.get('say', ''), w.phase):
            log('规则兜底输出违规（%s）：%s' % (char_id, resp.get('say', '')))
            resp['say'] = '……'
            resp['expr'] = 'normal'
        self._remember(char_id, '我说：%s' % resp.get('say', ''))      # C1：自传式记忆
        eff = resp.get('effects') or {}
        if eff.get('affection'):
            w.miyuki_affection_extra += eff['affection']
            w.change_relation('shuuji', 'miyuki', eff['affection'], 0, text)
        if eff.get('flag'):
            w.flags[eff['flag']] = True
        return resp

    def _memories_for(self, char_id, text):
        """C1：记忆流三因子检索；关闭/为空时回落知识库切片（旧行为）。"""
        if settings.MEMORY_ON:
            mems = self.world.memory_retrieve(char_id, text, k=6)
            if mems:
                return mems
        return [v.content for v in self.world.knowledge[char_id].values()][-6:]

    # ---------------------------------------------------------------- 推进入口
    def advance(self):
        if self.mode == 'scene':
            if self.pending_choices:
                return [self.last_frame]
            return [self.step()]
        return [self._after_interlude(self.frame('interlude', '', note='雪还在下。'))]

    def enter_offered_scene(self):
        nxt = self.director.should_advance()
        if nxt is None and getattr(self.director, 'pending_force', None):
            # C7 时机调整型：事件上门——把玩家带到场景地点再进入
            nxt = self.director.pending_force
            self.world.location = SCENES[nxt].get('location', self.world.location)
        if nxt is None and self.world.flags.get('time_skip') and self.world.phase == 'P6':
            nxt = 'P7'
        if nxt is None:
            return [self.frame('error', '', note='现在还没有到剧情推进的时机。')]
        return self.enter_scene(nxt)

    # ---------------------------------------------------------------- 存档
    def save(self, slot='auto'):
        data = {
            'ts': time.time(),
            'world': self.world.to_dict(),
            'engine': {
                'mode': self.mode, 'scene_id': self.scene_id,
                'beat_idx': self.beat_idx,
                'history': self.history[-200:],
            },
        }
        path = os.path.join(SAVE_DIR, '%s.json' % slot)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        # 事件溯源日志
        with open(os.path.join(SAVE_DIR, 'events_%s.jsonl' % slot), 'a', encoding='utf-8') as f:
            for ev in self.world.events:
                f.write(json.dumps(ev.to_dict(), ensure_ascii=False) + '\n')
        self.world.events = []
        return path

    def load(self, slot='auto'):
        path = os.path.join(SAVE_DIR, '%s.json' % slot)
        if not os.path.exists(path):
            raise FileNotFoundError(slot)
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        self.world.load(data['world'])
        self.director = Director(self.world)
        e = data['engine']
        self.mode = e['mode']
        self.scene_id = e['scene_id']
        self.beat_idx = e['beat_idx']
        self.history = e.get('history', [])
        self.pending_choices = None
        if self.mode == 'scene':
            return [self.frame('scene_title', '', note=SCENES.get(self.scene_id, {}).get('title', '')),
                    self.step()]
        return [self.frame('interlude', '', note='（读取存档：继续你的故事）')]
