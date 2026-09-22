# Generative Agents（Smallville 小镇）讲解 与 生成式社交模拟 / 剧情驱动方向的研究进展

> 整理日期：2026-09-14

---

## 一、Generative Agents（Smallville 小镇）

**论文**：*Generative Agents: Interactive Simulacra of Human Behavior*（Joon Sung Park 等，Stanford + Google，UIST 2023，[arXiv:2304.03442](https://arxiv.org/abs/2304.03442)）

它是第一个大规模证明"LLM 当作人来做社会模拟"可行的工作：25 个 agent 生活在一个《模拟人生》风格的像素小镇里，每个 agent 有人设（名字、职业、性格、记忆起点、社交关系），作者观察它们的日常行为，发现**没有人为编写剧本的情况下涌现出了社会性行为**。

### 核心：单 agent 内部的"认知管线"

Smallville 真正的影响力在于这套架构，此后几乎所有 agent 记忆/规划工作都在它的影响之下：

1. **Memory Stream（记忆流）**：agent 感知到的一切（看到谁、听到什么、自己做了什么）都变成一条条自然语言记录 + 时间戳，追加进一个不断增长的列表。
2. **检索（Retrieval）**：决定"现在该想起什么"，用三个因子打分——
   - **Recency** 近因性：时间越近权重越高（指数衰减）；
   - **Importance** 重要性：让 LLM 给每条记忆打 1–10 分（"吃早餐"=1，"失恋"=9）；
   - **Relevance** 相关性：当前情境与记忆的 embedding 余弦相似度。
3. **Reflection（反思）**：当累积的重要性分数超过阈值时触发——agent 暂停行动，把最近的记忆喂给 LLM 问"这说明了什么？"，生成更高层的洞察（"Klaus 在研究歧视问题" → "Klaus 是个专注的社会学者"），洞察再作为新记忆存回，形成树状抽象。这是"从事件记忆到态度/信念"的关键一步。
4. **Planning（规划）**：先以"天"为单位生成日程，再递归分解到小时、5–15 分钟粒度；环境突变（如听到火警）时重新规划。规划结果让行为表现出长时程连贯性，而不是每一步都随机漂移。
5. **React & 对话**：每次观察后，agent 判断"要不要响应"（继续做事 / 找人搭话），对话历史也写入记忆流，所以八卦会真实地"传开"。

### 两个标志性涌现现象

- **情人节派对**：酒馆老板 Isabella 自发决定办派对 → 逐一邀请朋友 → 装饰场地 → 消息在小镇上口口相传，有人还带了朋友来（谁没被邀请、谁最后来了都符合社交逻辑）。
- **市长竞选八卦**：候选人 Sam 挨个拉票，他支持竞选的信息通过 Klaus 中转给了另一个 agent John——经典的**信息级联**（后来作者团队的 zombie demo 则展示了谣言/恐慌的传播）。

### 评测与代价

- 用"采访式"人评 believability（可信度）：真实的行为轨迹 vs 消融版本，人类判断哪份采访更像人。
- 消融结论：去掉 **planning** 掉分最狠，其次是 **reflection**；只留记忆流不反思也不行——说明三件套缺一不可。
- 成本：2023 年用 gpt-3.5 跑 25 个 agent × 2 天 ≈ **1000+ 美元**，这也是后来所有工作都要面对的规模化瓶颈。代码开源在 [joonspk-research/generative_agents](https://github.com/joonspk-research/generative_agents)，社区复刻版有 a16z 的 AI Town 等。

---

## 二、后续知名论文：生成式社交模拟

这条线大致沿"**更大规模 → 更高保真 → 更长时程 → 更像科学工具**"四个方向推进：

| 工作 | 规模/特点 | 关键贡献 |
|---|---|---|
| **S³**（2023.10） | 10 万级 Twitter agent | 首个把 LLM agent 模拟做到社会网络尺度的系统 |
| **Concordia**（DeepMind，[arXiv:2312.03664](https://arxiv.org/abs/2312.03664)） | 框架/库 | 用"GameMaster"统一管环境与社会交互，主打**可复现的社会科学实验**，已发布 [v2.0](https://github.com/google-deepmind/concordia) |
| **OASIS**（Cornell，2024） | **百万级** agent 社交媒体 | 复现信息传播、群体极化、羊群效应等真实社会现象，用于虚假信息研究（[OpenReview](https://openreview.net/forum?id=P2BRs9uFwX)） |
| **AgentTorch**（2024） | 百万级、**可微分** | ABM 与反向传播结合，可做政策优化的"社会数字孪生" |
| **Generative Agent Simulations of 1,000 People**（Park 等，2024，[arXiv:2411.10109](https://arxiv.org/abs/2411.10109)） | **真人数字分身** | 用 GPT-4o 对 1052 个真人做 2 小时语音访谈再建 agent；在 GSS/大五人格等测试上复现了本人约 **85%** 的准确度（≈本人两周后重测自己答案的水平），代码开源（[genagents](https://github.com/joonspk-research/genagents)） |
| **Project Sid**（Altera，[arXiv:2411.00114](https://arxiv.org/abs/2411.00114)） | Minecraft 里 **1000+ agent** | 提出 PIANO 架构（并发的多模块"大脑"），首次观察到 agent 群体涌现出经济、文化、宗教、治理等**文明级**现象 |
| **AgentSociety**（清华 FIB Lab，2025，[arXiv:2502.08691](https://arxiv.org/html/2502.08691v1)） | 万级 agent + 社会环境模拟器 | 情绪–态度–行为三层驱动，做了疫情封控等真实场景复现，并开放为研究平台（[GitHub](https://github.com/tsinghua-fib-lab/AgentSociety/)） |
| **EconAgent / Agent Hospital**（2024） | 经济学 / 医疗 | LLM agent 模拟通胀预期下的经济决策；模拟医院里医生 agent 通过积累病例自我进化 |
| **综述** | — | *A Survey on Social Simulation Driven by LLMs*（ACM 2025，[链接](https://dl.acm.org/doi/10.1145/3800683)）、Xi 等 2023 年的 generative agents 综述是早期必读 |

其中 **"1000 People"** 和 **Project Sid** 是公认的两个分水岭：前者回答"agent 能不能像*某个具体的人*"，后者回答"agent 群体能不能像*一个社会*"。

---

## 三、剧情驱动 / 互动叙事方向

这条线关心的问题不同：**既要角色自由，又要故事好看**——本质是"作者意图 vs agent 自主性"的张力。

- **前置经典**：Dramatron（Google，2022，LLM 协作写剧本）、Re3/DOC（长篇故事生成）、AI Dungeon（产品化先例）。
- **Murder Mystery / 狼人杀类多 agent 社交推理**（2023–2024）：把隐藏信息、欺骗、说服作为研究社交 agent 的"实验台"，衍生出 SOTOPIA（社交智能评测基准）及后续 SOTOPIA-π 训练工作。
- **LARP**（2024）：面向开放世界游戏的角色扮演认知架构（目标驱动的行为树 + 记忆）。
- **NPC 记忆与规模化**：MemGPT、A-Mem（[OpenReview 2024](https://openreview.net/forum?id=FiM0M8gcct)）等做"无限记忆流"的工程化改进，直接针对 Smallville 的记忆瓶颈；微软 2024 年的工作把 Smallville 架构移植到 3A 游戏场景（数百 NPC、毫秒级预算）。
- **互动戏剧 2025 年的代表**：
  - *Towards Enhanced Immersion and Agency for LLM-based Interactive Drama*（[arXiv:2502.17878](https://arxiv.org/html/2502.17878v2)）——优化"剧情导演 + 角色 agent"双层架构，平衡玩家沉浸感与自由度；
  - **SENNA**——多 agent"引导而非铁轨"（guiding, not railroading）的叙事维持系统；
  - *Agents' Room*（ICLR 2025，[OpenReview](https://openreview.net/forum?id=HfWcFs7XLR)）——多步协作生成长篇叙事；
  - *Multi-Agent Character Simulation for Story Writing*（ACL 2025 workshop）——先有叙事大纲、再让角色 agent"活"出来；
  - EMNLP 2025 demo：开源的 LLM 互动戏剧工具包。
- **相邻但正在汇流的"世界模型"线**：Genie（2024）→ Genie 2（2024.12）→ Genie 3（2025，实时可交互世界生成）、GameNGen、Decart 的 Oasis——用生成模型直接生成"可玩环境"。它与 LLM agent 线的交汇点是：**环境本身可生成，角色由 LLM agent 扮演，剧情由两者共同涌现**。

---

## 四、目前（2025–2026）的研究前沿小结

1. **规模化已成共识，瓶颈从"能不能"变成"贵不贵、像不像"**：百万 agent（OASIS）靠的是蒸馏小模型 + 缓存；前沿问题是同质化（LLM 人口比真实人口更"平均"，会系统性抹平少数群体差异）。
2. **保真度方向转向"真人校准"**：1000 People 之后，主流做法是用访谈/问卷/行为数据把 agent 锚定到真实个体或人口分布上（AgentSociety 的疫情研究、各类选举/民意模拟），目标是把 LLM-ABM 变成社会科学的正式工具——随之而来的是**模拟真人的伦理问题**（知情同意、隐私）被反复讨论。
3. **长时程自治靠"并发认知架构"**：Smallville 的串行管线跑不动数月时间尺度，Project Sid 的 PIANO 用多模块并发 + 优先级仲裁，成为新一代 agent 架构模板（对照人脑的 System 1/System 2）。
4. **剧情驱动的核心问题被形式化为"导演–角色"分工**：用导演 agent 管节奏、伏笔、张力曲线，用自由 agent 保证可信反应；评测也开始用"叙事连贯性 × 角色一致性 × 玩家能动性"多维指标。
5. **尚未解决的开放问题**：可信的自动化评测（人评太贵、没有 ground truth）、模拟结果的统计效度（跑几次才算数）、多 agent 的串谋/越狱风险、以及成本——目前最贵的工作仍然是"一次模拟一辆车"的量级。

### 选型建议（针对 GAL 项目）

- 做**社会模拟**：参考 Concordia（实验严谨）和 AgentSociety（规模 + 平台化）；
- 做**剧情/互动体验**：重点看 arXiv:2502.17878 的导演架构 + Smallville 的记忆流实现，两者可以直接拼装。

---

## Sources

- [Generative Agents (arXiv:2304.03442)](https://arxiv.org/abs/2304.03442) / [代码](https://github.com/joonspk-research/generative_agents)
- [LLM Agents Grounded in Self-Reports Enable General-Purpose Simulation of Individuals (arXiv:2411.10109)](https://arxiv.org/abs/2411.10109) / [代码](https://github.com/joonspk-research/genagents) / [Stanford HAI 报道](https://hai.stanford.edu/news/ai-agents-simulate-1052-individuals-personalities-with-impressive-accuracy)
- [Project Sid (arXiv:2411.00114)](https://arxiv.org/abs/2411.00114)
- [AgentSociety (arXiv:2502.08691)](https://arxiv.org/html/2502.08691v1) / [GitHub](https://github.com/tsinghua-fib-lab/AgentSociety/)
- [OASIS (OpenReview)](https://openreview.net/forum?id=P2BRs9uFwX)
- [Concordia (GitHub)](https://github.com/google-deepmind/concordia) / [论文 arXiv:2312.03664](https://arxiv.org/abs/2312.03664)
- [A Survey on Social Simulation Driven by LLMs (ACM 2025)](https://dl.acm.org/doi/10.1145/3800683)
- [Towards Enhanced Immersion and Agency for LLM-based Interactive Drama (arXiv:2502.17878)](https://arxiv.org/html/2502.17878v2)
- [Agents' Room (OpenReview)](https://openreview.net/forum?id=HfWcFs7XLR)
- [A-Mem (OpenReview)](https://openreview.net/forum?id=FiM0M8gcct)
- [LLM Game Agents 综述 (arXiv:2404.02039)](https://arxiv.org/html/2404.02039v5) / [awesome-LLM-game-agent-papers](https://github.com/git-disl/awesome-LLM-game-agent-papers)
