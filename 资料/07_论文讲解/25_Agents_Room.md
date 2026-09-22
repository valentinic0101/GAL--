# 论文讲解 25：Agents' Room——多步协作生成长篇叙事

> 来源：《Generative_Agents_讲解与前沿进展.md》第三节（Agents' Room, ICLR 2025）
> 评分基准同 README

## 🎯 与 GAL 项目的相关度：6.5 / 10

不是交互系统而是**离线长篇生成**方法，但它验证了两个对本项目有意义的结论：① 把"冲突/角色/设定/情节"作为**独立规划产物**分开产出，比端到端直写好——人物圣经恰好就是这四样东西；② plan-only（只给计划不给专业写手）反而更差——**写作 agent 本身的专门化不可省**，对应到本项目即"台词必须由角色 agent 写，不能由导演层代笔"。

---

## 一、论文链接

- **OpenReview**：<https://openreview.net/forum?id=HfWcFs7XLR>（ICLR 2025 poster）
- **arXiv**：<https://arxiv.org/abs/2410.02603>
- **作者**：Fantine Huot, Reinald Kim Amplayo, Jennimaria Palomaki, Alice Shoshana Jakobovits, Elizabeth Clark, Mirella Lapata（Google DeepMind + 爱丁堡大学）
- **代码/数据集**：<https://github.com/google-deepmind/tell_me_a_story>（含 Tell Me A Story 数据集）

## 二、论文本身

### 2.1 要解决的问题

单 prompt 直出长故事质量差。受叙事理论（写作 = 多种认知过程的分工）启发，把写作拆成子任务交给**专门化的 agent 协作**完成。

### 2.2 方法

- **规划 agents**（只出要素不写正文）：分别产出 **CONFLICT**（冲突）、**CHARACTER**（角色）、**SETTING**（设定）、**PLOT**（情节）四类规划要素；
- **写作 agents**：按弗赖塔格五幕结构（EXPOSITION → RISING ACTION → CLIMAX → FALLING ACTION → RESOLUTION）各写一段；
- 共享 **scratchpad** 记忆，中央编排器确定性调度；底座 Gemini 1.5 Flash；
- **蒸馏微调**：用 Gemini Ultra 当教师，从人写故事**反推**规划要素、切分叙事段落构成合成训练数据，对每个 agent 做 LoRA 微调；
- 四种变体：ZS/FT × plan-only/plan+write。

## 三、评价所用的技术

- **专家人评**（作家及文学学位持有者）做**两两偏好比较**，五维：情节、创造力、人物发展、语言、整体；
- **关键结果**：人写故事全维最高（仍未被超越）；**AR(FT, plan+write) 全五维显著优于所有端到端单 prompt 基线**；**plan-only 变体反而不如简单基线**（专业写作 agent 不可缺）；FT 稳定优于 ZS；
- **生成统计**：AR 故事约 3000–3200 词 / 56–63 段，显著长于人写（1439 词/33 段）与基线（965–1207 词）——多 agent 倾向写长，需控制；
- 附带 LLM 评测器（后续工作沿用的自动评价）；
- **局限**：未及人写水平、输出偏长、依赖 Gemini 系模型与大规模蒸馏数据。

## 四、对 GAL 项目的启发

1. **四要素规划 = 人物圣经的学术镜像**：CONFLICT/CHARACTER/SETTING/PLOT 正好对应圣经的谜团冲突、人物卡、舞台设定、时间线 P0~P10——本项目的内容层已完成"规划 agents"的工作，剩下的是接一个"写作 agents"层。
2. **plan-only 反例的警示**：导演层如果直接根据大纲生成台词（跳过角色 agent 的"表演"），质量会低于让角色 agent 基于大纲即兴——这从反面支持"双层架构"里角色层的必要性。
3. **反推式蒸馏数据**：从正典文本反推结构化标注（哪段是起承转合、人物状态如何变化）来做微调数据——给素材文本的利用提供了一个可操作方向（比直接 SFT 更省标注）。
4. **长度控制**：多 agent 协作会越写越长；galgame 台词有句长上限，护栏层的句长校验在这里同样必要。
