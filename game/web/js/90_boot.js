/* 深雪 ~miyuki~ 前端 · 90 启动层：标题页绑定、请求去重包装、全局导出、开机副作用。
   必须最后加载——这里三件「运行期」的事都有顺序要求：
     1. 包装 advance / submitInput / doAct（被包装的函数在 50/60 层声明，此刻须已存在）；
     2. 把内联 onclick 用到的函数导出到 window（内联处理器只能看见全局对象，
        看不见全局词法环境，所以 const/let 声明的东西必须显式挂上去）；
     3. 标题页副作用：激活标题页、起标题曲、注入飘雪。
   依赖：以上全部。 */
'use strict';
spawnSnow(70);

const _origAdvance = advance;
advance = async function () {
  if (busyCount > 0) return;               // 防重复触发
  return guarded(async () => _origAdvance());
};
const _origSubmit = submitInput;
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

window.setSpeed = setSpeed; window.setAutoSec = setAutoSec; window.setSnow = setSnow;

$('btn-title').onclick = () => {
  $('game-screen').classList.remove('active');
  $('title-screen').classList.add('active');
};

// 全局暴露（onclick 内联需要）
window.doSave = doSave;
window.doLoad = doLoad;

