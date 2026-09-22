# tests/ —— 质量层

```
tests/
├── test_consistency.py        32 项一致性回归：人物圣经自检的自动化版（离线）
├── test_branching.py          多结局收束：路由穷举 + 五线实机通关 + 门控落空（离线，快）
├── test_stage_guardrails.py   阶段硬护栏 C3（离线）
├── test_memory.py             记忆流与三因子检索 C1 / 反思沉淀 C2（离线）
├── test_canon_guide_gossip.py 正典检索 C4 / 导演引导 C7 / 传闻强化 C8（离线）
├── test_llm.py                LLM 真实连通性（**真实调用 API，勿放周期任务**）
├── e2e_playthrough.py         HTTP 全链路自动通关至结局（**需服务已启动**）
├── capture_playthrough.py     采集真实通关轨迹 → web/doc/playthrough_data.json
├── adversary.py               对抗回归：往玩家侧灌攻击性输入（C6，产出 reports/adversary_report.md）
├── mystery_attack.py          谜团攻击集回归：试诱导 NPC 泄漏后设（C6，产出 reports/mystery_attack_report.md）
├── interview_eval.py          采访式角色评测基准（C5，产出 reports/eval_report.md）
├── tester_drive.py            监督会话专用驱动器：按《资料/01_剧情文本/全分叉树_评审确认版.md》驱动剧情并采帧
└── data/                      采访题库（interview_miyuki.json）与谜团攻击集（mystery_attacks.jsonl）
```

## 跑法

```bash
cd game
python3 tests/test_consistency.py          # 离线，随时可跑
python3 tests/test_branching.py            # 离线
python3 tests/e2e_playthrough.py           # 需要服务已在 8300 上运行
python3 tools/supervisor.py --once         # 全量离线回归 + 健康探测（不上 e2e 也无妨）
```

## 输出到哪

`adversary.py` / `mystery_attack.py` / `interview_eval.py` 的产出写在 **`game/reports/`**（生成物，已 gitignore）。
手写的报告与评审文档不在 `game/` 里，在 `资料/06_开发与评审/`。

## ⚠ 跑测试前须知：引擎是服务端单例

`e2e_playthrough.py`、`tester_drive.py`、`capture_playthrough.py` 都以 `http://127.0.0.1:8300` 为目标
（写死在脚本顶部）。而游戏状态活在**服务进程**里，所以：

- 服务上有一局正在玩的话，跑这些脚本会和它**争用同一份状态**——玩家的进度会被推着走。
- 想安全验证，另起一个隔离实例，并把存档指到临时目录：

```bash
cd game
GAL_SAVE_DIR=/tmp/gal_test/saves GAL_ACCESS_LOG=/tmp/gal_test/access.log \
  python3 -m uvicorn server.app:app --host 127.0.0.1 --port 8311
```

然后把脚本顶部的 `BASE` 改成 `http://127.0.0.1:8311` 再跑。

离线测试（前六个 + 三个带 `--offline` 的评测）不走 HTTP，直接 import 引擎，
但**仍会往 `game/saves/` 写自己的临时槽位**（`t*.json`、`*_test.json`），跑完自行清理。
想完全不碰正式目录，用 `GAL_SAVE_DIR=/tmp/gal_test/saves python3 tests/test_consistency.py` 隔离。
