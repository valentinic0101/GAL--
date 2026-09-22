# 开发文档 C3：stage 感知硬护栏（身份宣言 / 名字泄漏按阶段硬锁）

- **总报告排名**：第 1 位 ｜ 相关性 10 · 适用性 10 · 补充价值 9 ｜ 总分 29
- **论文依据**：《论文讲解/01_Generative_Agents》——STAGE_NOTES 这类 prompt 软约束必须配硬校验才构成完整护栏（Smallville 的"规划+记忆+反思缺一不可"结论同理）；《论文讲解/17_SOTOPIA》——SEC（秘密保护）思维：不该出现的**信息**必须被机制拦住，而不是被"请求"。
- **批次**：第 1 批（先行）｜ **预估**：2~3 小时 ｜ **风险**：低（单文件改动 + 一个调用点）

## 一、目标（一句话）

让 `guardrails` 感知当前剧情阶段：P1/P2 硬拦深雪的任何身份宣言、P6 之前硬拦名字泄漏——把 QA_REPORT P2-1 的遗留漏洞彻底堵死。

## 二、现状与差距（代码级）

- `engine.py:528` 调用 `guardrails.is_acceptable(char_id, say, w.phase)` —— **stage 已经传进来了**；
- 但 `guardrails.py:91-100` 的 `validate()` 对 miyuki 分支调用 `check_miyuki(text)` —— **把 stage 丢了**；
- 后果（QA P2-1 实锤）：`CANON_WHITELIST` 里的「你的姐姐啊」（P3 专用台词）在 P1/P2 也被白名单放行；STAGE_NOTES 只是 prompt 软约束，LLM 在 P1 输出「我是你的姐姐啊，小修」能直接过护栏上屏——**谜团锁（圣经 §1.3/§5.3）被打破且无人拦截**；
- 同类问题：深雪名字（「深雪」「miyuki」「写作深和雪两个字」）在 P1~P5 的台词中无任何拦截（P6 才是揭示点）；雪女台词（`yukihime`）无阶段限制（只应在 P0/P12M 出现）。

## 三、详细修改方案

### 3.1 数据结构调整（`agents/guardrails.py`）

把正典白名单从 `set` 改为 **`dict: 台词 → 允许阶段集合`**（`None` = 全阶段合法）：

```python
# (stage, text) 二元组：text 允许出现的阶段列表；None 表示任意阶段
CANON_WHITELIST = {
    '我没有骗你': None, '我都说了这不是骗你': None,
    '你的姐姐啊': ['P3'],                      # ← 关键：只有 P3 合法
    '写作深和雪两个字，miyuki': ['P6'],          # ← 名字揭示只在 P6
    'miyuki': ['P6'],
    '欢迎回来哦': ['P3', 'P7', 'E_SPRING'],
    # ……其余条目逐条标注，未标注的默认 None
}
```

新增阶段常量与两条阶段黑名单：

```python
STAGES_EARLY = ('P1', 'P2')          # 身份宣言禁发期
STAGES_BEFORE_NAME = ('P1', 'P2', 'P3', 'P4', 'P5')   # 名字禁提期
IDENTITY_DECLARATION = ['我是你的姐姐', '你的姐姐', '我是姐姐', '你的亲姐姐']
NAME_TOKENS = ['深雪', 'みゆき', 'miyuki', '写作深和雪']
```

### 3.2 函数签名改造

```python
def check_miyuki(text, stage=None):        # ← 增加 stage 参数
    issues = []
    # 1) 白名单（带阶段过滤）
    if text in CANON_WHITELIST:
        allowed = CANON_WHITELIST[text]
        if allowed is None or stage in allowed:
            return []
        # 白名单台词但阶段不对 → 继续走黑名单检查（不直接放行）
    # 2) 身份宣言硬锁（新）
    if stage in STAGES_EARLY and any(w in text for w in IDENTITY_DECLARATION):
        issues.append('identity_declaration_early')
    # 3) 名字硬锁（新）
    if stage in STAGES_BEFORE_NAME and any(w in text for w in NAME_TOKENS):
        issues.append('name_leak_early')
    if stage in ('P0', 'P12M') and text.count('修二') > 1:
        issues.append('yukihime_speech_rule')   # 幻影只唤一声「修二――――」
    # ……原有禁忌词/句长/语气词/谜团锁检查保持不变
    return issues

def is_acceptable(char_id, text, stage=None):
    return len(validate(char_id, text, stage)) == 0
```

`validate()` 内 miyuki 分支改为 `check_miyuki(text, stage)`；`shuuji` 分支已有 stage 逻辑不动。

### 3.3 引擎接入（唯一调用点已就绪）

`engine.py:528` 无需改动（已传 `w.phase`）。但 `rule_engine.respond()` 的规则兜底输出**也应过一遍同一校验**：在 `engine._agentRespond` 末尾对 `resp['say']` 补一次 `guardrails.validate`，违规则替换为安全句 `'……'`（规则引擎的台词都是人工正典，此检查为防御性，成本为零）。

### 3.4 日志（联动前置工程 E-4）

拦截发生时 `world.emit('guardrail_block', {'char': char_id, 'stage': stage, 'issues': issues})`——事件溯源 jsonl 里可回查拦截率。

## 四、验收标准

1. 新增 `tests/test_stage_guardrails.py`（≥8 断言）：
   - P1 深雪「我是你的姐姐啊，小修」→ 违规（identity_declaration_early）；
   - P3 同句 → 合法；P7 「我是你姐姐」→ 违规（阶段外，复用同一黑名单逻辑：P3 之后身份已确立不必拦，**设计取舍：P7+ 放行但记 info 日志**）；
   - P1 深雪「写作深和雪两个字，miyuki」→ 违规；P6 → 合法；
   - P3 「你的姐姐啊」→ 合法；P1 同句 → 违规；
   - P0 雪女「修二――――」→ 合法；雪女普通对话句 → 违规。
2. `python3 tests/test_consistency.py` 32 项全绿（现有用例的台词均在合法阶段，不应误伤——若误伤，按"标注正确阶段"修白名单而不是放宽规则）。
3. `python3 tests/e2e_playthrough.py` 离线全通。
4. 实机：P1 幕间对深雪说「你是不是我姐姐」10 次（LLM 开），上屏台词 0 次含身份宣言（拦截率 100%，拦截记录在 events jsonl）。

## 五、风险与回滚

- **误伤风险**：正典台词被误拦 → 全部白名单条目补阶段标注即解；e2e 全线回归是安全网。
- **回滚**：改动集中在 guardrails.py，`git checkout` 即回滚；引擎调用点无需变更。
