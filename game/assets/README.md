# 素材目录（可整体替换）

本目录只放**美术与音频素材**，是后期 AI 生图 / 配乐替换的唯一落点。生成脚本已移到 `../tools/`，代码只按下面的固定路径读取文件。

## 替换规则（重要）

1. **保持文件名与扩展名完全不变**，直接覆盖同名文件即可生效（服务器静态托管，刷新浏览器即见）。
2. 若想把立绘从 SVG 换成 PNG：新图命名为 `miyuki_normal.png` 这类名字放进 `sprites/`，再把 `../server/agents/personas.py` 中各角色 `sprites` 字段里的文件名后缀 `.svg` 改成 `.png`。
3. 各素材的生图提示词成品在根目录 `设计文档/AI绘图提示词.md`（含尺寸建议：背景 1280×720，立绘 2:3 约 1024×1536、纯色底便于抠图）。

## 目录清单

| 目录 | 内容 | 现状 |
|---|---|---|
| `backgrounds/` | 12 张场景背景图（1280×720 PNG） | PIL 程序化生成 |
| `sprites/` | 10 个角色立绘（SVG）：深雪×5 表情（normal/smile/sad/surprise/white）、修二×2 时期（child/teen）、鸟羽、亲戚男/女 | 程序化 SVG |
| `bgm/` | 6 首 BGM（m4a）：title/main/daily/sad/festival/blizzard | numpy 合成 |
| `ui/` | 名牌底 `nameplate.svg`、雪花角饰 `frame_corner.svg` | 程序化 SVG |

## 地面贴合机制

每张立绘的**脚底透明边距**由 `tools/integrate_art.py` 自动测算并写入 `web/sprites_meta.js`；每个背景的**地面线**标定在 `web/main.js` 的 `SCENE_GROUND` 表（视觉逐张校准，单位=脚线距底部占比与人物比例）。新增立绘/背景后重跑接入管线即可自动获得贴合，无需手工调位置。

## 重新生成（可选）

```bash
cd game
python3 tools/gen_backgrounds.py   # 重新生成 12 张背景（注意：无固定随机种子，图会变化）
python3 tools/gen_sprites.py       # 重新生成全部立绘与 UI SVG
python3 tools/gen_music.py         # 重新合成 6 首 BGM（依赖 numpy + afconvert）
```
