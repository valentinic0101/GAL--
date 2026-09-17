# 论文讲解 15：DOC——用详细大纲控制长故事连贯性

> 来源：《Generative_Agents_讲解与前沿进展.md》第三节"前置经典"（Re3/DOC）
> 评分基准同 README

## 🎯 与 GAL 项目的相关度：6 / 10

它是"**自由过程 + 既定骨架**"这个故事版：大纲=剧情时间线 P0~P10，正文生成=玩家面前的场景。它把"创作负担从起草前移到规划"的主张，与架构 V1"自由度 100% 在过程、骨架仍是既定时间线"是同一句话。技术上的重管线（logit 级干预）不必照搬，但"三层大纲 + 生成时贴合控制"的结构值得导演层参考。

---

## 一、论文链接

- **arXiv**：<https://arxiv.org/abs/2212.10077>（⚠️ 源笔记的 2301.12697 有误）
- **正式发表**：ACL 2023 长文（<https://aclanthology.org/2023.acl-long.190/>）
- **作者**：Kevin Yang, Dan Klein, Nanyun Peng, Yuandong Tian
- **代码**：<https://github.com/yangkevin2/doc-story-generation>（官方 v2 已扩展到 LLaMA-2/ChatGPT）

## 二、论文本身

### 2.1 要解决的问题

Re3 的顶层 outline 太粗，长篇仍会跑偏。DOC 主张：把创作负担**从起草阶段前移到规划阶段**——大纲足够细，起草只是"照着填"。

### 2.2 方法：outliner + controller 两件套

- **Detailed Outliner**：用 InstructGPT 生成**深度 3 层**的层级大纲，每一层都带 character/plan/event 摘要（对比 Re3 只有顶层 outline）。
- **Detailed Controller**：正文生成时保证段落贴合大纲，三种机制——
  1. 大纲顺序控制器（RoBERTa-large）；
  2. 相关性/连贯性重排序器（Longformer-base-4096，继承 Re3）；
  3. **FUDGE 式 token 级引导**：OPT-350m 对每步 logits 加权，引导模型按当前大纲条目续写——因为要改 logits，主实验底座用 OPT-175B（Alpa 部署）。
- 保留 recursive reprompting 与"机械性情节错误（角色/指代错误、场景跳变）检测-重写"模块。

## 三、评价所用的技术

- **人评**（与 Re3 同协议；公平基线=把 DOC 的大纲喂给 OPT-175B 跑 Re3）：
  - plot coherence **+22.5%**、outline relevance **+28.2%**、interestingness **+20.7%**（绝对提升）；
  - 摘要称 incoherence 相对基线最多降低 **51%**；
  - 交互式设置中人类认为 DOC 显著更可控。
- **消融**：三个控制器各自的贡献（如关掉 editor）、不同大纲深度。
- **局限**：管线极重（3 层大纲 + 3 个外挂小模型 + 175B 底座 + logit 干预）；"机械"错误检测覆盖不了语义级不连贯。

## 四、对 GAL 项目的启发

1. **大纲深度分层**：P0~P10 → 每个事件的 beat → 每个场景的目标/障碍/结果，三层层级可直接映射。导演层判断"当前进度"时查的就是大纲层，不是自由文本。
2. **"生成时引导" vs "生成后校验"**：FUDGE 的 logit 干预是护栏的另一种思路（事前引导），但工程重、锁死底座模型。架构 V1 选的"生成后校验+重试"更适配"一个模型演所有角色 + 可随时换 API 模型"的现实约束——这个选型有依据，不必羡慕 logit 级方案。
3. **可控性本身是卖点**：人评里"更可控"是独立维度——galgame 的导演层评测也应单列"可控性/引导有效性"指标（玩家跑题后多少回合被拉回主线）。
