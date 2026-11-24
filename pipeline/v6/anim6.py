"""Сосед Гена, серия 3: 'POV: попросил соседа-монстра разбудить в 7 утра'. Frame-by-frame, 24 fps (v4 style)."""
import os, sys, math, subprocess, wave, shutil, random
import numpy as np
sys.path.insert(0, "/home/claude/v3"); sys.path.insert(0, "/home/claude/v2"); sys.path.insert(0, "/home/claude/v5"); sys.path.insert(0, "/home/claude/v6")
import scenes3 as s3
import chars5 as c4
from chars import shaded, path, circle, ell, O

W, H, FPS, SR = 1080, 1920, 24, 44100
A = "/home/claude/v6/assets"; OUT = "/home/claude/v6/out"; FR = "/home/claude/v6/frames"
os.makedirs(OUT, exist_ok=True)
POV = "POV: попросил соседа-монстра разбудить в 7 утра"
QUESTION = "А ТЫ БЫ ПОДАРИЛ\\NГЕНЕ ЧАСЫ?"

SEG = {}   # filled from silencedetect below
TXT = {
    "A1": "А-А-А! ГЕНА! ТЫ ЧТО ДЕЛАЕШЬ НА ПОТОЛКЕ?!", "G1": "ТЫ ПРОСИЛ РАЗБУДИТЬ В СЕМЬ.",
    "A2": "Я ПРОСИЛ ПОСТУЧАТЬ, А НЕ ВИСЕТЬ НАДО МНОЙ ВСЮ НОЧЬ!", "G2": "У МЕНЯ НЕТ ЧАСОВ. Я ЖДАЛ.",
    "A3": "ДИМА! ОН ВСЮ НОЧЬ НА МЕНЯ СМОТРЕЛ!", "D1": "ЗАТО НЕ ПРОСПАЛ. МЕНЯ ОН ТАК ТРИ ГОДА БУДИТ.",
    "A4": "НА! ВОТ ТЕБЕ ЧАСЫ! ТОЛЬКО ОТСТАНЬ!", "G3": "СПАСИБО. ТЕПЕРЬ БУДУ ПРИХОДИТЬ РОВНО В ТРИ.",
    "D2": "ВСЁ. ТЕПЕРЬ ОН ЗНАЕТ, СКОЛЬКО ВРЕМЕНИ.",
}
import json
SEG = json.load(open("/home/claude/v6/seg.json"))
S = [
    ("A1", "ceiling", 0, (1.0, 1.08, .5, .45, .45, .45)),
    ("G1", "ceiling", 0, (1.9, 2.2, .50, .50, .52, .50)),
    ("A2", "ceiling", 0, (1.7, 1.9, .45, .55, .45, .55)),
    ("G2", "ceiling", 0, (2.2, 2.5, .60, .48, .60, .49)),
    ("A3", "kitchen", 0, (1.6, 1.8, .30, .45, .30, .44)),
    ("D1", "kitchen", 0, (1.7, 1.85, .76, .45, .76, .45)),
    ("A4", "gift", 0, (1.15, 1.25, .35, .45, .40, .45)),
    ("G3", "gift", 0, (1.7, 2.0, .5, .30, .5, .32)),
    ("D2", "dima_close", 0, (1.0, 1.1, .5, .40, .5, .38)),
    (None, "night3", 3.2, (1.0, 1.2, .5, .5, .55, .5)),
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

# ---------------------------------------------------------------- scenes
import scenes6
scene = scenes6.make(globals())

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
        i0 = int(st * SR); mix[i0:i0 + len(seg)] += seg[: n - i0] * gain
    mix /= max(1e-6, np.abs(mix).max()); mix *= 0.85
    rng = np.random.default_rng(3); tt = np.arange(n) / SR
    amb = np.convolve(rng.standard_normal(n), np.ones(60) / 60, mode="same") * 0.6 + 0.08 * np.sin(2 * np.pi * 50 * tt)
    amb /= np.abs(amb).max()
    for k in range(int(END / 0.5)):   # clock ticking
        i0 = int((0.1 + k * 0.5) * SR); m = int(0.03 * SR)
        if i0 + m < n:
            x = np.arange(m) / SR
            amb[i0:i0 + m] += (0.7 if k % 2 else 0.45) * np.sin(2 * np.pi * 2400 * x) * np.exp(-x * 200)
    i0 = 0; m = int(0.3 * SR); x = np.arange(m) / SR   # alarm ring at the hook
    amb[i0:i0 + m] += 1.2 * np.sign(np.sin(2 * np.pi * 1800 * x)) * (np.sin(2 * np.pi * 25 * x) > 0)
    stings = [st for line, st, d in lines if line in ("G1", "G3")] + [S[-1][4]]
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
    q0 = S[-1][4] + 0.6
    ass.append(f"Dialogue: 4,{ts(q0)},{ts(END)},Sub,,0,0,0,,{{\\pos(540,1420)\\fs104\\1c&H0040D8FF&\\fad(250,0)}}{QUESTION}")
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
