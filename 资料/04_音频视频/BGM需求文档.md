# BGM 需求文档 —— 雪国 GAL《深雪》

> 依据：剧本原文（素材文本/原文剧本.txt）+ 游戏流程（game/server/scenes/script.py、game/server/engine.py:52-65）。
> 目标：替换 `game/tools/gen_music.py` numpy 合成的 6 首 BGM。
> 替换机制：转成 **m4a** 后**同名覆盖** `game/assets/bgm/bgm_*.m4a`（见 game/assets/README.md，静态托管，刷新即生效）。新文件先存放于 `game/assets/bgm_mureka/`，确认后再覆盖。
> 提示词可直接整段粘贴进 Mureka 的描述框。所有曲目均为**纯音乐（instrumental, no vocals）**，需可循环、无突兀结尾。

---

## 一、BGM 需求总览（哪里需要、要什么感觉）

游戏情绪线：**丧亲之痛 → 雪国相遇的温暖 → 祭典夜的依靠 → 车站离别的约定 → 三年空缺 → 重逢的日常 → 离别与幸福之问 → 分歧结局**。

| # | 引擎键 | 标题 | 覆盖位置 | 核心情绪 | 优先级 |
|---|--------|------|----------|----------|--------|
| ① | `bgm_title` | 纯白的约定 | 标题画面（bg_title） | 纯净、怅然、命运的约定感 | ⚠️ 已上线（录音版偏闷，待重做） |
| ② | `bgm_main` | 与你看过的雪 | P1 初遇 / P5 刻身高 / P7 欢迎回家 / P9 柱上的痕 / P12B 田间小路 / E_SPRING 等到花开；幕间 station、fields | 温暖希望中的羁绊与宿命感 | ✅ 已完成上线 |
| ③ | `bgm_daily` | 炉边日常 | P3 你的姐姐啊 / P8 老屋的日常 / E_STAY 炉火与春讯；幕间 oldhouse 全部、town_street、toba_home | 治愈、俏皮、生活感 | ★★★ 今日 |
| ④ | `bgm_sad` | 无人站台 | P2 清雪（忆双亲痛哭）/ P6 深雪（车站离别）/ P10 齐刘海 / P11 一年后的岔路 / E_FAR 两行足迹 / E_TOKYO 东来的雪 | 克制的悲伤、思念、孤独 | ★★★ 今日 |
| ⑤ | `bgm_festival` | 篝火太鼓 | P4 冬祭之夜；幕间 shrine_road、shrine | 太鼓祭典的热闹与幻境感 | ★★ 明日 |
| ⑥ | `bgm_blizzard` | 白之彼方 | P0 白之彼方 / P12M 雪径；幕间 mountains、blizzard | 神秘、敬畏、山的魔性 | ★★ 明日 |
| ⑦ | （新增 `bgm_lullaby`） | 摇啊摇 | P4 结尾深雪背修二唱小夜曲一段；可延伸到 E_STAY | 摇篮曲、音乐盒、安心入眠 | ★ 后续 |
| ⑧ | （新增 `bgm_spring`） | 等到花开 | E_SPRING 结局专用（樱花树下的春天） | 春天、释然、奇迹般的美 | ★ 后续 |

> ⑦⑧ 为新增键，需要改 engine.py 映射后才生效，暂缓；E_SPRING 在此之前沿用 ②。

---

## 二、逐条需求（位置 - 标题 - 完整详细提示词）

### ① `bgm_title` 《纯白的约定》(Pure White Promise) —— 今日必做 ★★★

- **位置**：标题画面（bg_title，游戏打开的第一眼与第一耳）；结束回到标题时再次响起。
- **需求**：这是全游戏的"脸"。要像**站在无人的雪原上想起一个约定**：安静、纯净、微凉，但底下有一缕温柔的暖意。不能是纯悲伤，也不能甜腻。钢琴主导，要有让人记住的旋律主题。循环播放不腻、不吵。
- **时长目标**：100–140 秒，结尾平滑可循环。
- **完整提示词（粘贴用）**：

```
Instrumental anime visual novel title theme, no vocals. A gentle, pure and wistful winter ballad: solo piano carries a memorable, tender main melody like a quiet promise made in deep snow, joined by warm soft strings, a delicate music-box / glockenspiel sparkle like falling snowflakes, and a faint low pad like distant mountains under an overcast sky. Melancholic but with an undercurrent of warmth and hope, never sentimental or heavy. Slow tempo around 66 BPM, 6/8 swaying feel, spacious natural reverb, sparse arrangement with breathing silence between phrases. Ends softly so it can loop seamlessly. Snow-country nostalgia, Japanese countryside, pure white world, fate and longing.
```

- 中文对照：纯音乐视觉小说标题曲，无人声。温柔纯净、怅然的冬日叙事曲：钢琴独奏承担令人难忘的柔美主题，像在深雪中许下的安静约定；加入温暖的弦乐铺底、音乐盒/钢片琴的雪花般点缀、低音铺底如阴天下的远山。忧伤中藏着暖意与希望，不煽情不沉重。约 66 BPM，6/8 摇曳感，空间混响，乐句间留白，结尾轻收便于无缝循环。雪国乡愁、命运与思念。

### ② `bgm_main` 《与你看过的雪》(The Snow We Watched Together) —— 今日必做 ★★★

- **位置**：P1 初遇（她在雪光中走来）、P5 刻身高（柱上的约定）、P7 欢迎回家（三年后重逢）、P9 柱上的痕（约定延续）、P12B 田间小路（并肩同行）、E_SPRING 等到花开（樱花结局）；幕间自由行动：station、fields。
- **需求**：全游戏出场时间最长的"羁绊主题"。温暖、明亮、有希望，但要**始终罩着一层雪国的薄雾**——幸福里掺着"这一切或许不真实"的宿命感。中速流动感，钢琴+弦乐为主，可加长笛像风穿过林间。情绪比 ① 明亮、比 ③ 深沉。
- **时长目标**：120–160 秒，可循环。
- **完整提示词（粘贴用）**：

```
Instrumental anime visual novel main theme, no vocals. Warm, hopeful and flowing with a gentle fateful undertone: expressive piano lead, lush but restrained string ensemble, light flute like wind through winter trees, soft acoustic guitar arpeggios and a subtle glockenspiel like sunlight on snow. Middle tempo around 84 BPM, gentle forward motion, major key with occasional wistful minor-color chords, like happiness shadowed by the knowledge that it may be fleeting. Emotionally uplifting but serene and a little mysterious, the bond between two people in a snow country. Clean natural mix, smooth ending that can loop.
```

- 中文对照：纯音乐视觉小说主题曲，无人声。温暖、充满希望而流动，带着温柔的命运感：钢琴主奏，克制而丰盈的弦乐群，长笛如穿过冬林的清风，木吉他分解和弦与雪上阳光般的钢片琴。约 84 BPM 中速，大调为主、偶有怅然的小调色彩和弦——像被"这份幸福也许短暂"的预感罩上薄雾。振奋而安宁、略带神秘，雪国二人的羁绊。结尾平滑可循环。

### ③ `bgm_daily` 《炉边日常》(Everyday by the Hearth) —— 今日必做 ★★★

- **位置**：P3 你的姐姐啊（雪球大战的淘气）、P8 老屋的日常（被炉、清雪、纸牌、晚饭）、E_STAY 炉火与春讯（留下的结局）；幕间自由行动：oldhouse_in、oldhouse_corridor、courtyard、oldhouse_front、town_street、toba_home。
- **需求**：播出频率最高的"生活曲"。轻松、温暖、俏皮，冬天屋子里的炉火气与人情味；P3 有打雪仗，所以可以带一点**蹦跳的淘气感**，但整体是治愈系。不能阴郁，不能电子感，要"木头房子、热汤、笑声"的音色。
- **时长目标**：90–140 秒，轻快耐循环。
- **完整提示词（粘贴用）**：

```
Instrumental cozy slice-of-life visual novel BGM, no vocals. Heartwarming and playfully mischievous winter daily-life music: bouncy pizzicato strings, light cheerful piano, glockenspiel twinkles, soft clarinet or recorder melody, gentle acoustic guitar, hand claps and a light shaker groove. Mid tempo around 100 BPM, bouncy staccato rhythm like a snowball fight, switching to a warm singable legato phrase like relaxing by the irori hearth. Major key, innocent, funny and healing, Japanese countryside wooden house in winter, warm soup and laughter atmosphere. Simple catchy structure, smooth loopable ending.
```

- 中文对照：纯音乐治愈系日常 BGM，无人声。温暖带点淘气的冬日生活曲：蹦跳的拨弦弦乐、轻快钢琴、钢片琴闪烁、单簧管/竖笛旋律、木吉他、拍手与沙锤轻律动。约 100 BPM 中速，断奏节奏像打雪仗，间或转为温暖的如歌乐句像围炉休息。大调、天真、有趣、治愈，冬日木屋、热汤与笑声的气息。结构简单上口，结尾平滑可循环。

### ④ `bgm_sad` 《无人站台》(The Empty Platform) —— 今日必做 ★★★

- **位置**：P2 清雪（清雪时忆起父亲→痛哭）、P6 深雪（车站离别、"我还会回来"）、P10 齐刘海（离别与"现在幸福吗"）、P11 一年后的岔路（无人来接的站台）、E_FAR 两行足迹（怅然送别）、E_TOKYO 东来的雪（多年后的东京）。
- **需求**：全游戏情感最重的一曲。**克制的悲伤**——不是嚎啕，是"眼泪无声落在雪上"：孤独、思念、悔恨，也有一点点无法放弃的等待。钢琴独奏为主体，弦乐在第二段渗入，留白要多。60 BPM 上下，小调。结尾要轻到几乎消散（各场景常在其高潮或独白处切入，需安静兜底）。
- **时长目标**：120–160 秒，安静可循环。
- **完整提示词（粘贴用）**：

```
Instrumental sad visual novel BGM, no vocals. Restrained, deeply melancholic winter elegy: a lonely felted piano plays a sparse sorrowful melody with many silences between notes, a lamenting solo cello and faint violins slowly join in the second half, distant music box chimes like an almost-forgotten childhood memory. Very slow around 58 BPM, minor key, cold and quiet like snow falling on an empty countryside station platform at dusk, grief of loss and longing for someone who promised to wait, but with a fragile thread of hope that refuses to let go. Extremely sparse, delicate dynamics, long reverb tail, ends almost silently for seamless quiet looping.
```

- 中文对照：纯音乐悲伤 BGM，无人声。克制而深沉的冬日挽歌：孤独的毛毡钢琴奏出稀疏悲怆的旋律，音符之间大量留白；第二半段哀伤的大提琴与微弱小提琴缓缓渗入，远处的音乐盒音色像快要被遗忘的童年记忆。约 58 BPM 极慢，小调，冷而安静——像黄昏无人乡下站台落雪；失去的悲恸与对"说要一直等我"之人的思念，但仍有一缕不肯放手的微弱希望。极简、细腻的力度层次、长混响尾音，结尾近乎无声以便安静循环。

### ⑤ `bgm_festival` 《篝火太鼓》(Bonfire and Drums) —— 明日 ★★

- **位置**：P4 冬祭之夜（太鼓声、篝火、夜市、神社参道、背上的小夜曲前段）；幕间自由行动：shrine_road、shrine。
- **需求**：全游戏唯一"热闹"曲，也是唯一强烈和风曲。祭典太鼓+笛的热闹幻境感：**火焰般的赤色**与**群山之夜的深黑**并存——热闹里有神秘，靠近神社时黑暗渐浓。太鼓节奏贯穿，笛声悠扬，带仪式感。
- **时长目标**：100–140 秒，节奏型可循环。
- **完整提示词（粘贴用）**：

```
Instrumental Japanese winter festival music, no vocals. A lively traditional matsuri scene at night: powerful taiko drum ensemble with dynamic rhythmic patterns, bright shinobue bamboo flute playing a festive folk melody, hyoshishi wooden clappers and small kane gongs, a crowd-like festive energy with bonfire warmth. Energetic middle-fast tempo around 118 BPM, pentatonic Japanese scale, festive and communal but with a mysterious awe underneath, as if the glowing shrine gate at the mountain top stands between the human world and something sacred. Authentic folk instrumentation, acoustic, no modern instruments, driving rhythm suitable for looping.
```

- 中文对照：纯音乐日本冬祭曲，无人声。夜晚热闹的传统祭典场景：强劲的太鼓群动态节奏、明亮的筱笛奏出节庆民谣旋律、拍子木与小锣，篝火般温暖的人群热闹感。约 118 BPM 中快板，日本五声音阶，节庆而群聚，底下藏着神秘敬畏——像山顶发光的神社立于人间与神圣之物的边界。地道民乐编制、原声乐器、无现代乐器，节奏驱动型适合循环。

### ⑥ `bgm_blizzard` 《白之彼方》(Beyond the White) —— 明日 ★★

- **位置**：P0 白之彼方（暴风雪山中雪女幻影·谜之结局）、P12M 雪径（独自走在雪径）；幕间自由行动：mountains、blizzard。
- **需求**：全游戏最"异质"的一曲。**山的魔性**：暴风雪的呼啸、无边的纯白、孤独与死亡预感，同时又美得摄人心魄——恐怖与美是一体（雪女在此显现）。氛围音乐为主，人声可用"无词女声吟唱"质感表现雪女咏叹（如无法实现则用纯器乐+风声纹理），节奏感要弱。
- **时长目标**：120–180 秒，氛围循环。
- **完整提示词（粘贴用）**：

```
Instrumental dark ambient visual novel BGM, no percussion, no drums. A mystical and awe-inspiring blizzard on sacred mountains: cold wind-like filtered noise textures, deep slow drone pads, sparse resonant piano notes falling like lone snowflakes, and a distant ethereal female voice-like synth pad singing wordless ariettes from far away, beautiful and eerie like a snow spirit glimpsed through whiteout snow. Very slow, weightless, no beat, vast space and silence like a frozen otherworld that swallows time and life. Both frightening and breathtakingly beautiful, supernatural, sacred and lonely. Seamless ambient loop.
```

- 中文对照：纯音乐暗黑氛围 BGM，无打击乐无鼓点。神圣群山上神秘而令人敬畏的暴风雪：冷风般的滤波噪声纹理、深沉缓慢的持续音铺底、稀疏共鸣的钢琴音如孤落的雪花，远处空灵女声质感的合成器铺底唱着无词咏叹——像白毛风雪中惊鸿一瞥的雪之精灵，美丽而诡异。极慢、失重、无节拍，广阔的空间与寂静如冻结时间的异界，吞噬时间与生命。既骇人又美得令人屏息，超自然、神圣、孤独。无缝氛围循环。

### ⑦（新增）`bgm_lullaby` 《摇啊摇》(Yurayura) —— 后续 ★

- **位置**：P4 结尾——深雪背着修二走夜路，唱"摇啊摇，摇啊摇，山里的小狐狸也不吵"的古老歌谣；可延伸至 E_STAY 夜谈。**建议后续加进 engine：P4 后半段切换。**
- **需求**：音乐盒质感的摇篮曲，像少女在耳边轻轻哼唱。极简、催眠、安心。如 Mureka 支持人声，可选"轻柔女性哼唱 wordless humming"；默认仍做纯音乐。
- **完整提示词（粘贴用）**：

```
Instrumental gentle lullaby, no vocals. A fragile antique music box plays a simple old Japanese folk-style cradle melody, joined by very soft piano and a whisper of strings, extremely intimate and close like a girl softly humming beside your ear while carrying you through a dark snowy night path under a hazy moon. Very slow around 60 BPM, swaying rocking rhythm, dreamy, safe and tender, slightly melancholic and mysterious, like falling asleep wrapped in warmth while snow falls silently outside. Quiet ending for looping.
```

- 中文对照：纯音乐温柔摇篮曲，无人声。脆弱的古董音乐盒奏出简单的日本民谣风摇篮旋律，加入极轻的钢琴与一缕弦乐气声，极近距离的亲密感——像朦胧月下背着走过漆黑雪夜山路时，少女在耳畔轻轻哼唱。约 60 BPM 极慢，摇曳的摇篮节奏，梦幻、安稳、温柔，略带怅然与神秘，像在窗外无声落雪时裹着暖意入睡。安静收尾可循环。

### ⑧（新增）`bgm_spring` 《等到花开》(When the Flowers Bloom) —— 后续 ★

- **位置**：E_SPRING 等到花开（春假，樱花树下的奇迹）。接入前沿用 ②。
- **需求**：全游戏唯一"春天"曲：积雪消融、樱花开放、一切不可思议被温柔地原谅。明亮但不热烈，带着"奇迹终于发生"的释然与想落泪的美好。可视为 ② 的春天变奏。
- **完整提示词（粘贴用）**：

```
Instrumental spring visual novel ending theme, no vocals. Tender and luminous spring ballad: gentle piano and warm string ensemble, sweet solo violin melody, soft flute like a spring breeze through cherry blossoms, light harp glissando like petals falling. Moderate tempo around 76 BPM, bright major key with tears-of-relief bittersweet chords, the quiet miracle of snow melting and cherry blossoms finally blooming after a long promise. Serene, forgiving, breathtakingly gentle, ending softly like petals settling on still water. Smooth loopable ending.
```

- 中文对照：纯音乐春天结局曲，无人声。温柔明亮的春日叙事曲：钢琴与温暖弦乐群、甜美的独奏小提琴旋律、如春风穿过樱花的轻柔长笛、如落樱的轻竖琴滑音。约 76 BPM 中速，明亮大调掺着"释然之泪"的苦乐参半和弦——漫长约定后积雪消融、樱花终于盛开的静静奇迹。安宁、宽恕、美得令人屏息，如花瓣落定静水般轻收尾。平滑可循环。

---

## 三、时长与格式要求（无硬性上限）

- **时长**：每首目标 **90–150 秒**，**无硬性上限**——游戏引擎（web/main.js）对 BGM 是无限循环播放，略长可循环使用或后期剪短；过短（<60s）循环感才明显。
- **循环性**：必须能循环，避免突兀结尾（原提示词中已要求 soft ending / seamless loop）。
- **提示词追加要求**：向 AI 工具提交提示词时，在末尾追加时长指引，例如 `Around 2 minutes long` / `Target length 90-120 seconds`，减少无效生成。
- **格式链**：WAV 录制（48kHz/16bit）→ `afconvert -f m4af -d aac -b 256000` 转 m4a（与原 gen_music.py 输出一致）→ 同名覆盖 `game/assets/bgm/`。
- **Mureka 产出规则**：每次 Create 固定生成 **2 个版本**（无法改为 1 个），费用按一次计；每版都要录下来，择优替换。
- **混音要求（重要，实测教训）**：首曲《雪国ノスタルジー》的混音**低频严重过量**——40–120Hz 占总能量 26.7%、峰值频率 92Hz，且低频是**卡在节拍上的周期性闷响**（约 1.2 次/秒）；同时 **2kHz 以上仅剩 0.1%** 能量。
  - 后果：低频偏重会让整体发闷、并在小喇叭上加重“打闷包”感（**注：此前把“噗噗”归因于此，已证伪——噗噗实为录音端丢样本，见 4.3**）。
  - **后续提示词统一在末尾追加**：`Mid-forward balanced mix, bright clear piano, no drums, no percussion, no heavy sub-bass, avoid boomy low end; keep the melody in the 200Hz-2kHz range so it stays clear on laptop speakers.`
  - 生成后必查：用 ffmpeg 解码后做频谱分段统计，若 40–120Hz 占比 >15% 或 2–6kHz <1%，即需 EQ 修正或重生成。

## 四、替换实施说明

### 4.1 Mureka 实操要点（今日实测，重要）

- **桌面 App 不可用**：`Mureka Co.app`（mureka-desktop）整体是 Pro/Premier 专属，Free 账号连生成都会被付费墙拦截。
- **用网页版** `https://www.mureka.ai/`（账号「曲水」Free）：勾选 **Instrumental** 出纯音乐；模型 **V9.5 每日免费 1 次**，用完自动降级到 **V7.5-all（可无限免费创作）**；每次 Create 固定产出 **2 个版本**，按一次计费。
- **免费账号不能下载**：下载菜单里 MP3/WAV/Stems/Video 全部带 Pro 标记，点击会跳到订阅页。**解决方案 = 虚拟声卡录音**（见 4.2），音质等于播放流，反而比 MP3 下载更好。
- **输入提示词的手法**：页面的 Style 输入框是 React 组件，**空字段无法用辅助功能写值**。做法：先点一个官方示例提示词按钮把字段填非空，再用 `set_value` 替换成目标提示词（校验会返回 matched）。
- **时长**：生成版实测 150s / 133s，符合 BGM 需求；如需更短可在提示词末尾追加 `Around 90 seconds`。

### 4.2 虚拟声卡录音流程（BlackHole，已验证可用）

依赖：`brew install ffmpeg switchaudio-osx`、`brew install --cask blackhole-2ch`（驱动需 GUI 安装器输密码）。

1. 终端启动守护进程（**必须经 Terminal，否则 macOS 静默拒权限、录到全静音**）：
   `bash game/tools/rec_audio_daemon.sh`
2. 系统输出切到虚拟声卡（此期间听不到声音属正常）：
   `SwitchAudioSource -t output -s "BlackHole 2ch"`
3. 开始录：`echo "/tmp/take.wav" > /tmp/rec_start`；在浏览器里播完目标曲目；停止：`touch /tmp/rec_stop`
4. 切回音箱：`SwitchAudioSource -t output -s "MacBook Air扬声器"`
5. 切分（**关键坑**）：`-ss` 必须放在 `-i` **之前**（输入定位）；放在后面时时间戳不归零，`afade` 淡出点会落到音频开始之前导致整段静音。
   `ffmpeg -ss 22.19 -t 150.04 -i take.wav -af "afade=t=in:st=0:d=0.3,afade=t=out:st=149.74:d=0.3" out.wav`
6. 转 m4a：`afconvert -f m4af -d aac -b 256000 out.wav bgm_xxx.m4a`；峰值贴顶时加 `-af volume=-4.5dB` 留余量。

### 4.3 录音链路结论：BlackHole 不可用于成品交付（重要，已定案）

**现象**：成品文件在高音量下出现**有节奏的“噗噗 + 卡顿”**（约每秒 2–4 次）。

**定位过程**：
1. 频谱实验：白噪声经 BlackHole 播录，各频段衰减 +0.1dB 以内、到 20kHz 全程平坦 → **频谱上透明**（不染色、不吃高频）。
2. **但存在样本级不连续（丢样本）**：以「相邻样本突变」为指标量化——

| 文件 | 突变 >0.5×峰值 | >0.3×峰值 | >0.2×峰值 |
|---|---|---|---|
| 旧 numpy 曲（程序直接合成，未过录音） | **0** | **0** | **0** |
| 首曲录音第 1 版 | 92 | 331 | 611 |
| 首曲录音第 2 版 | 53 | 239 | 448 |

3. 判据：该曲带宽仅约 2kHz，2kHz 正弦在 48kHz 采样下的理论最大样本间斜率约 0.13。**故突变超过 0.1 即非音乐内容**；干净参照文件在 0.2×峰值以上为 0 处。
4. 用户听感对照（决定性）：**在 mureka.ai 网页直接播放 → 干净；同一个文件 → 噗噗**。音源无问题，瑕疵由录音写入。

**结论**：BlackHole 采集会引入每 150 秒约 300–600 处样本不连续（疑似时钟漂移/缓冲欠载），**性质上不可接受，不做后处理修复**（曾尝试 declick 修复，只能覆盖少量，无法根治）。

**因此：成品音频必须走官方下载获取**，不要再以 BlackHole 录音作为交付来源。若日后仍需录制，需先解决采集端时钟（聚合设备+漂移校正）并**用上述突变指标验收**（>0.2×峰值 必须为 0 处）后才可采用。

**备选方案（仅当平台无法下载时考虑，质量有损）**：

| 方案 | 原理 | 质量 | 说明 |
|---|---|---|---|
| 官方下载 | 直接取原文件 | ★★★ 无损 | 首选。注意 Suno 免费额度仅 7 次终身下载 |
| 电气回路 | 耳机口→线路输入，硬件时钟采集 | ★★☆ 接近原文件 | 需 USB 声卡或音频线；无房间反射、不漂移，**推荐优先试** |
| 麦克风声学 | 喇叭放声、麦克风采集 | ★☆☆ 明显发闷 | 用 `game/tools/rec_mic_daemon.sh`；受喇叭频响(150Hz 以下放不出)+房间反射+底噪限制 |

三种方案都必须过突变体检；Suno 条款明确禁止「录制播放」获取副本，选用时请自行权衡。

**验收脚本**（对本项目任何 BGM 成品都应执行）：

```bash
python3 - <<'EOF'
import numpy as np, subprocess
sr=48000
def load(p):
    raw=subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True).stdout
    return np.frombuffer(raw,dtype=np.float32).astype(np.float64)
x=load('待检文件.m4a'); pk=np.abs(x).max(); d=np.abs(np.diff(x))
print('突变 >0.5pk:%d  >0.3pk:%d  >0.2pk:%d'%((d>0.5*pk).sum(),(d>0.3*pk).sum(),(d>0.2*pk).sum()))
EOF
```

### 4.4 首曲低频修正记录（次低频过量，与上面是两回事）

首曲混音本身低频偏重（40–120Hz 占 26.7%、峰值 92Hz、2kHz 以上仅 0.1%），在笔记本小喇叭上会加重“打闷包”。已做外科式 EQ 修正（**注意：这一步不能解决 4.3 的丢样本问题**）：

- 配方：`highpass=f=40:poles=2, equalizer=f=92:t=q:w=1.2:g=-9, volume=-1dB`
- 效果：40–120Hz 26.7% → 8.4%，200–2000Hz 主体 53.1% → 76.8%，峰值 0.81 → 0.67。
- 更狠的备选：`highpass=f=110:poles=2`（40–120Hz 降至 9.2%）。

### 4.5 接入游戏

1. 生成音频 → `afconvert` 转 AAC m4a（与原 gen_music.py 输出一致）：
   `afconvert -f m4af -d aac -b 256000 输入.mp3 game/assets/bgm_mureka/bgm_xxx.m4a`
2. 新文件统一放 `game/assets/bgm_mureka/`（目录说明见该目录 `README.md`），**不直接覆盖** `game/assets/bgm/`；全部确认后用 `cp game/assets/bgm_mureka/bgm_*.m4a game/assets/bgm/` 同名覆盖（旧 numpy 版先备份到 `game/assets/bgm/_numpy_backup/`）。
3. 刷新浏览器即生效（静态托管，无需改代码）。⑦⑧ 需改 engine.py 的 SCENE_BGM/LOC_BGM 并在 web/main.js 注册文件后生效。
   - `/assets` 挂的是标准 `StaticFiles`（`app.py:182`），发 ETag/Last-Modified；带 `max-age=86400` 的 `NoCacheStaticFiles` 只作用于 `/` 前端目录，所以换 BGM 后普通刷新即可，不必清缓存。
   - 端到端自查：`curl -s -o /tmp/x.m4a http://127.0.0.1:8300/assets/bgm/bgm_main.m4a` 后比对 SHA，确认服务端返回的就是新文件。

### 4.6 ① ② 落地处理记录（2026-09-16 夜）

源文件存于 `game/assets/bgm_mureka/_源文件/`（用户经 OPPO 互联传入，均为 320kbps / 48kHz 立体声 mp3）。

处理链：`ffmpeg` 解成 48k/24bit WAV 母版 → `atrim` 裁掉开头 0.10s 数字静音并定长 → `volume` 对齐响度 → `afade` 首 0.4s 淡入 / 尾 1.3–1.5s 淡出 → `afconvert -f m4af -d aac -b 256000`。
**裁剪用 `atrim` 而非 `-ss`**：`-ss` 放在 `-i` 之后会因时间戳不归零让淡出点落到音频之前（4.2 踩过的坑）。

| 项目 | ① 标题曲（来自“音频1”，录音） | ② 主线曲（来自“音频2”，官方成品） |
|---|---|---|
| 源时长 / 落地时长 | 173.2s / **171.4s** | 210.1s / **210.1s** |
| 处理增益 | +9.2 dB | +1.8 dB |
| 成品响度 | −15.69 LUFS | −15.61 LUFS |
| 成品真峰 | −1.15 dBTP | −0.97 dBTP |
| **突变 >0.2×峰值**（交付门槛） | **0 处** ✅ | **0 处** ✅ |
| 99.9% 能量上限（中位） | 1324 Hz ⚠️ 闷 | 3949 Hz ✅ |
| 本底噪声 | −67 dBFS（可闻底噪） | —（数字淡出） |
| 与曲库一致性 | 现有 6 首为 −10.9~−15.4 LUFS / 真峰 ≈−1.2 dBTP，两者均落在同区间 | 同左 |

**结论**：② 是干净成品，直接可用。① 虽已修掉丢样本瑕疵（相比 Mureka 录音版 611 处突变是质变），但录音链把 2kHz 以上内容整个吃掉了，听感会偏闷、像隔着门，**属于临时可用、建议重做**——重做时务必走官方下载，不要再用录音。

> 更新时间：2026-09-16 夜。① ② 已上线到 `game/assets/bgm/`（原 6 首 numpy 版备份在 `bgm/_numpy_backup/`，SHA 校验通过）。

| # | 引擎键 | 标题 | 状态 | 来源 | 文件 |
|---|--------|------|------|-------------|------|
| ① | bgm_title | 纯白的约定 | ⚠️ **已上线但音质有短板**：无丢样本瑕疵，但录音把高频削掉了（99% 能量在 659Hz 以下，2kHz 以上 −57dB），且本底噪声 −67dBFS；**待用官方下载重做** | 录音版（音频1） | `bgm/bgm_title.m4a`（171.4s，已转 256k AAC）｜旧候选隔离在 `bgm_mureka/_废弃_Mureka录音瑕疵版/` |
| ② | bgm_main | 与你看过的雪 | ✅ **已完成并上线**：突变 0 处、响度 −15.6 LUFS / 真峰 −0.97 dBTP、99.9% 能量上限 3.9kHz（全项目最亮） | Suno 成品（音频2，官方文件） | `bgm/bgm_main.m4a`（210.1s）｜源文件 `bgm_mureka/_源文件/音频2_主线曲.mp3` |
| ③ | bgm_daily | 炉边日常 | 待制作（今日） | — | — |
| ④ | bgm_sad | 无人站台 | 待制作（今日） | — | — |
| ⑤ | bgm_festival | 篝火太鼓 | 待制作（明日限额恢复后） | — | — |
| ⑥ | bgm_blizzard | 白之彼方 | 待制作（明日限额恢复后） | — | — |
| ⑦ | bgm_lullaby | 摇啊摇 | 待制作 | — | — |
| ⑧ | bgm_spring | 等到花开 | 待制作 | — | — |
