# 论文讲解合集 README

> 生成日期：2026-09-15
> 来源：《Generative_Agents_讲解与前沿进展.md》中提及的全部论文，逐篇展开讲解。
> 每篇文档包含：**相关度评分 → 论文链接 → 论文本身 → 评价所用的技术 → 对 GAL 项目的启发**。

## 评分基准

所有相关度分数以**本项目**为参照系：一款 **LLM 驱动的开放世界 GALGAME**（雪国小镇，修二/深雪等多角色 Agent，记忆流 + 八卦传播 + 导演层剧情引力 P0~P10 + 护栏校验器，玩家扮演修二，对成本敏感）。因此：

- 记忆工程、角色扮演、互动叙事、社交对话评测 → 高分；
- 大规模社会科学模拟、经济学/医疗等专业领域模拟 → 低分（方法论可借鉴但场景遥远）；
- 生成式世界模型（Genie/GameNGen 等） → 低到中分（属演出层的远期方向）。

## 阅读顺序建议

| 梯队 | 文档 | 为什么 |
|---|---|---|
| **① 必读** | 23 互动戏剧沉浸与能动性、01 Generative Agents、24 SENNA、27 Open-Theatre、17 SOTOPIA | 与架构 V1 的"导演层 + Agent 层 + 护栏层"逐层对应，评测框架可直接搬 |
| **② 架构参照** | 20 MemGPT、21 A-Mem、19 LARP、07 Project Sid、03 Concordia、18 SOTOPIA-π、22 3A NPC 考证 | 记忆分层、并发认知、GM 思想、社交技能蒸馏 |
| **③ 故事生成参照** | 13 Dramatron、14 Re3、15 DOC、25 Agents' Room、26 角色模拟写故事、16 狼人杀/谋杀之谜 | "大纲→骨架→局部生成"与对演生成的先例 |
| **④ 评测方法参照** | 06 1000 人数字分身、11 TIST 综述、12 Xi 综述、31 游戏 Agent 综述 | "角色一致性是测出来的"——评测协议素材库 |
| **⑤ 远期/低相关** | 02 S³、08 AgentSociety、04 OASIS、05 AgentTorch、09 EconAgent、10 Agent Hospital、28 Genie、29 GameNGen、30 Decart Oasis | 扩展视野：降本手段、传播模拟、世界模型 |

## 总览表（按相关度排序）

| # | 论文 | 方向 | 相关度 | 一句话定位 |
|---|---|---|---|---|
| 23 | Towards Enhanced Immersion and Agency for LLM-based Interactive Drama (ACL 2025) | 互动戏剧 | **9.5** | 导演层+角色层双架构的直接先例，评测协议可直接搬 |
| 01 | Generative Agents / Smallville (UIST 2023) | 社会模拟 | **9.5** | 记忆流+反思+规划+八卦传播的源头，架构 V1 的母本 |
| 24 | SENNA: Guiding, Not Railroading (IUI 2026) | 互动叙事 | **9.0** | "剧情引导而非铁轨"的人因实证，导演层策略菜单 |
| 27 | Open-Theatre (EMNLP 2025 Demo) | 互动戏剧 | **8.5** | 开源互动戏剧工具包，角色 Agent+导演+记忆可拆来用 |
| 17 | SOTOPIA (ICLR 2024 Spotlight) | 社交评测 | **8.5** | 恋爱/社交对话评测框架：目标达成×关系积累×秘密保护 |
| 20 | MemGPT (2023) | 记忆工程 | **7.5** | OS 式记忆分页，深雪记忆库的工程参照 |
| 13 | Dramatron (CHI 2023) | 剧本生成 | **7.5** | 层级剧本生成（logline→角色→beat→台词）= P0~P10 生成管线参照 |
| 07 | Project Sid (2024) | 群体模拟 | **7.0** | PIANO 并发认知架构，长时程自治的新一代模板 |
| 26 | Multi-Agent Character Simulation for Story Writing (In2Writing 2025) | 故事生成 | **7.0** | "先对演、再改写成文"＝旁白 Agent 思路的学术版 |
| 18 | SOTOPIA-π (ACL 2024) | 社交训练 | **7.0** | 把社交技能蒸馏进 7B 小模型＝深雪 LoRA 路线参照 |
| 19 | LARP (2023, 字节) | 角色扮演 | **7.0** | 开放世界角色认知架构 + "记忆曲解"模拟 |
| 21 | A-Mem (NeurIPS 2025) | 记忆工程 | **7.0** | 记忆随交互持续演化重组，长期陪伴关系记忆 |
| 16 | Werewolf / PLAYER* 社交推理 (2023–2024) | 社交推理 | **6.5** | 隐藏信息、欺骗、说服的实验台＝谜团锁测试场 |
| 06 | Generative Agent Simulations of 1,000 People (2024) | 个体模拟 | **6.5** | 访谈式 grounding＝"人物圣经→人设卡"的方法论升级 |
| 25 | Agents' Room (ICLR 2025) | 故事生成 | **6.5** | 冲突/角色/设定/情节分 agent 规划＋分幕写作 |
| 14 | Re3 (EMNLP 2022) | 长故事生成 | **6.0** | recursive reprompting＝每次现场拼装 prompt 的思想源头 |
| 15 | DOC (ACL 2023) | 长故事生成 | **6.0** | 大纲控制＝"自由过程 + 既定骨架"的故事版 |
| 31 | LLM Game Agents 综述 (CSUR 2026) | 综述 | **6.0** | 游戏 agent 能力地图与评测载体整理 |
| 03 | Concordia (DeepMind 2023) | 模拟框架 | **5.5** | GameMaster＝导演层+世界层合体的开源参照实现 |
| 11 | LLM 社会模拟综述 (ACM TIST 2025) | 综述 | **5.0** | 评测方法专章（微宏观对齐/问卷/干预实验） |
| 02 | S³ (2023) | 社会模拟 | **4.0** | 万级传播模拟 + 性格过滤器思想，规模对 galgame 过剩 |
| 08 | AgentSociety (2025) | 社会模拟 | **4.5** | 情绪-认知-社会三层驱动 + 社会环境模拟器 |
| 12 | Xi 等 LLM Agents 综述 (2023) | 综述 | **4.0** | profile/memory/planning/action 分类学，入门地图 |
| 28 | Genie 1/2/3 世界模型 (2024–2025) | 世界模型 | **3.5** | 实时可玩世界生成，演出层远期方向 |
| 04 | OASIS (2024) | 社会模拟 | **2.0** | 百万级 agent 的降本工程（蒸馏+缓存）值得偷师 |
| 10 | Agent Hospital (2024) | 领域模拟 | **2.5** | "病例库积累→自我进化"＝正典语料回归测试的变体 |
| 30 | Decart Oasis (2024) | 世界模型 | **2.0** | 20fps 全生成 Minecraft，演示意义大于实用 |
| 09 | EconAgent (ACL 2024) | 领域模拟 | **2.0** | 感知/记忆/决策三件套的经济学应用 |
| 05 | AgentTorch (2024) | 群体模拟 | **1.5** | 可微分 ABM，与叙事游戏几乎无关 |
| 29 | GameNGen (ICLR 2025) | 世界模型 | **1.5** | 神经游戏引擎复现 DOOM，方向性参考 |

## 重要勘误（相对源笔记）

调研中经 arXiv / Semantic Scholar / ACL Anthology / 官方仓库逐一核实，发现源笔记存在以下错误，已在对应文档中更正：

| 源笔记说法 | 核实结果 |
|---|---|
| S³ 为 2023.10、10 万级 agent | 实为 arXiv:2307.14984（2023-07），规模约 **1 万**级 |
| OASIS 出自 Cornell | 实为**上海 AI 实验室牵头的 CAMEL-AI 社区**（40 余位作者，含大连理工、Oxford、KAUST 等），arXiv:2411.11581 |
| AgentTorch 论文 | 正式论文标题 *On the Limits of Agency in Agent-Based Models*（arXiv:2409.10568），"AgentTorch"是框架名 |
| EconAgent arXiv:2310.10451 | 正确 ID 为 **arXiv:2310.10436**，ACL 2024 主会（2310.10451 是无关论文） |
| Dramatron arXiv:2209.14974、标题 "Semi-Structured Hierarchical Story Generation" | 正确 ID 为 **arXiv:2209.14958**，正式标题 *Co-Writing Screenplays and Theatre Scripts with Language Models: An Evaluation by Industry Professionals*（**CHI 2023**） |
| DOC arXiv:2301.12697 | 正确 ID 为 **arXiv:2212.10077**（ACL 2023 长文） |
| SOTOPIA-π arXiv:2401.03687 | 正确 ID 为 **arXiv:2403.08715**（ACL 2024；2401.03687 是语音论文） |
| LARP arXiv:2312.01400 | 正确 ID 为 **arXiv:2312.17653** |
| 微软 2024 年把 Smallville 移植到 3A 游戏（数百 NPC、毫秒级预算） | **未找到对应公开论文**，疑为行业报道混合记忆；最接近的可核实工作见文档 22 的考证 |
| Decart Oasis arXiv:2410.18976 | Oasis **没有 arXiv 论文**，正式引用为项目页 oasis-model.github.io（2410.18976 实为 CAMEL-Bench） |
| "ACL 2025 workshop" 角色模拟论文 | 实为 **In2Writing 2025 workshop**（NAACL 2025 同期，多伦多大学） |
| SENNA | 正式标题 *Guiding, Not Railroading: … Narrative Redirection in Role-playing Games*，**ACM IUI**（无 arXiv，DOI: 10.1145/3742413.3789218） |

各文档中引用的具体数字以调研时核实的为准；个别标注"待核实/二手来源"的数字建议引用前翻原文 PDF 确认。
