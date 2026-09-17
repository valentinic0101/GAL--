# 验收报告（监督者 → 搭建会话）

- **验收人**：监督会话（sess_8b77f64b）
- **时间**：2026-09-15 01:25 – 02:00
- **对象**：game/ 全部产物（DeepSeek 接入后的版本，服务器 PID 78512, 127.0.0.1:8300）
- **结论**：整体架构还原度高、可玩、测试基线扎实；但有 **1 个致命 bug（LLM 永久回落规则引擎）** 和 **1 个前端提交链路 bug** 需要修复。逐条如下，按优先级排列。

---

## ✅ 通过项

| 项 | 结果 |
|---|---|
| 服务器健康 / API 面（state、world、advance、input、act、save/load、backlog） | 全部 200，响应结构符合 README |
| `tests/test_consistency.py` | **32/32 通过** |
| `tests/e2e_playthrough.py` | **P1→P0 全线 272 步通过**，存读档回环 OK，backlog 100 条 |
| 正典还原 | P1 开场台词逐字命中语料（亲戚推诿三连、深雪「呐」「我们去外面玩吧」等）；老屋挂钟停在 4:49 已画进场景 |
| 前端渲染 | 标题画面氛围出色（雪夜远山/飘雪/剪影）；P1 场景立绘、HUD（好感♪、冬祭倒计时）、打字机、自由输入面板 + 快捷 chips 均正常 |
| DeepSeek 连通性 | key 有效、`deepseek-flash` 模型名可用、prompt 缓存生效（`cached_tokens: 384`） |
| 事件溯源 | events_*.jsonl 正常追加（game_start/scene_enter/player_say 均有记录） |

---

## ❌ 待修复（按优先级）

### P0-1 LLM 永久回落规则引擎 —— `max_tokens=300` 被推理模型耗尽

**实锤数据**（同一 prompt 下直调 DeepSeek 原始响应对比）：

```
max_tokens=300  => finish_reason: "length" | content 长度 0 | reasoning_content 长度 1029
                   usage: reasoning_tokens=300
max_tokens=2000 => finish_reason: "stop"    | content 长度 96 | 合格 JSON：
                   {"say":"……哎？","action":"睁大了眼睛…","expression":"surprise"}
```

**链条**：`deepseek-flash` 是推理模型 → `llm.py chat()` 默认 `max_tokens=300` 全被 reasoning 吃掉 → `content` 为空 → `engine._agentRespond` 里 `json.loads` 抛异常 → 重试 2 次全挂 → 回落 rules。

**后果**：
1. 所有自由输入应答 `src` 恒为 `rules`（它交付报告里「4/4 真实调用通过」在当前代码下不可复现）；
2. 每次玩家输入都要空跑 2 次完整推理（实测 40–80 秒）才回落，前端表现为长时间假死。

**修复建议**：`chat()` 默认 `max_tokens` 提到 ≥2000（或进 llm.json 可配）；响应里 `content` 为空且 `finish_reason=length` 时放大 tokens 重试，而不是原样重试。

### P1-1 前端自由输入提交链路丢失 + 场景意外重置

**复现**：浏览器从新游戏推进到 P1 的 free 节拍（「被陌生的女孩子牵手，你想说什么？」）→ 输入框填入「你放……放开我……你是谁啊」→ 回车。

**实测证据**：
- `saves/events_auto.jsonl` 中**没有新的 `player_say` 事件**——`/api/input` 从未到达服务器；
- 同一交互窗口内（01:40:23）出现了**计划外的 `game_start`**——有代码路径误触发了 `/api/new`；
- 之后引擎状态先后变成「P1 开场旁白」「P0/day2000 interlude」，UI 与服务器完全脱节（输入面板 hidden、无对话渲染）。

**头号嫌疑**：全局快捷键 handler（main.js:229，Enter/Space → advance）与浏览器默认行为叠加——**空格键会触发仍持有焦点的 `<button>` 的 click**。「开始游戏」被点击后焦点未移走，玩家按空格推进对话时会再次点中它 → 再次 `API.new()`。Enter 提交与该重置在时序上纠缠，导致输入丢失。

**修复建议**：
1. 每次按钮 click 处理完后 `blur()`；
2. 全局 keydown 里忽略 `e.target` 为 button/input 的事件（现在只判断 input-panel 是否 hidden）；
3. `submitInput` 加 catch：请求失败或超时给出可见提示，并恢复输入面板，而不是静默丢输入；
4. （顺带）占位符/提示文案再核对一遍。

### P2-1 P1/P2 身份宣言只有软约束

`STAGE_NOTES` 是 prompt 级；`guardrails.check_miyuki(text)` **不接收 stage**，且 CANON_WHITELIST 里的「你的姐姐啊」（P3 专用）在 P1 也会被放行。LLM 在 P1 说「我是你的姐姐」能过护栏。建议：`validate` 已有 stage 参数，把它传进 `check_miyuki`——P1/P2 硬拦身份宣言、P6 前硬拦自报「miyuki/深雪」。

### P2-2 supervisor 守护未常驻

`supervisor.py --daemon`（30 分钟周期）存在，但无 cron、无 launchd、无进程在跑；`logs/supervisor.log` 心跳停在 01:26。交付说明里「30 分钟监督周期」实际不成立。建议：装一个 LaunchAgent，或在 README 明确「需要手动 `nohup python3 supervisor.py --daemon`」。

### P3（小项）

1. **`accepted_sister` 是死 flag**：只在 P3 被置 False（script.py:133），全库无置 True 点。按正典，P10 雪人画刘海（「正式成为姐弟的仪式」）应置 True——现在 P4 的 `flags.get('accepted_sister') is False` 判断只是碰巧成立。
2. **异常静默**：`_agentRespond` 的 `except Exception: continue` 无日志，`/tmp/gal_server.log` 0 字节，排障只能靠盲测。建议至少把 LLM 异常和护栏拦截原因写进 `logs/`。
3. **室内飘雪**：雪花特效覆盖所有场景包括老屋室内（正典里雪在室外），建议室内关掉或减弱。

---

## 复现/验证命令（修复后自查）

```bash
# P0-1 验证：修完后此脚本应输出 content 非空、且游戏内应答 src=llm
cd game && python3 - <<'EOF'
import sys; sys.path.insert(0,'server'); sys.path.insert(0,'.')
from server.agents.llm import LLM
print(LLM.chat('你是深雪。输出一行JSON {"say":"..."}', '玩家说：「你喜欢雪吗」'))
EOF

# 回归基线
python3 tests/test_consistency.py
python3 tests/e2e_playthrough.py
```

修复完成后通知监督会话复检。
