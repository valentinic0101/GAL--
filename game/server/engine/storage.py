# -*- coding: utf-8 -*-
"""存档目录、事件日志与落盘原语。

引擎只负责把「这一局要存什么」整理成 dict；路径、文件格式、事件溯源追加这些细节都在这里。
存档位于 game/saves/：<slot>.json 为状态快照，events_<slot>.jsonl 为只追加的事件溯源流水。

GAL_SAVE_DIR 可覆盖存档目录（起临时实例做验证时指向临时目录，就不必担心碰到正在玩的那一局）。
"""
import json
import os
import time

SAVE_DIR = os.environ.get('GAL_SAVE_DIR') or os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'saves')
os.makedirs(SAVE_DIR, exist_ok=True)
LOG_PATH = os.path.join(os.path.dirname(SAVE_DIR.rstrip(os.sep)), 'logs', 'engine.log')


def log(msg):
    """引擎事件日志（LLM 异常/护栏拦截/引导策略），排障不再靠盲测。"""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write('%s %s\n' % (time.strftime('%m-%d %H:%M:%S'), msg))
    except OSError:
        pass


def snapshot_path(slot='auto'):
    return os.path.join(SAVE_DIR, '%s.json' % slot)


def events_path(slot='auto'):
    return os.path.join(SAVE_DIR, 'events_%s.jsonl' % slot)


def write_snapshot(slot, data):
    """写入状态快照，返回落盘路径。"""
    path = snapshot_path(slot)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    return path


def read_snapshot(slot):
    """读取状态快照；槽位不存在时抛 FileNotFoundError（调用方按 404 处理）。"""
    path = snapshot_path(slot)
    if not os.path.exists(path):
        raise FileNotFoundError(slot)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def append_events(slot, events):
    """把（已序列化的）事件追加进溯源流水。只追加，从不回读。"""
    if not events:
        return
    with open(events_path(slot), 'a', encoding='utf-8') as f:
        for ev in events:
            f.write(json.dumps(ev.to_dict(), ensure_ascii=False) + '\n')
