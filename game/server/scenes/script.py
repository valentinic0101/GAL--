# -*- coding: utf-8 -*-
"""场景脚本数据的对外入口：把主干与分支两个分片汇总成同一个 SCENES 注册表。

    from scenes.script import SCENES

分片：
  trunk.py     P1~P10 主干 + 终章 P0
  branches.py  P11 / P12M / P12B / E_STAY / E_SPRING / E_FAR / E_TOKYO

分片只是文件切分，SCENES 全项目仍是同一个字典，节点 id 全局唯一。
"""
from .trunk import SCENES                                  # noqa: F401
from . import branches                                     # noqa: F401  导入即注册分支节点

__all__ = ['SCENES']
