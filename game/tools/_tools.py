# -*- coding: utf-8 -*-
"""雪国 galgame 程序化美术工具库：渐变/山峦/雪/光晕/暗角/噪点。"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter

W, H = 1280, 720


def lerp(a, b, t):
    return a + (b - a) * t


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def vgrad(size, stops):
    """垂直渐变。stops: [(pos0..1, '#hex'), ...]"""
    w, h = size
    img = Image.new('RGB', (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        # 找到所在区间
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                k = (t - p0) / max(p1 - p0, 1e-6)
                r = lerp(hex2rgb(c0)[0], hex2rgb(c1)[0], k)
                g = lerp(hex2rgb(c0)[1], hex2rgb(c1)[1], k)
                b = lerp(hex2rgb(c0)[2], hex2rgb(c1)[2], k)
                px[0, y] = (int(r), int(g), int(b))
                break
        else:
            px[0, y] = hex2rgb(stops[-1][1])
    return img.resize((w, h))


def ridge(img, base_y, amp, color, seed=1, peaks=7, jag=0.35):
    """山峦剪影：从 base_y 起伏 amp 的多边形覆盖到底部。"""
    rnd = random.Random(seed)
    w, h = img.size
    overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    pts = []
    n = peaks * 2
    for i in range(n + 1):
        x = w * i / n
        env = math.sin(i / n * math.pi)  # 中间高
        y = base_y - amp * env * (0.55 + 0.45 * rnd.random())
        if rnd.random() < jag:
            y += rnd.uniform(-amp * .18, amp * .18)
        pts.append((x, y))
    poly = pts + [(w, h), (0, h)]
    c = hex2rgb(color)
    d.polygon(poly, fill=c + (235,))
    out = img.convert('RGBA')
    out.alpha_composite(overlay)
    return out.convert('RGB')


def snow_layer(img, n=260, seed=2, big=True, wind=0.0, blur=1.2):
    """撒雪粒。wind: 水平漂移比例。"""
    rnd = random.Random(seed)
    w, h = img.size
    ov = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for _ in range(n):
        x = rnd.uniform(0, w)
        y = rnd.uniform(0, h)
        depth = rnd.random()
        r = lerp(0.7, 3.6, depth * depth) if big else lerp(0.6, 1.8, depth)
        alpha = int(lerp(90, 225, depth))
        dx = wind * lerp(2, 46, depth)
        d.ellipse([x - r, y - r * 1.6, x + r, y + r * 1.6], fill=(250, 252, 255, alpha))
    if blur:
        ov = ov.filter(ImageFilter.GaussianBlur(blur * 0.6))
    out = img.convert('RGBA')
    out.alpha_composite(ov)
    return out.convert('RGB')


def glow(img, cx, cy, radius, color, strength=140):
    """径向光晕（窗光/灯火/火光）。"""
    w, h = img.size
    small = max(8, radius // 6)
    g = Image.new('L', (small * 2, small * 2), 0)
    gd = ImageDraw.Draw(g)
    for i in range(small, 0, -1):
        a = int(255 * (1 - i / small) ** 2)
        gd.ellipse([small - i, small - i, small + i, small + i], fill=a)
    g = g.resize((radius * 2, radius * 2)).filter(ImageFilter.GaussianBlur(radius * 0.08))
    ov = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ov.paste(hex2rgb(color) + (strength,), (cx - radius, cy - radius), g)
    out = img.convert('RGBA')
    out.alpha_composite(ov)
    return out.convert('RGB')


def vignette(img, power=0.55):
    w, h = img.size
    mask = Image.new('L', (w // 4, h // 4), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([-w // 10, -h // 8, w // 4 + w // 10, h // 4 + h // 6], fill=255)
    mask = mask.resize((w, h)).filter(ImageFilter.GaussianBlur(60))
    black = Image.new('RGBA', (w, h), (8, 10, 20, int(255 * power)))
    black.putalpha(Image.eval(mask, lambda v: int(v * power)))
    out = img.convert('RGBA')
    out.alpha_composite(black)
    return out.convert('RGB')


def grain(img, alpha=8, seed=3):
    rnd = random.Random(seed)
    w, h = img.size
    small = Image.new('L', (w // 2, h // 2))
    small.putdata([rnd.randint(110, 145) for _ in range((w // 2) * (h // 2))])
    small = small.resize((w, h)).filter(ImageFilter.GaussianBlur(0.5))
    ov = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    ov.putalpha(Image.eval(small, lambda v: int((v - 128) and alpha * abs(v - 128) / 40)))
    out = img.convert('RGBA')
    out.alpha_composite(ov)
    return out.convert('RGB')


def rect(d, box, fill=None, outline=None, width=1):
    d.rectangle(box, fill=fill, outline=outline, width=width)


def tree(d, x, ground_y, scale, snow_color, trunk='#3a3230', leaf=None, snow=True):
    """积雪老树：树干 + 几组枝干 + 枝头雪。leaf!=None 时画树冠。"""
    tw = max(2, int(4 * scale))
    th = int(120 * scale)
    d.line([x, ground_y, x, ground_y - th], fill=hex2rgb(trunk), width=tw)
    rnd = random.Random(int(x) + int(scale * 100))
    for i in range(5):
        ty = ground_y - th * (0.35 + 0.13 * i)
        dirn = 1 if i % 2 == 0 else -1
        ln = (28 - 3 * i) * scale
        ex = x + dirn * ln
        ey = ty - (10 - i) * scale
        d.line([x, ty, ex, ey], fill=hex2rgb(trunk), width=max(1, int(tw * 0.5)))
        if snow:
            d.ellipse([ex - 7 * scale, ey - 9 * scale, ex + 7 * scale, ey + 2 * scale],
                      fill=hex2rgb(snow_color) + (215,))
    if leaf:
        for i in range(4):
            cx = x + rnd.uniform(-26, 26) * scale
            cy = ground_y - th - rnd.uniform(0, 14) * scale
            d.ellipse([cx - 22 * scale, cy - 16 * scale, cx + 22 * scale, cy + 16 * scale],
                      fill=hex2rgb(leaf) + (200,))


def footprint_trail(d, x0, y0, dx, dy, n, color, seed=7):
    """雪地足迹串。"""
    rnd = random.Random(seed)
    x, y = float(x0), float(y0)
    for i in range(n):
        d.ellipse([x - 3, y - 6, x + 3, y + 6], fill=hex2rgb(color) + (170,))
        x += dx + rnd.uniform(-2, 2)
        y += dy + rnd.uniform(-1.5, 1.5)


def snow_ground(img, horizon_y, base='#e8eef6', shadow='#c6d2e2'):
    """地面雪原：地平线以下亮色 + 微弱起伏阴影。"""
    w, h = img.size
    ov = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, horizon_y, w, h], fill=hex2rgb(base) + (255,))
    rnd = random.Random(11)
    for i in range(14):
        x = rnd.uniform(0, w)
        y = horizon_y + rnd.uniform(8, h - horizon_y - 10)
        rw = rnd.uniform(40, 160)
        d.ellipse([x - rw, y - rw * 0.18, x + rw, y + rw * 0.18],
                  fill=hex2rgb(shadow) + (70,))
    out = img.convert('RGBA')
    out.alpha_composite(ov)
    return out.convert('RGB')


def finalize(img, snow_n=200, seed=2, vign=0.5):
    img = snow_layer(img, n=snow_n, seed=seed)
    img = vignette(img, vign)
    img = grain(img)
    return img


def save(img, path):
    img.save(path, 'PNG')
    print('saved', path)
