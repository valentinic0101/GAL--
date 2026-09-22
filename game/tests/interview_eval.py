# -*- coding: utf-8 -*-
"""C5：采访式角色一致性评测基准。

方法依据（《资料/06_开发与评审/开发文档_C5》）：
- Generative Agents：采访提纲 25 题 × 5 类，把"角色立没立住"变成可评测问题；
- 千人分身：重测一致性归一——先给"正典参考回应"打分得到上限 S_max、
  无 persona 的裸模型得到下限 S_base，一致性指数 = (S_agent-S_base)/(S_max-S_base)；
- SOTOPIA：LLM judge 必须报告与人评校准情况；未校准前只信规则轨。

用法：
  python3 tests/interview_eval.py --offline            # 规则轨（进 CI）
  python3 tests/interview_eval.py --llm                # judge 轨（手动/每周）
  python3 tests/interview_eval.py --llm --ablate memory    # 消融：关记忆检索
  python3 tests/interview_eval.py --llm --ablate stage_notes
  python3 tests/interview_eval.py --llm --ablate canon
输出：reports/eval_report.md + reports/eval_history.jsonl
"""
import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'server'))

from agents import guardrails, rule_engine            # noqa: E402
from agents import canon as canon_mod                 # noqa: E402
from agents.llm import LLM, assemble_prompt           # noqa: E402
from agents.personas import persona_card              # noqa: E402
from director.director import Director                # noqa: E402
from world.world import World                         # noqa: E402
from scenes.script import SCENES                      # noqa: E402

DATA = os.path.join(ROOT, 'tests', 'data', 'interview_miyuki.json')
DOCS = os.path.join(ROOT, 'reports')

JUDGE_SYSTEM = (
    '你是视觉小说角色扮演的评测员。给你角色设定摘要、问题与角色的回答，'
    '按 5 个维度各打 1~5 分（整数）：'
    '称谓正确（对男主用「小修」等设定称谓）、语言风格（短句+句尾语气词，不文艺）、'
    '人设符合（恒定温柔、不解释身世、不愤怒不责备）、'
    '谜团合规（不解释她是什么/从何而来）、整体印象。'
    '只输出一行 JSON：{"称谓":n,"语言":n,"人设":n,"谜团":n,"整体":n}')

PERSONA_BRIEF = (
    '角色设定摘要：深雪，自称男主修二的姐姐（年长两岁），恒定温柔、气定神闲，'
    '三不原则（不解释、不辩论、不愤怒）；称男主为「小修」，自称「姐姐」/「我」；'
    '短句+句尾语气词（哦/呢/啦/嘛/吧/――）；绝不解释自己的来历与身份（谜团锁），'
    '被问只能真心不解/沉默/微笑/「我会在那里，一直等啊。一直」。')


def load_questions():
    with open(DATA, encoding='utf-8') as f:
        data = json.load(f)
    out = []
    for cat in data['categories']:
        for q in cat['questions']:
            out.append({'cat': cat['name'], 'q': q['q'], 'canon': q['canon'],
                        'stage': q['stage'], 'rule': q.get('rule', '')})
    return out


def build_world(stage):
    """构造采访所在的最小世界状态（离线确定性）。"""
    w = World()
    w.phase = stage
    w.day = 1000 if stage in ('P7', 'P8', 'P9', 'P10', 'E_STAY', 'E_SPRING', 'P12B') else 5
    for f in ('met_miyuki', 'likes_snow', 'snowball_fight', 'comforted', 'height_marked',
              'left_town', 'knows_name', 'reunion_done', 'daily_life', 'height_remarked'):
        w.flags[f] = True
    return w


def ask(question, stage, world, ablate=None):
    """单题提问：LLM 可用走真 agent 管线；离线走规则引擎。返回 (reply, src)。"""
    ablate = ablate or set()
    if LLM.available and not LLM.rate_limited:
        persona = persona_card('miyuki')
        memories = ([] if 'memory' in ablate
                    else world.memory_retrieve('miyuki', question, k=6))
        kb = [v.content for v in world.knowledge['miyuki'].values()][:8]
        scene = Director(world).scene_desc()
        canon = None if 'canon' in ablate else canon_mod.retrieve_canon(stage, question, 'miyuki')
        prompt = assemble_prompt(persona, world, 'miyuki', memories, scene, kb, canon=canon)
        if stage in STAGE_NOTES and 'stage_notes' not in ablate:
            prompt += '\n\n【阶段约束（最高优先级，覆盖上述一切暗示）】\n' + STAGE_NOTES[stage]
        try:
            out = LLM.chat(prompt, '（采访提问）「%s」\n请以角色身份回应。' % question,
                           temperature=0.7, max_tokens=300)
            obj = json.loads(out[out.find('{'):out.rfind('}') + 1])
            return obj.get('say', out), 'llm'
        except Exception:
            pass
    r = rule_engine.respond('miyuki', question, world)
    return r['say'], 'rules'


STAGE_NOTES = {
    'P5': '他仍不知你的名字；你尚未对他说过身份宣言以外的心里话。',
    'P7': '三年后重逢。他已长大；你一如既往。',
    'P8': '老屋同居日常。',
    'P9': '归省最后一夜。',
    'P12B': '田间小路上的最后散步。',
    'E_SPRING': '春天，樱花开了。被问到为何在，只以「因为约好了呀」带过。',
}


def judge_score(reply, question):
    """LLM judge 五维 1~5。失败返回 None。"""
    try:
        out = LLM.chat(JUDGE_SYSTEM,
                       '【角色摘要】%s\n【采访问题】%s\n【角色回答】%s'
                       % (PERSONA_BRIEF, question, reply),
                       temperature=0.1, max_tokens=80)
        obj = json.loads(out[out.find('{'):out.rfind('}') + 1])
        vals = [int(re.findall(r'-?\d+', str(obj.get(k, 3)))[0]) for k in
                ('称谓', '语言', '人设', '谜团', '整体')]
        return [max(1, min(5, v)) for v in vals]
    except Exception:
        return None


import re  # noqa: E402  (judge_score 用)


def run(llm_mode=False, ablate=None):
    qs = load_questions()
    results = []
    LLM.enabled = True if llm_mode else LLM.enabled
    if llm_mode and not LLM.available:
        print('[warn] 未配置 LLM key，退化为离线规则轨')
        llm_mode = False
        LLM.enabled = False

    for q in qs:
        world = build_world(q['stage'])
        reply, src = ask(q['q'], q['stage'], world, ablate)
        issues = guardrails.check_miyuki(reply, q['stage'])
        row = {'cat': q['cat'], 'q': q['q'], 'reply': reply, 'src': src,
               'issues': issues, 'pass': not issues, 'judge': None}
        if llm_mode:
            row['judge'] = judge_score(reply, q['q'])
        results.append(row)

    summary = summarize(qs, results, llm_mode, ablate)
    report(qs, results, summary, llm_mode, ablate)
    return summary


def summarize(qs, results, llm_mode, ablate):
    hard_pass = sum(1 for r in results if r['pass'])
    s = {'n': len(results), 'hard_pass': hard_pass,
         'hard_rate': round(hard_pass / max(1, len(results)), 3),
         'ablate': sorted(ablate or []), 'mode': 'llm' if llm_mode else 'offline',
         'ts': time.strftime('%Y-%m-%d %H:%M:%S')}
    if llm_mode:
        dims = list(zip(*[r['judge'] for r in results if r['judge']])) or None
        if dims:
            s['judge_avg'] = [round(sum(d) / len(d), 2) for d in dims]
            s['judge_total'] = round(sum(s['judge_avg']) / len(s['judge_avg']), 2)
        # 归一：上限=正典参考回应、下限=裸模型（无 persona）
        s_max = _avg_judge([q['canon'] for q in qs], qs)
        s_base = _avg_judge([q['q'] for q in qs], qs, bare=True)
        if s_max and s_base:
            s['s_max'], s_base_v = round(s_max, 2), round(s_base, 2)
            s['s_base'] = s_base_v
            if s.get('judge_total') is not None and s_max > s_base_v:
                s['index'] = round((s['judge_total'] - s_base_v) / (s_max - s_base_v) * 100, 1)
    return s


def _avg_judge(replies, qs, bare=False):
    """给一组回应打 judge 平均分（bare=True 时不带人设摘要，测下限）。"""
    scores = []
    for q, reply in zip(qs, replies):
        if bare:
            out = None
            try:
                out = LLM.chat('请以普通聊天助手身份回答下面这句话。',
                               q['q'], temperature=0.7, max_tokens=120)
            except Exception:
                return None
            j = judge_score(out or '……', q['q'])
        else:
            j = judge_score(reply, q['q'])
        if j:
            scores.append(sum(j) / len(j))
    return sum(scores) / len(scores) if scores else None


def report(qs, results, summary, llm_mode, ablate):
    os.makedirs(DOCS, exist_ok=True)
    lines = ['# 角色一致性采访评测报告', '',
             '- 时间：%s ｜ 模式：%s ｜ 消融：%s' % (summary['ts'], summary['mode'],
                                                summary['ablate'] or '无'),
             '- 规则硬断言：**%d/%d 通过（%.0f%%）**' % (summary['hard_pass'], summary['n'],
                                                    summary['hard_rate'] * 100)]
    if 'judge_avg' in summary:
        lines.append('- LLM judge 五维均分：%s ｜ 总均分 %s' %
                     (summary['judge_avg'], summary.get('judge_total')))
    if 'index' in summary:
        lines.append('- **一致性指数：%s%%**（上限 S_max=%s，下限 S_base=%s）' %
                     (summary['index'], summary.get('s_max'), summary.get('s_base')))
    lines.append('')
    lines.append('| 类别 | 问题 | 回应 | 来源 | 硬断言 |')
    lines.append('|---|---|---|---|---|')
    for r in results:
        lines.append('| %s | %s | %s | %s | %s |' % (
            r['cat'], r['q'], (r['reply'] or '')[:40].replace('|', '，'),
            r['src'], '✅' if r['pass'] else '❌' + str(r['issues'][:2])))
    with open(os.path.join(DOCS, 'eval_report.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    with open(os.path.join(DOCS, 'eval_history.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(summary, ensure_ascii=False) + '\n')
    print('\n'.join(lines[:6]))
    print('[report] reports/eval_report.md 已更新')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--llm', action='store_true', help='启用 LLM judge 轨（默认离线规则轨）')
    ap.add_argument('--offline', action='store_true', help='离线规则轨（默认）')
    ap.add_argument('--ablate', choices=['memory', 'stage_notes', 'canon'], default=None,
                    help='消融某组件，观察指数掉多少')
    args = ap.parse_args()
    ablate = {args.ablate} if args.ablate else set()
    if not args.llm:
        LLM.enabled = False
    s = run(llm_mode=args.llm, ablate=ablate)
    # CI 门槛（仅离线规则轨）：硬断言必须全过
    ok = (not args.llm) and s['hard_pass'] == s['n'] or args.llm
    sys.exit(0 if ok else 1)
