# 深雪 ~miyuki~ · 雪国开放世界 GALGAME

> 她一直在等，我一直在逃，雪一直落在两人之间。

基于《设计文档/架构设计V1.md》五层架构与《设计文档/人物设定与关系总览.md》（人物圣经 v1.0，依据《素材文本/原文剧本.txt》写成）实现的完整可玩 galgame。
玩家扮演修二，在雪国小镇自由行动；深雪等 NPC 由 Agent 驱动；导演层用 P0~P10 剧情吸引子保证叙事骨架。

**▶ 文档：<http://127.0.0.1:8300/flow.html>（六张巨型 Mermaid 流程图）｜ [代码结构与运行通路全解](http://127.0.0.1:8300/code.html) ｜ [通关实录（403 条真实轨迹）](http://127.0.0.1:8300/playthrough.html) ｜ [画布总览图](http://127.0.0.1:8300/docs.html)**

## 快速开始

```bash
pip3 install fastapi uvicorn pillow   # 一次性
cd game
python3 -m uvicorn server.app:app --host 127.0.0.1 --port 8300
# 浏览器打开 http://127.0.0.1:8300
```

### 一键启动（推荐）

不用敲命令，在访达里双击即可：

| 文件 | 平台 | 作用 |
|---|---|---|
| `启动游戏.command` | **macOS** | 检查依赖 → 启动服务（后台运行，关掉终端窗口也不会停）→ 自动打开浏览器 |
| `停止游戏.command` | **macOS** | 结束服务，释放 8300 端口 |
| `启动游戏.bat` / `停止游戏.bat` | Windows | 同上 |

macOS 用 `.command`，Windows 用 `.bat`——两者不能互换（`.bat` 在 macOS 上双击无效）。`启动游戏.command` 是幂等的：服务已在运行时重复双击只会打开浏览器，不会起第二个实例。

> 若 macOS 首次双击提示「无法打开，因为它来自身份不明的开发者」，右键该文件 → 选「打开」→ 再点「打开」即可放行（只需一次）。

## 目录结构

```
game/
├── server/                    # 引擎（五层架构）
│   ├── world/world.py         # 世界层：事实库·场景图·知识库·关系矩阵·事件总线
│   ├── agents/
│   │   ├── personas.py        # 人设卡（纯 system prompt，无任何框架前置词）
│   │   ├── guardrails.py      # 护栏层：风格校验器 + 谜团锁 + 正典白名单
│   │   ├── rule_engine.py     # 规则引擎兜底（意图分类 + 正典行为模式库 + 旁白库）
│   │   └── llm.py             # 可插拔 LLM 适配层（现场拼装 prompt）
│   ├── director/
│   │   ├── director.py        # 导演层：剧情吸引子 P0~P10 + 前置条件表 + 叙事压力
│   │   └── gossip.py          # 八卦传播引擎（性格过滤器·走样·后果回流）
│   ├── scenes/script.py       # 剧本数据：P0~P10 全节点（正典台词+旁白+选项+效果）
│   ├── engine.py              # 运行时：场景推进·幕间自由行动·存档·事件溯源
│   └── app.py                 # FastAPI：REST API + 静态托管
├── web/                       # 前端（原生 HTML/CSS/JS galgame 界面）
├── assets/                    # 素材目录（只放可替换的美术与音频，替换规则见 assets/README.md）
│   ├── backgrounds/           # 12 张 1280x720 背景（PIL 生成）
│   ├── sprites/               # 10 个角色立绘 SVG（深雪×5表情）
│   ├── bgm/                   # 6 首程序化合成 BGM（numpy 合成 → afconvert AAC）
│   └── ui/                    # 名牌底、雪花角饰
├── tools/                     # 素材生成脚本（输出到 ../assets/，与素材分离）
│   ├── _tools.py              # 美术工具库（渐变/山峦/雪/光晕）
│   ├── gen_backgrounds.py     # 重新生成 backgrounds/
│   ├── gen_sprites.py         # 重新生成 sprites/ 与 ui/
│   └── gen_music.py           # 重新合成 bgm/
├── tests/
│   ├── e2e_playthrough.py     # 自动通关测试（P1→任一结局全链路 + 存读档）
│   ├── test_branching.py      # 多结局收束测试（路由穷举 + 五线实机通关 + 门控落空）
│   └── test_consistency.py    # 角色一致性回归（人物圣经§5 自检的自动化版）
├── docs/                      # 过程文档（QA_REPORT.md 验收报告、night_notes.md 值守日志）
├── supervisor.py              # 监督者：健康探测·自动重启·回归测试
└── saves/                     # 存档（JSON 快照 + 事件溯源 jsonl）
```

## 玩法

- **剧情模式**：点击/回车推进；选项处可选正典选项，也可「自由输入」任意台词，NPC 会按人设应答。
- **幕间自由模式**：每个剧情节点之间可自由行动——`移动`（场景图邻接移动）、`交谈`（对在场 NPC 自由说话）、`等待/过夜`（推进游戏日：冬祭倒计时、八卦传播、季节压力累积）。叙事压力到位后出现「▶ 推进剧情」按钮。
- **系统**：自动播放 / 日志（回想）/ 世界状态（含镇上传闻）/ 3 档存读档 + 自动存档。

## LLM 接入（已启用）

已接入智谱 BigModel（`glm-4.5-flash`，thinking 关闭），配置在 `game/llm.json`（删除该文件即回落规则引擎）：

```json
{ "apiKey": "…", "baseUrl": "https://open.bigmodel.cn/api/paas/v4", "model": "glm-4.5-flash", "extraBody": {"thinking":{"type":"disabled"}}, "timeout": 12 }
```

角色 Agent 按架构 §2.1 现场拼装：人设卡（静态前缀，可缓存）+ 检索记忆 + 场景 + 知识边界 + **阶段约束**（防 LLM 泄漏后设，如 P1 不提前说「你的姐姐啊」），生成后过护栏校验（称谓/语气词/禁忌词/谜团锁），违规重试 2 次后回落规则引擎。台词帧的 `src` 字段标明来源（`llm` / `rules`）。

实链路验证：`python3 tests/test_llm.py`（真实调用 API，勿放进周期任务以免消耗额度）。

## API 摘览

| 端点 | 说明 |
|---|---|
| POST /api/new | 新游戏（进入 P1） |
| POST /api/advance | 推进一拍 |
| POST /api/input | 提交选项/自由输入 `{text|choice_index}` |
| POST /api/act | 幕间行动 `{action: move/talk/wait/enter_scene}` |
| GET /api/state · /api/world · /api/backlog | 当前帧 · 世界状态（含传闻）· 对话日志 |
| POST /api/save/{slot} · /api/load/{slot} | 存档/读档（事件溯源见 saves/events_*.jsonl） |

## 多结局（三轴 · 四结局）

主干 P1~P10 之后进入分支层（设计详见《设计文档/多结局分支设计.md》，全景图见「绘画/剧情分支树.html」）：

- **三轴**：羁绊♪ / 山之念▲ / 现世◇——正典选项与自由输入（模型打分，离线关键词兜底）都会累积；状态栏实时显示。
- **决策点**：P11 一年后的岔路（入山〔▲≥35〕/ 归省 / 留京〔◇≥35〕）→ P12B 幸福之问（原文未答之问由玩家回答）：留下〔♪≥50〕/ 春天再见〔♪≥50 且 ▲<35〕/ 沉默兜底。
- **四结局**：`END_SNOW` 白之彼方（入山·悲壮）｜`END_STAY` 炉火与春讯（留守）｜`END_SPRING` 等到花开（真结局，接通 accepted_sister）｜`END_FAR` 两行足迹（原作向，含留京变体）。
- **收束保证**：门控不足的选项会被剧情化拒绝并回落，任何玩法状态必达某个结局（tests/test_branching.py 穷举证明）。

## 测试与监督

```bash
python3 tests/test_consistency.py   # 32 项：深雪一致性·谜团锁·修二护栏·八卦·资产·世界层
python3 tests/test_branching.py     # 多结局收束：路由穷举 720 组合 + 五线实机通关（离线，快）
python3 tests/e2e_playthrough.py   # HTTP 全链路自动通关至结局（需服务器已启动）
python3 supervisor.py --once       # 健康探测 + 自动重启 + 全量回归
```

## 背景音乐

六首均为程序化合成（钢琴/长笛/太鼓/风声音色，`tools/gen_music.py` 可重新生成或改谱）：

| 曲目 | 氛围 | 触发 |
|---|---|---|
| bgm_title | 深雪主题·慢板 | 标题画面 |
| bgm_main | 深雪主题 | P1/P5/P7/P9、幕间车站与田间 |
| bgm_daily | 日常·温馨五声 | P3/P8、幕间老屋与小镇 |
| bgm_sad | 雪落·下行小调 | P2/P6/P10 |
| bgm_festival | 太鼓+笛 | P4 冬祭、幕间参道与神社 |
| bgm_blizzard | 风声+稀疏长音 | P0 终章、群山 |

前端随场景自动淡入淡出切曲；右上角 ♪ 可静音（偏好持久化）。首次需一次点击解锁浏览器自动播放（点「开始游戏」即触发）。

## 已知限制

- 生图/配乐：环境内无可用生成类 API，美术与音乐均为程序化生成（PIL/SVG、numpy 合成→AAC），风格统一但为示意级；
  接入生成模型后按 `tools/gen_*.py` 的清单替换 assets/ 下同名文件即可升级（详见 assets/README.md）。
- LLM：已接入智谱 GLM flash（`game/llm.json`）；key 失效时自动回落规则引擎，游戏始终可玩。
