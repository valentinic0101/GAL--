# web/gen/ —— 生成物，勿手改

本目录的三个 JS 文件**全部由 `game/tools/` 生成**，被 `index.html` 在游戏逻辑之前加载。
手改会在下次重跑工具时被覆盖。

| 文件 | 生成者 | 内容 | 谁在读 |
|---|---|---|---|
| `asset_manifest.js` | `tools/audit_stage.py`、`tools/integrate_art.py` | 已存在的背景/CG/立绘文件名清单 | `js/40_stage.js` —— 缺图时优雅降级（柔和渐晕底 + 「待素材」角标） |
| `stage_meta.js` | `tools/audit_stage.py` | 逐场景地面线、缩放、光照、纵深 | `js/40_stage.js` —— 立绘的地面贴合与亮度匹配 |
| `sprites_meta.js` | `tools/audit_stage.py`、`tools/integrate_art.py` | 每张立绘的脚底透明边距（占图高比例） | `js/40_stage.js` —— 让脚正好踩在地面线上 |

## 要改参数怎么办

舞台参数（每个背景的地面线 / 缩放 / 光照 / 阴影浓度）的**单一来源**是 `game/tools/stage_config.json`。
改它，然后重跑：

```bash
cd game
python3 tools/audit_stage.py
```

该脚本同时做两件事：按《资料/02_设定与设计/舞台匹配规范.md》的六条规则穷举校验「人物–场景匹配」
是否落实，并把校验结果写成上面三个文件。

新增了背景或立绘时同理——先放进 `assets/`，跑一次 `tools/audit_stage.py`，前端就认识它们了。
