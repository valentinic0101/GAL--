# -*- coding: utf-8 -*-
"""游戏运行时引擎。原先是单文件 server/engine.py（769 行），按职责拆成包：

    from engine import Engine, SAVE_DIR

  config.py   阶段提示 / BGM 映射 / 场景转场 / 在场演员 / 幕间候选词（纯数据）
  storage.py  存档目录、事件日志与落盘原语
  core.py     class Engine：帧构造·场景推进·幕间自由行动·导演调度·Agent 应答

对外接口与拆分前完全一致：Engine / SAVE_DIR / LOG_PATH / log，以及六张配置表。

下面的兼容再导出：拆分前 engine.py 顶部 import 过这些名字，于是它们都是该模块的模块级属性，
`import engine as engine_mod; engine_mod.LLM` 这类写法（回归脚本里有）才成立。
拆包后这些 import 落在了 core.py，所以要在这里再导出一遍，旧写法才不会断。
"""
from .config import (STAGE_NOTES, SCENE_BGM, LOC_BGM, TRANSITIONS,           # noqa: F401
                     SCENE_CAST, INTERLUDE_CHIPS)
from .storage import SAVE_DIR, LOG_PATH, log                                  # noqa: F401
from .core import Engine                                                      # noqa: F401

# ---- 兼容再导出（拆分前 engine.py 的模块级可达名）----
from .core import (World, LOCATIONS, CHAR_NAME, Director, PHASE_ORDER,        # noqa: F401
                   ENDINGS, ENDINGS_TITLE, ENDING_SUBTITLE, eval_cond,
                   axis_score, gossip, rule_engine, LLM, assemble_prompt,
                   PERSONAS, persona_card, guardrails, canon_mod,
                   memory_mod, guide_mod, settings, SCENES)

__all__ = ['Engine', 'SAVE_DIR', 'LOG_PATH', 'log',
           'STAGE_NOTES', 'SCENE_BGM', 'LOC_BGM', 'TRANSITIONS',
           'SCENE_CAST', 'INTERLUDE_CHIPS',
           # 兼容再导出
           'World', 'LOCATIONS', 'CHAR_NAME', 'Director', 'PHASE_ORDER',
           'ENDINGS', 'ENDINGS_TITLE', 'ENDING_SUBTITLE', 'eval_cond',
           'axis_score', 'gossip', 'rule_engine', 'LLM', 'assemble_prompt',
           'PERSONAS', 'persona_card', 'guardrails', 'canon_mod',
           'memory_mod', 'guide_mod', 'settings', 'SCENES']
