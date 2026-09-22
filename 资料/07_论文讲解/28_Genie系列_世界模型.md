# 论文讲解 28：Genie 系列——生成式交互世界模型（Genie 1/2/3）

> 来源：《Generative_Agents_讲解与前沿进展.md》第三节"世界模型线"（Genie → Genie 2 → Genie 3）
> 评分基准同 README

## 🎯 与 GAL 项目的相关度：3.5 / 10

世界模型线与 LLM agent 线的汇合点（"环境可生成、角色由 agent 扮演、剧情共同涌现"）是远期图景：Genie 3 的"文字指定天气/新增角色"若成熟，galgame 的**演出层**（雪国小镇的动态背景、事件演出）可以低成本生成。但当下它们无论文版评测、一致性只能维持分钟级，对本项目没有可执行动作。

---

## 一、论文链接

| 代际 | 形式 | 链接 |
|---|---|---|
| **Genie 1**（2024.02） | ICML 2024 正式论文（PMLR v235） | <https://arxiv.org/abs/2402.15391> ｜ [项目页](https://sites.google.com/view/genie-2024/home) |
| **Genie 2**（2024.12） | DeepMind 官方博客，**无论文** | <https://deepmind.google/discover/blog/genie-2-a-large-scale-foundation-world-model/> |
| **Genie 3**（2025.08） | DeepMind 官方博客，**无论文**，limited research preview | <https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/> |

作者：Jake Bruce, Michael Dennis, Ashley Edwards, Jack Parker-Holder 等 25 人（Google DeepMind × UC Berkeley）。

## 二、论文本身

### 2.1 Genie 1：从无标注视频学生成可玩游戏

11B 参数，三个组件：① 时空视频 tokenizer（VQ-VAE + ST-transformer）；② **Latent Action Model（LAM）**：从相邻帧之间**无监督推断离散隐动作**（仅 8 个，类似手柄按键）——不需要任何动作标签；③ 自回归 dynamics model（MaskGIT 式并行去噪），据历史 token + 隐动作预测下一帧。训练数据：约 3 万小时 2D 平台游戏网络视频（数字来自第三方解读，请以论文为准）。推理约 1 fps、16 帧上下文。学到的隐动作空间还能训练 agent 模仿从未见过的视频行为。

### 2.2 Genie 2：大规模基础世界模型

单张图片（Imagen 3 或真实照片）→ 可玩 3D 环境；自编码器潜帧 + 因果掩码大 transformer（官方称 "autoregressive latent diffusion"），每步接收键鼠动作，classifier-free guidance 增强动作服从。**长时程记忆**：记住离开视野的区域并在回看时正确重渲染；涌现物体交互、NPC、物理（水/烟/重力）、光照反射。

### 2.3 Genie 3：实时可交互世界生成

**720p、24 fps** 实时可导航；一致性可持续数分钟（视觉记忆约 1 分钟）；无需显式 3D 表征（一致性是涌现能力）；新增 **promptable world events**——运行中用文字改变天气、添加新物体和角色（但事件不由 agent 自身执行）。

## 三、评价所用的技术

- **Genie 1**：人类评估者对动作可控性打分/偏好评估；**线性探针**（如 CoinRun 物体位置解码）比较训练/未见环境的**探针泛化差距**——表征泛化性的代理指标；用 Genie 隐动作训练的 BC agent 接近 oracle 策略。无统一标准数字（FVD 等待核原文）。
- **Genie 2 / Genie 3**：**纯定性**——试玩演示、同起点反事实轨迹、用 SIMA agent 测环境一致性；无任何量化基准（因为是博客发布）。官方自述局限：只能连续交互几分钟、事件不能由 agent 执行、多智能体未解决、真实地理精度不足。

## 四、对 GAL 项目的启发

1. **演出层的远期选项**：立绘/背景的"动态化"（雪一直下、钟停 4:49 的氛围镜头）未来可能直接由世界模型/视频生成模型承担，AI绘图提示词.md 的美术资产未来可升级为生成式背景。**当下不动**：现有 AI 绘图 + 静态立绘的性价比远高于实时世界生成。
2. **对"可玩性"的定义**：Genie 线证明"世界可以被生成"，但 NPC 依然要靠 LLM agent 扮演——源笔记"环境可生成、角色由 agent 扮演、剧情由两者共同涌现"的分工判断成立，galgame 的核心投资应继续在角色与叙事上。
3. **评测启发（反向）**：Genie 2/3 无量化基准即发布——这是演示驱动研究的极端；本项目验收绝不能学这个，"能跑通一次"不等于"稳定可玩"，回归测试次数就是为此设的。
