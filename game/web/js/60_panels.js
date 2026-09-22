/* 深雪 ~miyuki~ 前端 · 60 交互面板层：选项、自由输入与快捷回答、幕间自由行动、
   结局卡、场景标题卡、状态条。
   依赖：00_core（$ / API）、50_flow（playFrames）。 */
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

