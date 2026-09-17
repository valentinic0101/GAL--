/* 深雪 ~miyuki~ 前端逻辑 */
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

// ---------------- 全局状态 ----------------
let typing = false, typeTimer = null;
let currentText = '', shownText = '';
let autoMode = false, autoTimer = null;
let lastKind = null;
let bgFlip = false;
let currentBg = null;

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

// ---------------- 雪花 ----------------
// 修复：原来只往游戏画面的 #snow-overlay 注入，标题页 .title-snow 是个空 div ——
//       「雪国」题材的标题画面一颗雪花都没有。
function spawnSnow(n) {
  const html = settings.snow ? Array.from({ length: n }, makeFlake).join('') : '';
  ['snow-overlay', 'title-snow'].forEach(id => {
    const el = $(id);
    if (el) el.innerHTML = html;
  });
}
function makeFlake() {
  // 修复：原来 2–7px / 35–90% 不透明度，在暗场景底上全屏仅约 40 个可辨像素。
  //       改为「迎光雪片」：粒径更大、亮度更高，并加一道柔光。
  const size = 2.5 + Math.random() * 6.5;
  const left = Math.random() * 100;
  const dur = 8 + Math.random() * 14;
  const delay = -Math.random() * 20;
  const op = 0.45 + Math.random() * 0.5;
  return `<div class="snowflake" style="left:${left}vw;width:${size}px;height:${size}px;opacity:${op};animation-duration:${dur}s;animation-delay:${delay}s"></div>`;
}
spawnSnow(70);

// ---------------- 背景音乐 ----------------
const bgmAudio = new Audio();
bgmAudio.loop = true;
bgmAudio.preload = 'auto';
bgmAudio.volume = 0;
window.bgm = bgmAudio;   // 便于调试验证
let bgmKey = null;
let bgmMuted = localStorage.getItem('gal_bgm_muted') === '1';
let bgmFadeTimer = null;

function updateBgmBtn() {
  const b = $('btn-bgm');
  b.classList.toggle('off', bgmMuted);
  // 修复：原来音乐开关用 ♪，而状态栏里 ♪ 又同时表示好感度与羁绊轴（一号三义），
  //       且静音态与默认态外观完全一致，玩家判断不出 BGM 是开是关。
  b.textContent = bgmMuted ? '♫̸' : '♫';
  b.title = bgmMuted ? '背景音乐：关（点击开启）' : '背景音乐：开（点击关闭）';
}
function rampVolume(target, ms, done) {
  clearInterval(bgmFadeTimer);
  const stepMs = 50;
  const steps = Math.max(1, Math.round(ms / stepMs));
  const start = bgmAudio.volume;
  let i = 0;
  bgmFadeTimer = setInterval(() => {
    i++;
    bgmAudio.volume = Math.max(0, Math.min(1, start + (target - start) * (i / steps)));
    if (i >= steps) { clearInterval(bgmFadeTimer); if (done) done(); }
  }, stepMs);
}
function setBgm(key, force) {
  if (!key || (key === bgmKey && !force)) return;
  bgmKey = key;
  const src = `/assets/bgm/${key}.m4a`;
  const startNew = () => {
    bgmAudio.src = src;
    bgmAudio.volume = 0;
    bgmAudio.muted = bgmMuted;
    bgmAudio.play().catch(() => { /* 浏览器尚未解锁自动播放 */ });
    rampVolume(settings.vol, 1800);
  };
  if (!bgmAudio.src) { startNew(); return; }
  rampVolume(0, 900, startNew);   // 旧曲淡出 → 换曲淡入
}
function unlockBgm() {           // 首次用户交互时解锁
  if (!bgmAudio.src && bgmKey) setBgm(bgmKey, true);
  else if (bgmAudio.paused && bgmKey) bgmAudio.play().catch(() => {});
}
$('btn-bgm').onclick = () => {
  bgmMuted = !bgmMuted;
  localStorage.setItem('gal_bgm_muted', bgmMuted ? '1' : '0');
  bgmAudio.muted = bgmMuted;
  if (!bgmMuted) unlockBgm();
  updateBgmBtn();
  toast(bgmMuted ? '背景音乐：关' : '背景音乐：开');
};
updateBgmBtn();
document.addEventListener('pointerdown', unlockBgm, { once: true });
document.addEventListener('keydown', unlockBgm, { once: true });

// ---------------- 忙碌指示（LLM 响应期间：右下角低调进度条） ----------------
let busyCount = 0, lwTimer = null, lwShowTimer = null, lwSec = 0;
const lwEl = () => document.getElementById('llm-wait');
function busyOn(msg) {
  busyCount++;
  if (msg) toast(msg);
  if (busyCount === 1) {
    lwSec = 0;
    // 400ms 内返回就不打扰玩家（快回复无感）
    lwShowTimer = setTimeout(() => {
      lwEl().classList.add('show');
      lwTimer = setInterval(() => {
        lwSec++;
        document.getElementById('lw-sec').textContent = lwSec + 's';
      }, 1000);
    }, 400);
  }
  document.body.style.cursor = 'wait';
}
function busyOff() {
  busyCount = Math.max(0, busyCount - 1);
  if (busyCount === 0) {
    clearTimeout(lwShowTimer); clearInterval(lwTimer);
    lwEl().classList.remove('show');
    document.body.style.cursor = '';
  }
}
async function guarded(promiseFactory, msg) {
  busyOn(msg);
  try { return await promiseFactory(); }
  finally { busyOff(); }
}

const _origAdvance = advance;
advance = async function () {
  if (busyCount > 0) return;               // 防重复触发
  return guarded(async () => _origAdvance());
};
const _origSubmit = submitInput;
let talkMode = false;
submitInput = async function (text, choiceIndex) {
  if (busyCount > 0) return;
  return guarded(async () => {
    if (talkMode) {                    // 幕间交谈模式
      talkMode = false;
      $('input-panel').classList.add('hidden');
      return _origTalkAct('talk', { text });
    }
    return _origSubmit(text, choiceIndex);
  }, null);
};
const _origTalkAct = doAct;
doAct = async function (action, payload) {
  if (busyCount > 0) return;
  return guarded(async () => _origTalkAct(action, payload), null);
};

// ---------------- 标题 ----------------
$('title-screen').classList.add('active');
setBgm('bgm_title');   // 标题曲（等待首次交互解锁）
$('btn-new').onclick = async () => {
  showGame();
  const r = await API.new();
  playFrames(r.frames);
};
$('btn-continue').onclick = async () => {
  const r = await API.load('auto');
  if (r.error) { toast('没有自动存档，开始新游戏'); return startNew(); }
  showGame(); playFrames(r.frames);
};
$('btn-load-title').onclick = async () => {
  const r = await API.saves();
  showSavesModal(r.saves, true, r.meta);
};
// 没有自动存档时把「继续旅程」标为禁用观感（点击仍会提示并开始新游戏，保持既有行为）
(async () => {
  try {
    const r = await API.saves();
    if (!(r.saves || []).includes('auto')) {
      const b = $('btn-continue');
      b.classList.add('disabled');
      b.title = '还没有自动存档，点击将开始新游戏';
    }
  } catch (e) { /* 忽略 */ }
})();
async function startNew() { showGame(); const r = await API.new(); playFrames(r.frames); }
function showGame() {
  $('title-screen').classList.remove('active');
  $('game-screen').classList.add('active');
}

// ---------------- 帧播放器 ----------------
// 帧队列：一次 API 响应可能包含多帧（你的话 → 她的回应 → 下一拍）。
// 逐帧展示、点击推进——回应不再被下一拍覆盖；遇到交互帧（选项/输入/幕间）即停。
let frameQueue = [];
function playFrames(frames) {
  if (!frames || !frames.length) return;
  frameQueue = frames.slice();
  stepQueue();
}
function stepQueue() {
  while (frameQueue.length) {
    const f = frameQueue.shift();
    if (f.kind === 'choice' || f.kind === 'free' || f.kind === 'interlude' || f.kind === 'error' || f.kind === 'scene_title') {
      frameQueue = [];          // 交互帧之后的内容由下一次 API 响应提供
      applyFrame(f);
      return;
    }
    applyFrame(f);
    if (frameQueue.length) return;   // 还有排队的帧：等待点击（或自动模式）继续
  }
}

function applyFrame(f) {
  if (!f) return;
  if (f.chips !== undefined && f.chips !== null) lastChips = f.chips;
  if (f.kind === 'free' || f.kind === 'interlude') renderChips(lastChips || ['……']);
  setBg(f.bg);
  setBgm((f.meta && f.meta.bgm) || null);
  setSprites(f.sprites || [], f.bg);
  updateStatus(f.meta || {});
  handleSceneOffer(f.meta || {});
  hideAllPanels();

  if (f.kind === 'cg') {
    showCg(f.meta && f.meta.cg, f.text);
    return;
  }
  if (f.kind === 'scene_title') {
    showSceneCard(f.note || '');
    setTimeout(() => advance(), 2100);
    return;
  }
  if (f.kind === 'interlude') {
    showInterlude(f);
    return;
  }
  if (f.kind === 'choice') {
    showChoices(f.choices || []);
    return;
  }
  if (f.kind === 'free') {
    showInput(f.note || '你想说什么？', true);
    return;
  }
  if (f.kind === 'error') {
    toast(f.note || '出错了');
    showInterlude({ note: f.note, meta: f.meta });
    return;
  }
  // narration / line / me
  lastKind = f.kind;
  if (f.kind === 'narration') {
    $('narration-box').classList.remove('hidden');
    $('dialog-box').classList.add('hidden');
    $('action-text').classList.add('hidden');
    typeWriter($('narration-text'), f.text);
  } else {
    $('dialog-box').classList.remove('hidden');
    $('narration-box').classList.add('hidden');
    $('name-text').textContent = f.name || (f.kind === 'me' ? '修二' : '');
    const at = $('action-text');
    if (f.action) { at.textContent = f.action; at.classList.remove('hidden'); }
    else at.classList.add('hidden');
    $('nameplate').style.display = '';
    typeWriter($('dialog-text'), f.text);
  }
  saveAuto();
}

function showCg(img, caption) {
  if (!img) return;
  const ov = $('cg-overlay');
  $('cg-img').src = '/assets/cg/' + img;
  let hint = ov.querySelector('.cg-hint');
  if (!hint) { hint = document.createElement('div'); hint.className = 'cg-hint'; ov.appendChild(hint); }
  hint.textContent = (caption || '') + '　▼ 点击继续';
  ov.classList.remove('hidden');
}
$('cg-overlay').onclick = () => { $('cg-overlay').classList.add('hidden'); if (!typing) advance(); };
function hideAllPanels() {
  ['choice-panel', 'input-panel', 'interlude-panel'].forEach(i => $(i).classList.add('hidden'));
  $('cg-overlay').classList.add('hidden');
  $('dialog-box').classList.add('hidden');
  $('narration-box').classList.add('hidden');
}

// ---------------- 打字机 ----------------
function typeWriter(el, text) {
  clearInterval(typeTimer);
  typing = true; currentText = text || ''; shownText = '';
  el.textContent = '';
  el.onclick = completeType;
  // 「瞬间」档直接整段显示（用 setInterval(…,0) 会被浏览器节流到 ~4ms，并不真的瞬间）
  if (!settings.speed) {
    el.textContent = currentText; shownText = currentText;
    typing = false; scheduleAuto(); return;
  }
  let i = 0;
  typeTimer = setInterval(() => {
    if (i >= currentText.length) { clearInterval(typeTimer); typing = false; scheduleAuto(); return; }
    const step = Math.random() < 0.3 ? 2 : 1;
    shownText = currentText.slice(0, i + step);
    el.textContent = shownText;
    i += step;
  }, settings.speed);
}
function completeType() {
  if (typing) {
    clearInterval(typeTimer); typing = false;
    if (lastKind === 'narration') $('narration-text').textContent = currentText;
    else $('dialog-text').textContent = currentText;
    scheduleAuto();
  }
}

// ---------------- 推进 ----------------
async function advance() {
  if (typing) { completeType(); return; }
  if (frameQueue.length) { stepQueue(); return; }
  const r = await API.advance();
  playFrames(r.frames);
}
$('dialog-box').onclick = () => { if (!typing) advance(); else completeType(); };
$('narration-box').onclick = () => { if (!typing) advance(); else completeType(); };
document.addEventListener('keydown', (e) => {
  // QA P1-1：焦点在按钮/输入框上时空格/回车交给元素自身，防止误触残留焦点的按钮（如「开始游戏」）
  const tag = (e.target && e.target.tagName) || '';
  if (tag === 'BUTTON' || tag === 'INPUT' || tag === 'TEXTAREA') return;
  if (e.key === 'Enter' || e.key === ' ') {
    // 标题页不推进：此时服务端尚未开始游戏（scene_id 为空），
    // 原实现会发出 /api/advance 并拿到 500（服务端 SCENES[None] 抛 KeyError）。
    if (!$('game-screen').classList.contains('active')) return;
    if ($('input-panel').classList.contains('hidden')) { e.preventDefault(); advance(); }
  }
  if (e.key === 'Escape') closeModal();
});
// QA P1-1：按钮点击后移除焦点
document.addEventListener('click', (e) => {
  const b = e.target && e.target.closest && e.target.closest('button');
  if (b) b.blur();
}, true);

// ---------------- 选项 ----------------
function showChoices(choices) {
  const panel = $('choice-panel');
  panel.innerHTML = '';
  choices.forEach((opt, idx) => {
    const b = document.createElement('button');
    b.className = 'choice-btn';
    b.textContent = opt.label;
    b.onclick = () => submitInput(null, idx);
    panel.appendChild(b);
  });
  // 自由输入入口
  const free = document.createElement('button');
  free.className = 'choice-btn';
  free.style.opacity = '.82';
  free.textContent = '✎ （自由输入想说的话…）';
  free.onclick = () => {
    panel.classList.add('hidden');
    showInput('此刻，你想说什么？', false);
  };
  panel.appendChild(free);
  panel.classList.remove('hidden');
}

async function submitInput(text, choiceIndex) {
  const r = await API.input({ text, choice_index: choiceIndex });
  $('choice-panel').classList.add('hidden');
  $('input-panel').classList.add('hidden');
  playFrames(r.frames);
}

// ---------------- 自由输入 ----------------
function showInput(hint) {
  $('input-hint').textContent = hint || '你想说什么？';
  $('input-panel').classList.remove('hidden');
  $('free-input').value = '';
  $('free-input').focus();
}
$('btn-send').onclick = () => {
  const t = $('free-input').value.trim();
  if (t) submitInput(t, null);
};
$('free-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    e.stopPropagation();
    const t = $('free-input').value.trim();
    if (t) submitInput(t, null);
  }
});
// 快捷回答：由当前帧的 chips 字段下发（逐场景/逐节点定制），点击即填入输入框
function renderChips(list) {
  const box = document.querySelector('.input-quick');
  if (!box) return;
  box.innerHTML = '';
  (list || []).slice(0, 3).forEach(t => {
    const b = document.createElement('button');
    b.className = 'quick';
    b.textContent = t;
    b.onclick = () => {
      $('free-input').value = (t === '……' ? '……' : t);
      $('free-input').focus();
    };
    box.appendChild(b);
  });
}
let lastChips = null;

// ---------------- 结局卡 ----------------
let endingShown = null;
function renderEndingCard(ending) {
  const el = $('ending-card');
  if (!ending) { el.classList.add('hidden'); return; }
  if (endingShown === ending.id) return;   // 每个结局每次载入只弹一次
  endingShown = ending.id;
  el.innerHTML = `<div class="ec-label">— ENDING —</div>
    <div class="ec-title">${ending.title}</div>
    ${ending.subtitle ? `<div class="ec-sub">· ${ending.subtitle} ·</div>` : ''}
    <div class="ec-btns"><button id="ec-new">开始新的故事</button><button id="ec-stay">留在回忆里</button></div>`;
  el.classList.remove('hidden');
  $('ec-new').onclick = async () => { el.classList.add('hidden'); endingShown = null; const r = await API.new(); playFrames(r.frames); };
  $('ec-stay').onclick = () => el.classList.add('hidden');
}

// ---------------- 幕间 ----------------
async function showInterlude(f) {
  $('interlude-panel').classList.remove('hidden');
  $('inter-note').textContent = f.note || '雪还在下。';
  renderEndingCard(f.meta && f.meta.ending);
  // 移动按钮
  const loc = await API.locations();
  const mb = $('move-btns');
  mb.innerHTML = '';
  (loc.adjacent || []).forEach(l => {
    const b = document.createElement('button');
    b.className = 'move-btn';
    b.textContent = '→ ' + l.name;
    b.onclick = () => doAct('move', { to: l.id });
    mb.appendChild(b);
  });
  // 若有剧情推进
  const offer = f.meta && f.meta.scene_offer;
  const btnOffer = $('btn-scene-offer');
  if (offer) {
    btnOffer.classList.remove('hidden');
    btnOffer.textContent = '▶ 推进剧情：' + (f.meta.scene_offer_title || offer);
    btnOffer.onclick = () => doAct('enter_scene', {});
  } else btnOffer.classList.add('hidden');
}
async function doAct(action, payload) {
  const r = await API.act(Object.assign({ action }, payload || {}));
  playFrames(r.frames);
}
$('btn-talk').onclick = () => { showInput('想和谁说点什么？（当前在场的人会回应你）'); talkMode = true; };
$('btn-wait').onclick = () => doAct('wait', {});

// ---------------- 场景推进提示 ----------------
function handleSceneOffer(meta) { /* 在 showInterlude 中处理 */ }

// ---------------- 背景 / 立绘 ----------------
function setBg(bg) {
  if (!bg || bg === currentBg) return;
  currentBg = bg;
  // QA P3-3：室内场景关闭飘雪（正典：雪在室外）。室外/标题画面保持。
  const INDOOR_BG = ['bg_oldhouse_room.png', 'bg_oldhouse_room_night.png',
                     'bg_oldhouse_corridor.png', 'bg_toba_home.png', 'bg_tokyo.png'];
  const snow = $('snow-overlay');
  if (snow) snow.classList.toggle('hidden', INDOOR_BG.includes(bg));
  const a = $('bg-a'), b = $('bg-b');
  const showEl = bgFlip ? a : b;
  const hideEl = bgFlip ? b : a;
  const manifest = window.ASSET_MANIFEST;
  const missing = !!(manifest && manifest.bg && manifest.bg.length && !manifest.bg.includes(bg));
  if (missing) {
    // 素材未生成：优雅降级（柔和渐晕底 + 「待素材」角标），图放入 assets 后自动生效
    showEl.style.backgroundImage =
      'linear-gradient(180deg, #dfe9f5 0%, #cdd9ef 42%, #e6d9e4 78%, #b9c4dc 100%)';
    showEl.classList.add('bg-missing');
  } else {
    showEl.style.backgroundImage = `url('/assets/backgrounds/${bg}')`;
    showEl.classList.remove('bg-missing');
  }
  showEl.classList.add('show');
  hideEl.classList.remove('show');
  hideEl.classList.remove('bg-missing');
  bgFlip = !bgFlip;
  const note = $('bg-note');
  if (note) {
    note.textContent = (bg.includes('spring') ? '春天 · ' : '') + '素材生成中';
    note.classList.toggle('hidden', !missing);
  }
}
// ---------------- 立绘舞台：地面贴合 + 纵深 + 亮度匹配 + 接触投影 ----------------
// 配置单一来源：tools/stage_config.json → web/stage_meta.js（audit_stage.py 负责校验与再生成）
const M = window.STAGE_META || {};
const CHAR_HEIGHT = M.char_height || {};
const sceneStage = bg => (M.scene_stage || {})[bg] || M.default_stage ||
  { ground: .08, scale: .95, light: 'brightness(.9)', shadowO: .30 };
const depthOf = n => {
  const dp = M.depth_profile || {};
  return dp[String(n)] || dp['default'] || [1];
};
const FEET = () => window.SPRITE_FEET || {};

// 缩放身材比（未加载完成时用估算值）
function aspectOf(box, sp) {
  const img = box && box.querySelector ? box.querySelector('img') : null;
  if (img && img.naturalWidth && img.naturalHeight) return img.naturalWidth / img.naturalHeight;
  return (window.SPRITE_ASPECT && window.SPRITE_ASPECT[sp.sprite]) || .66;
}
function baseHeight(sp) {
  const key = (sp.sprite || '').replace('\\.png$', '').replace('\\.svg$', '');
  return CHAR_HEIGHT[key] != null ? CHAR_HEIGHT[key] : (CHAR_HEIGHT[sp.id] != null ? CHAR_HEIGHT[sp.id] : .74);
}

// 槽位求解：角色序 → 中心 x（px），保证不出屏且相邻不重叠（从外向内收敛）
function solveSlots(order, sizes, vw) {
  const n = order.length;
  const xs = n === 1 ? [.58] : n === 2 ? [.24, .74] : n === 3 ? [.15, .45, .78]
    : order.map((_, i) => .12 + i * (.78 / Math.max(1, n - 1)));
  const pts = xs.map(f => f * vw);
  const half = i => sizes[i] / 2;
  const pad = 10;
  // 右端先钳到屏内
  pts[n - 1] = Math.min(pts[n - 1], vw - half(n - 1) - pad);
  for (let i = n - 2; i >= 0; i--) {
    const lim = pts[i + 1] - half(i + 1) - half(i) - pad;   // 不与右侧重叠
    pts[i] = Math.min(Math.max(pts[i], half(i) + pad), lim);
  }
  // 最左也不得出屏（必要时整体右移）
  if (pts[0] < half(0) + pad) {
    const shift = half(0) + pad - pts[0];
    for (let i = 0; i < n; i++) pts[i] += shift;
    for (let i = 1; i < n; i++) pts[i] = Math.min(pts[i], vw - half(i) - pad);
  }
  return pts;
}

// 人群自适应：总宽超出画面时按比例收缩全体身高（与 audit_stage.py 同一算法）
function fitCrowd(dispHs, aspects, vw, pad, edge) {
  let hs = [...dispHs];
  for (let t = 0; t < 4; t++) {
    const total = hs.reduce((acc, h, i) => acc + h * aspects[i], 0) + (hs.length - 1) * pad;
    const avail = vw - 2 * edge;
    if (total <= avail || hs.length === 1) break;
    const k = Math.max(.6, Math.pow(avail / total, .9));
    hs = hs.map(h => h * k);
  }
  return hs;
}

// 场景光的 brightness 取下限，非发言者只压到 0.88。
// 修复：原「暗场景基色 × 非发言者 0.74」是双重压暗 —— corridor/shrine 等场景的 light 是
//       brightness(.60)，乘 0.74 后立绘只剩 44.4% 亮度，实测主角立绘区域 mean 20.2，
//       与空背景 19.4 在统计上无法区分（玩家看不到自己）。改成给 brightness 设下限 0.78，
//       场景的幽暗氛围仍由背景图片承担，但立绘始终可辨。
const LIGHT_FLOOR = 0.78, DIM_NONSPEAK = 0.88, BOOST_SPEAK = 1.05;
function lightFilter(light, speaking) {
  return light.replace(/brightness\(([\d.]+)\)/, (m, v) => {
    const base = Math.max(parseFloat(v), LIGHT_FLOOR);
    const k = speaking ? BOOST_SPEAK : DIM_NONSPEAK;
    return 'brightness(' + Math.min(1, base * k).toFixed(3) + ')';
  });
}

function setSprites(sprites, bg) {
  const layer = $('sprite-layer');
  const stageH = layer.clientHeight || innerHeight;
  const vw = layer.clientWidth || innerWidth;
  const stage = sceneStage(bg);
  const order = [...sprites].sort((a, b) => {
    const rank = c => (c.id === 'shuuji' ? -1 : (c.id === 'miyuki' ? 9 : 0));
    return rank(a) - rank(b);
  });
  const n = order.length;
  const depths = depthOf(n);
  const pad = 10, edge = 10;
  let dispHs = order.map(sp => baseHeight(sp) * stage.scale * depthOf(n)[order.indexOf(sp)] * stageH);
  // 真实宽高比 → 人群压缩 → 槽位求解
  const aspects = order.map(sp => aspectOf(null, sp));
  dispHs = fitCrowd(dispHs, aspects, vw, pad, edge);
  const pts = solveSlots(order, dispHs.map((h, i) => h * aspects[i]), vw);
  const seen = new Set();
  order.forEach((sp, i) => {
    seen.add(sp.id);
    let box = layer.querySelector(`[data-key="${sp.id}"]`);
    if (!box) {
      box = document.createElement('div');
      box.className = 'sprite';
      box.dataset.key = sp.id;
      box.innerHTML = '<img alt="' + (sp.name || '') + '"><div class="shadow"></div>';
      layer.appendChild(box);
    }
    const img = box.querySelector('img');
    const url = '/assets/sprites/' + sp.sprite;
    if (img.getAttribute('src') !== url) img.src = url;

    const depth = depths[i] != null ? depths[i] : 1;
    const dispH = dispHs[i];
    const foot = FEET()[sp.sprite] || .01;
    const groundY = stage.ground * (1 - (1 - depth) * .5) * stageH;
    box.style.setProperty('--x', pts[i] + 'px');
    box.style.height = dispH + 'px';
    box.style.bottom = Math.round(groundY - foot * dispH) + 'px';
    box.classList.toggle('depth', depth < .95);
    box.classList.toggle('speaking', !!sp.speaking);
    box.classList.add('on');
    img.style.filter = lightFilter(stage.light, !!sp.speaking);
    box.style.setProperty('--s', sp.speaking ? 1.035 : 1);
    const sh = box.querySelector('.shadow');
    const setShadow = () => {
      const w = dispH * aspectOf(box, sp);
      sh.style.width = Math.round(w * .58) + 'px';
      sh.style.height = Math.round(dispH * .075) + 'px';
      sh.style.opacity = stage.shadowO;
    };
    if (img.complete) setShadow(); else { img.onload = setShadow; }
  });
  layer.querySelectorAll('.sprite').forEach(box => {
    if (!seen.has(box.dataset.key)) box.classList.remove('on');
    else box.classList.add('on');
  });
  layer.classList.toggle('narrating', sprites.length > 0 && !sprites.some(s => s.speaking));
}

// ---------------- 状态条 ----------------
function updateStatus(meta) {
  $('st-phase').textContent = meta.scene_title || (meta.phase ? '阶段 ' + meta.phase : '');
  $('st-day').textContent = meta.day != null ? '第 ' + meta.day + ' 天' : '';
  $('st-loc').textContent = meta.location || '';
  $('st-affection').textContent = meta.affection != null ? '深雪♪ ' + meta.affection : '';
  const ax = meta.axes;
  if (ax) $('st-axes').textContent = `羁绊♪${ax.bond} 山之念▲${ax.obsession} 现世◇${ax.worldly}`;
  $('st-countdown').textContent = meta.countdown > 0 ? '冬祭还有 ' + meta.countdown + ' 天' : (meta.countdown === 0 ? '♪ 今晚是冬祭 ♪' : '');
}

// ---------------- 场景标题卡 ----------------
function showSceneCard(title) {
  const card = $('scene-title-card');
  card.querySelector('span').textContent = title;
  card.classList.remove('hidden');
  card.style.animation = 'none'; card.offsetHeight; card.style.animation = '';
  setTimeout(() => card.classList.add('hidden'), 2300);
}

// ---------------- 自动模式 ----------------
$('btn-auto').onclick = () => {
  autoMode = !autoMode;
  $('btn-auto').classList.toggle('on', autoMode);
  if (autoMode) scheduleAuto(600);
};
function scheduleAuto(delay) {
  clearTimeout(autoTimer);
  if (!autoMode) return;
  autoTimer = setTimeout(() => {
    if (!typing && $('choice-panel').classList.contains('hidden') &&
        $('input-panel').classList.contains('hidden') &&
        $('interlude-panel').classList.contains('hidden')) advance();
  }, delay || Math.round(settings.autoSec * 1000));
}

// ---------------- 弹窗 ----------------
function openModal(title, html) {
  $('modal-title').textContent = title;
  $('modal-body').innerHTML = html;
  $('modal').classList.remove('hidden');
}
function closeModal() { $('modal').classList.add('hidden'); }
$('modal-close').onclick = closeModal;

$('btn-log').onclick = async () => {
  const r = await API.backlog();
  const html = (r.history || []).map(h =>
    h.name === '旁白' || h.name === null
      ? `<div class="log-item narration">${esc(h.text)}</div>`
      : `<div class="log-item"><span class="log-name">${esc(h.name)}：</span>${esc(h.text)}${h.action ? `<div class="narration" style="font-size:13px">${esc(h.action)}</div>` : ''}</div>`
  ).join('') || '（还没有记录）';
  openModal('回 想', html);
};
$('btn-world').onclick = async () => {
  const r = await API.world();
  const flags = Object.entries(r.flags || {}).filter(([k]) => k !== 'time_skip')
    .map(([k]) => k).join('、') || '（无）';
  const rumors = [];
  for (const [c, ks] of Object.entries(r.knowledge || {})) {
    for (const [k, v] of Object.entries(ks)) {
      if (v.source === 'heard') rumors.push(`${cName(c)} 听说：${esc(v.content)}`);
    }
  }
  openModal('世界状态', `
    <div class="world-kv"><b>游戏日</b>：${r.day} ｜ <b>地点</b>：${r.location} ｜ <b>阶段</b>：${r.phase}</div>
    <div class="world-kv"><b>与深雪的羁绊</b>：${r.affection} / 100</div>
    <div class="world-kv"><b>冬祭倒计时</b>：${r.countdown > 0 ? r.countdown + ' 天' : '已至'}</div>
    <div class="world-kv"><b>经历的事件</b>：${flags}</div>
    <div class="world-kv" style="margin-top:14px"><b>◆ 镇子上的传闻（八卦传播引擎）</b></div>
    ${rumors.length ? rumors.map(x => `<div class="rumor">・${x}</div>`).join('') : '<div class="rumor">（传闻还在酝酿……）</div>'}
  `);
};
function cName(c) { return ({ shuuji: '修二', miyuki: '深雪', toba: '鸟羽老人', relative_man: '叔父', relative_woman: '婶婶' })[c] || c; }
function esc(s) { const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }

// ---------------- 设置 ----------------
// 新增面板：文字速度 / BGM 音量 / 自动间隔 / 飘雪开关，全部持久化到 localStorage。
// 标题页那句面向开发者的宣传语（多 Agent 驱动…）也移到这里，让标题页保持文学向调性。
function openSettings() {
  const speedSeg = SPEED_PRESETS.map(([label, ms]) =>
    `<button class="${settings.speed === ms ? 'on' : ''}" onclick="setSpeed(${ms})">${label}</button>`).join('');
  const autoSeg = [[1.0, '1.0 秒'], [1.4, '1.4 秒'], [2.4, '2.4 秒'], [4.0, '4.0 秒']].map(([sec, label]) =>
    `<button class="${Math.abs(settings.autoSec - sec) < .01 ? 'on' : ''}" onclick="setAutoSec(${sec})">${label}</button>`).join('');
  const snowSeg = [[1, '开'], [0, '关']].map(([v, label]) =>
    `<button class="${(settings.snow ? 1 : 0) === v ? 'on' : ''}" onclick="setSnow(${v})">${label}</button>`).join('');
  openModal('设 置', `
    <div class="set-row">
      <div class="set-label">文字速度<small>打字机逐字显示的速度</small></div>
      <div class="set-ctl"><div class="seg">${speedSeg}</div></div>
    </div>
    <div class="set-row">
      <div class="set-label">背景音乐<small>当前曲目：${bgmKey || '—'}</small></div>
      <div class="set-ctl">
        <div class="vol-track" id="vol-track">
          <div class="vol-fill" style="width:${Math.round(settings.vol * 100)}%"></div>
          <div class="vol-knob" style="left:${Math.round(settings.vol * 100)}%"></div>
        </div>
      </div>
    </div>
    <div class="set-row">
      <div class="set-label">自动播放间隔<small>自动模式下每句停留时间</small></div>
      <div class="set-ctl"><div class="seg">${autoSeg}</div></div>
    </div>
    <div class="set-row">
      <div class="set-label">飘雪与特效<small>关闭可提升低配设备帧率</small></div>
      <div class="set-ctl"><div class="seg">${snowSeg}</div></div>
    </div>
    <div class="about-block">
      <b>关于本作</b>　多 Agent 驱动 · 导演层调度 · 八卦传播引擎 · 事件溯源存档<br>
      基于《架构设计V1》五层架构实现，NPC 由 Agent 驱动，导演层用 P0~P10 剧情吸引子保证叙事骨架。
    </div>`);
  // 音量条拖动
  const track = $('vol-track');
  if (track) {
    const setFromX = (clientX) => {
      const r = track.getBoundingClientRect();
      const v = Math.max(0, Math.min(1, (clientX - r.left) / r.width));
      settings.vol = v; saveSettings();
      track.querySelector('.vol-fill').style.width = Math.round(v * 100) + '%';
      track.querySelector('.vol-knob').style.left = Math.round(v * 100) + '%';
      bgmAudio.muted = false; bgmMuted = false;
      updateBgmBtn();
      if (!bgmAudio.src && bgmKey) setBgm(bgmKey, true); else bgmAudio.volume = v;
    };
    track.onpointerdown = (e) => {
      setFromX(e.clientX);
      const move = (ev) => setFromX(ev.clientX);
      const up = () => { window.removeEventListener('pointermove', move); window.removeEventListener('pointerup', up); };
      window.addEventListener('pointermove', move);
      window.addEventListener('pointerup', up);
    };
  }
}
function setSpeed(ms) { settings.speed = ms; saveSettings(); openSettings(); toast('文字速度：' + (SPEED_PRESETS.find(p => p[1] === ms) || ['', ''])[0]); }
function setAutoSec(sec) { settings.autoSec = sec; saveSettings(); openSettings(); }
function setSnow(v) { settings.snow = !!v; saveSettings(); spawnSnow(70); openSettings(); toast(v ? '飘雪：开' : '飘雪：关'); }
window.setSpeed = setSpeed; window.setAutoSec = setAutoSec; window.setSnow = setSnow;
$('btn-settings').onclick = openSettings;
$('btn-settings-title').onclick = openSettings;

// ---------------- 存档 ----------------
// 改动：槽位改用卡片式（编号印章 + 进度描述），元数据来自 /api/saves 新增的 meta 字段。
const SLOT_IDS = ['1', '2', '3'];
function slotMetaLine(m) {
  if (!m || m.day == null) return '尚未保存';
  const parts = [`第 ${m.day} 天`];
  if (m.location) parts.push(m.location);
  if (m.phase) parts.push(m.phase);
  if (m.axes && m.axes.bond != null) parts.push(`羁绊♪${m.axes.bond}`);
  if (m.countdown > 0) parts.push(`冬祭还有 ${m.countdown} 天`);
  else if (m.countdown === 0) parts.push('♪ 今晚是冬祭 ♪');
  if (m.ts) {
    const d = new Date(m.ts * 1000);
    const p = (n) => String(n).padStart(2, '0');
    parts.push(`${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`);
  }
  return parts.join('　·　');
}
function slotCard(slot, meta, action, label, extraClass) {
  return `<div class="slot-card ${extraClass || ''}">
    <div class="slot-no">${slot}</div>
    <div class="slot-meta">
      <div class="s-title">${label}</div>
      <div class="s-sub">${esc(slotMetaLine(meta))}</div>
    </div>
    <div class="slot-act"><button class="inter-btn" onclick="${action}">${action.startsWith('doSave') ? '保存' : '读取'}</button></div>
  </div>`;
}
$('btn-save').onclick = () => showSaveModal();
$('btn-load').onclick = async () => { const r = await API.saves(); showSavesModal(r.saves, false, r.meta); };
async function showSaveModal() {
  const r = await API.saves().catch(() => ({ meta: {} }));
  const meta = r.meta || {};
  openModal('存 档', SLOT_IDS.map(s => {
    const m = meta[s];
    const empty = !m || m.day == null;
    return slotCard(s, m, `doSave('${s}')`, empty ? '空档位' : '覆盖此档位', empty ? 'empty' : '');
  }).join('') + '<div class="about-block">自动存档在每次推进时写入，可在标题页「继续旅程」处恢复。</div>');
}
async function doSave(slot) {
  const r = await API.save(slot);
  if (r.ok) { toast('已保存到档位 ' + slot); closeModal(); }
}
async function showSavesModal(saves, fromTitle, meta) {
  const list = (saves || []).filter(s => s !== 'auto' && !/^t\d/.test(s));
  const html = list.length
    ? list.map(s => slotCard(s, (meta || {})[s], `doLoad('${s}', ${!!fromTitle})`, '存档 ' + s, '')).join('')
    : '<div class="about-block">（暂无存档）</div>';
  openModal('读 档', html);
}
async function doLoad(slot, fromTitle) {
  const r = await API.load(slot);
  if (r.error) { toast('读档失败'); return; }
  closeModal();
  if (fromTitle) showGame();
  playFrames(r.frames);
  toast('已读取档位 ' + slot);
}
$('btn-title').onclick = () => {
  $('game-screen').classList.remove('active');
  $('title-screen').classList.add('active');
};

// ---------------- 自动存档 ----------------
async function saveAuto() { try { await API.save('auto'); } catch (e) { /* ignore */ } }

// ---------------- Toast ----------------
let toastTimer = null;
function toast(msg) {
  const t = $('toast');
  t.textContent = msg;
  t.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.add('hidden'), 2200);
}

// 全局暴露（onclick 内联需要）
window.doSave = doSave;
window.doLoad = doLoad;
