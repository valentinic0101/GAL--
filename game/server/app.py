# -*- coding: utf-8 -*-
"""FastAPI 服务：静态托管前端 + 游戏 REST API。"""
import os
import json
import time
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import Engine, SAVE_DIR
from world.world import LOCATIONS, CHAR_NAME
from scenes.script import SCENES
from agents.personas import PERSONAS
from agents.llm import LLM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title='雪国之恋 · 开放世界 GAL 引擎')
engine = Engine()

# 访问日志：玩家每一步操作在服务器侧可查（logs/access.log）
ACCESS_LOG = os.path.join(ROOT, 'logs', 'access.log')


@app.middleware('http')
async def access_log(request: Request, call_next):
    t0 = time.time()
    resp = await call_next(request)
    try:
        with open(ACCESS_LOG, 'a', encoding='utf-8') as f:
            f.write('%s %s %s -> %s (%.0fms)\n' % (
                time.strftime('%H:%M:%S'), request.method, request.url.path,
                resp.status_code, (time.time() - t0) * 1000))
    except OSError:
        pass
    return resp


class InputBody(BaseModel):
    text: Optional[str] = None
    choice_index: Optional[int] = None


class ActBody(BaseModel):
    action: str            # move / talk / wait / enter_scene
    to: Optional[str] = None
    text: Optional[str] = None


# ---------------------------------------------------------------- API
@app.get('/api/state')
def state():
    w = engine.world
    return engine.last_frame or {
        'kind': 'title', 'text': '', 'meta': {
            'phase': w.phase, 'day': w.day, 'llm': LLM.available}}


@app.post('/api/new')
def new_game():
    return {'frames': engine.new_game()}


@app.post('/api/advance')
def advance():
    # 尚未开始游戏时（engine.scene_id 为空）不去推进：原实现会走到
    # engine.step() 里的 SCENES[self.scene_id]，抛 KeyError: None 并返回 500。
    if not engine.scene_id:
        return {'frames': []}
    return {'frames': engine.advance()}


@app.post('/api/input')
def submit_input(body: InputBody):
    return {'frames': engine.submit_input(text=body.text, choice_index=body.choice_index)}


@app.post('/api/act')
def act(body: ActBody):
    if body.action == 'enter_scene':
        return {'frames': engine.enter_offered_scene()}
    frames = engine.interlude_act(body.action, {'to': body.to, 'text': body.text})
    if not isinstance(frames, list):
        frames = [frames]
    return {'frames': frames}


@app.get('/api/locations')
def locations():
    w = engine.world
    cur = LOCATIONS.get(w.location, {})
    return {'current': w.location, 'current_name': cur.get('name'),
            'bg': cur.get('bg'), 'adjacent': [
                {'id': k, 'name': LOCATIONS[k]['name']} for k in cur.get('adjacent', [])]}


@app.get('/api/backlog')
def backlog():
    return {'history': engine.history[-100:]}


@app.get('/api/world')
def world_info():
    w = engine.world
    return {
        'day': w.day, 'phase': w.phase, 'location': w.location,
        'flags': {k: v for k, v in w.flags.items() if not k.startswith('_')},
        'affection': w.affection('shuuji', 'miyuki'),
        'countdown': w.festival_countdown,
        'knowledge': {c: w.knowledge_of(c) for c in ('relative_man', 'relative_woman', 'toba')},
    }


@app.post('/api/save/{slot}')
def save(slot: str):
    path = engine.save(slot)
    return {'ok': True, 'slot': slot, 'path': path}


@app.post('/api/load/{slot}')
def load(slot: str):
    try:
        return {'frames': engine.load(slot)}
    except FileNotFoundError:
        return JSONResponse({'error': 'save not found'}, status_code=404)


@app.get('/api/saves')
def saves():
    """存档列表。`saves` 保持原有的槽位名数组，`meta` 为追加的元数据（读档界面展示进度），
    不影响既有调用方。"""
    out, meta = [], {}
    if os.path.isdir(SAVE_DIR):
        for fn in sorted(os.listdir(SAVE_DIR)):
            if not fn.endswith('.json'):
                continue
            slot = fn[:-5]
            out.append(slot)
            try:
                with open(os.path.join(SAVE_DIR, fn), encoding='utf-8') as f:
                    d = json.load(f)
                w = d.get('world') or {}
                loc = LOCATIONS.get(w.get('location'), {})
                meta[slot] = {
                    'ts': d.get('ts'),
                    'day': w.get('day'),
                    'phase': w.get('phase'),
                    'location': loc.get('name') or w.get('location'),
                    'countdown': w.get('festival_countdown'),
                    'axes': w.get('axes'),
                }
            except Exception:
                meta[slot] = {}
    return {'saves': out, 'meta': meta}


@app.get('/api/personas')
def personas():
    return {c: {'display': p.get('display'), 'has_prompt': bool(p.get('system_prompt'))}
            for c, p in PERSONAS.items()}


@app.get('/api/health')
def health():
    return {'ok': True, 'llm': LLM.available, 'model': LLM.model if LLM.available else None}


class ModeBody(BaseModel):
    llm: Optional[bool] = None


@app.post('/api/mode')
def set_mode(body: ModeBody):
    """运行时开关 LLM（回归测试离线跑，避免真实 API 调用与超时）。"""
    if body.llm is not None:
        LLM.enabled = body.llm
    return {'llm': LLM.available, 'model': LLM.model if LLM.available else None}


# ---------------------------------------------------------------- 静态资源
class NoCacheStaticFiles(StaticFiles):
    """HTML/JS/CSS 禁止缓存（避免浏览器拿旧版代码），媒体文件保留缓存。"""

    def file_response(self, *args, **kwargs):
        resp = super().file_response(*args, **kwargs)
        path = str(getattr(resp, 'path', ''))
        if path.endswith(('.html', '.js', '.css', '.json')):
            resp.headers['Cache-Control'] = 'no-store, must-revalidate'
        else:
            resp.headers['Cache-Control'] = 'public, max-age=86400'
        return resp


@app.get('/play', include_in_schema=False)
def play_entry():
    """免缓存入口：地址本身从未被缓存过，保证拿到最新前端。"""
    return FileResponse(os.path.join(ROOT, 'web', 'index.html'),
                        headers={'Cache-Control': 'no-store'})


app.mount('/assets', StaticFiles(directory=os.path.join(ROOT, 'assets')), name='assets')
app.mount('/', NoCacheStaticFiles(directory=os.path.join(ROOT, 'web'), html=True), name='web')
