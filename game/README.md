# 深雪 ~miyuki~ · 雪国开放世界 GALGAME — 游戏本体

> 她一直在等，我一直在逃，雪一直落在两人之间。

本目录是**游戏本体，可独立运行**：跑起来只需要 `game/` 自身（`server/` 引擎 + `web/` 前端 + `assets/` 素材）。
项目根目录另有 `资料/`（剧本原稿、设定、生图源文件、论文笔记、评审记录等），**运行游戏不需要它**。

基于《资料/02_设定与设计/架构设计V1.md》五层架构与《资料/02_设定与设计/人物设定与关系总览.md》（人物圣经 v1.0，
依据《资料/01_剧情文本/原文剧本.txt》写成）实现。玩家扮演修二在雪国小镇自由行动；深雪等 NPC 由 Agent 驱动；
导演层用 P0~P10 剧情吸引子保证叙事骨架。

**▶ 在线文档（服务已启动时）：[六张 Mermaid 流程图](http://127.0.0.1:8300/doc/flow.html) ｜ [代码结构与运行通路全解](http://127.0.0.1:8300/doc/code.html) ｜ [通关实录（403 条真实轨迹）](http://127.0.0.1:8300/doc/playthrough.html) ｜ [画布总览图](http://127.0.0.1:8300/doc/docs.html)**

## 快速开始

### 一键启动（推荐）

不用敲命令，在访达 / 资源管理器里双击即可：

| 文件 | 平台 | 作用 |
|---|---|---|
| `启动游戏.command` | **macOS** | 检查依赖 → 后台起服务（关掉终端也不会停）→ 自动打开浏览器 |
| `停止游戏.command` | **macOS** | 结束服务，释放 8300 端口 |
| `启动游戏.bat` / `停止游戏.bat` | Windows | 同上 |

macOS 用 `.command`，Windows 用 `.bat`——两者不能互换（`.bat` 在 macOS 上双击无效）。启动脚本是幂等的：
服务已在运行时重复双击只会打开浏览器，不会起第二个实例。

> macOS 首次双击若提示「无法打开，因为它来自身份不明的开发者」，右键该文件 → 选「打开」→ 再点「打开」放行（只需一次）。

### 命令行

```bash
pip3 install fastapi uvicorn pillow   # 一次性
cd game
python3 -m uvicorn server.app:app --host 127.0.0.1 --port 8300
# 浏览器打开 http://127.0.0.1:8300  （或 /play，二者等价，后者强制不缓存）
```

## 目录结构

```
game/
├── 启动游戏.command / .bat        # 一键启动（双击 → 起服务 + 开浏览器）
├── 停止游戏.command / .bat        # 停止服务
├── README.md                     # 本文件：运行说明与玩法
├── llm.json                      # LLM 配置（key/baseUrl/model/timeout）；删除即回落规则引擎
│
├── server/                       # ===== 引擎（Python / FastAPI）===== 详见 server/README.md
│   ├── app.py                    # FastAPI 入口：REST 端点 + 静态挂载（全局单例 Engine）
│   ├── engine/                   # 运行时引擎（包）
│   │   ├── core.py               #   class Engine：帧构造·场景推进·幕间·Agent 应答·记忆反思
│   │   ├── config.py             #   阶段提示/BGM 映射/转场/在场演员/幕间候选词（纯数据）
│   │   ├── storage.py            #   存档目录、事件日志与落盘原语
│   │   └── __init__.py           #   对外接口：Engine / SAVE_DIR / LOG_PATH / log + 六张配置表
│   ├── settings.py               # C1~C8 各机制的运行时开关（可单项关闭以定位问题）
│   ├── world/world.py            # 世界层：事实库·场景图·知识库·关系矩阵·事件总线
│   ├── agents/                   # 角色层：personas 人设卡 / guardrails 护栏 / rule_engine 兜底
│   │                             #         / llm 适配 / memory 记忆流 / score 三轴打分 / canon 正典检索
│   ├── director/                 # 导演层：director 吸引子与压力 / gossip 八卦传播 / guide 引导策略
│   └── scenes/                   # 剧本数据（详见下）
│       ├── script.py             #   对外入口：汇总成同一个 SCENES 注册表
│       ├── trunk.py              #   主干：P1~P10 + 终章 P0
│       └── branches.py           #   分歧与结局：P11 / P12M / P12B / E_STAY / E_SPRING / E_FAR / E_TOKYO
│
├── web/                          # ===== 前端（原生 HTML/CSS/JS，无框架无构建）=====
│   ├── index.html                # 游戏页 DOM（唯一入口）
│   ├── style.css                 # 全部样式：设计令牌（和纸/墨/朱/金）+ 组件
│   ├── js/                       # 前端逻辑，按层编号——加载顺序即依赖顺序
│   │   ├── 00_core.js            #   $ / REST 封装 / 全局状态 / 玩家设置 / toast
│   │   ├── 10_audio.js           #   BGM 播放与淡入淡出
│   │   ├── 20_snow.js            #   飘雪（标题页与游戏画面共用）
│   │   ├── 30_busy.js            #   忙碌指示与重复触发防护
│   │   ├── 40_stage.js           #   背景切换与立绘布景：地面贴合/纵深/亮度匹配/接触投影
│   │   ├── 50_flow.js            #   打字机·帧队列播放器·点击与键盘推进·自动模式
│   │   ├── 60_panels.js          #   选项/自由输入/幕间自由行动/结局卡/场景卡/状态条
│   │   ├── 70_modals.js          #   回想日志/世界状态/设置面板/存档读档
│   │   └── 90_boot.js            #   标题页绑定·请求去重包装·全局导出·开机副作用（必须最后）
│   ├── gen/                      # 由 tools 生成的素材清单（勿手改，见 gen/README.md）
│   ├── doc/                      # 在线文档页（/doc/*.html）
│   └── vendor/mermaid.min.js     # 流程图离线依赖
│
├── assets/                       # ===== 素材层：只放可替换的美术与音频 =====
│   ├── backgrounds/ 16 张 1280×720 背景 ｜ sprites/ 22 个透明立绘 ｜ cg/ 13 张事件 CG
│   ├── bgm/ 6 首 BGM（m4a）｜ ui/ 名牌底与雪花角饰
│   └── README.md                 # 替换规则与尺寸约定（换素材只改这里说的文件名）
│
├── tools/                        # ===== 开发期脚本：生成·接入·审计·守护 ===== 详见 tools/README.md
├── tests/                        # ===== 质量层：一致性·分支·护栏·记忆·评测·通关 ===== 详见 tests/README.md
├── reports/                      # 测试脚本的输出（生成物，勿手改）
├── saves/                        # {slot}.json 状态快照 + events_{slot}.jsonl 事件溯源（运行时数据）
└── logs/                         # access/engine/server/supervisor/last_fail 日志（运行时数据，可清空）
```

### 剧本数据为什么分成三个文件

`script.py` 只是对外入口。节点数据按「主干 / 分歧结局」分片，是因为主干是线性剧情、分支是按三轴阈值挂上去的
另一类东西，放在一起改一处要翻 600 行。三个文件写进的是**同一个 `SCENES` 字典**，节点 id 全局唯一，
所以 `from scenes.script import SCENES` 的用法、`tools/integrate_art.py` 的自动嵌 CG，都不受影响。

## 玩法

- **剧情模式**：点击 / 回车推进；选项处可选正典选项，也可「自由输入」任意台词，NPC 会按人设应答。
- **幕间自由模式**：每个剧情节点之间可自由行动——`移动`（场景图邻接移动）、`交谈`（对在场 NPC 自由说话）、
  `等待/过夜`（推进游戏日：冬祭倒计时、八卦传播、季节压力累积）。叙事压力到位后出现「▶ 推进剧情」按钮。
- **系统**：自动播放 / 日志（回想）/ 世界状态（含镇上传闻）/ 3 档存读档 + 自动存档 / 设置（文字速度·音量·自动间隔·飘雪）。
- **快捷键**：回车或空格推进（输入框内不触发）；Esc 关闭弹窗。

## LLM 接入（已启用）

已接入智谱 BigModel（`glm-4.5-flash`，thinking 关闭），配置在 `game/llm.json`（删除该文件即回落规则引擎）：

```json
{ "apiKey": "…", "baseUrl": "https://open.bigmodel.cn/api/paas/v4", "model": "glm-4.5-flash",
  "extraBody": {"thinking":{"type":"disabled"}}, "timeout": 8 }
```

角色 Agent 现场拼装：人设卡（静态前缀，可缓存）+ 检索记忆 + 场景 + 知识边界 + **阶段约束**（防 LLM 泄漏后设，
如 P1 不提前说「你的姐姐啊」），生成后过护栏校验（称谓/语气词/禁忌词/谜团锁），违规重试后回落规则引擎。
台词帧的 `src` 字段标明来源（`llm` / `rules`）。实链路验证：`python3 tests/test_llm.py`（真实调用，勿放进周期任务）。

## API 摘览

| 端点 | 说明 |
|---|---|
| POST /api/new | 新游戏（进入 P1） |
| POST /api/advance | 推进一拍 |
| POST /api/input | 提交选项/自由输入 `{text\|choice_index}` |
| POST /api/act | 幕间行动 `{action: move/talk/wait/enter_scene}` |
| GET /api/state · /api/world · /api/backlog | 当前帧 · 世界状态（含传闻）· 对话日志 |
| GET /api/saves · POST /api/save/{slot} · /api/load/{slot} | 存档列表（含进度元数据）· 存档 · 读档 |
| POST /api/mode | 运行时开关 LLM（离线回归用）· GET /api/health 健康探测 |

## 多结局（三轴 · 四结局）

主干 P1~P10 之后进入分支层（设计见《资料/02_设定与设计/多结局分支设计.md》，全景图见《资料/01_剧情文本/剧情分支树.html》）：

- **三轴**：羁绊♪ / 山之念▲ / 现世◇——正典选项与自由输入（模型打分，离线关键词兜底）都会累积；状态栏实时显示。
- **决策点**：P11 一年后的岔路（入山〔▲≥35〕/ 归省 / 留京〔◇≥35〕）→ P12B 幸福之问（原文未答之问由玩家回答）：
  留下〔♪≥50〕/ 春天再见〔♪≥50 且 ▲<35〕/ 沉默兜底。
- **四结局**：`END_SNOW` 白之彼方（入山·悲壮）｜`END_STAY` 炉火与春讯（留守）｜`END_SPRING` 等到花开
  （真结局，接通 accepted_sister）｜`END_FAR` 两行足迹（原作向，含留京变体）。
- **收束保证**：门控不足的选项会被剧情化拒绝并回落，任何玩法状态必达某个结局（`tests/test_branching.py` 穷举证明）。

## 测试与监督

```bash
cd game
python3 tests/test_consistency.py   # 32 项：深雪一致性·谜团锁·修二护栏·八卦·资产·世界层（离线）
python3 tests/test_branching.py     # 多结局收束：路由穷举 + 五线实机通关（离线，快）
python3 tests/e2e_playthrough.py    # HTTP 全链路自动通关至结局（需服务已启动）
python3 tools/supervisor.py --once  # 健康探测 + 自动重启 + 全量离线回归
```

> 跑 `e2e_playthrough.py` 之前注意：引擎是**服务端单例**，这些脚本会与正在玩的那一局争用同一份状态。
> 想并行验证就另起一个实例并隔离存档：`GAL_SAVE_DIR=/tmp/gal_test/saves python3 -m uvicorn server.app:app --port 8311`。

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

前端随场景自动淡入淡出切曲；HUD 上的 ♫ 可静音（偏好持久化）。首次需一次点击解锁浏览器自动播放（点「开始游戏」即触发）。

## 已知限制

- **服务端单例**：游戏状态活在服务进程里，不在浏览器。重启服务会重置进行中的进度（存档不受影响）；
  两个浏览器标签页会争用同一局。
- 美术与音乐为程序化生成（PIL/SVG、numpy 合成→AAC）+ AI 生图两条来源，风格统一但为示意级；
  接入生成模型后按 `tools/gen_*.py` 的清单替换 `assets/` 下同名文件即可升级（详见 `assets/README.md`）。
- LLM：key 失效时自动回落规则引擎，游戏始终可玩。
