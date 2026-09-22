/* 深雪 ~miyuki~ 前端 · 00 基础层：DOM 缩写、REST 封装、全局可变状态、玩家设置、提示条。
   依赖：无（必须最先加载）。 */
'use strict';
const $ = (id) => document.getElementById(id);

const API = {
  new: () => post('/api/new'),
  advance: () => post('/api/advance'),
  input: (body) => post('/api/input', body),
  act: (body) => post('/api/act', body),
  state: () => get('/api/state'),
  locations: () => get('/api/locations'),
  backlog: () => get('/api/backlog'),
  world: () => get('/api/world'),
  saves: () => get('/api/saves'),
  save: (slot) => post('/api/save/' + slot),
  load: (slot) => post('/api/load/' + slot),
};

async function get(url) { const r = await fetch(url); return r.json(); }
async function post(url, body) {
  const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });
  return r.json();
}

// ---------------- 全局可变状态（跨模块共享，故集中声明在此） ----------------
let typing = false, typeTimer = null;
let currentText = '', shownText = '';
let autoMode = false, autoTimer = null;
let lastKind = null;
let bgFlip = false;
let currentBg = null;
let lastChips = null;   // 当前帧下发的快捷回答候选：50 推进层写入，60 面板层渲染
let talkMode = false;   // 幕间「交谈」模式：下一次提交走 talk 行动，而不是正典选项

// ---------------- 玩家设置（持久化） ----------------
// 原版没有设置面板，文字速度 34ms、自动间隔 1.4s、音量 0.55 全部写死在代码里。
const settings = {
  speed: parseInt(localStorage.getItem('gal_text_speed') || '34', 10),   // 打字机每字毫秒
  autoSec: parseFloat(localStorage.getItem('gal_auto_sec') || '1.4'),    // 自动模式每句停留秒
  snow: localStorage.getItem('gal_snow') !== '0',                        // 飘雪开关
  vol: parseFloat(localStorage.getItem('gal_bgm_vol') || '0.55'),        // BGM 音量
};
function saveSettings() {
  localStorage.setItem('gal_text_speed', String(settings.speed));
  localStorage.setItem('gal_auto_sec', String(settings.autoSec));
  localStorage.setItem('gal_snow', settings.snow ? '1' : '0');
  localStorage.setItem('gal_bgm_vol', String(settings.vol));
}
const SPEED_PRESETS = [['慢', 60], ['标准', 34], ['快', 16], ['瞬间', 0]];

function cName(c) { return ({ shuuji: '修二', miyuki: '深雪', toba: '鸟羽老人', relative_man: '叔父', relative_woman: '婶婶' })[c] || c; }
function esc(s) { const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }

// ---------------- Toast ----------------
let toastTimer = null;
function toast(msg) {
  const t = $('toast');
  t.textContent = msg;
  t.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.add('hidden'), 2200);
}

