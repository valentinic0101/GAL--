# -*- coding: utf-8 -*-
"""程序化合成 BGM：六首雪国氛围曲（钢琴/长笛/太鼓/风声，五声音阶与自然小调）。

输出 WAV（numpy 合成）后由 run() 调 afconvert 转 m4a。
文件名即曲目 key：bgm_title / bgm_main / bgm_daily / bgm_sad / bgm_festival / bgm_blizzard
"""
import os
import subprocess

import numpy as np

SR = 44100
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'bgm')
os.makedirs(OUT, exist_ok=True)

NOTE_SEMI = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5,
             'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def nfreq(name):
    """'A4' 'G#4' → Hz"""
    key, octv = name[:-1], int(name[-1])
    midi = 12 * (octv + 1) + NOTE_SEMI[key]
    return 440.0 * 2 ** ((midi - 69) / 12)


# ---------------------------------------------------------------- 音色
def piano(f, dur, vol=0.5):
    """钢琴感：泛音叠加 + 指数衰减 + 轻击键噪声。"""
    n = int(SR * dur * 1.6)  # 尾音延长
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k, a in [(1, 1.0), (2, 0.42), (3, 0.20), (4, 0.09), (5, 0.045)]:
        x += a * np.sin(2 * np.pi * f * k * t)
    env = np.exp(-t * (2.6 + f / 500))          # 音越高衰减越快
    att = np.minimum(t / 0.004, 1.0)
    x = x * env * att
    x[:int(SR * 0.012)] += np.random.uniform(-1, 1, int(SR * 0.012)) * 0.02 * env[:int(SR * 0.012)]
    return x * vol * 0.22


def flute(f, dur, vol=0.5):
    """笛/尺八感：慢起音 + 颤音。"""
    n = int(SR * dur * 1.3)
    t = np.arange(n) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t)
    x = (np.sin(2 * np.pi * f * vib * t) + 0.28 * np.sin(2 * np.pi * 2 * f * t)
         + 0.10 * np.sin(2 * np.pi * 3 * f * t))
    att = np.minimum(t / 0.10, 1.0)
    rel = np.exp(-t * 1.4)
    return x * att * rel * vol * 0.20


def pad(f, dur, vol=0.5):
    """长音垫：纯音 + 五度，慢呼吸。"""
    n = int(SR * dur)
    t = np.arange(n) / SR
    breath = 0.75 + 0.25 * np.sin(2 * np.pi * 0.10 * t)
    x = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 1.5 * t + 0.5)
    att = np.minimum(t / 1.2, 1.0)
    rel = np.minimum((n / SR - t) / 1.5, 1.0)
    return x * att * rel * breath * vol * 0.10


def taiko(vol=0.9):
    """太鼓：低频下滑 + 击皮噪声。"""
    n = int(SR * 0.5)
    t = np.arange(n) / SR
    f = 95 * np.exp(-t * 9) + 45
    phase = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(phase) * np.exp(-t * 7)
    x += np.random.uniform(-1, 1, n) * np.exp(-t * 55) * 0.5
    return x * vol * 0.42


def clap(vol=0.5):
    n = int(SR * 0.09)
    t = np.arange(n) / SR
    return np.random.uniform(-1, 1, n) * np.exp(-t * 60) * vol * 0.16


def wind(dur, vol=0.5):
    """风声：白噪过一阶低通 + 慢幅度起伏。"""
    n = int(SR * dur)
    x = np.random.uniform(-1, 1, n)
    y = np.zeros(n)
    a = 0.045
    for i in range(1, n):          # one-pole lowpass
        y[i] = y[i - 1] + a * (x[i] - y[i - 1])
    t = np.arange(n) / SR
    swell = 0.45 + 0.55 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t + 1.2)) ** 2
    return y * swell * vol * 2.2


def reverb(x, taps=((0.085, 0.26), (0.163, 0.17), (0.271, 0.09))):
    y = x.copy()
    for sec, g in taps:
        d = int(SR * sec)
        y[d:] += x[:-d] * g
    return y


# ---------------------------------------------------------------- 曲谱渲染
def render(events, total_beats, tempo, tail=3.0, windvol=0.0):
    """events: (beat, samples_fn or callable, vol)。返回 stereo float ndarray。"""
    spb = 60.0 / tempo
    # 以最长事件为准扩容缓冲，防止越界
    need_beats = total_beats
    for beat, wav in events:
        need_beats = max(need_beats, beat + len(wav) / SR / spb)
    total = need_beats * spb + tail
    buf = np.zeros(int(SR * total))
    if windvol > 0:
        buf += wind(total, windvol)
    for beat, wav in events:
        i = int(beat * spb * SR)
        if i >= len(buf):
            continue
        end = min(i + len(wav), len(buf))
        buf[i:end] += wav[:end - i]
    buf = reverb(buf)
    peak = np.max(np.abs(buf))
    if peak > 0:
        buf = buf / peak * 0.86
    # 立体声：Haas 微展宽 + 尾部轻淡出，保证循环点不爆音
    right = np.concatenate([np.zeros(int(SR * 0.012)), buf[:-int(SR * 0.012)]])
    fade = int(SR * 0.8)
    env = np.ones(len(buf))
    env[-fade:] = np.linspace(1, 0, fade)
    stereo = np.stack([buf * env, right * env], axis=1)
    return stereo


def write_wav(path, stereo):
    import wave
    data = (np.clip(stereo, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print('wav', path, '%.1fs' % (len(stereo) / SR))


def mel_events(notes, start=0.0, inst=piano, vol=0.5):
    """notes: [(音名或'r', 拍数), ...] → 事件列表。"""
    evs, b = [], start
    for name, beats in notes:
        if name != 'r':
            evs.append((b, inst(nfreq(name), beats, vol)))
        b += beats
    return evs, b


# ================================================================ 曲目
def track_main(tempo=66, vol=1.0):
    """深雪主题：A 小调，温柔而怅然。"""
    mel = [('A4', 1.5), ('C5', .5), ('E5', 2), ('D5', 1), ('C5', 1), ('B4', 2),
           ('C5', 1.5), ('D5', .5), ('E5', 1), ('A4', 1), ('G4', 1), ('B4', 1),
           ('A4', 3), ('r', 1),
           ('E5', 1.5), ('D5', .5), ('C5', 2), ('B4', 1), ('C5', 1), ('D5', 2),
           ('E5', 1), ('C5', 1), ('B4', 1), ('G#4', 1), ('A4', 2), ('r', 2),
           ('A5', 1.5), ('G5', .5), ('E5', 2), ('D5', 1), ('E5', 1), ('C5', 2),
           ('B4', 1.5), ('C5', .5), ('B4', 1), ('G#4', 1), ('A4', 2), ('r', 2)]
    bass = [('A2', 8), ('F2', 8), ('C3', 8), ('G2', 8),
            ('A2', 8), ('F2', 8), ('D3', 8), ('E2', 8), ('A2', 8)]
    arp_chords = [['A3', 'C4', 'E4'], ['F3', 'A3', 'C4'], ['C4', 'E4', 'G4'], ['G3', 'B3', 'D4'],
                  ['A3', 'C4', 'E4'], ['F3', 'A3', 'C4'], ['D4', 'F4', 'A4'], ['E3', 'G#3', 'B3'],
                  ['A3', 'C4', 'E4']]
    evs = []
    me, end = mel_events(mel, 0, piano, 0.62 * vol)
    evs += me
    be, _ = mel_events(bass, 0, lambda f, d, v: piano(f, d, v * 0.9), 0.34 * vol)
    evs += be
    # 琶音垫：每小节 4 拍一个音，循环和弦音
    for bar, chord in enumerate(arp_chords):
        for i in range(4):
            evs.append((bar * 8 + i * 2, piano(nfreq(chord[i % 3]), 2, 0.13 * vol)))
    return render(evs, end + 8, tempo)


def track_title():
    """标题：深雪主题慢板 + 长音垫 + 空旷混响。"""
    x = track_main(tempo=54, vol=0.9)
    n = len(x)
    p = pad(nfreq('A2'), n / SR, 1.4)
    p2 = pad(nfreq('E3'), n / SR, 0.9)
    st = np.stack([p, p2], axis=1)[:n]
    y = x + reverb(st.reshape(-1)).reshape(-1, 2)[:n] * 0.34
    peak = np.max(np.abs(y))
    return y / peak * 0.86


def track_daily(tempo=96):
    """日常·温馨：C 五声，轻快。"""
    mel = [('E5', .5), ('G5', .5), ('A5', 1), ('G5', .5), ('E5', .5), ('D5', 1),
           ('C5', .5), ('D5', .5), ('E5', 1), ('D5', .5), ('C5', .5), ('A4', 1),
           ('G4', .5), ('A4', .5), ('C5', 1), ('D5', .5), ('E5', .5), ('G5', 1),
           ('E5', 1), ('D5', 1), ('C5', 2),
           ('G5', .5), ('A5', .5), ('C6', 1), ('A5', .5), ('G5', .5), ('E5', 1),
           ('D5', .5), ('E5', .5), ('G5', 1), ('E5', .5), ('D5', .5), ('C5', 1),
           ('A4', .5), ('C5', .5), ('D5', 1), ('E5', .5), ('D5', .5), ('C5', .5), ('A4', .5),
           ('G4', 1), ('A4', 1), ('C5', 2)]
    bass = [('C3', 4), ('G2', 4), ('A2', 4), ('F2', 4),
            ('C3', 4), ('G2', 4), ('F2', 4), ('C3', 4)] * 1
    evs = []
    me, end = mel_events(mel, 0, piano, 0.60)
    evs += me
    be, _ = mel_events(bass, 0, lambda f, d, v: piano(f, d, v), 0.30)
    evs += be
    return render(evs, end + 4, tempo)


def track_sad(tempo=52):
    """悲伤·雪落：A 小调下行，大量留白。"""
    mel = [('E5', 2), ('C5', 1), ('B4', 1), ('A4', 3), ('r', 1),
           ('C5', 2), ('B4', 1), ('A4', 1), ('G#4', 2), ('r', 2),
           ('A4', 1.5), ('B4', .5), ('C5', 2), ('E5', 2), ('D5', 2),
           ('C5', 1), ('B4', 1), ('A4', 1), ('G#4', 1), ('A4', 4), ('r', 2)]
    bass = [('A2', 8), ('F2', 8), ('C3', 8), ('E2', 8), ('A2', 8), ('E2', 8), ('A2', 8)]
    evs = []
    me, end = mel_events(mel, 0, piano, 0.55)
    evs += me
    be, _ = mel_events(bass, 0, lambda f, d, v: piano(f, d, v), 0.36)
    evs += be
    for i, name in enumerate(['E4', 'C4', 'B3', 'A3']):
        evs.append((i * 8, piano(nfreq(name), 3, 0.12)))
    return render(evs, end + 8, tempo)


def track_festival(tempo=102):
    """冬祭：太鼓 + 笛（D 五声）。"""
    mel = [('D5', 1), ('E5', 1), ('G5', 1), ('A5', 1), ('G5', .5), ('E5', .5), ('D5', 1), ('r', 1),
           ('A5', 1), ('G5', 1), ('E5', 1), ('D5', 1), ('E5', 2), ('D5', 1), ('r', 1),
           ('D5', 1), ('E5', 1), ('G5', 1), ('A5', 1), ('B5', .5), ('A5', .5), ('G5', 1), ('E5', 1),
           ('G5', 1), ('E5', 1), ('D5', 1), ('E5', 1), ('D5', 2), ('r', 2)]
    evs = []
    me, end = mel_events(mel, 0, flute, 0.62)
    evs += me
    # 太鼓：每小节 dum-dum-dak 节奏
    bar = 0
    while bar * 4 < end + 4:
        b = bar * 4
        evs.append((b + 0.0, taiko(0.9)))
        evs.append((b + 1.0, taiko(0.55)))
        evs.append((b + 1.5, taiko(0.9)))
        evs.append((b + 2.5, clap(0.5)))
        evs.append((b + 3.0, taiko(0.7)))
        evs.append((b + 3.5, clap(0.35)))
        bar += 1
    # 低音笛垫
    for i, name in enumerate(['D3', 'G3', 'A3', 'D3'] * 2):
        evs.append((i * 4, pad(nfreq(name), 4, 1.2)))
    return render(evs, end + 4, tempo)


def track_blizzard():
    """雪原·终章：风声 + 稀疏长音。"""
    total = 40.0
    n = int(SR * total)
    buf = wind(total, 0.55)
    for name, beat, dur in [('E4', 0, 6), ('B4', 6, 6), ('D#5', 12, 6), ('F#5', 18, 8),
                            ('E5', 26, 8), ('B4', 33, 6)]:
        w = piano(nfreq(name), dur, 0.4)
        i = int(beat * SR)
        end = min(i + len(w), n)
        buf[i:end] += w[:end - i]
    p = pad(nfreq('E2'), total, 2.2)
    buf += p[:n] * 0.8
    buf = reverb(buf)
    peak = np.max(np.abs(buf))
    buf = buf / peak * 0.84
    fade = int(SR * 1.5)
    env = np.ones(n)
    env[-fade:] = np.linspace(1, 0, fade)
    env[:fade] = np.linspace(0, 1, fade)
    right = np.concatenate([np.zeros(int(SR * 0.014)), buf[:-int(SR * 0.014)]])
    return np.stack([buf * env, right * env], axis=1)


# ---------------------------------------------------------------- 输出
def to_m4a(wav_path):
    m4a = wav_path.replace('.wav', '.m4a')
    r = subprocess.run(['afconvert', '-f', 'm4af', '-d', 'aac', '-b', '128000',
                        wav_path, m4a], capture_output=True, text=True)
    if r.returncode == 0:
        os.remove(wav_path)
        print('m4a', m4a, '%.0fKB' % (os.path.getsize(m4a) / 1024))
    else:
        print('afconvert failed, keep wav:', r.stderr[:200])
    return m4a if r.returncode == 0 else wav_path


def main():
    import wave as wavmod
    tracks = {
        'bgm_title': track_title(),
        'bgm_main': track_main(),
        'bgm_daily': track_daily(),
        'bgm_sad': track_sad(),
        'bgm_festival': track_festival(),
        'bgm_blizzard': track_blizzard(),
    }
    for name, stereo in tracks.items():
        p = os.path.join(OUT, name + '.wav')
        write_wav(p, stereo)
        to_m4a(p)
    print('ALL BGM DONE')


if __name__ == '__main__':
    main()
