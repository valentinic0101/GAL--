# -*- coding: utf-8 -*-
"""LLM 适配层（可插拔）。

- 若配置了 GAL_LLM_API_KEY（bigmodel / z.ai / openai 兼容端点），角色 Agent 走真 LLM：
  现场拼装 = 人设卡（静态前缀）+ 记忆检索 + 场景状态 + 知识边界，无任何框架前置词。
- 未配置或调用失败 → 由 rule_engine 兜底（正典语料 + 意图匹配），保证完整可玩。
"""
import json
import os
import time
import urllib.request
import urllib.error


class LLMAdapter:
    """配置优先级：环境变量 > game/llm.json > 禁用（规则引擎兜底）。"""

    CONFIG_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'llm.json')

    def __init__(self):
        cfg = {}
        if os.path.exists(self.CONFIG_PATH):
            try:
                with open(self.CONFIG_PATH, encoding='utf-8') as f:
                    cfg = json.load(f)
            except (ValueError, OSError):
                cfg = {}
        self.api_key = (os.environ.get('GAL_LLM_API_KEY')
                        or cfg.get('apiKey') or '')
        self.base_url = (os.environ.get('GAL_LLM_BASE_URL')
                         or cfg.get('baseUrl')
                         or 'https://api.deepseek.com')
        self.model = (os.environ.get('GAL_LLM_MODEL')
                      or cfg.get('model') or 'deepseek-flash')
        # 关闭思考模式（实测：开启时 token 全被 reasoning 吃掉，正文为空且延迟暴涨）
        self.extra_body = cfg.get('extraBody') or {'thinking': {'type': 'disabled'}}
        self.timeout = int(cfg.get('timeout', 25))
        self.enabled = True     # 运行时开关（/api/mode），供回归测试离线跑
        self.cooldown_until = 0.0   # 限流冷却期：期内直接走规则引擎，不空耗重试

    @property
    def rate_limited(self):
        return time.time() < self.cooldown_until

    @property
    def available(self):
        return bool(self.api_key) and self.enabled

    def chat(self, system, user, temperature=0.7, max_tokens=300):
        if not self.available:
            raise RuntimeError('LLM not configured')
        if self.rate_limited:
            raise RuntimeError('LLM rate-limit cooldown (%.0fs left)'
                               % (self.cooldown_until - time.time()))
        body = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user},
            ],
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        body.update(self.extra_body)   # 如 thinking disabled
        req = urllib.request.Request(
            self.base_url.rstrip('/') + '/chat/completions',
            data=json.dumps(body).encode('utf-8'),
            headers={'Content-Type': 'application/json',
                     'Authorization': 'Bearer %s' % self.api_key})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            # 智谱限流时可能返回 HTTP 200 + error JSON（code 1302），必须显式检查
            if isinstance(data, dict) and data.get('error'):
                err = data['error']
                code = str(err.get('code', ''))
                msg = str(err.get('message', ''))
                if code == '1302' or '速率' in msg or code == '429':
                    self.cooldown_until = time.time() + 45
                    raise RuntimeError('rate limited -> cooldown 45s')
                raise RuntimeError('LLM API error %s: %s' % (code, msg[:120]))
            content = (data['choices'][0]['message'].get('content') or '').strip()
            if not content:
                raise RuntimeError('empty content (thinking burned all tokens?)')
            return content
        except urllib.error.HTTPError as e:
            # 限流（智谱 1302 / HTTP 429）：进入冷却期，调用方应立即回落，不再重试
            detail = ''
            try:
                detail = e.read().decode('utf-8')[:200]
            except Exception:
                pass
            if e.code == 429 or '1302' in detail or '速率' in detail:
                self.cooldown_until = time.time() + 45
                raise RuntimeError('rate limited -> cooldown 45s')
            raise RuntimeError('LLM HTTP %s: %s' % (e.code, detail))
        except (urllib.error.URLError, KeyError, TimeoutError, ValueError) as e:
            raise RuntimeError('LLM call failed: %s' % e)


def assemble_prompt(persona, world, char_id, memories, scene_desc, knowledge_boundary,
                    canon=None, rumors=None):
    """现场拼装：人设卡 + 正典示范(C4) + 记忆 + 场景 + 知识边界 + 传闻(C8)。"""
    parts = [persona]
    if canon:
        parts.append('【你的台词示范（正典语料，模仿其语气与句式；除非玩家原话引用，不要逐字复述）】\n'
                     + '\n'.join('- 「%s」' % c for c in canon))
    if memories:
        parts.append('【你的相关记忆】\n' + '\n'.join('- ' + m for m in memories))
    parts.append('【当前场景】\n' + scene_desc)
    kb = '\n'.join('- ' + k for k in knowledge_boundary) if knowledge_boundary else '- （你知道的不比别人多）'
    parts.append('【你的知识边界（你只知道这些，此外一概不知）】\n' + kb)
    if rumors:
        parts.append('【镇上最近流传（你听说的，未必是真）】\n'
                     + '\n'.join('- ' + r for r in rumors))
    parts.append('输出格式：一行 JSON {"say": "台词", "action": "动作提示", "expression": "normal|smile|sad|surprise"}。台词必须符合你的语言硬规则。')
    return '\n\n'.join(parts)


LLM = LLMAdapter()
