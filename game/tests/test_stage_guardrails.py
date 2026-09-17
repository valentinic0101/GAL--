# -*- coding: utf-8 -*-
"""C3 阶段硬护栏回归：身份宣言/名字泄漏按阶段拦截，白名单不豁免阶段锁。

运行：python3 tests/test_stage_guardrails.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'server'))

from agents import guardrails                                    # noqa: E402
from agents.llm import LLM                                       # noqa: E402

LLM.enabled = False

PASS = FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print('  [pass]', name)
    else:
        FAIL += 1
        print('  [FAIL]', name, detail)


def has(issues, key):
    return any(i.startswith(key) for i in issues)


# ---- C3-1 身份宣言：P1/P2 硬拦，P3 合法 ----
check('P1 身份宣言被拦', has(guardrails.check_miyuki('我是你的姐姐啊，小修', 'P1'),
                           'identity_declaration_early'))
check('P2 身份宣言被拦', has(guardrails.check_miyuki('你的姐姐哦', 'P2'),
                           'identity_declaration_early'))
check('P3 身份宣言合法（正典节拍）', not guardrails.check_miyuki('你的姐姐啊', 'P3'))
check('P7 提及姐姐身份不拦（身份已确立）', not has(guardrails.check_miyuki('姐姐不是说过了吗，会在这里等你', 'P7'),
                                             'identity_declaration_early'))

# ---- C3-2 名字泄漏：P1~P5 硬拦，P6 合法 ----
check('P5 名字泄漏被拦', has(guardrails.check_miyuki('写作深和雪两个字，miyuki', 'P5'), 'name_leak_early'))
check('P6 名字揭示合法', not guardrails.check_miyuki('写作深和雪两个字，miyuki', 'P6'))
check('P3 白名单台词（旧名场面）不因白名单绕过阶段锁',
      has(guardrails.check_miyuki('miyuki', 'P3'), 'name_leak_early'))

# ---- C3-3 雪女：只许唤名 ----
check('雪女唤名合法', not guardrails.check_yukihime('修二――――'))
check('雪女普通对话被拦', guardrails.check_yukihime('小修，欢迎回来') != [])
check('雪女校验接入 validate', guardrails.validate('yukihime', '你好啊', 'P0') != [])

# ---- C3-4 白名单语义保持：全阶段台词不受影响 ----
check('白名单全阶段台词合法', not guardrails.check_miyuki('我没有骗你', 'P1'))
check('白名单台词阶段外不再豁免风格检查',
      guardrails.check_miyuki('拉～勾！', 'P1') == [] or
      not has(guardrails.check_miyuki('拉～勾！', 'P1'), 'forbidden'))

# ---- C3-5 谜团锁不回退 ----
check('谜团泄漏仍被拦', has(guardrails.check_miyuki('其实我是雪女哦', 'P7'), 'mystery_leak') or
      has(guardrails.check_miyuki('其实我是雪女哦', 'P7'), 'forbidden'))

# ---- C4 explain：违规解释为人话 ----
ex = guardrails.explain('miyuki', '其实我是雪女哦', 'P7')
check('explain 返回非空且为中文', bool(ex) and any('谜团' in e or '禁忌' in e for e in ex), ex)
ex2 = guardrails.explain('miyuki', '我是你的姐姐啊', 'P1')
check('explain 解释阶段锁', any('身份宣言' in e for e in ex2), ex2)


if __name__ == '__main__':
    print('== C3/C4 护栏回归 ==')
    print('RESULT: %d passed, %d failed' % (PASS, FAIL))
    sys.exit(1 if FAIL else 0)
