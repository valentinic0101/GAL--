# -*- coding: utf-8 -*-
"""LLM 实链路测试：真实调用 DeepSeek，验证 Agent 应答来源与护栏。

流程：P1 自由输入点一句 + 幕间交谈三句（含谜团锁探测）。
（不进 supervisor 周期任务，避免持续消耗 API 额度。）
"""
import json
import sys
import urllib.request

BASE = 'http://127.0.0.1:8300'


def call(path, body=None):
    if body is None:
        req = urllib.request.Request(BASE + path)
    else:
        req = urllib.request.Request(BASE + path,
                                     data=json.dumps(body).encode(),
                                     headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def answered(frames):
    """取带 src 标记的应答帧（LLM/规则引擎即兴应答）。"""
    for f in frames:
        if f.get('kind') == 'line' and f.get('src'):
            return f
    return None


def main():
    st = call('/api/state')
    llm_on = (st.get('meta') or {}).get('llm')
    print('[info] 服务器 LLM 状态:', llm_on)
    assert llm_on, 'LLM 未生效：请检查 game/llm.json 并重启服务器'

    # ---- 场景内自由输入（P1）
    call('/api/new', {})
    for _ in range(40):
        f = call('/api/state')
        if f['kind'] == 'free':
            break
        call('/api/advance', {})
    assert f['kind'] == 'free', '未到自由输入点: %s' % f['kind']
    scene_probe = '你放……放开我……你是谁啊'
    r = call('/api/input', {'text': scene_probe})
    results = [('P1·场景内', scene_probe, answered(r['frames']))]

    # ---- 走完 P1 进入幕间，然后逐句交谈
    for _ in range(60):
        f = call('/api/state')
        if f['kind'] == 'interlude':
            break
        if f['kind'] == 'choice':
            call('/api/input', {'choice_index': 0}); continue
        if f['kind'] == 'free':
            call('/api/input', {'text': '……'}); continue
        call('/api/advance', {})
    assert f['kind'] == 'interlude', '未进入幕间: %s' % f['kind']

    talk_probes = [
        '你到底是人是鬼？是雪女吧！',     # 谜团锁探测
        '呐……你平时都一个人住在这吗？',   # 身世试探（软）
        '我喜欢这雪，你呢？',             # 日常
    ]
    for text in talk_probes:
        r = call('/api/act', {'action': 'talk', 'text': text})
        results.append(('幕间·交谈', text, answered(r['frames'])))

    pass_n = fail_n = llm_n = 0
    for where, text, resp in results:
        if resp is None:
            print('[FAIL] %s 无应答帧: %s' % (where, text))
            fail_n += 1
            continue
        src, say = resp.get('src'), resp['text']
        if src == 'llm':
            llm_n += 1
        leak = any(k in say for k in ('我是雪女', '我不是人类', '我其实已经', '雪女的真身',
                                       '我死在这里', '我是幽灵', '我是妖怪'))
        ok = (not leak) and len(say) > 0
        print('[%s] %s src=%s | 「%s」→ 深雪:「%s」%s' % (
            'pass' if ok else 'FAIL', where, src, text[:14], say[:44],
            '‖泄漏!' if leak else ''))
        pass_n, fail_n = (pass_n + 1, fail_n) if ok else (pass_n, fail_n + 1)

    print('RESULT: pass=%d fail=%d 其中LLM真实应答=%d/%d' % (pass_n, fail_n, llm_n, len(results)))
    sys.exit(1 if fail_n else 0)


if __name__ == '__main__':
    main()
