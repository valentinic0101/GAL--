/* 深雪 ~miyuki~ 前端 · 70 弹窗层：回想日志、世界状态、设置面板、存档 / 读档。
   依赖：00_core（$ / API / settings）、10_audio（音量联动）、50_flow（playFrames）。 */
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

// ---------------- 自动存档 ----------------
async function saveAuto() { try { await API.save('auto'); } catch (e) { /* ignore */ } }

