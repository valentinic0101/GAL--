/* 深雪 ~miyuki~ 前端 · 40 舞台层：背景切换与立绘布景（地面贴合/纵深/亮度匹配/接触投影）。
   版面数学的配置单一来源：tools/stage_config.json → web/gen/stage_meta.js。
   依赖：00_core 的 $；读取 window.STAGE_META / SPRITE_FEET / SPRITE_ASPECT / ASSET_MANIFEST。 */
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

