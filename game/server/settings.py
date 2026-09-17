# -*- coding: utf-8 -*-
"""运行时功能开关：论文补充批次（C1~C8，见《修改意见与开发文档/》）逐项可独立关闭与回滚。

全部默认开启；回归排障时可单独关闭某一机制以定位问题。
"""
import os

# C3: 阶段硬护栏（P1/P2 禁身份宣言、P1~P5 禁名字泄漏）；False 回退为无阶段检查
STAGE_GUARD = os.environ.get('GAL_STAGE_GUARD', '1') == '1'
# C4: 正典台词 few-shot 注入
CANON_INJECT = os.environ.get('GAL_CANON_INJECT', '1') == '1'
# C4: 护栏反馈式重试（把违规原因喂回模型）
FEEDBACK_RETRY = os.environ.get('GAL_FEEDBACK_RETRY', '1') == '1'
# C1: 记忆流与三因子检索（False 时 agent 记忆回落为知识库切片旧行为）
MEMORY_ON = os.environ.get('GAL_MEMORY', '1') == '1'
# C1: 记忆重要度用 LLM 打分（默认规则打分：省调用、确定性）
IMPORTANCE_LLM = os.environ.get('GAL_IMPORTANCE_LLM', '0') == '1'
# C2: 反思与信念沉淀
REFLECT_ON = os.environ.get('GAL_REFLECT', '1') == '1'
# C7: 导演 diegetic 引导策略菜单（False 回落旧 _interlude_hint 固定文案）
GUIDE_V2 = os.environ.get('GAL_GUIDE_V2', '1') == '1'
# C8: 传闻强度衰减与回流
RUMOR_STRENGTH = os.environ.get('GAL_RUMOR_STRENGTH', '1') == '1'
