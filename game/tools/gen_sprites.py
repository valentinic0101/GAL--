# -*- coding: utf-8 -*-
"""生成角色立绘 SVG（统一动漫赛璐璐扁平风格）+ UI 元素。"""
import os
import xml.dom.minidom

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'sprites')
UI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'ui')
os.makedirs(OUT, exist_ok=True)
os.makedirs(UI, exist_ok=True)

OL = '#2a2430'  # 统一描边色


def svg_doc(body, extra_defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 1000" '
            f'width="600" height="1000">\n<defs>\n{extra_defs}\n</defs>\n{body}\n</svg>')


def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    xml.dom.minidom.parseString(content)  # 校验
    print('saved', path)


# ============================================================ 深雪基础几何
MIYUKI_DEFS = f'''
<linearGradient id="hairG" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#241f2b"/><stop offset="0.45" stop-color="#3d3450"/>
  <stop offset="0.55" stop-color="#3d3450"/><stop offset="1" stop-color="#201b28"/>
</linearGradient>
<linearGradient id="kimonoG" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#33406b"/><stop offset="1" stop-color="#232c48"/>
</linearGradient>
<linearGradient id="apronG" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#f4f6f9"/><stop offset="1" stop-color="#dfe4ec"/>
</linearGradient>
<linearGradient id="skinG" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#f9f1e8"/><stop offset="1" stop-color="#efdfcf"/>
</linearGradient>
'''


def miyuki_hair_back(wind=False):
    if not wind:
        return f'''<g id="hair-back" stroke="{OL}" stroke-width="3">
  <path fill="url(#hairG)" d="M300 108 C 188 108 158 190 162 268 C 164 350 150 470 138 590
    C 130 680 140 760 158 800 L 214 800 C 196 700 198 560 208 470 L 392 470
    C 402 560 404 700 386 800 L 442 800 C 460 760 470 680 462 590
    C 450 470 436 350 438 268 C 442 190 412 108 300 108 Z"/>
  <path fill="none" stroke="#585070" stroke-width="7" opacity="0.75" stroke-linecap="round"
    d="M226 200 C 214 320 210 480 202 620"/>
  <path fill="none" stroke="#585070" stroke-width="7" opacity="0.75" stroke-linecap="round"
    d="M374 200 C 386 320 390 480 398 620"/>
</g>'''
    return f'''<g id="hair-back" stroke="{OL}" stroke-width="3">
  <path fill="url(#hairG)" d="M300 108 C 196 110 164 192 170 268 C 172 340 160 440 130 540
    C 96 650 60 720 36 780 L 96 800 C 130 720 150 640 166 560
    L 240 520 C 260 480 268 420 272 360 L 328 360 C 332 420 340 480 360 520
    L 434 560 C 450 640 470 720 504 800 L 564 780 C 540 720 504 650 470 540
    C 440 440 428 340 430 268 C 436 192 404 110 300 108 Z"/>
  <path fill="none" stroke="#6a6482" stroke-width="6" opacity="0.7" stroke-linecap="round"
    d="M232 210 C 200 330 170 470 130 620"/>
  <path fill="none" stroke="#6a6482" stroke-width="6" opacity="0.7" stroke-linecap="round"
    d="M368 210 C 400 330 430 470 470 620"/>
</g>'''


def miyuki_body(kimono='url(#kimonoG)', scarf=True, apron=True, skin='url(#skinG)', white=False):
    scarf_s = ''
    if scarf:
        scarf_s = f'''<g id="scarf" stroke="{OL}" stroke-width="3">
  <path fill="#efe7d9" d="M240 300 C 264 322 336 322 360 300 C 376 316 372 344 352 356
    C 330 342 270 342 248 356 C 228 344 224 316 240 300 Z"/>
  <path fill="#e2d7c4" d="M330 348 L 372 470 L 336 486 L 302 368 Z"/>
</g>'''
    apron_s = ''
    if apron:
        apron_s = f'''<path fill="url(#apronG)" stroke="{OL}" stroke-width="3"
      d="M258 360 L 342 360 L 366 640 L 348 900 L 252 900 L 234 640 Z"/>'''
    collar = '#eef1f5' if not white else '#dfe6ee'
    collar_in = '#b84850'
    return f'''<g id="body">
  <!-- 长裙 -->
  <path fill="{kimono}" stroke="{OL}" stroke-width="3"
    d="M224 420 C 200 560 192 740 206 920 L 394 920 C 408 740 400 560 376 420 Z"/>
  {apron_s}
  <!-- 足袋 -->
  <ellipse cx="272" cy="942" rx="22" ry="16" fill="#f2efe8" stroke="{OL}" stroke-width="2.5"/>
  <ellipse cx="328" cy="942" rx="22" ry="16" fill="#f2efe8" stroke="{OL}" stroke-width="2.5"/>
  <!-- 上身和服 -->
  <path fill="{kimono}" stroke="{OL}" stroke-width="3"
    d="M238 312 C 214 344 206 392 210 436 C 220 448 260 456 300 456
       C 340 456 380 448 390 436 C 394 392 386 344 362 312 Z"/>
  <!-- 衣领（左压右） -->
  <path fill="{collar}" stroke="{OL}" stroke-width="2.5" d="M268 306 L 300 372 L 332 306 L 318 300 L 300 336 L 282 300 Z"/>
  <path fill="{collar_in}" opacity="0.85" d="M275 303 L 300 356 L 325 303 L 319 301 L 300 342 L 281 301 Z"/>
  <!-- 左臂（观者左侧，微屈身前） -->
  <g id="arm-l">
    <path fill="{kimono}" stroke="{OL}" stroke-width="3"
      d="M222 330 C 196 356 186 408 194 456 C 200 492 216 512 238 520
         L 258 486 C 240 474 230 456 228 428 C 226 396 232 366 246 348 Z"/>
    <ellipse cx="248" cy="508" rx="20" ry="24" fill="{skin}" stroke="{OL}" stroke-width="2.5"/>
  </g>
  <!-- 右臂（自然下垂） -->
  <g id="arm-r">
    <path fill="{kimono}" stroke="{OL}" stroke-width="3"
      d="M378 330 C 404 356 414 408 408 460 C 402 506 388 540 368 556
         L 348 522 C 364 504 372 480 372 448 C 372 412 366 372 354 350 Z"/>
    <ellipse cx="356" cy="548" rx="19" ry="24" fill="{skin}" stroke="{OL}" stroke-width="2.5"/>
  </g>
  <!-- 腰带 -->
  <path fill="{'#1d2540' if not white else '#c9d4e4'}" stroke="{OL}" stroke-width="3"
    d="M216 424 L 384 424 L 380 462 L 220 462 Z"/>
  <path fill="{'#8fb6d8' if not white else '#aebfd4'}" opacity="0.5" d="M226 430 L 374 430 L 372 440 L 228 440 Z"/>
  {scarf_s}
</g>'''


def miyuki_body_wave():
    """微笑版：右臂抬起在胸前打招呼。"""
    return miyuki_body().replace('''<g id="arm-r">
    <path fill="url(#kimonoG)" stroke="''' + OL + '''" stroke-width="3"
      d="M378 330 C 404 356 414 408 408 460 C 402 506 388 540 368 556
         L 348 522 C 364 504 372 480 372 448 C 372 412 366 372 354 350 Z"/>
    <ellipse cx="356" cy="548" rx="19" ry="24" fill="url(#skinG)" stroke="''' + OL + '''" stroke-width="2.5"/>
  </g>''', '''<g id="arm-r-wave">
    <path fill="url(#kimonoG)" stroke="''' + OL + '''" stroke-width="3"
      d="M378 330 C 410 340 424 380 418 420 C 412 456 396 480 372 490
         L 352 458 C 370 448 380 430 378 408 C 376 384 370 362 356 350 Z"/>
    <ellipse cx="362" cy="484" rx="20" ry="23" fill="url(#skinG)" stroke="''' + OL + '''" stroke-width="2.5"/>
  </g>''')


def miyuki_face(skin='url(#skinG)'):
    return f'''<g id="face-base">
  <path d="M300 300 C 252 300 226 262 226 210 C 226 158 258 126 300 126
           C 342 126 374 158 374 210 C 374 262 348 300 300 300 Z"
        fill="{skin}" stroke="{OL}" stroke-width="3"/>
  <ellipse cx="228" cy="216" rx="10" ry="16" fill="{skin}" stroke="{OL}" stroke-width="2.5"/>
  <ellipse cx="372" cy="216" rx="10" ry="16" fill="{skin}" stroke="{OL}" stroke-width="2.5"/>
</g>'''


def miyuki_hair_front():
    """齐刘海（标志）+ 两侧长鬓。"""
    return f'''<g id="hair-front" stroke="{OL}" stroke-width="3">
  <path fill="url(#hairG)" d="M300 106 C 210 106 170 172 172 254
    C 174 214 190 186 216 170 C 244 152 268 148 300 148
    C 332 148 356 152 384 170 C 410 186 426 214 428 254
    C 430 172 390 106 300 106 Z"/>
  <path fill="url(#hairG)" d="M176 200 C 168 260 164 330 168 400
    C 170 430 178 452 190 462 L 210 452 C 198 420 194 380 196 336
    C 182 296 178 246 176 200 Z"/>
  <path fill="url(#hairG)" d="M424 200 C 432 260 436 330 432 400
    C 430 430 422 452 410 462 L 390 452 C 402 420 406 380 404 336
    C 418 296 422 246 424 200 Z"/>
  <path fill="none" stroke="#5c5478" stroke-width="5" opacity="0.8" stroke-linecap="round"
    d="M236 158 C 224 178 218 202 218 226"/>
  <path fill="none" stroke="#5c5478" stroke-width="5" opacity="0.8" stroke-linecap="round"
    d="M364 158 C 376 178 382 202 382 226"/>
  <!-- 发饰 -->
  <path fill="#9fc4e2" stroke="{OL}" stroke-width="2.5"
    d="M398 176 l 16 -12 l -2 20 l 18 8 l -18 8 l 2 20 l -16 -12 l -16 12 l 2 -20 l -18 -8 l 18 -8 l -2 -20 Z"/>
  <circle cx="398" cy="192" r="4" fill="#e8f2fa"/>
</g>'''


def eye_open(cx, cy, iris='#38303f', s=1.0, look=0):
    """睁眼：睫毛+虹膜+高光。look: -1 下垂 0 正视 1 半闭"""
    lid_top = cy - 22 * s + (4 * s if look > 0 else 0)
    iris_cy = cy + 2 * s + (3 * s if look < 0 else 0)
    return f'''<g>
  <path fill="#ffffff" d="M{cx-24*s} {cy+6*s} C {cx-22*s} {lid_top+6*s} {cx-12*s} {lid_top} {cx} {lid_top}
      C {cx+12*s} {lid_top} {cx+22*s} {lid_top+6*s} {cx+24*s} {cy+6*s}
      C {cx+20*s} {cy+16*s} {cx+10*s} {cy+20*s} {cx} {cy+20*s}
      C {cx-10*s} {cy+20*s} {cx-20*s} {cy+16*s} {cx-24*s} {cy+6*s} Z"/>
  <ellipse cx="{cx}" cy="{iris_cy}" rx="{11*s}" ry="{13*s if look>=0 else 10*s}" fill="{iris}"/>
  <circle cx="{cx-3.5*s}" cy="{iris_cy-4*s}" r="{4*s}" fill="#ffffff" opacity="0.95"/>
  <circle cx="{cx+3*s}" cy="{iris_cy+4*s}" r="{2*s}" fill="#ffffff" opacity="0.6"/>
  <path fill="none" stroke="{OL}" stroke-width="{4.5*s}" stroke-linecap="round"
    d="M{cx-24*s} {cy+5*s} C {cx-20*s} {lid_top+2*s} {cx-12*s} {lid_top-2*s} {cx} {lid_top-2*s}
       C {cx+12*s} {lid_top-2*s} {cx+20*s} {lid_top+2*s} {cx+24*s} {cy+5*s}"/>
  <path fill="none" stroke="{OL}" stroke-width="2" opacity="0.55" stroke-linecap="round"
    d="M{cx-14*s} {cy+19*s} C {cx-8*s} {cy+22*s} {cx+8*s} {cy+22*s} {cx+14*s} {cy+19*s}"/>
</g>'''


def eye_closed_happy(cx, cy, s=1.0):
    return f'''<g>
  <path fill="none" stroke="{OL}" stroke-width="{4.5*s}" stroke-linecap="round"
    d="M{cx-20*s} {cy+8*s} C {cx-14*s} {cy-8*s} {cx+14*s} {cy-8*s} {cx+20*s} {cy+8*s}"/>
  <path fill="none" stroke="#c98a92" stroke-width="2" opacity="0" d=""/>
</g>'''


def eye_sad(cx, cy, s=1.0):
    return f'''<g>
  <path fill="#ffffff" d="M{cx-22*s} {cy+4*s} C {cx-20*s} {cy-12*s} {cx-10*s} {cy-18*s} {cx} {cy-18*s}
      C {cx+10*s} {cy-18*s} {cx+20*s} {cy-12*s} {cx+22*s} {cy+4*s}
      C {cx+18*s} {cy+12*s} {cx+10*s} {cy+15*s} {cx} {cy+15*s}
      C {cx-10*s} {cy+15*s} {cx-18*s} {cy+12*s} {cx-22*s} {cy+4*s} Z"/>
  <ellipse cx="{cx}" cy="{cy+6*s}" rx="9*s" ry="9.5*s" fill="#38303f"/>
  <circle cx="{cx-3*s}" cy="{cy+2*s}" r="3.4*s" fill="#ffffff" opacity="0.95"/>
  <path fill="none" stroke="{OL}" stroke-width="4.5*s" stroke-linecap="round"
    d="M{cx-22*s} {cy+3*s} C {cx-18*s} {cy-11*s} {cx-10*s} {cy-16*s} {cx} {cy-16*s}
       C {cx+10*s} {cy-16*s} {cx+18*s} {cy-11*s} {cx+22*s} {cy+3*s}"/>
  <path fill="none" stroke="{OL}" stroke-width="2.2*s" opacity="0.7" stroke-linecap="round"
    d="M{cx-10*s} {cy+16*s} L {cx-16*s} {cy+21*s}"/>
</g>'''


def eye_wide(cx, cy, s=1.0):
    return f'''<g>
  <path fill="#ffffff" d="M{cx-25*s} {cy} C {cx-23*s} {cy-20*s} {cx-12*s} {cy-27*s} {cx} {cy-27*s}
      C {cx+12*s} {cy-27*s} {cx+23*s} {cy-20*s} {cx+25*s} {cy}
      C {cx+21*s} {cy+15*s} {cx+11*s} {cy+21*s} {cx} {cy+21*s}
      C {cx-11*s} {cy+21*s} {cx-21*s} {cy+15*s} {cx-25*s} {cy} Z"/>
  <ellipse cx="{cx}" cy="{cy-1*s}" rx="11.5*s" ry="14*s" fill="#38303f"/>
  <circle cx="{cx-4*s}" cy="{cy-6*s}" r="4.4*s" fill="#ffffff" opacity="0.95"/>
  <circle cx="{cx+3.5*s}" cy="{cy+4*s}" r="2.2*s" fill="#ffffff" opacity="0.6"/>
  <path fill="none" stroke="{OL}" stroke-width="4.5*s" stroke-linecap="round"
    d="M{cx-25*s} {cy-1*s} C {cx-23*s} {cy-19*s} {cx-12*s} {cy-26*s} {cx} {cy-26*s}
       C {cx+12*s} {cy-26*s} {cx+23*s} {cy-19*s} {cx+25*s} {cy-1*s}"/>
</g>'''


def miyuki_features(expr):
    ex_l, ex_r = 264, 336
    ey = 218
    if expr == 'normal':
        eyes = eye_open(ex_l, ey) + eye_open(ex_r, ey)
        brows = f'''<path fill="none" stroke="#4a3f42" stroke-width="4" stroke-linecap="round"
          d="M240 184 C 250 176 262 174 272 178"/>
        <path fill="none" stroke="#4a3f42" stroke-width="4" stroke-linecap="round"
          d="M328 178 C 338 174 350 176 360 184"/>'''
        mouth = f'''<path fill="none" stroke="{OL}" stroke-width="3.4" stroke-linecap="round"
          d="M286 262 C 292 268 308 268 314 262"/>'''
        blush = '<ellipse cx="248" cy="248" rx="13" ry="7" fill="#e8a8ac" opacity="0.35"/><ellipse cx="352" cy="248" rx="13" ry="7" fill="#e8a8ac" opacity="0.35"/>'
        nose = f'<path fill="none" stroke="{OL}" stroke-width="2.2" opacity="0.6" stroke-linecap="round" d="M300 240 l 3 5"/>'
    elif expr == 'smile':
        eyes = eye_closed_happy(ex_l, ey) + eye_closed_happy(ex_r, ey)
        brows = f'''<path fill="none" stroke="#4a3f42" stroke-width="4" stroke-linecap="round"
          d="M240 182 C 250 174 262 172 272 176"/>
        <path fill="none" stroke="#4a3f42" stroke-width="4" stroke-linecap="round"
          d="M328 176 C 338 172 350 174 360 182"/>'''
        mouth = f'''<path fill="#8c5560" stroke="{OL}" stroke-width="3" stroke-linejoin="round"
          d="M282 258 C 290 272 310 272 318 258 C 308 264 292 264 282 258 Z"/>'''
        blush = '<ellipse cx="246" cy="246" rx="14" ry="7.5" fill="#e8a0a6" opacity="0.5"/><ellipse cx="354" cy="246" rx="14" ry="7.5" fill="#e8a0a6" opacity="0.5"/>'
        nose = f'<path fill="none" stroke="{OL}" stroke-width="2.2" opacity="0.6" stroke-linecap="round" d="M300 240 l 3 5"/>'
    elif expr == 'sad':
        eyes = eye_sad(ex_l, ey + 4) + eye_sad(ex_r, ey + 4)
        brows = f'''<path fill="none" stroke="#4a3f42" stroke-width="4" stroke-linecap="round"
          d="M242 186 C 252 182 262 184 272 190"/>
        <path fill="none" stroke="#4a3f42" stroke-width="4" stroke-linecap="round"
          d="M328 190 C 338 184 348 182 358 186"/>'''
        mouth = f'''<path fill="none" stroke="{OL}" stroke-width="3.2" stroke-linecap="round"
          d="M288 266 C 294 262 306 262 312 266"/>'''
        blush = ''
        nose = f'<path fill="none" stroke="{OL}" stroke-width="2.2" opacity="0.6" stroke-linecap="round" d="M300 242 l 3 5"/>'
    else:  # surprise
        eyes = eye_wide(ex_l, ey - 2) + eye_wide(ex_r, ey - 2)
        brows = f'''<path fill="none" stroke="#4a3f42" stroke-width="4" stroke-linecap="round"
          d="M240 176 C 250 168 262 166 272 170"/>
        <path fill="none" stroke="#4a3f42" stroke-width="4" stroke-linecap="round"
          d="M328 170 C 338 166 350 168 360 176"/>'''
        mouth = f'''<ellipse cx="300" cy="264" rx="9" ry="12" fill="#8c5560" stroke="{OL}" stroke-width="3"/>'''
        blush = ''
        nose = f'<path fill="none" stroke="{OL}" stroke-width="2.2" opacity="0.6" stroke-linecap="round" d="M300 240 l 3 5"/>'
    return f'''<g id="features">{nose if False else ''}{eyes}{brows}{mouth}{blush}
  <path fill="none" stroke="{OL}" stroke-width="2.2" opacity="0.6" stroke-linecap="round" d="M300 240 l 3 5"/>
</g>'''


def miyuki_white_features():
    ex_l, ex_r = 264, 336
    ey = 218
    eyes = f'''<g>
  <path fill="#ffffff" d="M{ex_l-23} {ey} C {ex_l-21} {ey-16} {ex_l-11} {ey-22} {ex_l} {ey-22}
      C {ex_l+11} {ey-22} {ex_l+21} {ey-16} {ex_l+23} {ey}
      C {ex_l+19} {ey+11} {ex_l+10} {ey+15} {ex_l} {ey+15}
      C {ex_l-10} {ey+15} {ex_l-19} {ey+11} {ex_l-23} {ey} Z"/>
  <ellipse cx="{ex_l}" cy="{ey+3}" rx="10" ry="10" fill="#2e2836"/>
  <circle cx="{ex_l-3}" cy="{ey-1}" r="3.6" fill="#ffffff" opacity="0.9"/>
  <path fill="none" stroke="{OL}" stroke-width="4.5" stroke-linecap="round"
    d="M{ex_l-23} {ey-1} C {ex_l-19} {ey-15} {ex_l-11} {ey-20} {ex_l} {ey-20}
       C {ex_l+11} {ey-20} {ex_l+19} {ey-15} {ex_l+23} {ey-1}"/>
</g>
<g>
  <path fill="#ffffff" d="M{ex_r-23} {ey} C {ex_r-21} {ey-16} {ex_r-11} {ey-22} {ex_r} {ey-22}
      C {ex_r+11} {ey-22} {ex_r+21} {ey-16} {ex_r+23} {ey}
      C {ex_r+19} {ey+11} {ex_r+10} {ey+15} {ex_r} {ey+15}
      C {ex_r-10} {ey+15} {ex_r-19} {ey+11} {ex_r-23} {ey} Z"/>
  <ellipse cx="{ex_r}" cy="{ey+3}" rx="10" ry="10" fill="#2e2836"/>
  <circle cx="{ex_r-3}" cy="{ey-1}" r="3.6" fill="#ffffff" opacity="0.9"/>
  <path fill="none" stroke="{OL}" stroke-width="4.5" stroke-linecap="round"
    d="M{ex_r-23} {ey-1} C {ex_r-19} {ey-15} {ex_r-11} {ey-20} {ex_r} {ey-20}
       C {ex_r+11} {ey-20} {ex_r+19} {ey-15} {ex_r+23} {ey-1}"/>
</g>'''
    brows = f'''<path fill="none" stroke="#4a3f42" stroke-width="4" stroke-linecap="round" d="M242 184 C 252 179 262 181 272 187"/>
<path fill="none" stroke="#4a3f42" stroke-width="4" stroke-linecap="round" d="M328 187 C 338 181 348 179 358 184"/>'''
    mouth = f'''<path fill="#b8505e" stroke="{OL}" stroke-width="3" d="M290 260 C 296 268 304 268 310 260 C 304 266 296 266 290 260 Z"/>'''
    return f'<g id="features">{eyes}{brows}{mouth}</g>'


def build_miyuki(expr, white=False):
    if white:
        body = miyuki_body(kimono='#f2f5fa', scarf=False, apron=False, skin='#f6efe8', white=True)
        hair_back = miyuki_hair_back(wind=True)
        features = miyuki_white_features()
        # 白和服红腰带点缀
        body = body.replace('fill=\'#1d2540\'', 'fill=\'#b8505e\'')
        glow = '<ellipse cx="300" cy="500" rx="210" ry="380" fill="#ffffff" opacity="0.10"/>'
    else:
        body = miyuki_body_wave() if expr == 'smile' else miyuki_body()
        hair_back = miyuki_hair_back()
        features = miyuki_features(expr)
        glow = ''
    return svg_doc(
        hair_back + body + miyuki_face() + miyuki_hair_front() + features + glow,
        MIYUKI_DEFS)


# ============================================================ 修二
SHUUJI_DEFS = f'''
<linearGradient id="hairB" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#211d26"/><stop offset="0.5" stop-color="#37313f"/><stop offset="1" stop-color="#1d1a22"/>
</linearGradient>
<linearGradient id="coatChild" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#96764e"/><stop offset="1" stop-color="#7a5f3e"/>
</linearGradient>
<linearGradient id="coatTeen" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#5e646e"/><stop offset="1" stop-color="#484d57"/>
</linearGradient>
<linearGradient id="skinS" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#f7ecdc"/><stop offset="1" stop-color="#ecdcc6"/>
</linearGradient>
'''


def shuuji_face(cy, rx, ry, skin='url(#skinS)'):
    cx = 300
    return f'''<g id="face-base">
  <path d="M{cx} {cy+ry} C {cx-rx+6} {cy+ry} {cx-rx} {cy-ry*0.25} {cx-rx} {cy-ry*0.55}
    C {cx-rx} {cy-ry-8} {cx-rx//2} {cy-ry-14} {cx} {cy-ry-14}
    C {cx+rx//2} {cy-ry-14} {cx+rx} {cy-ry-8} {cx+rx} {cy-ry*0.55}
    C {cx+rx} {cy-ry*0.25} {cx+rx-6} {cy+ry} {cx} {cy+ry} Z"
    fill="{skin}" stroke="{OL}" stroke-width="3"/>
  <ellipse cx="{cx-rx+2}" cy="{cy+6}" rx="8" ry="13" fill="{skin}" stroke="{OL}" stroke-width="2.5"/>
  <ellipse cx="{cx+rx-2}" cy="{cy+6}" rx="8" ry="13" fill="{skin}" stroke="{OL}" stroke-width="2.5"/>
</g>'''


def shuuji_hair(cy, rx, ry):
    """黑色短发微乱。"""
    cx = 300
    top = cy - ry - 12
    return f'''<g id="hair-front" stroke="{OL}" stroke-width="3">
  <path fill="url(#hairB)" d="M{cx-rx-4} {cy-ry*0.4} C {cx-rx-6} {top+20} {cx-rx+10} {top} {cx-30} {top-6}
    L {cx} {top-16} L {cx+34} {top-4} C {cx+rx-8} {top+4} {cx+rx+6} {top+26} {cx+rx+4} {cy-ry*0.4}
    C {cx+rx} {cy-ry*0.7} {cx+rx-14} {cy-ry*0.95} {cx} {cy-ry*0.95}
    C {cx-rx+14} {cy-ry*0.95} {cx-rx} {cy-ry*0.7} {cx-rx-4} {cy-ry*0.4} Z"/>
  <path fill="url(#hairB)" d="M{cx-rx-2} {cy-ry*0.5} C {cx-rx-10} {cy-6} {cx-rx-4} {cy+26} {cx-rx+10} {cy+30}
    L {cx-rx+16} {cy-8} Z"/>
  <path fill="url(#hairB)" d="M{cx+rx+2} {cy-ry*0.5} C {cx+rx+10} {cy-6} {cx+rx+4} {cy+26} {cx+rx-10} {cy+30}
    L {cx+rx-16} {cy-8} Z"/>
  <path fill="none" stroke="#4e4658" stroke-width="4" opacity="0.8" stroke-linecap="round"
    d="M{cx-38} {top+8} C {cx-30} {top+2} {cx-18} {top} {cx-10} {top+4}"/>
  <path fill="none" stroke="#4e4658" stroke-width="4" opacity="0.8" stroke-linecap="round"
    d="M{cx+14} {top+2} C {cx+24} {top-2} {cx+36} {top+2} {cx+44} {top+10}"/>
</g>'''


def boy_eye(cx, cy, s=1.0, mood='grumpy'):
    """修二的眼：grumpy 别扭 / calm 平实。"""
    lid = cy - 16 * s if mood == 'grumpy' else cy - 18 * s
    return f'''<g>
  <path fill="#ffffff" d="M{cx-17*s} {cy+4*s} C {cx-16*s} {lid+4*s} {cx-9*s} {lid} {cx} {lid}
      C {cx+9*s} {lid} {cx+16*s} {lid+4*s} {cx+17*s} {cy+4*s}
      C {cx+14*s} {cy+12*s} {cx+8*s} {cy+15*s} {cx} {cy+15*s}
      C {cx-8*s} {cy+15*s} {cx-14*s} {cy+12*s} {cx-17*s} {cy+4*s} Z"/>
  <ellipse cx="{cx}" cy="{cy+2*s}" rx="8*s" ry="9.5*s" fill="#3a3242"/>
  <circle cx="{cx-2.5*s}" cy="{cy-2*s}" r="3*s" fill="#fff" opacity="0.95"/>
  <path fill="none" stroke="{OL}" stroke-width="4*s" stroke-linecap="round"
    d="M{cx-17*s} {cy+3*s} C {cx-14*s} {lid+1*s} {cx-9*s} {lid-2*s} {cx} {lid-2*s}
       C {cx+9*s} {lid-2*s} {cx+14*s} {lid+1*s} {cx+17*s} {cy+3*s}"/>
</g>'''


def shuuji_child():
    cy, rx, ry = 322, 58, 66
    ex_l, ex_r, ey = 272, 328, cy + 2
    eyes = boy_eye(ex_l, ey) + boy_eye(ex_r, ey)
    brows = f'''<path fill="none" stroke="#3c333a" stroke-width="4" stroke-linecap="round"
      d="M254 {ey-26} C 262 {ey-31} 272 {ey-30} 280 {ey-26}"/>
    <path fill="none" stroke="#3c333a" stroke-width="4" stroke-linecap="round"
      d="M320 {ey-26} C 328 {ey-30} 338 {ey-31} 346 {ey-26}"/>'''
    mouth = f'''<path fill="none" stroke="{OL}" stroke-width="3.2" stroke-linecap="round"
      d="M286 {cy+40} C 293 {cy+36} 307 {cy+36} 314 {cy+40}"/>'''
    blush = '<ellipse cx="252" cy="342" rx="11" ry="6" fill="#e8a49c" opacity="0.4"/><ellipse cx="348" cy="342" rx="11" ry="6" fill="#e8a49c" opacity="0.4"/>'
    features = f'<g id="features">{eyes}{brows}{mouth}{blush}</g>'
    body = f'''<g id="body">
  <!-- 腿与雪靴 -->
  <path fill="#3d3a44" stroke="{OL}" stroke-width="3" d="M262 800 L 262 930 L 292 930 L 296 800 Z"/>
  <path fill="#3d3a44" stroke="{OL}" stroke-width="3" d="M338 800 L 338 930 L 308 930 L 304 800 Z"/>
  <path fill="#4a3d30" stroke="{OL}" stroke-width="3" d="M256 928 L 298 928 L 302 958 L 250 958 Z"/>
  <path fill="#4a3d30" stroke="{OL}" stroke-width="3" d="M344 928 L 302 928 L 298 958 L 350 958 Z"/>
  <!-- 棉外套 -->
  <path fill="url(#coatChild)" stroke="{OL}" stroke-width="3"
    d="M244 392 C 220 424 214 500 222 560 C 226 620 240 700 252 810
       L 348 810 C 360 700 374 620 378 560 C 386 500 380 424 356 392
       C 330 376 270 376 244 392 Z"/>
  <path fill="#6b5436" opacity="0.5" d="M252 560 L 348 560 L 350 596 L 250 596 Z"/>
  <circle cx="300" cy="470" r="5" fill="#3a2f22"/><circle cx="300" cy="540" r="5" fill="#3a2f22"/>
  <circle cx="300" cy="610" r="5" fill="#3a2f22"/>
  <!-- 口袋 -->
  <path fill="none" stroke="{OL}" stroke-width="2.5" d="M252 640 L 284 640 L 280 688 L 254 688 Z"/>
  <path fill="none" stroke="{OL}" stroke-width="2.5" d="M348 640 L 316 640 L 320 688 L 346 688 Z"/>
  <!-- 左臂（插兜别扭状） -->
  <path fill="url(#coatChild)" stroke="{OL}" stroke-width="3"
    d="M230 408 C 206 440 202 500 214 550 C 220 576 232 592 248 598
       L 262 560 C 250 548 244 528 244 500 C 244 462 250 430 262 412 Z"/>
  <!-- 右臂微握拳 -->
  <path fill="url(#coatChild)" stroke="{OL}" stroke-width="3"
    d="M370 408 C 394 440 398 500 388 552 C 382 580 372 596 356 602
       L 344 566 C 356 552 362 532 362 502 C 362 464 356 432 346 414 Z"/>
  <circle cx="352" cy="604" r="16" fill="url(#skinS)" stroke="{OL}" stroke-width="2.5"/>
  <!-- 围巾 -->
  <g id="scarf">
    <path fill="#d8a24a" stroke="{OL}" stroke-width="3" d="M248 386 C 270 404 330 404 352 386
      C 364 398 362 420 346 430 C 326 420 274 420 254 430 C 238 420 236 398 248 386 Z"/>
    <path fill="#c8923e" stroke="{OL}" stroke-width="3" d="M322 424 L 352 520 L 322 530 L 296 440 Z"/>
  </g>
</g>'''
    return svg_doc(body + shuuji_face(cy, rx, ry) + shuuji_hair(cy, rx, ry) + features, SHUUJI_DEFS)


def shuuji_teen():
    cy, rx, ry = 250, 62, 70
    ex_l, ex_r, ey = 272, 328, cy + 4
    eyes = boy_eye(ex_l, ey, 1.05, 'calm') + boy_eye(ex_r, ey, 1.05, 'calm')
    brows = f'''<path fill="none" stroke="#3c333a" stroke-width="4" stroke-linecap="round"
      d="M254 {ey-28} C 262 {ey-32} 274 {ey-32} 282 {ey-29}"/>
    <path fill="none" stroke="#3c333a" stroke-width="4" stroke-linecap="round"
      d="M318 {ey-29} C 326 {ey-32} 338 {ey-32} 346 {ey-28}"/>'''
    mouth = f'''<path fill="none" stroke="{OL}" stroke-width="3" stroke-linecap="round"
      d="M288 {cy+42} C 295 {cy+39} 305 {cy+39} 312 {cy+42}"/>'''
    ears_red = '<ellipse cx="240" cy="260" rx="9" ry="13" fill="#e89a92" opacity="0.55"/><ellipse cx="360" cy="260" rx="9" ry="13" fill="#e89a92" opacity="0.55"/>'
    features = f'<g id="features">{eyes}{brows}{mouth}{ears_red}</g>'
    body = f'''<g id="body">
  <!-- 长裤与靴 -->
  <path fill="#3a3f4a" stroke="{OL}" stroke-width="3" d="M266 780 L 262 930 L 294 930 L 298 780 Z"/>
  <path fill="#3a3f4a" stroke="{OL}" stroke-width="3" d="M334 780 L 338 930 L 306 930 L 302 780 Z"/>
  <path fill="#2f2a26" stroke="{OL}" stroke-width="3" d="M258 928 L 298 928 L 302 956 L 252 956 Z"/>
  <path fill="#2f2a26" stroke="{OL}" stroke-width="3" d="M342 928 L 302 928 L 298 956 L 348 956 Z"/>
  <!-- 学生大衣 -->
  <path fill="url(#coatTeen)" stroke="{OL}" stroke-width="3"
    d="M240 340 C 216 376 208 460 216 530 C 222 600 236 700 248 790
       L 352 790 C 364 700 378 600 384 530 C 392 460 384 376 360 340
       C 332 322 268 322 240 340 Z"/>
  <path fill="#3f434d" d="M240 340 C 260 330 280 326 300 326 L 300 790 L 248 790
    C 236 700 222 600 216 530 C 208 460 216 376 240 340 Z" opacity="0.5"/>
  <!-- 大衣领 -->
  <path fill="#454a55" stroke="{OL}" stroke-width="3" d="M252 336 L 300 402 L 348 336 L 332 328 L 300 376 L 268 328 Z"/>
  <circle cx="304" cy="470" r="6" fill="#2b2e36"/><circle cx="304" cy="550" r="6" fill="#2b2e36"/>
  <circle cx="304" cy="630" r="6" fill="#2b2e36"/>
  <!-- 左臂自然垂 -->
  <path fill="url(#coatTeen)" stroke="{OL}" stroke-width="3"
    d="M226 356 C 202 392 198 470 210 540 C 216 576 228 600 246 608
       L 260 566 C 248 550 242 526 242 494 C 242 450 248 408 262 380 Z"/>
  <circle cx="256" cy="610" r="15" fill="url(#skinS)" stroke="{OL}" stroke-width="2.5"/>
  <!-- 右臂（抓书包带） -->
  <path fill="url(#coatTeen)" stroke="{OL}" stroke-width="3"
    d="M374 356 C 398 392 402 470 392 544 C 386 578 376 600 358 608
       L 346 566 C 358 552 364 530 364 498 C 364 454 358 410 348 382 Z"/>
  <circle cx="350" cy="610" r="15" fill="url(#skinS)" stroke="{OL}" stroke-width="2.5"/>
  <!-- 围巾（暗红） -->
  <g id="scarf">
    <path fill="#a04848" stroke="{OL}" stroke-width="3" d="M250 330 C 272 350 328 350 350 330
      C 362 342 360 364 344 374 C 324 364 276 364 256 374 C 240 364 238 342 250 330 Z"/>
    <path fill="#8e3d3d" stroke="{OL}" stroke-width="3" d="M326 368 L 356 470 L 328 480 L 300 384 Z"/>
  </g>
</g>'''
    return svg_doc(body + shuuji_face(cy, rx, ry) + shuuji_hair(cy, rx, ry) + features, SHUUJI_DEFS)


# ============================================================ 鸟羽老人
def toba():
    cx, cy, rx, ry = 340, 268, 56, 62
    face = f'''<g id="face-base">
  <path d="M{cx} {cy+ry} C {cx-rx+4} {cy+ry-6} {cx-rx} {cy} {cx-rx} {cy-ry*0.5}
    C {cx-rx} {cy-ry-16} {cx-rx//2} {cy-ry-22} {cx} {cy-ry-22}
    C {cx+rx//2} {cy-ry-22} {cx+rx} {cy-ry-16} {cx+rx} {cy-ry*0.5}
    C {cx+rx} {cy} {cx+rx-4} {cy+ry-6} {cx} {cy+ry} Z"
    fill="#e8d8bc" stroke="{OL}" stroke-width="3"/>
  <!-- 皱纹 -->
  <path fill="none" stroke="{OL}" stroke-width="2" opacity="0.5" d="M{cx-30} {cy-18} C {cx-10} {cy-24} {cx+10} {cy-24} {cx+30} {cy-18}"/>
  <path fill="none" stroke="{OL}" stroke-width="2" opacity="0.5" d="M{cx-26} {cy+26} C {cx-10} {cy+30} {cx+10} {cy+30} {cx+26} {cy+26}"/>
  <path fill="none" stroke="{OL}" stroke-width="2" opacity="0.5" d="M{cx-rx+14} {cy-8} L {cx-rx+26} {cy-4}"/>
  <!-- 左眼（独眼：右眼戴罩） -->
  <path fill="none" stroke="{OL}" stroke-width="3.6" stroke-linecap="round" d="M{cx-34} {cy} C {cx-28} {cy-6} {cx-18} {cy-6} {cx-12} {cy}"/>
  <path fill="none" stroke="{OL}" stroke-width="2.4" stroke-linecap="round" d="M{cx-30} {cy+8} C {cx-24} {cy+11} {cx-18} {cy+11} {cx-14} {cy+8}"/>
  <!-- 眼罩 -->
  <path fill="#1e1a20" stroke="{OL}" stroke-width="2.5" d="M{cx+8} {cy-12} C {cx+22} {cy-16} {cx+36} {cy-14} {cx+42} {cy-6}
    C {cx+44} {cy+4} {cx+38} {cy+12} {cx+24} {cy+12} C {cx+12} {cy+12} {cx+6} {cy+4} {cx+8} {cy-12} Z"/>
  <path fill="none" stroke="{OL}" stroke-width="3" d="M{cx-rx+6} {cy-16} C {cx-20} {cy-30} {cx+20} {cy-32} {cx+rx-4} {cy-14}"/>
  <!-- 嘴（抿）与须 -->
  <path fill="none" stroke="{OL}" stroke-width="3" stroke-linecap="round" d="M{cx-12} {cy+40} C {cx-4} {cy+44} {cx+4} {cy+44} {cx+12} {cy+40}"/>
  <path fill="#d8d2c4" d="M{cx-24} {cy+34} C {cx-12} {cy+52} {cx+12} {cy+52} {cx+24} {cy+34}
    C {cx+16} {cy+58} {cx-16} {cy+58} {cx-24} {cy+34} Z" stroke="{OL}" stroke-width="2"/>
</g>'''
    hair = f'''<g id="hair" stroke="{OL}" stroke-width="3">
  <path fill="#d8d4cc" d="M{cx-rx} {cy-ry*0.5} C {cx-rx-4} {cy-ry-8} {cx-20} {cy-ry-20} {cx} {cy-ry-20}
    C {cx+20} {cy-ry-20} {cx+rx+4} {cy-ry-8} {cx+rx} {cy-ry*0.5}
    C {cx+rx-8} {cy-ry-2} {cx-rx+8} {cy-ry-2} {cx-rx} {cy-ry*0.5} Z" opacity="0.9"/>
  <circle cx="{cx}" cy="{cy-ry-22}" r="12" fill="#cfcac0"/>
  <path fill="#d8d4cc" d="M{cx-rx-2} {cy-ry*0.4} C {cx-rx-10} {cy+30} {cx-rx-2} {cy+70} {cx-rx+16} {cy+80}
    L {cx-rx+18} {cy+30} Z"/>
  <path fill="#d8d4cc" d="M{cx+rx+2} {cy-ry*0.4} C {cx+rx+10} {cy+30} {cx+rx+2} {cy+70} {cx+rx-16} {cy+80}
    L {cx+rx-18} {cy+30} Z"/>
</g>'''
    body = f'''<g id="body">
  <!-- 佝偻背形和服 -->
  <path fill="#6a5c4c" stroke="{OL}" stroke-width="3"
    d="M286 350 C 240 380 222 450 226 520 C 230 600 240 700 250 800
       L 420 800 C 430 700 440 600 444 520 C 448 450 430 380 384 350
       C 350 332 316 332 286 350 Z"/>
  <path fill="#5a4e40" opacity="0.6" d="M250 800 C 240 700 230 600 226 520 C 222 450 240 380 286 350
    C 300 342 316 337 332 336 L 336 800 Z"/>
  <path fill="#e5ded2" stroke="{OL}" stroke-width="2.5" d="M316 344 L 340 400 L 366 344 L 352 338 L 340 368 L 328 338 Z"/>
  <!-- 拄杖右臂 -->
  <path fill="#6a5c4c" stroke="{OL}" stroke-width="3"
    d="M400 372 C 428 392 436 440 430 480 C 424 516 412 540 396 552
       L 380 516 C 394 502 400 482 398 452 C 396 420 392 392 384 378 Z"/>
  <circle cx="392" cy="552" r="14" fill="#e8d8bc" stroke="{OL}" stroke-width="2.5"/>
  <path fill="none" stroke="#4a3a28" stroke-width="10" stroke-linecap="round" d="M420 320 L 452 950"/>
  <!-- 左臂掩袖 -->
  <path fill="#6a5c4c" stroke="{OL}" stroke-width="3"
    d="M270 372 C 244 392 236 440 242 482 C 248 518 260 542 278 554
       L 292 518 C 278 504 272 484 274 454 C 276 422 280 392 288 378 Z"/>
  <!-- 下摆与足 -->
  <path fill="#4e4336" stroke="{OL}" stroke-width="3" d="M250 790 L 420 790 L 424 920 L 246 920 Z"/>
  <rect x="300" y="918" width="30" height="14" fill="#8a7458" stroke="{OL}" stroke-width="2.5"/>
  <rect x="352" y="918" width="30" height="14" fill="#8a7458" stroke="{OL}" stroke-width="2.5"/>
  <rect x="298" y="930" width="8" height="14" fill="#5a4a36"/>
  <rect x="376" y="930" width="8" height="14" fill="#5a4a36"/>
</g>'''
    defs = '<linearGradient id="kG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6a5c4c"/><stop offset="1" stop-color="#5a4e40"/></linearGradient>'
    return svg_doc(body + face + hair, defs)


# ============================================================ 亲戚·叔父
def relative_man():
    cx, cy, rx, ry = 300, 236, 68, 74
    face = f'''<g id="face-base">
  <path d="M{cx} {cy+ry} C {cx-rx+8} {cy+ry-4} {cx-rx} {cy+10} {cx-rx} {cy-ry*0.55}
    C {cx-rx} {cy-ry-10} {cx-rx//2} {cy-ry-16} {cx} {cy-ry-16}
    C {cx+rx//2} {cy-ry-16} {cx+rx} {cy-ry-10} {cx+rx} {cy-ry*0.55}
    C {cx+rx} {cy+10} {cx+rx-8} {cy+ry-4} {cx} {cy+ry} Z"
    fill="#f0dfc8" stroke="{OL}" stroke-width="3"/>
  <!-- 八字眉（为难） -->
  <path fill="none" stroke="#4a4038" stroke-width="4.5" stroke-linecap="round"
    d="M{cx-44} {cy-26} C {cx-34} {cy-32} {cx-24} {cy-30} {cx-16} {cy-24}"/>
  <path fill="none" stroke="#4a4038" stroke-width="4.5" stroke-linecap="round"
    d="M{cx+16} {cy-24} C {cx+24} {cy-30} {cx+34} {cy-32} {cx+44} {cy-26}"/>
  <!-- 眼（小，尴尬） -->
  <path fill="none" stroke="{OL}" stroke-width="3.6" stroke-linecap="round" d="M{cx-36} {cy} C {cx-30} {cy-5} {cx-22} {cy-5} {cx-16} {cy}"/>
  <path fill="none" stroke="{OL}" stroke-width="3.6" stroke-linecap="round" d="M{cx+16} {cy} C {cx+22} {cy-5} {cx+30} {cy-5} {cx+36} {cy}"/>
  <!-- 圆眼镜 -->
  <circle cx="{cx-26}" cy="{cy}" r="17" fill="none" stroke="{OL}" stroke-width="3"/>
  <circle cx="{cx+26}" cy="{cy}" r="17" fill="none" stroke="{OL}" stroke-width="3"/>
  <path fill="none" stroke="{OL}" stroke-width="3" d="M{cx-9} {cy-2} L {cx+9} {cy-2}"/>
  <!-- 嘴（向下撇） -->
  <path fill="none" stroke="{OL}" stroke-width="3.4" stroke-linecap="round"
    d="M{cx-14} {cy+46} C {cx-6} {cy+41} {cx+6} {cy+41} {cx+14} {cy+46}"/>
  <!-- 鼻 -->
  <path fill="none" stroke="{OL}" stroke-width="2.6" opacity="0.7" stroke-linecap="round" d="M{cx} {cy+18} l 4 8 l -8 2"/>
  <!-- 冷汗 -->
  <path fill="#bfe0ee" stroke="{OL}" stroke-width="1.6" d="M{cx+rx-16} {cy-24} C {cx+rx-20} {cy-14} {cx+rx-14} {cy-10} {cx+rx-12} {cy-18} C {cx+rx-12} {cy-24} {cx+rx-16} {cy-28} {cx+rx-16} {cy-24} Z"/>
</g>'''
    hair = f'''<g id="hair" stroke="{OL}" stroke-width="3">
  <path fill="#4e463e" d="M{cx-rx+2} {cy-ry*0.5} C {cx-rx-2} {cy-ry-14} {cx-24} {cy-ry-22} {cx} {cy-ry-22}
    C {cx+24} {cy-ry-22} {cx+rx+2} {cy-ry-14} {cx+rx-2} {cy-ry*0.5}
    C {cx+rx-14} {cy-ry-6} {cx-rx+14} {cy-ry-6} {cx-rx+2} {cy-ry*0.5} Z" opacity="0.85"/>
  <!-- 地中海：两侧发 -->
  <path fill="#4e463e" d="M{cx-rx} {cy-ry*0.45} C {cx-rx-6} {cy-10} {cx-rx} {cy+26} {cx-rx+14} {cy+32}
    L {cx-rx+16} {cy-20} Z"/>
  <path fill="#4e463e" d="M{cx+rx} {cy-ry*0.45} C {cx+rx+6} {cy-10} {cx+rx} {cy+26} {cx+rx-14} {cy+32}
    L {cx+rx-16} {cy-20} Z"/>
</g>'''
    body = f'''<g id="body">
  <!-- 发福身躯：毛衣+背心 -->
  <path fill="#5c7050" stroke="{OL}" stroke-width="3"
    d="M232 330 C 200 360 188 430 196 500 C 204 570 216 650 226 720
       L 374 720 C 384 650 396 570 404 500 C 412 430 400 360 368 330
       C 336 310 264 310 232 330 Z"/>
  <!-- 背心 -->
  <path fill="#3e4436" opacity="0.9" d="M244 336 L 268 322 L 268 716 L 236 716 L 230 520
    C 224 452 234 376 244 336 Z"/>
  <path fill="#3e4436" opacity="0.9" d="M356 336 L 332 322 L 332 716 L 364 716 L 370 520
    C 376 452 366 376 356 336 Z"/>
  <!-- 衬衫领 -->
  <path fill="#e8e4da" stroke="{OL}" stroke-width="2.5" d="M270 318 L 300 356 L 330 318 L 318 310 L 300 334 L 282 310 Z"/>
  <!-- 推诿的双手（摊开） -->
  <path fill="#5c7050" stroke="{OL}" stroke-width="3"
    d="M226 350 C 196 386 190 452 202 512 C 208 544 220 566 238 576
       L 254 538 C 240 522 234 498 236 464 C 238 428 244 390 258 364 Z"/>
  <ellipse cx="252" cy="578" rx="20" ry="14" fill="#f0dfc8" stroke="{OL}" stroke-width="2.5" transform="rotate(-18 252 578)"/>
  <path fill="#5c7050" stroke="{OL}" stroke-width="3"
    d="M374 350 C 404 386 410 452 398 512 C 392 544 380 566 362 576
       L 346 538 C 360 522 366 498 364 464 C 362 428 356 390 342 364 Z"/>
  <ellipse cx="348" cy="578" rx="20" ry="14" fill="#f0dfc8" stroke="{OL}" stroke-width="2.5" transform="rotate(18 348 578)"/>
  <!-- 裤与鞋 -->
  <path fill="#43423e" stroke="{OL}" stroke-width="3" d="M232 716 L 372 716 L 378 930 L 322 930 L 302 800 L 282 930 L 226 930 Z"/>
  <path fill="#2c2a26" d="M226 928 L 284 928 L 284 952 L 222 952 Z" stroke="{OL}" stroke-width="2.5"/>
  <path fill="#2c2a26" d="M316 928 L 378 928 L 380 952 L 318 952 Z" stroke="{OL}" stroke-width="2.5"/>
</g>'''
    return svg_doc(body + face + hair, '')


# ============================================================ 亲戚·婶婶
def relative_woman():
    cx, cy, rx, ry = 300, 242, 62, 70
    face = f'''<g id="face-base">
  <path d="M{cx} {cy+ry} C {cx-rx+6} {cy+ry-4} {cx-rx} {cy+8} {cx-rx} {cy-ry*0.55}
    C {cx-rx} {cy-ry-10} {cx-rx//2} {cy-ry-16} {cx} {cy-ry-16}
    C {cx+rx//2} {cy-ry-16} {cx+rx} {cy-ry-10} {cx+rx} {cy-ry*0.55}
    C {cx+rx} {cy+8} {cx+rx-6} {cy+ry-4} {cx} {cy+ry} Z"
    fill="#f2e2ce" stroke="{OL}" stroke-width="3"/>
  <!-- 游移的眼（瞳孔偏一侧+小） -->
  <path fill="#ffffff" stroke="{OL}" stroke-width="3"
    d="M{cx-40} {cy+2} C {cx-38} {cy-14} {cx-20} {cy-16} {cx-16} {cy}
     C {cx-20} {cy+12} {cx-36} {cy+12} {cx-40} {cy+2} Z"/>
  <ellipse cx="{cx-30}" cy="{cy}" rx="5.5" ry="7" fill="#3a3040"/>
  <path fill="#ffffff" stroke="{OL}" stroke-width="3"
    d="M{cx+16} {cy} C {cx+20} {cy-16} {cx+38} {cy-14} {cx+40} {cy+2}
     C {cx+36} {cy+12} {cx+20} {cy+12} {cx+16} {cy} Z"/>
  <ellipse cx="{cx+38}" cy="{cy}" rx="5.5" ry="7" fill="#3a3040"/>
  <!-- 眉（挑起） -->
  <path fill="none" stroke="#4a4038" stroke-width="4" stroke-linecap="round" d="M{cx-40} {cy-24} C {cx-32} {cy-30} {cx-22} {cy-29} {cx-16} {cy-26}"/>
  <path fill="none" stroke="#4a4038" stroke-width="4" stroke-linecap="round" d="M{cx+16} {cy-26} C {cx+22} {cy-29} {cx+32} {cy-30} {cx+40} {cy-24}"/>
  <!-- 鼻与嘴（被手掩，只露上唇线） -->
  <path fill="none" stroke="{OL}" stroke-width="2.4" opacity="0.7" stroke-linecap="round" d="M{cx} {cy+20} l 3 6"/>
  <path fill="none" stroke="{OL}" stroke-width="3" stroke-linecap="round" d="M{cx-10} {cy+40} C {cx-4} {cy+37} {cx+4} {cy+37} {cx+10} {cy+40}"/>
</g>'''
    hair = f'''<g id="hair" stroke="{OL}" stroke-width="3">
  <!-- 棕色烫发：一圈圆卷 -->
  <circle cx="{cx-52}" cy="{cy-30}" r="20" fill="#7a563c"/><circle cx="{cx-44}" cy="{cy-64}" r="21" fill="#7a563c"/>
  <circle cx="{cx-16}" cy="{cy-84}" r="22" fill="#7a563c"/><circle cx="{cx+18}" cy="{cy-84}" r="22" fill="#7a563c"/>
  <circle cx="{cx+46}" cy="{cy-62}" r="21" fill="#7a563c"/><circle cx="{cx+54}" cy="{cy-28}" r="20" fill="#7a563c"/>
  <circle cx="{cx-58}" cy="{cy+8}" r="17" fill="#7a563c"/><circle cx="{cx+60}" cy="{cy+8}" r="17" fill="#7a563c"/>
  <path fill="#7a563c" d="M{cx-58} {cy-30} C {cx-56} {cy-84} {cx-20} {cy-104} {cx} {cy-104}
    C {cx+20} {cy-104} {cx+56} {cy-84} {cx+58} {cy-30}
    C {cx+40} {cy-64} {cx-40} {cy-64} {cx-58} {cy-30} Z"/>
  <circle cx="{cx-36}" cy="{cy-52}" r="10" fill="#8e6648"/><circle cx="{cx+8}" cy="{cy-72}" r="11" fill="#8e6648"/>
  <circle cx="{cx+40}" cy="{cy-44}" r="10" fill="#8e6648"/>
</g>'''
    body = f'''<g id="body">
  <!-- 紫红大衣 -->
  <path fill="#b04a72" stroke="{OL}" stroke-width="3"
    d="M238 336 C 208 366 200 440 208 510 C 216 580 226 660 236 730
       L 364 730 C 374 660 384 580 392 510 C 400 440 392 366 362 336
       C 334 318 266 318 238 336 Z"/>
  <!-- 大衣领 -->
  <path fill="#93385c" stroke="{OL}" stroke-width="3" d="M246 332 C 268 356 332 356 354 332
    C 366 344 364 368 348 378 C 326 368 274 368 252 378 C 236 368 234 344 246 332 Z"/>
  <path fill="#f2e2ce" stroke="{OL}" stroke-width="2.5" d="M262 326 L 300 372 L 338 326 L 324 318 L 300 350 L 276 318 Z"/>
  <!-- 掩嘴的右手 -->
  <path fill="#b04a72" stroke="{OL}" stroke-width="3"
    d="M370 350 C 398 380 404 440 394 490 C 388 522 378 544 362 554
       L 346 518 C 358 506 364 488 364 460 C 364 424 358 386 348 364 Z"/>
  <ellipse cx="352" cy="330" rx="26" ry="20" fill="#f2e2ce" stroke="{OL}" stroke-width="2.5"/>
  <path fill="none" stroke="{OL}" stroke-width="2" opacity="0.6" d="M336 324 L 368 324 M334 334 L 370 334"/>
  <!-- 左臂提包 -->
  <path fill="#b04a72" stroke="{OL}" stroke-width="3"
    d="M230 350 C 202 380 196 440 206 490 C 212 522 222 544 238 554
       L 254 518 C 242 506 236 488 236 460 C 236 424 242 386 252 364 Z"/>
  <circle cx="248" cy="558" r="15" fill="#f2e2ce" stroke="{OL}" stroke-width="2.5"/>
  <path fill="#8e3d3d" stroke="{OL}" stroke-width="3" d="M232 560 L 264 560 L 282 640 L 250 640 Z"/>
  <path fill="none" stroke="{OL}" stroke-width="4" d="M240 560 C 240 542 256 542 256 560"/>
  <!-- 裙与鞋 -->
  <path fill="#8e3a5e" stroke="{OL}" stroke-width="3" d="M236 728 L 364 728 L 384 920 L 216 920 Z"/>
  <path fill="#3a2c30" d="M252 918 L 296 918 L 300 948 L 248 948 Z" stroke="{OL}" stroke-width="2.5"/>
  <path fill="#3a2c30" d="M348 918 L 304 918 L 300 948 L 352 948 Z" stroke="{OL}" stroke-width="2.5"/>
</g>'''
    return svg_doc(body + face + hair, '')


# ============================================================ UI 元素
def ui_nameplate():
    snow = '<g stroke="#d8c68a" stroke-width="2" fill="none" opacity="0.9">'
    for i in range(6):
        snow += f'<line x1="38" y1="26" x2="38" y2="10" transform="rotate({i*30} 38 26)"/>'
    snow += '</g>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 76 360" width="76" height="360">
<defs><linearGradient id="np" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#232c48"/><stop offset="0.7" stop-color="#1a2138"/><stop offset="1" stop-color="#141a2c"/>
</linearGradient></defs>
<rect x="4" y="4" width="68" height="352" rx="14" fill="url(#np)" stroke="#d8c68a" stroke-width="2.5" opacity="0.96"/>
{snow}
<rect x="12" y="46" width="52" height="296" rx="8" fill="none" stroke="#d8c68a" stroke-width="1" opacity="0.5"/>
</svg>'''


def ui_corner():
    flakes = ''
    for i in range(6):
        flakes += (f'<line x1="60" y1="60" x2="60" y2="18" stroke="#e8ecf4" stroke-width="3" stroke-linecap="round" '
                   f'transform="rotate({i*30} 60 60)"/>'
                   f'<line x1="60" y1="30" x2="54" y2="22" stroke="#e8ecf4" stroke-width="2" stroke-linecap="round" '
                   f'transform="rotate({i*30} 60 60)"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120">
<g opacity="0.9">{flakes}</g>
<circle cx="60" cy="60" r="6" fill="#e8ecf4"/>
</svg>'''


if __name__ == '__main__':
    write(os.path.join(OUT, 'miyuki_normal.svg'), build_miyuki('normal'))
    write(os.path.join(OUT, 'miyuki_smile.svg'), build_miyuki('smile'))
    write(os.path.join(OUT, 'miyuki_sad.svg'), build_miyuki('sad'))
    write(os.path.join(OUT, 'miyuki_surprise.svg'), build_miyuki('surprise'))
    write(os.path.join(OUT, 'miyuki_white.svg'), build_miyuki('white', white=True))
    write(os.path.join(OUT, 'shuuji_child.svg'), shuuji_child())
    write(os.path.join(OUT, 'shuuji_teen.svg'), shuuji_teen())
    write(os.path.join(OUT, 'toba.svg'), toba())
    write(os.path.join(OUT, 'relative_man.svg'), relative_man())
    write(os.path.join(OUT, 'relative_woman.svg'), relative_woman())
    write(os.path.join(UI, 'nameplate.svg'), ui_nameplate())
    write(os.path.join(UI, 'frame_corner.svg'), ui_corner())
    print('ALL SPRITES DONE')
