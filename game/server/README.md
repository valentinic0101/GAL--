# server/ —— 服务端引擎

FastAPI + 全局单例 `Engine`。游戏状态活在**进程内存**里（`app.engine`），浏览器只是表现层——
这是本项目最容易踩的一条：重启服务会重置进行中的进度，两个标签页会争用同一局。

```
server/
├── app.py               FastAPI 入口：REST 端点 + 静态挂载（/assets、/ 与 /doc 的 301 旧址）
├── settings.py          C1~C8 各机制的运行时开关（环境变量 GAL_* 覆盖，默认全开）
├── engine/              ★ 运行时引擎（原单文件 engine.py 按职责拆分而来）
│   ├── core.py            class Engine：帧构造·场景推进·幕间自由行动·导演调度·Agent 应答·记忆与反思
│   ├── config.py          阶段提示 / BGM 映射 / 场景转场 / 在场演员 / 幕间候选词 —— 纯数据，调内容改这里
│   ├── storage.py         存档目录、事件日志与落盘原语
│   └── __init__.py        对外接口：Engine / SAVE_DIR / LOG_PATH / log + 六张配置表
├── world/world.py       世界层：事实库·场景图·知识库·关系矩阵·事件总线
├── agents/              角色层
│   ├── personas.py        人设卡（纯 system prompt，无框架前置词）+ persona_card()
│   ├── llm.py             可插拔 LLM 适配层（配置优先级：环境变量 > game/llm.json > 禁用）
│   ├── guardrails.py      护栏：风格校验 + 谜团锁 + 正典白名单
│   ├── rule_engine.py     规则引擎兜底：意图分类 + 行为模式库 + 旁白库（LLM 不可用时游戏仍可玩）
│   ├── memory.py          记忆流与三因子检索（C1）
│   ├── score.py           自由输入的三轴打分
│   └── canon.py           正典台词检索，从剧本的 line 节拍自动建语料（C4）
├── director/            导演层
│   ├── director.py        剧情吸引子 + 分支后继图 SUCCESSORS + 叙事压力 + 收束到四结局
│   ├── gossip.py          八卦传播引擎（性格过滤器·走样·后果回流）
│   └── guide.py           diegetic 引导策略菜单（C7）
└── scenes/              剧本数据
    ├── script.py          对外入口：汇总成同一个 SCENES 注册表
    ├── trunk.py           主干：P1~P10 + 终章 P0
    └── branches.py        分歧与结局：P11 / P12M / P12B / E_STAY / E_SPRING / E_FAR / E_TOKYO
```

## 五层架构与目录的对应

| 层 | 目录 | 职责 |
|---|---|---|
| 世界层 | `world/` | 世界的事实：地点图、知识边界、关系数值、事件流水。**不依赖任何上层。** |
| 角色层 | `agents/` | 人设、记忆、模型调用、护栏。产出「这个角色此刻会说什么」。 |
| 导演层 | `director/` | 什么时候把哪段剧情推到玩家面前；分支收束；传闻传播。 |
| 运行时 | `engine/` + `app.py` | 把上面三层串成一拍一拍的游戏，管理存档与对外 API。 |
| 表现层 | `../web/` | 只负责渲染帧数据与采集玩家输入，不含任何游戏规则。 |

无循环依赖：`world` 不依赖上层；`scenes` 只被 `engine` 引用。

## 一次请求的通路

浏览器（`web/js/50_flow.js`）→ `POST /api/advance` → `engine/core.py`：`step()` 读当前场景的下一拍 →
导演层决定是否推进节点 → 角色 Agent 现场拼 prompt 调 LLM → 护栏校验（违规重试后回落 `rule_engine`）→
世界层记账（`world.py` + `gossip.py`）→ 返回帧数组 → 前端逐帧渲染（背景/立绘/BGM 按 `assets/` 文件名装配）。

## 常用命令

```bash
cd game
python3 -m uvicorn server.app:app --host 127.0.0.1 --port 8300     # 启动
python3 tools/supervisor.py --once                                  # 健康探测 + 自动重启 + 离线回归
GAL_SAVE_DIR=/tmp/gal_test/saves python3 -m uvicorn server.app:app --port 8311   # 隔离存档的临时实例
```

## 可覆盖的环境变量

| 变量 | 作用 |
|---|---|
| `GAL_SAVE_DIR` | 覆盖存档目录（起临时实例验证时用，避免碰到正在玩的那一局） |
| `GAL_ACCESS_LOG` | 覆盖访问日志路径 |
| `GAL_STAGE_GUARD` / `GAL_CANON_INJECT` / `GAL_FEEDBACK_RETRY` / `GAL_MEMORY` / `GAL_REFLECT` / `GAL_GUIDE_V2` / `GAL_RUMOR_STRENGTH` | 逐项开关 C1~C8 机制（`0` 关闭），用于回归排障时定位到具体机制 |

## 为什么要拆 `engine/`

原先是一个 769 行的 `engine.py`，里面混了三类东西：静态配置表（阶段提示、BGM 映射、转场、演员表，
约 95 行）、存档落盘细节、以及真正的运行时逻辑。改一处剧情提示要在 700 行里翻。

拆成 `config.py`（纯数据）+ `storage.py`（落盘）+ `core.py`（Engine 类）之后，对外接口一字未变
（`from engine import Engine, SAVE_DIR` 照旧）。拆分做过 A/B 验证：同一随机种子下，新旧实现各跑 400 步，
406 帧逐字节相同，世界状态相同，存档 JSON 相同。
