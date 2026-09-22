# 论文讲解 13：Dramatron——与 LLM 协作写剧本

> 来源：《Generative_Agents_讲解与前沿进展.md》第三节"前置经典"
> 评分基准同 README

## 🎯 与 GAL 项目的相关度：7.5 / 10

它的**层级提示链**（logline → 角色 → 逐场 beat → 场景 → 台词）正是把"P0~P10 主线"翻译成具体场景与台词的管线先例；它的人评也揭示了互动叙事产品的重要教训——**AI 代笔会让使用者丧失"所有权感"**（仅 46% 的合作者对作品自豪），这对"玩家生成内容 vs 作者叙事"的平衡是直接警示。

---

## 一、论文链接

- **arXiv**：<https://arxiv.org/abs/2209.14958>（⚠️ 源笔记的 2209.14974 有误；社区流传的标题 "Semi-Structured Hierarchical Story Generation" 未获权威索引证实，正式标题如下）
- **正式发表**：*Co-Writing Screenplays and Theatre Scripts with Language Models: An Evaluation by Industry Professionals*，**ACM CHI 2023**（DOI: 10.1145/3544548.3581225）；早期版本为 NeurIPS 2022 ML for Creativity workshop 论文
- **作者**：Piotr Mirowski, Kory W. Mathewson, Jaylen Pittman, Richard Evans（Google DeepMind）
- **代码**：<https://github.com/google-deepmind/dramatron>

## 二、论文本身

### 2.1 要解决的问题

LLM 直出长剧本会结构散架。Dramatron 把剧本创作形式化为**层级化的半结构生成**，让"结构先验"由 prompt 链承载，人在任意层级介入编辑。

### 2.2 方法：五级提示链

从用户给的 logline 出发，依次生成（上一级输出拼入下一级 prompt）：

1. 标题 → 2. **角色描述** → 3. **逐场情节 beat**（每个 beat 标注地点与叙事弧位置：Exposition / Rising Action…）→ 4. **地点描述** → 5. **带说话人标签的场景对白**。

工程细节：每级 1–4 个 few-shot 范例、prompt 控制在 2k token 内、nucleus sampling（p=0.9, t=1.0）、对白级有重复检测+重采样防循环；底座 Chinchilla 70B（方法与模型无关）。本质是纯 prompt 工程的人机共创工具。

## 三、评价所用的技术

两部分：

1. **行业专家共创研究**：15 位戏剧/影视专业人士（剧作家、编剧、导演、即兴演员）参加约 2 小时共创会，9 题 Likert 问卷 + 开放式访谈：
   - 84% 认为有帮助、77% 享受共创、92% 对输出感到惊讶、**仅 46% 对作品有自豪感**（所有权感低）。
2. **文本量化**：Levenshtein 距离、lemma-Jaccard 相似度、重复度等对比生成与人写文本。
3. **公演检验**：5 部合写剧本在 2022 Edmonton Fringe Theatre Festival 公演。
4. **定性批评**：性别偏见与刻板印象、对白缺乏潜台词、偏套路化、更适合 world-building。

## 四、对 GAL 项目的启发

1. **beat 层 = 剧情吸引子的展开层**：P5（刻身高）是 logline 级；Dramatron 提示先展开成"场次 beat（含地点与弧线位置）"，再生成场景与台词。导演层可以把每个 P 事件预先做成 beat 模板，运行时只填玩家相关的变量。
2. **人物一致性靠角色卡先行**：先生成全部角色描述再写台词（而不是边写边加角色）——与人物圣经"先圣经后台词"的流程一致，学术先例在手。
3. **所有权感问题**：如果未来做"玩家共创剧情"功能，46% 的自豪感数据提示：AI 代笔太多会削弱玩家的叙事参与感——galgame 里旁白是修二第一人称，恰好把"声音的所有权"留给了角色而非 AI。
4. **它不适合直接生成台词**：专家批评对白直白无潜台词——印证架构 V1"台词必须由被硬约束的角色 agent 生成 + 正典检索锚点"的设计，不能指望通用故事模型。
