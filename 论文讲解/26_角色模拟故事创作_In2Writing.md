# 论文讲解 26：Multi-Agent Based Character Simulation for Story Writing

> 来源：《Generative_Agents_讲解与前沿进展.md》第三节（"Multi-Agent Character Simulation for Story Writing, ACL 2025 workshop"）
> 评分基准同 README

## 🎯 与 GAL 项目的相关度：7 / 10

它主张的故事生成方式——**先让角色 agent 在叙事计划约束下"演"出来，再把演绎产物改写成文**——与本项目"双 Agent 对演 + 旁白 Agent 文学化"的分工是同一件事。篇幅所限（workshop 论文）其实验细节较少，但思想与本项目的阶段 0 原型高度同构。

---

## 一、论文链接

- **ACL Anthology**：<https://aclanthology.org/2025.in2writing-1.9/>（[PDF](https://aclanthology.org/2025.in2writing-1.9.pdf)，DOI: 10.18653/v1/2025.in2writing-1.9，pp.87–108）
- **正式标题**：*Multi-Agent Based Character Simulation for Story Writing*
- **作者**：Tian Yu, Ken Shi, Zixin Zhao, Gerald Penn（多伦多大学）
- **venue 勘误**：源笔记写"ACL 2025 workshop"，实为 **In2Writing 2025**（第四届 Intelligent and Interactive Writing Assistants workshop，**NAACL 2025 同期**，Albuquerque，由 ACL 出版）

## 二、论文本身

### 2.1 要解决的问题

"叙事计划 → 成文"直接生成时，情节自然度差（角色像提线木偶）。论文主张在两者之间插入**角色模拟**环节：故事不该是"写出来的"，而该是"**演出来的**"。

### 2.2 方法：role-play + rewrite 两步

1. **Role-play（角色模拟）**：多个 LLM 角色 agent 在既定 narrative plan 约束下，按时间顺序即兴演绎情节与对白——用角色自主性换取情节自然度，同时由叙事计划保证不跑题；
2. **Rewrite（改写）**：把演绎产物改写成符合计划的连贯成文。

这相当于把"演员排练"和"成书"分成两道工序，各用各的 prompt 优化。

## 三、评价所用的技术

- 论文报告其生成故事**优于另外两种 LLM 故事生成方法**，并将优势归因于角色模拟策略（摘要可确认的部分）；
- **注意**：详细的人评/自动指标与消融数字在 22 页正文中，本次调研未能在线核实（Anthology PDF 未抓取成功）——引用具体数字前请自行核对第 5 节；
- **局限**：workshop 论文、评估规模较小；rewrite 步骤可能抹掉 role-play 阶段涌现的细节（演出来的鲜活感被"规范化"掉）。

## 四、对 GAL 项目的启发

1. **阶段 0 对演原型的学术原型**：修二 Agent × 深雪 Agent 按圣经 §6 预设对演 → 旁白 Agent 整理成文学化第一人称——正是这篇的 role-play + rewrite 两步。可以直接引用它说明该流程有先例。
2. **rewrite 的度**：它点出一个本项目也会遇到的问题——旁白改写台词时**别把口语的毛边修掉**。圣经要求台词短句口语、旁白文学化，两者必须分开生成、只组合不融合，rewrite 只作用于旁白层。
3. **plan 约束下的即兴**：role-play 阶段给角色 agent 的"narrative plan 约束"应该是最小必要信息（本场景目标 + 禁止事项），给多了角色就开始念稿——与文档 23 的 Director-Actor 信息隔离互证。
