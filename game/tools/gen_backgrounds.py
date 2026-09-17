# -*- coding: utf-8 -*-
"""生成 12 张 1280x720 背景图。风格：雪国·清冷唯美·扁平插画。"""
import math
import random
import sys
import os
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _tools import (W, H, vgrad, ridge, snow_layer, glow, vignette, grain,
                    tree, footprint_trail, snow_ground, save, hex2rgb, lerp)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'backgrounds')
os.makedirs(OUT, exist_ok=True)


def p(name):
    return os.path.join(OUT, name)


# ---------------------------------------------------------------- 站台·白天
def bg_station_day():
    img = vgrad((W, H), [(0, '#8fa3bd'), (0.55, '#b9c8dd'), (1, '#d9e2ee')])
    img = ridge(img, 300, 150, '#6f7f96', seed=4, peaks=9)
    img = ridge(img, 360, 100, '#8494aa', seed=5, peaks=7)
    img = snow_ground(img, 470, '#e6ecf5', '#c3cfe1')
    d = ImageDraw.Draw(img, 'RGBA')
    # 铁轨从近景弯向远方
    d.polygon([(0, 720), (120, 640), (118, 600), (0, 660)], fill=hex2rgb('#9aa6b8') + (255,))
    for t, wx in [(0.0, 500), (0.25, 460), (0.5, 430), (0.8, 410)]:
        y = lerp(720, 500, t)
        x = lerp(560, 410, t)
        d.line([x, y, x - 320 * (1 - t * .6), y + 30 * (1 - t)], fill=(120, 128, 140, 230), width=max(2, int(10 * (1 - t))))
    # 站房
    d.polygon([(680, 470), (680, 350), (980, 350), (980, 470)], fill=hex2rgb('#7d6a55') + (255,))
    d.polygon([(660, 350), (830, 300), (1000, 350)], fill=hex2rgb('#5d5348') + (255,))
    d.polygon([(662, 348), (830, 298), (998, 348), (998, 338), (830, 288), (662, 338)], fill=hex2rgb('#f0f4fa') + (230,))
    for i in range(4):
        x = 700 + i * 72
        d.rectangle([x, 375, x + 46, 425], fill=(38, 46, 58, 200))
        d.rectangle([x, 375, x + 46, 425], outline=(30, 34, 40, 220), width=2)
        img = glow(img, x + 23, 400, 46, '#ffd98a', 60)
        d = ImageDraw.Draw(img, 'RGBA')
    # 站牌与长椅
    d.rectangle([1010, 380, 1020, 500], fill=(80, 72, 62, 255))
    d.rectangle([970, 360, 1090, 395], fill=(32, 60, 92, 255), outline=(220, 228, 240, 255), width=2)
    d.line([560, 540, 660, 540], fill=(110, 90, 70, 255), width=6)
    for x in (566, 650):
        d.line([x, 540, x, 560], fill=(90, 76, 60, 255), width=4)
    # 空无一人的强调：远小站灯
    d.line([300, 470, 300, 380], fill=(90, 84, 76, 255), width=4)
    img = glow(img, 300, 372, 34, '#ffe9b8', 90)
    img = finalize_station(img)
    save(img, p('bg_station_day.png'))


def finalize_station(img):
    img = snow_layer(img, n=230, seed=12)
    img = vignette(img, 0.5)
    img = grain(img)
    return img


# ---------------------------------------------------------------- 老屋·走廊
def bg_corridor():
    img = vgrad((W, H), [(0, '#241f22'), (0.6, '#3a3134'), (1, '#2b2426')])
    ov = ImageDraw.Draw(img, 'RGBA')
    # 透视走廊：两侧柱子向远处收缩
    van_x, van_y = 640, 380
    for i, t in enumerate([0.0, 0.22, 0.44, 0.66, 0.85]):
        k = 1 - t * 0.72
        # 左柱
        x0 = 40 + t * 320
        top = 40 + t * 90
        bot = 720 - t * 160
        wcol = 46 * k
        ov.rectangle([x0, top, x0 + wcol, bot], fill=hex2rgb('#4a3a30') + (255,))
        ov.rectangle([x0, top, x0 + wcol, bot], outline=hex2rgb('#2e231d') + (255,), width=2)
        # 右柱
        x1 = 1240 - t * 320 - wcol
        ov.rectangle([x1, top, x1 + wcol, bot], fill=hex2rgb('#443529') + (255,))
        ov.rectangle([x1, top, x1 + wcol, bot], outline=hex2rgb('#2b2119') + (255,), width=2)
    # 地板
    ov.polygon([(0, 720), (300, 540), (980, 540), (1280, 720)], fill=hex2rgb('#5a463a') + (255,))
    for i in range(9):
        t = i / 8
        y = lerp(560, 700, t)
        x0 = lerp(320, 60, t)
        x1 = lerp(960, 1220, t)
        ov.line([x0, y, x1, y], fill=hex2rgb('#3c2e26') + (180,), width=2)
    # 尽头格子门透光
    ov.rectangle([520, 250, 760, 540], fill=hex2rgb('#232c38') + (255,))
    for gx in range(3):
        for gy in range(4):
            ov.rectangle([526 + gx * 76, 258 + gy * 70, 594 + gx * 76, 322 + gy * 70],
                         fill=hex2rgb('#cfe0f2') + (150,), outline=(40, 40, 44, 200), width=1)
    img = glow(img, 640, 400, 240, '#bcd4ee', 66)
    d = ImageDraw.Draw(img, 'RGBA')
    # 深海般的尘埃浮光
    rnd = random.Random(6)
    for _ in range(90):
        x = rnd.uniform(360, 940)
        y = rnd.uniform(160, 640)
        r = rnd.uniform(0.6, 2.2)
        a = rnd.randint(26, 80)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 230, 245, a))
    img = vignette(img, 0.62)
    img = grain(img, 10, seed=9)
    save(img, p('bg_oldhouse_corridor.png'))


# ---------------------------------------------------------------- 老屋·客厅白天
def _room_common(night=False):
    img = vgrad((W, H), [(0, '#2e2a33'), (0.5, '#443d46'), (1, '#38323b')] if night
                else [(0, '#4a4a55'), (0.5, '#6b6a75'), (1, '#57555f')])
    d = ImageDraw.Draw(img, 'RGBA')
    # 榻榻米地板透视
    d.polygon([(0, 720), (200, 480), (1080, 480), (1280, 720)],
              fill=hex2rgb('#8a7f5f' if not night else '#565043') + (255,))
    for i in range(8):
        t = i / 7
        y = lerp(500, 710, t)
        x0 = lerp(215, -30, t)
        x1 = lerp(1065, 1310, t)
        d.line([x0, y, x1, y], fill=(60, 55, 42, 160), width=2)
    for i in range(7):
        t = i / 6
        x = lerp(200, 1080, t)
        d.line([x, 480, lerp(60, 1220, t), 720], fill=(60, 55, 42, 120), width=2)
    # 墙
    d.rectangle([0, 0, 1280, 480], fill=hex2rgb('#6b6252' if not night else '#3f3a35') + (255,))
    # 格子窗（右）
    wx0, wy0, wx1, wy1 = 880, 90, 1220, 400
    d.rectangle([wx0, wy0, wx1, wy1], fill=hex2rgb('#dbe8f6' if not night else '#101722') + (255,))
    for gx in range(4):
        d.line([wx0 + (wx1 - wx0) * gx / 4, wy0, wx0 + (wx1 - wx0) * gx / 4, wy1],
               fill=(50, 44, 40, 255), width=5)
    d.line([wx0, (wy0 + wy1) // 2, wx1, (wy0 + wy1) // 2], fill=(50, 44, 40, 255), width=5)
    d.rectangle([wx0, wy0, wx1, wy1], outline=(44, 38, 34, 255), width=8)
    # 壁龛（左）：地台 + 厚柱
    d.rectangle([60, 120, 260, 460], fill=hex2rgb('#57503f') + (255,))
    d.rectangle([60, 120, 260, 460], outline=(40, 34, 28, 255), width=4)
    d.rectangle([70, 150, 250, 300], fill=hex2rgb('#4a4436') + (255,))
    # 厚柱（身高刻痕之柱）
    d.rectangle([270, 40, 350, 700], fill=hex2rgb('#7c6248') + (255,))
    d.rectangle([270, 40, 350, 700], outline=(52, 40, 30, 255), width=4)
    for i, hy in enumerate([430, 465, 500]):
        d.line([292, hy, 348, hy], fill=(48, 36, 26, 255), width=3)
    # 摆钟（中墙）
    cx = 610
    d.rectangle([cx - 45, 130, cx + 45, 360], fill=hex2rgb('#3d2f24') + (255,))
    d.rectangle([cx - 45, 130, cx + 45, 360], outline=(28, 22, 18, 255), width=4)
    d.ellipse([cx - 32, 150, cx + 32, 214], fill=(232, 226, 205, 255))
    # 指针停摆 4:49
    ang_h = math.radians((4 + 49 / 60) / 12 * 360 - 90)
    ang_m = math.radians(49 / 60 * 360 - 90)
    d.line([cx, 182, cx + 16 * math.cos(ang_h), 182 + 16 * math.sin(ang_h)], fill=(40, 34, 28), width=3)
    d.line([cx, 182, cx + 24 * math.cos(ang_m), 182 + 24 * math.sin(ang_m)], fill=(40, 34, 28), width=2)
    d.line([cx - 45, 290, cx + 45, 290], fill=(210, 190, 150, 255), width=3)  # 摆杆
    d.ellipse([cx - 12, 300, cx + 12, 324], fill=(200, 176, 130, 255))
    return img


def bg_room_day():
    img = _room_common(night=False)
    img = glow(img, 1050, 240, 260, '#cfe2f8', 80)  # 窗外雪光
    img = snow_layer(img, n=70, seed=21, big=False, blur=0.6)
    img = vignette(img, 0.45)
    img = grain(img)
    save(img, p('bg_oldhouse_room.png'))


def bg_room_night():
    img = _room_common(night=True)
    # 被炉暖光
    d = ImageDraw.Draw(img, 'RGBA')
    d.rounded_rectangle([420, 520, 900, 700], 26, fill=hex2rgb('#6d3b2a') + (255,))
    d.rounded_rectangle([430, 505, 890, 560], 20, fill=hex2rgb('#c8402e') + (255,), outline=(90, 30, 24, 255), width=3)
    img = glow(img, 660, 560, 300, '#ff9a4a', 130)
    img = glow(img, 660, 620, 200, '#ffc98a', 80)
    # 窗外冷蓝
    img = glow(img, 1050, 240, 180, '#3d5a80', 70)
    img = vignette(img, 0.66)
    img = grain(img, 12, seed=8)
    save(img, p('bg_oldhouse_room_night.png'))


# ---------------------------------------------------------------- 庭院
def bg_courtyard():
    img = vgrad((W, H), [(0, '#93a7c2'), (0.5, '#b9cade'), (1, '#e9eff8')])
    img = ridge(img, 330, 170, '#7c8ca4', seed=31, peaks=8)
    img = snow_ground(img, 480, '#eef3fa', '#ccd8e8')
    d = ImageDraw.Draw(img, 'RGBA')
    # 远处老屋檐廊轮廓
    d.rectangle([60, 350, 520, 470], fill=hex2rgb('#57493c') + (235,))
    d.polygon([(40, 350), (290, 295), (540, 350)], fill=hex2rgb('#463a30') + (235,))
    d.polygon([(44, 348), (290, 292), (536, 348), (536, 336), (290, 280), (44, 336)], fill=hex2rgb('#f2f6fb') + (225,))
    for i in range(5):
        x = 90 + i * 88
        d.rectangle([x, 380, x + 44, 445], fill=(30, 36, 46, 170))
    # 老树群
    tree(d, 660, 500, 1.35, '#f4f8fd')
    tree(d, 850, 490, 1.1, '#eef3fa')
    tree(d, 1080, 505, 1.25, '#f4f8fd')
    # 中央樱花树（无花，积雪）
    x, gy, s = 880, 640, 2.1
    d.line([x, gy, x, gy - 240], fill=hex2rgb('#4a3a30'), width=int(10 * s / 2))
    rnd = random.Random(77)
    for i in range(7):
        ty = gy - 240 * (0.3 + 0.1 * i)
        dirn = 1 if i % 2 == 0 else -1
        ln = (60 - 6 * i) * s / 1.6
        ex, ey = x + dirn * ln, ty - (24 - 2 * i) * s / 1.8
        d.line([x, ty, ex, ey], fill=hex2rgb('#4a3a30'), width=int(5 * s / 2))
        d.ellipse([ex - 10 * s / 2, ey - 13 * s / 2, ex + 10 * s / 2, ey + 3 * s / 2], fill=hex2rgb('#f6fafe') + (225,))
    # 门前两个雪人（戴水桶帽）
    for sx in (300, 380):
        sy = 660
        d.ellipse([sx - 26, sy - 62, sx + 26, sy - 12], fill=(246, 250, 255, 255))
        d.ellipse([sx - 18, sy - 92, sx + 18, sy - 58], fill=(250, 252, 255, 255))
        d.rectangle([sx - 14, sy - 100, sx + 14, sy - 84], fill=(120, 110, 96, 255))  # 水桶帽
    img = snow_layer(img, n=240, seed=13)
    img = vignette(img, 0.4)
    img = grain(img)
    save(img, p('bg_courtyard.png'))


# ---------------------------------------------------------------- 小镇街道
def bg_town_street():
    img = vgrad((W, H), [(0, '#8ba0ba'), (0.6, '#b7c6da'), (1, '#dfe7f1')])
    img = ridge(img, 290, 150, '#71829a', seed=41, peaks=9)
    img = snow_ground(img, 500, '#e9eef6', '#c9d4e4')
    d = ImageDraw.Draw(img, 'RGBA')
    # 两排覆雪木屋
    for i in range(5):
        x = 40 + i * 250
        hgt = 150 + (i % 3) * 22
        d.rectangle([x, 500 - hgt, x + 210, 500], fill=hex2rgb('#6a5b4b') + (255,))
        d.polygon([x - 14, 500 - hgt, x + 105, 500 - hgt - 55, x + 224, 500 - hgt], fill=hex2rgb('#50453a') + (255,))
        d.polygon([x - 12, 500 - hgt + 2, x + 105, 500 - hgt - 52, x + 222, 500 - hgt + 2,
                   x + 222, 500 - hgt - 8, x + 105, 500 - hgt - 62, x - 12, 500 - hgt - 8],
                  fill=hex2rgb('#f0f4fa') + (225,))
        # 门窗暖光
        d.rectangle([x + 30, 500 - hgt + 46, x + 74, 500 - 30], fill=(40, 44, 52, 220))
        img = glow(img, x + 52, 500 - hgt + 80, 60, '#ffd98a', 70)
        d = ImageDraw.Draw(img, 'RGBA')
        d.rectangle([x + 130, 500 - hgt + 40, x + 172, 500 - 24], fill=(240, 226, 190, 235))
    # 电线杆与电线
    d.line([620, 500, 620, 280], fill=(70, 66, 60, 255), width=7)
    d.line([150, 330, 620, 300], fill=(50, 48, 44, 200), width=2)
    d.line([620, 300, 1150, 330], fill=(50, 48, 44, 200), width=2)
    # 路灯
    d.line([980, 500, 980, 330], fill=(84, 78, 70, 255), width=6)
    img = glow(img, 980, 322, 40, '#ffe9b8', 90)
    img = snow_layer(img, n=210, seed=14)
    img = vignette(img, 0.42)
    img = grain(img)
    save(img, p('bg_town_street.png'))


# ---------------------------------------------------------------- 冬祭参道
def bg_festival():
    img = vgrad((W, H), [(0, '#1a1630'), (0.45, '#2c2140'), (1, '#46304a')])
    img = ridge(img, 260, 120, '#241d33', seed=51, peaks=7)
    d = ImageDraw.Draw(img, 'RGBA')
    # 参道地面反光
    d.polygon([(0, 720), (420, 470), (860, 470), (1280, 720)], fill=hex2rgb('#3a2c3e') + (255,))
    # 远处神社灯火山坡
    img = glow(img, 640, 300, 220, '#ff8c4a', 66)
    # 两侧夜市摊位（透视排列）
    for t, side in [(0.0, -1), (0.0, 1), (0.35, -1), (0.35, 1), (0.65, -1), (0.65, 1)]:
        k = 1 - t * 0.45
        base_y = 700 - t * 190
        w_stall = 260 * k
        if side < 0:
            x0 = -60 + t * 260
        else:
            x0 = 1340 - t * 260 - w_stall
        h_stall = 170 * k
        d.rectangle([x0, base_y - h_stall, x0 + w_stall, base_y], fill=hex2rgb('#3a2c28') + (245,))
        d.rectangle([x0, base_y - h_stall - 14 * k, x0 + w_stall, base_y - h_stall], fill=hex2rgb('#e8e2d4') + (235,))
        # 摊内暖光与吊灯
        for j in range(3):
            lx = x0 + w_stall * (0.2 + 0.3 * j)
            img = glow(img, int(lx), int(base_y - h_stall * 0.55), int(60 * k), '#ffb14a', 110)
        d = ImageDraw.Draw(img, 'RGBA')
        # 灯笼串
        for j in range(4):
            lx = x0 + w_stall * (0.12 + 0.25 * j)
            ly = base_y - h_stall - 34 * k
            d.ellipse([lx - 11 * k, ly - 14 * k, lx + 11 * k, ly + 14 * k], fill=(226, 88, 74, 245))
            d.line([lx, ly - 14 * k, lx, ly - 26 * k], fill=(60, 50, 44, 255), width=1)
    # 蒸汽白气
    rnd = random.Random(5)
    for _ in range(16):
        x = rnd.uniform(120, 1160)
        y = rnd.uniform(430, 660)
        r = rnd.uniform(16, 52)
        d.ellipse([x - r, y - r * .5, x + r, y + r * .5], fill=(232, 226, 220, 34))
    # 人群剪影
    rnd = random.Random(15)
    for _ in range(26):
        x = rnd.uniform(80, 1200)
        t = (x - 80) / 1120
        y = 560 + abs(x - 640) / 640 * 130 + rnd.uniform(0, 26)
        hh = rnd.uniform(26, 44)
        d.ellipse([x - hh * .3, y - hh, x + hh * .3, y - hh * .4], fill=(14, 10, 18, 235))
        d.rectangle([x - hh * .26, y - hh * .45, x + hh * .26, y], fill=(14, 10, 18, 235))
    img = snow_layer(img, n=150, seed=16)
    img = vignette(img, 0.52)
    img = grain(img, 9, seed=10)
    save(img, p('bg_town_night_festival.png'))


# ---------------------------------------------------------------- 神社夜
def bg_shrine():
    img = vgrad((W, H), [(0, '#150f26'), (0.5, '#31183a'), (1, '#57283c')])
    img = ridge(img, 230, 130, '#1d1430', seed=61, peaks=6)
    d = ImageDraw.Draw(img, 'RGBA')
    # 神社平台与石鸟居剪影
    d.rectangle([0, 560, 1280, 720], fill=hex2rgb('#241722') + (255,))
    d.rectangle([430, 380, 850, 560], fill=hex2rgb('#170f1a') + (255,))
    d.rectangle([560, 300, 720, 380], fill=hex2rgb('#170f1a') + (255,))
    # 鸟居
    d.rectangle([470, 330, 500, 560], fill=hex2rgb('#120b14') + (255,))
    d.rectangle([780, 330, 810, 560], fill=hex2rgb('#120b14') + (255,))
    d.rectangle([440, 300, 840, 322], fill=hex2rgb('#120b14') + (255,))
    d.rectangle([452, 336, 828, 350], fill=hex2rgb('#120b14') + (255,))
    # 中央篝火
    img = glow(img, 640, 520, 320, '#ff7a2e', 150)
    img = glow(img, 640, 470, 180, '#ffc25e', 120)
    d = ImageDraw.Draw(img, 'RGBA')
    for i in range(26):  # 火星
        rnd = random.Random(i)
        x = 640 + rnd.uniform(-70, 70)
        y = 470 - rnd.uniform(0, 220)
        r = rnd.uniform(1, 2.6)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 200, 120, 230))
    # 大锅白气
    d.ellipse([880, 500, 980, 560], fill=(60, 50, 52, 255))
    for i in range(6):
        y = 500 - i * 26
        r = 20 + i * 9
        d.ellipse([930 - r, y - r * .4, 930 + r, y + r * .4], fill=(230, 224, 220, 30 + i * 3))
    # 太鼓与人群剪影
    d.ellipse([180, 420, 260, 480], fill=(10, 8, 14, 255))
    d.rectangle([150, 400, 290, 500], outline=(10, 8, 14, 255), width=6)
    rnd = random.Random(25)
    for _ in range(30):
        x = rnd.uniform(0, 1280)
        y = rnd.uniform(590, 700)
        hh = rnd.uniform(24, 40)
        d.ellipse([x - hh * .3, y - hh, x + hh * .3, y - hh * .4], fill=(8, 6, 12, 240))
        d.rectangle([x - hh * .26, y - hh * .45, x + hh * .26, y], fill=(8, 6, 12, 240))
    img = snow_layer(img, n=120, seed=17)
    img = vignette(img, 0.58)
    img = grain(img, 10, seed=11)
    save(img, p('bg_shrine_night.png'))


# ---------------------------------------------------------------- 群山
def bg_mountains():
    img = vgrad((W, H), [(0, '#7f93ad'), (0.5, '#a9bacf'), (1, '#e7edf6')])
    img = ridge(img, 420, 300, '#66788f', seed=71, peaks=6, jag=0.5)
    img = ridge(img, 480, 210, '#8395ab', seed=72, peaks=8, jag=0.42)
    img = ridge(img, 540, 120, '#a5b5c9', seed=73, peaks=10)
    img = snow_ground(img, 600, '#eef2f9', '#ccd7e6')
    d = ImageDraw.Draw(img, 'RGBA')
    # 山顶雪冠高光
    rnd = random.Random(3)
    footprint_trail(d, 260, 700, 14, -7, 22, '#5c6c80')
    # 阴沉天际的雾带
    for i in range(3):
        y = 380 + i * 60
        d.ellipse([-100 - i * 40, y - 30, 1380 + i * 40, y + 30], fill=(226, 233, 242, 40))
    img = snow_layer(img, n=200, seed=18)
    img = vignette(img, 0.46)
    img = grain(img)
    save(img, p('bg_mountains.png'))


def bg_blizzard():
    img = vgrad((W, H), [(0, '#c9d4e0'), (0.5, '#dde5ee'), (1, '#eef2f8')])
    img = ridge(img, 430, 240, '#aebccc', seed=81, peaks=5, jag=0.5)
    img = snow_ground(img, 580, '#f0f4fa', '#dbe3ee')
    # 大风雪：多层斜向雪
    for i, (n, wind, blur, alpha) in enumerate([(160, 60, 0.4, 200), (220, 95, 1.0, 170), (150, 130, 1.8, 120)]):
        img = snow_layer(img, n=n, seed=90 + i, wind=wind * 0.02, blur=blur)
    ov = Image.new('RGBA', (W, H), (240, 245, 252, 0))
    od = ImageDraw.Draw(ov)
    rnd = random.Random(2)
    for _ in range(30):  # 风雪横抹
        y = rnd.uniform(0, H)
        x = rnd.uniform(-200, W)
        ln = rnd.uniform(120, 420)
        od.line([x, y, x + ln, y - ln * 0.18], fill=(255, 255, 255, 60), width=rnd.randint(2, 6))
    ov = ov.filter(ImageFilter.GaussianBlur(2))
    img.paste(ov, (0, 0), ov)
    img = vignette(img, 0.36)
    img = grain(img, 6, seed=12)
    save(img, p('bg_mountains_blizzard.png'))


# ---------------------------------------------------------------- 鸟羽老人家
def bg_toba():
    img = vgrad((W, H), [(0, '#2a2018'), (0.5, '#413226'), (1, '#332820')])
    d = ImageDraw.Draw(img, 'RGBA')
    # 木墙与地板
    d.rectangle([0, 0, 1280, 560], fill=hex2rgb('#4a382a') + (255,))
    for i in range(8):
        d.line([i * 170, 0, i * 170, 560], fill=(54, 40, 30, 255), width=4)
    d.rectangle([0, 560, 1280, 720], fill=hex2rgb('#5c4534') + (255,))
    for i in range(6):
        d.line([0, 570 + i * 26, 1280, 570 + i * 26], fill=(46, 34, 26, 200), width=2)
    # 木格窗（夜）
    wx0, wy0, wx1, wy1 = 120, 100, 400, 340
    d.rectangle([wx0, wy0, wx1, wy1], fill=hex2rgb('#1a2230') + (255,))
    for gx in range(3):
        d.line([wx0 + (wx1 - wx0) * gx / 3, wy0, wx0 + (wx1 - wx0) * gx / 3, wy1], fill=(40, 30, 24, 255), width=6)
    d.line([wx0, (wy0 + wy1) // 2, wx1, (wy0 + wy1) // 2], fill=(40, 30, 24, 255), width=6)
    d.rectangle([wx0, wy0, wx1, wy1], outline=(36, 28, 22, 255), width=8)
    img = glow(img, 260, 220, 150, '#3d5a80', 60)
    # 地炉
    d.ellipse([520, 590, 800, 680], fill=hex2rgb('#2c2018') + (255,))
    img = glow(img, 660, 640, 260, '#ff8a3e', 130)
    img = glow(img, 660, 600, 140, '#ffce8a', 90)
    d = ImageDraw.Draw(img, 'RGBA')
    # 吊锅
    d.line([660, 480, 660, 580], fill=(70, 62, 54, 255), width=3)
    d.arc([600, 560, 720, 640], 0, 180, fill=(90, 80, 70, 255), width=5)
    # 木桌与碗筷
    d.rectangle([860, 520, 1220, 540], fill=(96, 74, 56, 255))
    d.rectangle([880, 540, 900, 600], fill=(80, 60, 46, 255))
    d.rectangle([1180, 540, 1200, 600], fill=(80, 60, 46, 255))
    d.ellipse([940, 495, 990, 525], fill=(214, 200, 176, 255))
    d.ellipse([1050, 495, 1100, 525], fill=(214, 200, 176, 255))
    d.line([960, 520, 1010, 512], fill=(120, 96, 70, 255), width=3)
    # 悬挂的灯
    d.line([1080, 0, 1080, 120], fill=(60, 50, 42, 255), width=2)
    img = glow(img, 1080, 140, 120, '#ffca7a', 120)
    img = vignette(img, 0.6)
    img = grain(img, 10, seed=13)
    save(img, p('bg_toba_home.png'))


# ---------------------------------------------------------------- 标题
def bg_title():
    img = vgrad((W, H), [(0, '#5d729a'), (0.4, '#93a8c6'), (0.75, '#d7e1ee'), (1, '#eef2f9')])
    img = ridge(img, 470, 330, '#5f7391', seed=95, peaks=7, jag=0.45)
    img = ridge(img, 540, 220, '#7d90ab', seed=96, peaks=9, jag=0.4)
    img = snow_ground(img, 660, '#eef3fa', '#ccd8e8')
    d = ImageDraw.Draw(img, 'RGBA')
    # 少女剪影（黑长发，回望）
    bx, by = 660, 690
    # 裙摆
    d.polygon([(bx - 62, by), (bx - 40, by - 150), (bx + 40, by - 150), (bx + 62, by)], fill=(22, 24, 34, 255))
    # 上身与头
    d.ellipse([bx - 34, by - 235, bx + 34, by - 165], fill=(24, 26, 36, 255))
    d.ellipse([bx - 27, by - 300, bx + 27, by - 246], fill=(24, 26, 36, 255))  # 头
    # 长发向后飘
    d.polygon([(bx - 27, by - 290), (bx - 90, by - 240), (bx - 110, by - 120), (bx - 60, by - 170), (bx - 27, by - 200)], fill=(20, 22, 32, 255))
    d.polygon([(bx + 27, by - 290), (bx + 80, by - 230), (bx + 70, by - 110), (bx + 40, by - 160), (bx + 27, by - 200)], fill=(20, 22, 32, 255))
    # 风雪
    img = snow_layer(img, n=320, seed=97, wind=1.2, blur=1.1)
    img = glow(img, 640, 240, 400, '#dfe9f6', 40)
    img = vignette(img, 0.55)
    img = grain(img)
    save(img, p('bg_title.png'))


if __name__ == '__main__':
    bg_station_day()
    bg_corridor()
    bg_room_day()
    bg_room_night()
    bg_courtyard()
    bg_town_street()
    bg_festival()
    bg_shrine()
    bg_mountains()
    bg_blizzard()
    bg_toba()
    bg_title()
    print('ALL BACKGROUNDS DONE')
