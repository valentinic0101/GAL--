# tools/ —— 开发期脚本

这些脚本**不参与游戏运行**，只在做素材、接素材、审计版面、守护服务时用。
全部按 `python3 tools/<脚本>.py` 的形式在 `game/` 目录下运行。

```
tools/
├── paths.py                  ★ 路径单一来源：游戏内素材目录 + 树外的 AI 生图源目录
├── _tools.py                 程序化美术库：渐变/山峦/雪/光晕/暗角/噪点/树/足迹
├── gen_backgrounds.py        重新生成 assets/backgrounds/（16 张，PIL 绘制）
├── gen_sprites.py            重新生成 assets/sprites/ 与 assets/ui/（SVG 立绘 + UI 元素）
├── gen_music.py              重新合成 assets/bgm/（numpy 合成 → afconvert 转 m4a）
├── cutout_sprites.py         立绘抠图：AI 生图源 → assets/sprites/ 透明 PNG
├── integrate_art.py          素材接入管线：扫描生图源 → 裁切/抠图 → 覆盖 assets/ → 写入场景脚本
├── audit_stage.py            舞台匹配审计（对应《资料/02_设定与设计/舞台匹配规范.md》）
├── stage_config.json         ★ 舞台参数单一来源（每个场景的地面线/缩放/光照）→ web/gen/stage_meta.js
├── supervisor.py             监督者：健康探测 → 自动重启 → 离线全量回归（cron 每 30 分钟）
├── rec_audio_daemon.sh       音频录制守护（录网页播放的 BGM，经 BlackHole 虚拟声卡）
├── rec_mic_daemon.sh         麦克风录音守护（扬声器播放 + 麦克风采集）
└── requirements.txt          抠图/绘图依赖清单（rembg 依赖链较重，按需安装）
```

## 两条素材来源

项目的美术有两条来源，替换素材时先弄清你要走哪一条：

| 来源 | 入口 | 说明 |
|---|---|---|
| **AI 生图**（当前主线） | `cutout_sprites.py` / `integrate_art.py` | 从 `资料/03_美术/AI生图源文件/` 读取，裁 16:9、抠成透明 PNG、并自动把 CG/背景嵌进剧本场景 |
| **程序化生成**（初版占位） | `gen_backgrounds.py` / `gen_sprites.py` / `gen_music.py` | 用 PIL/SVG/numpy 画出来的示意级素材，风格统一但精度有限 |

## 关于路径

`paths.py` 是唯一写路径的地方：

```python
ART_SRC     # AI 生图源目录（在 game/ 之外：资料/03_美术/AI生图源文件/）
ASSETS / BACKGROUNDS / SPRITES / CG / BGM / WEB
```

以前 `SRC = os.path.join(os.path.dirname(ROOT), 'Gemini 绘图')` 硬编码在两个脚本里，
资料一搬家就要改多处。现在源目录可以用环境变量覆盖：

```bash
GAL_ART_SRC=/path/to/生图源 python3 tools/integrate_art.py
```

## 关于抠图环境（重要）

`cutout_sprites.py` 的主算法用 `rembg(isnet-anime)`，它的依赖链（onnxruntime + opencv + scipy +
llvmlite/numba）装完约 495MB，因此**项目内不再保留 `.venv`**。需要重新抠图时：

```bash
python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
.venv/bin/python tools/cutout_sprites.py            # 全部立绘
.venv/bin/python tools/cutout_sprites.py miyuki_smile toba   # 指定立绘
```

用系统 `python3` 直接跑也不会报错，但会因缺少 rembg 而自动退回旧的「边框取色 + 洪泛填充」算法，
边缘质量明显较差（发丝与浅色衣物尤其明显）。只需改尺寸或裁切时，`pillow` + `numpy`（约 33MB）就够。

首次跑 rembg 会下载 isnet-anime 模型（约 176MB）到用户目录。

## audit_stage.py 会写文件

`audit_stage.py` 除审计外还负责**再生成**前端的三个素材清单：

```
tools/stage_config.json  ──►  web/gen/stage_meta.js     逐场景地面线/缩放/光照
assets/sprites/*.png     ──►  web/gen/sprites_meta.js   每张立绘的脚底透明边距
assets/*                 ──►  web/gen/asset_manifest.js 已有素材清单（前端缺图优雅降级用）
```

这三份是生成物，**不要手改**（改了下次重跑就被覆盖）。要改参数请改 `stage_config.json` 后重跑本脚本。
