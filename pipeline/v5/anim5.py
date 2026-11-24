"""Сосед Гена, серия 2: 'POV: сосед-монстр занял ванную на 3 часа'. Frame-by-frame, 24 fps (v4 style)."""
import os, sys, math, subprocess, wave, shutil, random
import numpy as np
sys.path.insert(0, "/home/claude/v3"); sys.path.insert(0, "/home/claude/v2"); sys.path.insert(0, "/home/claude/v5")
import scenes3 as s3
import chars5 as c4
from chars import shaded, path, circle, ell, O

W, H, FPS, SR = 1080, 1920, 24, 44100
A = "/home/claude/v5/assets"; OUT = "/home/claude/v5/out"; FR = "/home/claude/v5/frames"
os.makedirs(OUT, exist_ok=True)
POV = "POV: сосед-монстр занял ванную на 3 часа"

SEG = {
    "A1": ("artyom", 0.00, 3.00), "A2": ("artyom", 4.12, 6.65), "A3": ("artyom", 7.44, 9.10),
    "A4": ("artyom", 9.94, 11.85), "A5": ("artyom", 12.80, 14.44),
    "D1": ("dima", 0.00, 3.20), "D2": ("dima", 4.45, 7.55),
    "G1": ("gena", 0.25, 1.27), "G2": ("gena", 2.75, 5.68), "G3": ("gena", 6.42, 10.03),
}
TXT = {
    "A1": "ГЕНА! ТЫ ТРИ ЧАСА В ВАННОЙ СИДИШЬ!", "G1": "ЗАНЯТО.", "A2": "ДИМА! ЧТО ОН ТАМ ДЕЛАЕТ?!",
    "D1": "ЛИНЯЕТ. НОЯБРЬ ЖЕ, У НИХ СЕЗОН.", "A3": "В СМЫСЛЕ — ЛИНЯЕТ?!",
    "G2": "СВОБОДНО. Я ТЕПЕРЬ КАК НОВЕНЬКИЙ.", "A4": "ТЫ ВЫГЛЯДИШЬ ТОЧНО ТАК ЖЕ!",
    "A5": "А ЭТО ЧТО В ВАННЕ?!", "G3": "СТАРЫЙ Я. ВЫСОХНЕТ — БУДЕТ ЖИТЬ В КЛАДОВКЕ.",
    "D2": "ОТЛИЧНО. КВАРТПЛАТУ ДЕЛИМ НА ЧЕТВЕРЫХ.",
}
# (line|None, scene, beat, (z0,z1,cx0,cy0,cx1,cy1))
S = [
    ("A1", "door_bang", 0, (1.0, 1.12, .5, .45, .6, .45)),
    ("G1", "door_eye", 0, (2.2, 2.5, .50, .40, .50, .40)),
    ("A2", "two", 0, (1.8, 2.0, .58, .48, .58, .46)),
    ("D1", "two", 0, (1.8, 1.95, .86, .48, .86, .48)),
    ("A3", "two", 0, (1.15, 1.3, .7, .48, .62, .46)),
    (None, "door_open", 0.7, (1.0, 1.05, .5, .45, .5, .45)),
    ("G2", "door_open", 0, (1.6, 1.8, .32, .37, .32, .36)),
    ("A4", "door_open", 0, (1.05, 1.15, .6, .45, .65, .45)),
    (None, "tub", 0.9, (1.0, 1.1, .5, .55, .5, .55)),
    ("A5", "tub", 0, (1.1, 1.25, .5, .58, .5, .60)),
    ("G3", "door_open", 0, (1.7, 1.9, .32, .32, .32, .30)),
    ("D2", "dima_close", 0, (1.0, 1.1, .5, .40, .5, .38)),
    (None, "tub_eyes", 2.2, (1.6, 2.4, .5, .58, .5, .60)),
]
GAP, TAIL = 0.22, 0.4
t = 0.30; lines = []
for i, (line, img, beat, mv) in enumerate(S):
    st = t
    if line:
        f, a, b = SEG[line]; lines.append((line, st, b - a)); t = st + (b - a) + GAP
    else:
        t = st + beat
    S[i] = (line, img, beat, mv, st)
END = t + TAIL
NF = int(round(END * FPS))

def load(f):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{A}/{f}.mp3", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True)
    return np.frombuffer(r.stdout, dtype=np.float32)
src = {k: load(k) for k in ("artyom", "dima", "gena")}
env = {}
for line, st, dur in lines:
    f, a, b = SEG[line]
    seg = src[f][int(a * SR):int(b * SR)]
    hop = SR // FPS
    rms = np.array([np.sqrt(np.mean(seg[i:i + hop] ** 2) + 1e-9) for i in range(0, len(seg), hop)])
    rms = rms / (np.percentile(rms, 90) + 1e-6)
    m = np.clip((rms - 0.15) * 2.4, 0, 2)
    m = np.convolve(m, [0.25, 0.5, 0.25], mode="same")
    env[line] = (st, m)
WHO = {"A": "artyom", "D": "dima", "G": "gena"}

def mouth_of(char, tt):
    for line, (st, m) in env.items():
        if WHO[line[0]] == char:
            k = int((tt - st) * FPS)
            if 0 <= k < len(m):
                return float(m[k]), True
    return 0.0, False

def blink_of(char, tt):
    per, off = {"artyom": (3.3, 0.4), "dima": (4.1, 1.7), "gena": (5.2, 2.9)}[char]
    ph = (tt + off) % per
    return 1.0 if ph < 0.09 else (0.5 if ph < 0.14 else 0.0)

def breath_of(char, tt):
    off = {"artyom": 0, "dima": 1.1, "gena": 2.3}[char]
    return math.sin(2 * math.pi * (tt + off) / (2.6 if char == "artyom" else 3.4))

def G(inner, x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})">{inner}</g>'

def P(char, tt, expr_talk=None, expr_idle="normal"):
    m, talking = mouth_of(char, tt)
    sh = (3 * math.sin(tt * 47), 2 * math.cos(tt * 39)) if char == "artyom" and talking else (0, 0)
    expr = (expr_talk or expr_idle) if talking else expr_idle
    return dict(expr=expr, mouth=m, blink=blink_of(char, tt), breath=breath_of(char, tt), shake=sh, talking=talking)

def artyom(tt, arms, x, y, s, talk="shout", idle="panic", look=0):
    p = P("artyom", tt, talk, idle)
    return G(c4.guy("artyom", p["expr"], arms, p["mouth"], p["blink"], p["breath"], shake=p["shake"], look=look), x, y, s)

def dima(tt, arms, x, y, s, look=-1):
    p = P("dima", tt, "deadpan", "deadpan")
    return G(c4.guy("dima", p["expr"], arms, min(p["mouth"] * 0.5, 0.8), p["blink"], p["breath"], look=look if not p["talking"] else 0), x, y, s)

def gena(tt, arms, x, y, s, expr="grin", towel=False):
    p = P("gena", tt, expr, expr)
    return G(c4.gena(expr, arms, p["mouth"] if p["talking"] else 0.0, p["blink"], p["breath"], towel=towel,
                     lean=0.15 * math.sin(tt * 0.9)), x, y, s)

# ---------------------------------------------------------------- backgrounds
DX0, DX1, DY0, DY1 = 110, 530, 330, 1712   # bathroom door frame

def steam(tt, x0, x1, y0, y1, n=9, a=0.22):
    rnd = random.Random(5); b = []
    for i in range(n):
        x = rnd.uniform(x0, x1); ph = rnd.uniform(0, 6); sp = rnd.uniform(40, 90); r = rnd.uniform(60, 140)
        y = y1 - ((tt * sp + ph * 100) % (y1 - y0))
        x += 30 * math.sin(tt * 0.8 + ph)
        fade = min(1, (y1 - y) / 200) * min(1, (y - y0) / 200)
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="url(#stm)" opacity="{a*fade*1.6:.3f}"/>')
    return "".join(b)

def corridor_bg(tt, state="closed"):
    b = [f'<rect width="{W}" height="{H}" fill="#3a3f4f"/>']
    for yy in range(0, 1700, 90):
        for xx in range(0, W + 90, 90):
            ox = 45 if (yy // 90) % 2 else 0
            b.append(f'<path d="M{xx+ox} {yy} l20 30 l-20 30 l-20 -30 Z" fill="#454b5d"/>')
    b.append(f'<rect y="1200" width="{W}" height="510" fill="#2f3a3f"/>')
    b.append(f'<line x1="0" y1="1200" x2="{W}" y2="1200" stroke="{O}" stroke-width="5"/>')
    # coat hooks + light switch on the right wall
    b.append(s3.R(700, 520, 300, 34, "#6a5442", rx=6))
    for x in (740, 820, 900, 970):
        b.append(path(f"M{x} 554 l0 30 q0 16 14 12", sw=6, stroke="#c9b37a"))
    b.append(s3.R(620, 900, 50, 80, "#d8d2c2", rx=6, sw=4)); b.append(s3.R(636, 920, 18, 36, "#bdb6a4", rx=3, sw=3))
    # frame
    b.append(s3.R(DX0 - 30, DY0 - 30, DX1 - DX0 + 60, DY1 - DY0 + 30, "#6a5442", rx=6))
    if state == "open":
        b.append(f'<rect x="{DX0}" y="{DY0}" width="{DX1-DX0}" height="{DY1-DY0}" fill="#c9b98a"/>')
        # bathroom tiles seen through doorway
        for yy in range(DY0, DY1, 56):
            b.append(f'<line x1="{DX0}" y1="{yy}" x2="{DX1}" y2="{yy}" stroke="#a89a70" stroke-width="3"/>')
        for xx in range(DX0, DX1, 56):
            b.append(f'<line x1="{xx}" y1="{DY0}" x2="{xx}" y2="{DY1}" stroke="#a89a70" stroke-width="3"/>')
        b.append(f'<rect x="{DX0}" y="{DY0}" width="{DX1-DX0}" height="{DY1-DY0}" fill="#fff3c8" opacity="0.25"/>')
        # door swung inward (thin sliver)
        b.append(f'<polygon points="{DX0},{DY0} {DX0+70},{DY0+40} {DX0+70},{DY1-30} {DX0},{DY1}" fill="#8a6f55" stroke="{O}" stroke-width="5"/>')
    else:
        b.append(shaded(f"M{DX0} {DY0} L{DX1} {DY0} L{DX1} {DY1} L{DX0} {DY1} Z", "#8a6f55",
                        [(f"M{DX1-60} {DY0} L{DX1} {DY0} L{DX1} {DY1} L{DX1-60} {DY1} Z", "#735b45")]))
        b.append(s3.R(DX0 + 50, DY0 + 420, DX1 - DX0 - 100, 500, "none", rx=6, sw=4, stroke="#5e4936"))
        b.append(s3.R(DX0 + 50, DY0 + 1000, DX1 - DX0 - 100, 300, "none", rx=6, sw=4, stroke="#5e4936"))
        # frosted glass with warm light
        b.append(s3.R(DX0 + 70, DY0 + 60, DX1 - DX0 - 140, 280, "#f2dc9a", rx=6, sw=5))
        b.append(f'<rect x="{DX0+70}" y="{DY0+60}" width="{DX1-DX0-140}" height="280" fill="#ffffff" opacity="{0.15+0.08*math.sin(tt*3):.3f}"/>')
        # light strip under the door
        b.append(f'<rect x="{DX0}" y="{DY1-8}" width="{DX1-DX0}" height="8" fill="#ffe7a0"/>')
        b.append(f'<ellipse cx="{(DX0+DX1)/2}" cy="{DY1+20}" rx="260" ry="40" fill="#ffe7a0" opacity="0.18"/>')
        b.append(circle(DX1 - 50, DY0 + 760, 14, "#c9b37a", sw=4))
        b.append(path(f"M{DX1-50} {DY0+760} l-50 0", sw=12, stroke="#c9b37a"))
        # shower sign
        b.append(s3.R(DX0 + 150, DY0 - 140, 120, 90, "#d8d2c2", rx=10, sw=4))
        b.append(path(f"M{DX0+180} {DY0-120} q30 -10 40 20 M{DX0+188} {DY0-84} l0 14 M{DX0+204} {DY0-80} l0 14 M{DX0+220} {DY0-84} l0 14", sw=4, stroke="#4f6f86"))
    b.append(path("M540 0 L540 90", sw=4)); b.append(circle(800, 120, 34, "#f3e3a6", sw=5))
    b.append(f'<circle cx="800" cy="120" r="320" fill="#f3e3a6" opacity="0.07"/>')
    b.append(f'<rect y="1710" width="{W}" height="210" fill="{s3.P["floor"]}"/>')
    b.append(f'<line x1="0" y1="1710" x2="{W}" y2="1710" stroke="{O}" stroke-width="6"/>')
    b.append(f'<polygon points="120,1716 520,1716 600,1830 40,1830" fill="#4f6f86" stroke="{O}" stroke-width="5"/>')  # bath mat
    if state == "open":
        b.append(f'<polygon points="{DX0},{DY1} {DX1},{DY1} {DX1+220},1920 {DX0-120},1920" fill="#fff3c8" opacity="0.10"/>')
    return "".join(b)

def door_eye_bg(tt):
    """Door ajar by a crack; Gena's face visible in the gap."""
    b = [corridor_bg(tt, "closed")]
    gx0, gx1 = 455, 530
    b.append(f'<rect x="{gx0}" y="{DY0}" width="{gx1-gx0}" height="{DY1-DY0}" fill="#d8c48a"/>')
    cid = "gap"
    b.append(f'<clipPath id="{cid}"><rect x="{gx0}" y="{DY0}" width="{gx1-gx0}" height="{DY1-DY0}"/></clipPath>')
    p = P("gena", tt, "grin", "grin")
    head = c4.gena_head("grin", p["mouth"], p["blink"], look=1)
    b.append(f'<g clip-path="url(#{cid})">{G(head, 455, 860, 1.25)}'
             f'<rect x="{gx0}" y="{DY0}" width="{gx1-gx0}" height="{DY1-DY0}" fill="#000" opacity="0.25"/></g>')
    b.append(steam(tt, gx0 - 40, gx1 + 80, DY0, 1300, 5, 0.18))
    b.append(path(f"M{gx0} {DY0} L{gx0} {DY1}", sw=6))
    return "".join(b)

def tub_bg(tt, eyes_open=False):
    b = [f'<rect width="{W}" height="{H}" fill="#9aa9a6"/>']
    for yy in range(0, 1300, 72):
        for xx in range(0, W, 72):
            b.append(f'<rect x="{xx}" y="{yy}" width="70" height="70" fill="#a9b8b4" stroke="#7f8e8b" stroke-width="2"/>')
    b.append(f'<rect width="{W}" height="{H}" fill="#e9d79a" opacity="0.18"/>')
    # shower hose + head
    b.append(path("M880 200 L880 640 Q880 700 820 700", sw=10, stroke="#c8ccd0"))
    b.append(shaded("M840 170 L940 170 L920 230 L860 230 Z", "#c8ccd0"))
    # mirror-less wall shelf with bottles
    b.append(s3.R(90, 520, 360, 26, "#d8d2c2", rx=6, sw=4))
    for x, h, c in ((120, 110, "#5a8f7b"), (190, 150, "#b8362b"), (270, 90, "#e8c96a"), (350, 130, "#4f6f86")):
        b.append(s3.R(x, 520 - h, 54, h, c, rx=12, sw=4))
    # bathtub
    b.append(f'<rect y="1650" width="{W}" height="270" fill="#4a4a46"/>')
    b.append(shaded("M20 1100 L1060 1100 L1040 1600 C1030 1660 980 1680 920 1680 L160 1680 C100 1680 50 1660 40 1600 Z", "#eef0ec",
                    [("M700 1090 L1080 1090 L1080 1690 L700 1690 Z", "#d3d6d1")], lines=[("M60 1160 L1020 1160", 4)]))
    b.append(f'<path d="M50 1130 L1030 1130 L1020 1180 L60 1180 Z" fill="#7c9aa0" opacity="0.6"/>')  # water surface
    # ---- the shed skin: draped over the rim, deflated
    sk, skS, skD = "#b7bdb0", "#9aa194", "#7b8276"
    b.append(shaded("M180 1110 C220 980 420 940 540 960 C660 980 820 1000 880 1110 L860 1300 C800 1340 760 1260 700 1320 "
                    "C640 1380 600 1280 540 1330 C480 1380 420 1290 360 1340 C300 1390 240 1300 200 1320 Z", sk,
                    [("M620 940 L900 940 L900 1340 L620 1340 Z", skS)],
                    lines=[("M260 1080 q40 30 90 10 q50 -20 100 10 M480 1060 q50 40 110 0 M640 1080 q60 30 120 0", 3),
                           ("M300 1200 q30 20 60 0 M560 1210 q40 22 80 0", 2.5)]))
    # limp arms hanging over the rim with empty fingers
    for x0, s in ((200, -1), (860, 1)):
        b.append(shaded(f"M{x0} 1120 C{x0+40*s} 1260 {x0+30*s} 1420 {x0+50*s} 1560 L{x0+10*s} 1570 C{x0-10*s} 1420 {x0-20*s} 1260 {x0-40*s} 1140 Z", sk,
                        lines=[(f"M{x0+10*s} 1300 q10 10 0 20", 2.5)]))
        for k in range(4):
            fx = x0 + (50 - k * 14) * s
            b.append(path(f"M{fx} 1560 q{6*s} 50 {-4*s} 90", sw=10)); b.append(path(f"M{fx} 1560 q{6*s} 50 {-4*s} 90", sw=6, stroke=sk))
    # the face: Gena's head, flattened and sagging, hung over the rim
    head = c4.gena_head("closed" if not eyes_open else "grin", 0.0, 1.0 if not eyes_open else blink_of("gena", tt), look=0)
    b.append(f'<g transform="translate(540,1010) rotate(-8) scale(1.25,0.78)" opacity="0.95">{head}</g>')
    b.append(f'<path d="M420 860 Q540 820 660 870 L650 1010 Q540 980 430 1000 Z" fill="{sk}" opacity="0.35"/>')
    b.append(path("M440 900 q40 16 80 0 q40 -16 90 6 M450 960 q50 20 100 0", sw=2.5, stroke=skD))
    if eyes_open:
        bl = blink_of("gena", tt) > 0.5
        if not bl:
            for ex in (-38, 38):
                b.append(f'<circle cx="{540+ex*1.25:.0f}" cy="{1010-128*0.78:.0f}" r="44" fill="#f2e7b0" opacity="0.12"/>')
    b.append(steam(tt, 60, 1020, 500, 1150, 10, 0.20))
    return "".join(b)

def scene(name, tt):
    if name == "door_bang":
        return corridor_bg(tt) + steam(tt, DX0, DX1, DY0, DY1, 4, 0.10) + artyom(tt, "point", 820, 1880, 1.08, "shout", "panic", look=-1)
    if name == "door_eye":
        return door_eye_bg(tt)
    if name == "two":
        return corridor_bg(tt) + artyom(tt, "head", 640, 1880, 1.0, "panic", "panic", look=1) + dima(tt, "mug", 930, 1880, 1.0, look=-1)
    if name == "door_open":
        b = corridor_bg(tt, "open") + gena(tt, "down", 330, 1740, 0.92, "grin", towel=True)
        b += steam(tt, DX0 - 40, DX1 + 120, 200, DY1, 10, 0.20)
        b += artyom(tt, "head", 840, 1880, 1.02, "panic", "panic", look=-1)
        return b
    if name == "tub":
        return tub_bg(tt, False)
    if name == "tub_eyes":
        return tub_bg(tt, True)
    if name == "dima_close":
        return corridor_bg(tt) + f'<rect width="{W}" height="{H}" fill="#000" opacity="0.15"/>' + dima(tt, "mug", 540, 2600, 2.05, look=0)
    raise ValueError(name)

VIG = ('<defs><radialGradient id="vig" cx="50%" cy="45%" r="75%"><stop offset="50%" stop-color="#000" stop-opacity="0"/>'
       '<stop offset="100%" stop-color="#000" stop-opacity="0.6"/></radialGradient></defs>'
       f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')

def camera(inner, z, cx, cy):
    hw, hh = W / (2 * z), H / (2 * z)
    px = min(max(cx * W, hw), W - hw); py = min(max(cy * H, hh), H - hh)
    return f'<g transform="translate({W/2},{H/2}) scale({z}) translate({-px},{-py})">{inner}</g>'

def frame_svg(k):
    tt = k / FPS
    idx = 0
    for i, sh in enumerate(S):
        if tt >= (0 if i == 0 else sh[4]):
            idx = i
    line, img, beat, mv, st = S[idx]
    st0 = 0 if idx == 0 else st
    en = S[idx + 1][4] if idx + 1 < len(S) else END
    p = min(1.0, max(0.0, (tt - st0) / max(en - st0, 1e-3)))
    e = 1 - (1 - p) ** 2
    z0, z1, x0, y0, x1, y1 = mv
    z = z0 + (z1 - z0) * e; cx = x0 + (x1 - x0) * e; cy = y0 + (y1 - y0) * e
    STM = ('<defs><radialGradient id="stm"><stop offset="0%" stop-color="#eeeae0" stop-opacity="1"/>'
           '<stop offset="100%" stop-color="#eeeae0" stop-opacity="0"/></radialGradient></defs>')
    body = STM + camera(scene(img, tt), z, cx, cy) + VIG
    if idx == len(S) - 1 and tt > END - 0.5:
        body += f'<rect width="{W}" height="{H}" fill="#000" opacity="{min(1,(tt-(END-0.5))/0.5):.3f}"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>'

# ---------------------------------------------------------------- audio + subs
def build_audio():
    n = int(END * SR); mix = np.zeros(n)
    for line, st, dur in lines:
        f, a, b = SEG[line]
        seg = src[f][int(a * SR):int(b * SR)].astype(np.float64)
        fade = int(0.02 * SR); seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
        gain = 1.15 if f == "gena" else 1.0
        if line == "G1":  # muffled behind the door
            seg = np.convolve(seg, np.ones(12) / 12, mode="same") * 1.6
        i0 = int(st * SR); mix[i0:i0 + len(seg)] += seg[: n - i0] * gain
    mix /= max(1e-6, np.abs(mix).max()); mix *= 0.85
    rng = np.random.default_rng(3); tt = np.arange(n) / SR
    amb = np.convolve(rng.standard_normal(n), np.ones(60) / 60, mode="same") * 0.6 + 0.08 * np.sin(2 * np.pi * 50 * tt)
    amb /= np.abs(amb).max()
    for k in range(int(END / 0.9)):   # dripping tap
        i0 = int((0.4 + k * 0.9 + 0.13 * math.sin(k)) * SR); m = int(0.08 * SR)
        if i0 + m < n:
            x = np.arange(m) / SR
            amb[i0:i0 + m] += 0.9 * np.sin(2 * np.pi * (900 + 600 * np.exp(-x * 40)) * x) * np.exp(-x * 60)
    knock = [0.32, 0.62, 0.92]                 # knocks under A1
    for kk in knock:
        i0 = int(kk * SR); m = int(0.15 * SR); x = np.arange(m) / SR
        amb[i0:i0 + m] += 4.0 * np.sin(2 * np.pi * 90 * x) * np.exp(-x * 35)
    stings = [st for line, st, d in lines if line == "G1"] + [S[-1][4]] + [S[8][4]]
    for st in stings:
        i0 = int(st * SR); m = min(int(2.2 * SR), n - i0); x = np.arange(m) / SR
        amb[i0:i0 + m] += 2.2 * np.sin(2 * np.pi * 44 * x) * np.exp(-x * 1.6)
    final = np.clip(mix + 0.08 * amb, -1, 1)
    with wave.open(f"{OUT}/mix.wav", "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((final * 32767).astype(np.int16).tobytes())

WHOT = {"A": ("АРТЁМ", "&H00A0E8B0&", "&H00406A50&"), "D": ("ДИМА", "&H00F5D49A&", "&H006A5A3A&"), "G": ("ГЕНА", "&H00E6E6E6&", "&H00404040&")}
SUBY = {"default": (1262, 1370)}
def build_subs():
    def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
    ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
           "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           "Style: Sub,Montserrat Black,92,&H00FFFFFF,&H00FFFFFF,&H00111418,&H90000000,1,0,0,0,100,100,0,0,1,8,4,5,60,60,0",
           "Style: Tag,Montserrat Black,46,&H00111418,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,1,0,0,0,100,100,3,0,3,10,0,5,0,0,0",
           "Style: Pov,DejaVu Serif,44,&H00111418,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,1,0,0,0,100,100,0,0,3,16,0,8,0,0,190",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    ass.append(f"Dialogue: 3,{ts(0)},{ts(END)},Pov,,0,0,0,,{POV}")
    for line, st, dur in lines:
        name, col, tagbg = WHOT[line[0]]
        ty, sy = SUBY.get(line, SUBY["default"])
        words = TXT[line].split()
        chunks, cur = [], []
        for w in words:
            cur.append(w)
            if (len(cur) >= 3 or w[-1] in ".!?,") and w != "—":
                chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        total = sum(len(" ".join(c)) for c in chunks)
        t0 = st
        ass.append(f"Dialogue: 2,{ts(st)},{ts(st+dur+0.15)},Tag,,0,0,0,,{{\\pos(540,{ty})\\3c{tagbg}\\4c{tagbg}\\1c&HFFFFFF&}}{name}")
        for k, c in enumerate(chunks):
            d = dur * len(" ".join(c)) / total
            e = t0 + d + (0.15 if k == len(chunks) - 1 else 0)
            ass.append(f"Dialogue: 1,{ts(t0)},{ts(e)},Sub,,0,0,0,,{{\\pos(540,{sy})\\1c{col}\\fscx85\\fscy85\\t(0,100,\\fscx100\\fscy100)}}{' '.join(c)}")
            t0 += d
    open(f"{OUT}/subs.ass", "w").write("\n".join(ass) + "\n")

if __name__ == "__main__":
    if "--test" in sys.argv:
        ks = [int(float(x) * FPS) for x in sys.argv[2:]]
        for k in ks:
            open(f"{OUT}/t{k}.svg", "w").write(frame_svg(k))
            subprocess.run(["rsvg-convert", f"{OUT}/t{k}.svg", "-o", f"{OUT}/t{k}.png"], check=True)
        print(" ".join(f"{OUT}/t{k}.png" for k in ks)); sys.exit()
    if "--plan" in sys.argv:
        for s_ in S: print(s_[0], s_[1], round(s_[4], 2))
        print("END", round(END, 2), "NF", NF); sys.exit()
    build_audio(); build_subs()
    shutil.rmtree(FR, ignore_errors=True); os.makedirs(FR)
    for k in range(NF):
        open(f"{FR}/f{k:05d}.svg", "w").write(frame_svg(k))
    print("svgs", NF, "end", round(END, 2))
