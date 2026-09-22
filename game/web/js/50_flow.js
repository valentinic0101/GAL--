/* 深雪 ~miyuki~ 前端 · 50 推进层：打字机、帧队列播放器、点击与键盘推进、自动模式。
   「一次 API 响应可能含多帧」的逐帧展示逻辑都在这里。
   依赖：00_core（$ / API / 全局状态）、40_stage（画面）、60_panels（交互帧落地）。 */
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

