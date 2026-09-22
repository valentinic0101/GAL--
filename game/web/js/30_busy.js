/* 深雪 ~miyuki~ 前端 · 30 请求节流层：LLM 响应期间的忙碌指示与重复触发防护。
   依赖：00_core 的 $ / toast（#llm-wait 元素懒取）。 */
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

