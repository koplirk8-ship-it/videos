"""Frame-by-frame animated version of 'POV: снял комнату за 9 тысяч' (24 fps).
Reuses the voice mix + subtitles from v3 (same timeline)."""
import os, sys, math, subprocess, wave, shutil
import numpy as np
sys.path.insert(0, "/home/claude/v3"); sys.path.insert(0, "/home/claude/v2"); sys.path.insert(0, "/home/claude/v4")
import scenes3 as s3
import chars4 as c4
from chars import shaded, path, circle, O

W, H, FPS, SR = 1080, 1920, 24, 44100
V3 = "/home/claude/v3"; OUT = "/home/claude/v4/out"; FR = "/home/claude/v4/frames"
os.makedirs(OUT, exist_ok=True)

# ---------------- timeline (identical to build3)
SEG = {
    "A1": ("artyom", 0.00, 1.42), "A2": ("artyom", 3.02, 5.78), "A3": ("artyom", 7.20, 8.57),
    "A4": ("artyom", 9.88, 12.03), "A5": ("artyom", 13.43, 14.08),
    "D1": ("dima", 0.00, 3.58), "D2": ("dima", 5.05, 6.88), "D3": ("dima", 8.15, 10.95), "D4": ("dima", 12.05, 14.16),
    "G1": ("gena", 0.00, 1.62), "G2": ("gena", 2.88, 4.20), "G3": ("gena", 5.12, 5.85), "G4": ("gena", 6.94, 10.64),
}
S = [
    ("A1", "kitchen", 0, (1.0, 1.12, .5, .45, .6, .42)),
    ("G1", "kitchen", 0, (1.9, 2.15, .28, .29, .28, .29)),
    ("A2", "hall", 0, (1.9, 2.1, .18, .50, .18, .50)),
    ("D1", "hall", 0, (1.9, 2.05, .83, .50, .83, .50)),
    ("A3", "hall", 0, (1.0, 1.1, .5, .5, .5, .45)),
    ("D2", "hall", 0, (2.0, 2.15, .83, .50, .83, .50)),
    ("G2", "hall_plate", 0, (1.6, 1.8, .5, .36, .5, .34)),
    ("A4", "hall_measure", 0, (1.0, 1.15, .55, .45, .6, .45)),
    ("D3", "dima_scarf", 0, (1.0, 1.1, .5, .40, .5, .38)),
    (None, "bed_dark", 1.4, (1.0, 1.1, .5, .45, .55, .45)),
    ("G3", "bed_gena", 0, (1.2, 1.5, .6, .30, .62, .26)),
    ("A5", "bed_dark", 0, (1.8, 2.0, .39, .55, .39, .55)),
    ("D4", "black_eyes", 0, (1.0, 1.0, .5, .5, .5, .5)),
    ("G4", "bed_lamp", 0, (1.0, 1.12, .5, .52, .45, .55)),
]
GAP, TAIL = 0.22, 1.8
t = 0.35; lines = []
for i, (line, img, beat, mv) in enumerate(S):
    st = t
    if line:
        f, a, b = SEG[line]; lines.append((line, st, b - a)); t = st + (b - a) + GAP
    else:
        t = st + beat
    S[i] = (line, img, beat, mv, st)
END = t + TAIL
NF = int(round(END * FPS))

# ---------------- lip-sync envelopes
def load(f):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{V3}/assets/{f}.mp3", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True)
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

# ---------------- scene composition with animated characters
def G(inner, x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})">{inner}</g>'

def P(char, tt, expr_talk=None, expr_idle="normal"):
    m, talking = mouth_of(char, tt)
    sh = (0, 0)
    if char == "artyom" and talking:
        sh = (3 * math.sin(tt * 47), 2 * math.cos(tt * 39))
    expr = (expr_talk or expr_idle) if talking else expr_idle
    return dict(expr=expr, mouth=m, blink=blink_of(char, tt), breath=breath_of(char, tt), shake=sh, talking=talking)

def artyom(tt, arms, x, y, s, talk="shout", idle="panic"):
    p = P("artyom", tt, talk, idle)
    return G(c4.guy("artyom", p["expr"], arms, p["mouth"], p["blink"], p["breath"], shake=p["shake"]), x, y, s)

def dima(tt, arms, x, y, s, scarf=False):
    p = P("dima", tt, "deadpan", "deadpan")
    return G(c4.guy("dima", p["expr"], arms, min(p["mouth"] * 0.5, 0.8), p["blink"], p["breath"], scarf=scarf, look=-1 if not p["talking"] else 0), x, y, s)

def gena(tt, arms, x, y, s, expr="grin", lean=0.0):
    p = P("gena", tt, expr, expr)
    mo = p["mouth"] if p["talking"] else (0.35 if arms == "pot" else 0.0)
    return G(c4.gena(expr, arms, mo, p["blink"], p["breath"], lean=lean + 0.15 * math.sin(tt * 0.9)), x, y, s)

def bedroom_bg(state):
    b = [f'<rect width="{W}" height="{H}" fill="#1f2731"/>', s3.window(110, 260, 300, 380)]
    b.append(s3.R(640, 200, 420, 1300, "#3b3029", rx=10))
    b.append(f'<rect x="660" y="230" width="380" height="1250" fill="#050608"/>')
    b.append(s3.R(700, 220, 360, 1270, "#4a3c32", rx=8))
    b.append(f'<polygon points="660,230 720,226 720,1486 660,1480" fill="#050608"/>')
    b.append(f'<rect y="1500" width="{W}" height="420" fill="#2a2321"/>')
    b.append(s3.R(40, 860, 760, 260, "#5a4636", rx=20))
    b.append(s3.R(30, 1080, 780, 560, "#d9d4c8", rx=30))
    if state == "lamp":
        b.append(f'<circle cx="930" cy="1000" r="420" fill="#ffd98a" opacity="0.18"/>')
        b.append(s3.R(860, 1100, 150, 400, "#4a3c32", rx=8))
        b.append(shaded("M880 960 L990 960 L1010 1040 L860 1040 Z", "#f1c96b"))
        b.append(s3.R(925, 1040, 20, 60, "#3b3029", sw=4))
    return "".join(b)

def blanket():
    return shaded("M20 1150 C200 1120 640 1120 820 1150 L830 1650 L10 1650 Z", "#55708a",
                  [("M500 1100 L860 1100 L860 1660 L500 1660 Z", "#46607a")],
                  lines=[("M120 1300 Q300 1270 480 1310 M200 1480 Q420 1440 700 1490", 4)])

def scene(name, tt):
    if name == "kitchen":
        return (s3.kitchen_bg() + gena(tt, "pot", 300, 1800, 0.95, "grin") +
                artyom(tt, "point", 800, 1840, 1.12, "shout", "panic"))
    if name in ("hall", "hall_plate"):
        return (s3.hall_bg() + gena(tt, "plate" if name == "hall_plate" else "down", 540, 1730, 0.95) +
                artyom(tt, "head", 180, 1880, 1.05, "panic", "panic") + dima(tt, "mug", 900, 1880, 1.05))
    if name == "hall_measure":
        return s3.hall_bg() + gena(tt, "measure", 330, 1730, 0.95) + artyom(tt, "down", 840, 1880, 1.05, "panic", "panic")
    if name == "dima_scarf":
        return s3.hall_bg() + f'<rect width="{W}" height="{H}" fill="#000" opacity="0.15"/>' + dima(tt, "mug", 540, 2600, 2.05, scarf=True)
    if name in ("bed_dark", "bed_gena"):
        p = P("artyom", tt, "scared", "scared")
        b = [bedroom_bg("dark")]
        b.append(f'<ellipse cx="420" cy="1060" rx="190" ry="70" fill="#eeeae0" stroke="{O}" stroke-width="6"/>')
        b.append(G(c4.guy_head("artyom", "scared", p["mouth"], p["blink"], look=1), 420, 1010 + 3 * p["breath"], 1.1))
        b.append(blanket())
        if name == "bed_gena":
            b.append(gena(tt, "down", 700, 1900, 1.1, "grin", lean=-0.6))
        b.append(f'<rect width="{W}" height="{H}" fill="#03050a" opacity="0.45"/>')
        if name == "bed_dark":
            bl = blink_of("gena", tt) > 0.5
            if not bl:
                b.append(circle(686, 620, 6, "#e8dcb4", sw=0)); b.append(circle(706, 622, 6, "#e8dcb4", sw=0))
                b.append(f'<circle cx="696" cy="620" r="30" fill="#e8dcb4" opacity="0.10"/>')
        return "".join(b)
    if name == "black_eyes":
        bl = blink_of("gena", tt) > 0.5
        b = [f'<rect width="{W}" height="{H}" fill="#020305"/>']
        if not bl:
            b.append(circle(510, 820, 9, "#e8dcb4", sw=0)); b.append(circle(570, 822, 9, "#e8dcb4", sw=0))
            b.append(f'<circle cx="540" cy="820" r="80" fill="#e8dcb4" opacity="0.05"/>')
        return "".join(b)
    if name == "bed_lamp":
        pa = P("artyom", tt, "deadpan", "deadpan"); pg = P("gena", tt, "timid", "timid")
        b = [bedroom_bg("lamp")]
        b.append(f'<ellipse cx="260" cy="1060" rx="190" ry="70" fill="#eeeae0" stroke="{O}" stroke-width="6"/>')
        b.append(f'<ellipse cx="590" cy="1060" rx="190" ry="70" fill="#eeeae0" stroke="{O}" stroke-width="6"/>')
        b.append(G(c4.guy_head("artyom", "deadpan", 0, pa["blink"], look=1), 260, 1010 + 3 * pa["breath"], 1.05))
        gh = c4.gena_head("timid", pg["mouth"], pg["blink"], look=-1)
        gh += shaded("M-96 -230 C-100 -340 100 -340 96 -230 Z", "#b8362b", lines=[("M-60 -240 L-60 -310 M-20 -236 L-20 -324 M20 -236 L20 -324 M60 -240 L60 -310", 6)])
        gh += shaded("M-104 -250 L104 -250 L104 -206 L-104 -206 Z", "#e8e2d2") + circle(0, -336, 28, "#e8e2d2")
        b.append(G(gh, 590, 1130 + 3 * pg["breath"], 0.85))
        b.append(blanket())
        return "".join(b)
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
    body = camera(scene(img, tt), z, cx, cy) + VIG
    if idx == len(S) - 1 and tt > END - 0.6:
        body += f'<rect width="{W}" height="{H}" fill="#000" opacity="{min(1,(tt-(END-0.6))/0.6):.3f}"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>'

if __name__ == "__main__":
    if "--test" in sys.argv:
        ks = [int(float(x) * FPS) for x in sys.argv[2:]]
        for k in ks:
            open(f"/tmp/f{k}.svg", "w").write(frame_svg(k))
            subprocess.run(["rsvg-convert", f"/tmp/f{k}.svg", "-o", f"/tmp/f{k}.png"], check=True)
        print(" ".join(f"/tmp/f{k}.png" for k in ks)); sys.exit()
    shutil.rmtree(FR, ignore_errors=True); os.makedirs(FR)
    for k in range(NF):
        open(f"{FR}/f{k:05d}.svg", "w").write(frame_svg(k))
    print("svgs", NF, "end", round(END, 2))
