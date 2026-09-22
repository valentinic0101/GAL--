/* 深雪 ~miyuki~ 前端 · 20 特效层：飘雪注入（标题页与游戏画面共用同一份雪）。
   依赖：00_core 的 $ 与 settings.snow。 */
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

