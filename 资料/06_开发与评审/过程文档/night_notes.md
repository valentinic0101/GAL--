## 2026-09-15 01:45 — TEST-FAIL (e2e 卡死于 P1) → 已修复
- 现象：e2e 通关测试 900 步停在 P1 第一帧，advance 接口永远返回同一旁白帧。
- 诊断：`new_game()`/`enter_scene()` 未清空 `pending_choices`。任一会话停在选项帧后（如浏览器玩到输入点停住），后续所有「新游戏」都带着旧待输入状态，advance 恒返回 last_frame。属存量 bug，此前测试碰巧未踩中（01:26 的 e2e 通过时 pending 恰为 None）。
- 修复：engine.py `enter_scene()` 开头置 `self.pending_choices = None`（1 行）。
- 验证：卡死场景复现脚本 PASS；supervisor 完整回归 HEARTBEAT-OK（01:49:57，含 e2e P1→P0 全线）。
- 服务器已重启（新代码），LLM（deepseek-flash）与 BGM 正常。
- [2026-09-15 02:16] HEARTBEAT-OK（服务器在线，引擎一致性 32/32 + e2e 全线通关通过）
## 2026-09-15 02:46 — TEST-FAIL (e2e 客户端 socket 超时) → 已修复
- 现象：e2e 通关测试 HTTP 调用 30s 超时。原因：LLM 接入后测试机器人的每次自由输入/交谈都触发真实 DeepSeek 调用（重试最多 2×45s），超过测试客户端超时；且监督每 30 分钟跑一次 e2e 会整夜消耗 API 额度。
- 修复：新增运行时开关 POST /api/mode {llm:bool}（LLMAdapter.enabled）；e2e 改为离线回归——开始前关 LLM、finally 恢复。e2e 现在测的是引擎流程（规则引擎应答），272 步 0.5s 完成。
- 验证：mode 开关往返 OK；e2e 全线 PASS；supervisor 完整回归 HEARTBEAT-OK（02:47:34）。真玩家的 LLM 已恢复开启。
- 明日建议：多会话隔离（每浏览器会话独立 Engine 实例），避免监督回归与玩家共享全局状态。
- [2026-09-15 03:15] HEARTBEAT-OK（离线 e2e 0.5s 全线通过，服务器在线）
- [2026-09-15 03:45] HEARTBEAT-OK
- [2026-09-15 04:15 ~ 06:15] HEARTBEAT-OK（多轮巡检合并记录：服务器持续在线，历次离线 e2e 全线通过，无异常）
- [2026-09-15 06:45] HEARTBEAT-OK
- [2026-09-15 07:15] 新增 code.html（代码结构全解 18 章）与 playthrough.html（通关实录，403 条真实轨迹）+ capture_playthrough.py 采集脚本
- [2026-09-15 07:17] HEARTBEAT-OK
- [2026-09-15 07:37] 新增 flow.html：六张巨型 Mermaid 流程图（总架构/完整生命周期/输入通路/导演调度/八卦传播/启动存档监督），Mermaid 11 本地离线（web/vendor/）
- [2026-09-15 08:00] 修复玩家输入无响应：①静态资源 no-cache 中间件（根因：浏览器缓存旧 main.js 导致输入发不出去且无指示器）②智谱免费档限流(1302)处理：识别 HTTP200+error JSON 与 HTTPError 两种形态→45s 冷却期直接回落规则引擎，异常不再重试（最坏等待 50s→12s）③浏览器端到端验收：输入→指示器出现→2.3s 应答上屏→指示器消失
- [2026-09-15 10:20] 玩家旧标签页缓存旧 JS 导致输入不发请求：新增 /play 免缓存入口 + no-store 头 + 资源 v=17；超时收紧至 8s
## 2026-09-16 08:05 — 【论文补充批次 C1~C8 实施完成】（依据《修改意见与开发文档/》）

- **第 0 批（BUG 修复）**：index.html 多余 `</div>`（BUG-1，全部面板曾脱离 .screen 定位上下文）；enter_scene 同步 location/time + 结局吸收态保留 _bg_override（BUG-2，结局卡背景错位）；beat 级 `cast` 字段立绘按拍入场，P7/E_SPRING 深雪延迟登台（BUG-3）；新增 logs/engine.log（LLM 异常/护栏拦截/反思事件，QA P3-2）。
- **第 1 批**：C3 stage 感知硬护栏（P1/P2 禁身份宣言+正则变体、P1~P5 禁名字、雪女只许唤名；QA P2-1 闭环）；C4 正典检索注入（agents/canon.py 从剧本自动建语料+HOLDOUT 验证集）+ 反馈式重试（违规原因喂回模型，重试降温 0.4）。
- **第 2 批**：C1 记忆流三因子检索（agents/memory.py；写入钩子×6：场景台词/正典 me/玩家输入/agent 应答/知识镜像；recency×importance×relevance；200 条压缩摘要；随存档序列化）；C2 反思（能量槽阈值 40 → 洞察 importance=9 回写；离线模板兜底；深雪洞察过谜团锁；亲戚信念放大传播概率）。
- **第 3 批**：C5 采访评测（25 题×5 类；规则轨 CI 100% + LLM judge 归一指数 + 消融开关）；C6 谜团攻击集（50 条×4 阶段=200 攻击，离线轨 0 泄漏）+ 对抗玩家五线回归（全部到达预期结局、0 语义泄漏）。
- **第 4 批**：C7 导演 diegetic 引导菜单（info_hook/npc_redirect/event_comes/world_consequence，pending_force 时机调整）；C8 传闻强度（1.2/1.0 初值、每日 ×0.9、<0.2 停传、NPC 引用升温、LLM 即时扭曲、回流进 agent prompt）。
- **新开关**：server/settings.py（MEMORY_ON/REFLECT_ON/GUIDE_V2/RUMOR_STRENGTH/CANON_INJECT/FEEDBACK_RETRY/STAGE_GUARD，均可独立回滚）。
- **真机冒烟（glm-4.5-flash）**：P1 身份试探 src=llm 且零泄漏；P3 时深雪记忆 17 条；冒烟抓到「我是小修的姐姐啊」绕过字面黑名单 → 已加正则 `我是.{0,3}姐姐` 拦截。
- **回归**：consistency 32/32、branching 五线全通、guardrails 15、memory 18、canon_guide_gossip 25、mystery_attack 200 攻击 0 泄漏、adversary 5/5、interview 25/25 —— **全部 EXIT=0**；supervisor 回归清单已扩至 9 项。

## 2026-09-15 10:40 — 【真凶】POST /api/input 422：玩家所有点击/输入被服务器静默拒绝 → 已修复

- 现象（用户三次反馈）：点选项/输入回答后久无反应、无指示器、界面空白。
- 定性证据：新增访问日志捕获 `POST /api/input -> 422 (3ms)`；curl 形态矩阵复现：`{"text":"…","choice_index":null}` 与 `{"text":null,"choice_index":0}`（即玩家点击选项/输入框的两种真实形态）均 422。
- 根因：Pydantic v2 中 `text: str = None` / `choice_index: int = None` 不接受显式 null（默认值≠可空类型）。此前所有自动化测试用单参调用（undefined 字段被 JSON.stringify 丢弃）恰好绕过，真实浏览器路径必现。
- 修复：InputBody/ActBody/ModeBody 字段改为 Optional[...]。重放四种形态全部 200。
- 附带：/play 免缓存入口（旧标签缓存 JS 输入不发请求的绕行道）、访问日志中间件、静态资源 no-store、限流 1302 快速回落、超时 8s。
- 验证：真实 UI 路径（fill 输入框→点「说」）→ 指示器亮起计时 → 深雪应答上屏 → 指示器消失。supervisor HEARTBEAT-OK (10:4x)。
- 用户现有标签页无需刷新即可恢复（服务端修复，请求形态不变）。
