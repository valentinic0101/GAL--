/* 深雪 ~miyuki~ 前端 · 10 音频层：BGM 播放 / 淡入淡出 / 静音开关。
   依赖：00_core 的 $ 与 settings.vol。 */
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

