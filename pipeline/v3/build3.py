import os, subprocess, sys, wave
import numpy as np

ART = "/home/claude/v3/art"; A = "/home/claude/v3/assets"; OUT = "/home/claude/v3/out"
os.makedirs(OUT, exist_ok=True)
W, H, FPS, SR = 1080, 1920, 30, 44100
ENC = ["-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS)]

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2500:]); sys.exit(1)

# ---- voice segments (file, start, end) from silencedetect
SEG = {
    "A1": ("artyom", 0.00, 1.42), "A2": ("artyom", 3.02, 5.78), "A3": ("artyom", 7.20, 8.57),
    "A4": ("artyom", 9.88, 12.03), "A5": ("artyom", 13.43, 14.08),
    "D1": ("dima", 0.00, 3.58), "D2": ("dima", 5.05, 6.88), "D3": ("dima", 8.15, 10.95), "D4": ("dima", 12.05, 14.16),
    "G1": ("gena", 0.00, 1.62), "G2": ("gena", 2.88, 4.20), "G3": ("gena", 5.12, 5.85), "G4": ("gena", 6.94, 10.64),
}
TXT = {
    "A1": "ЭТО МОЙ БОРЩ!", "G1": "БЫЛ ТВОЙ.", "A2": "ДИМА! У НАС В ШКАФУ КТО-ТО ЖИВЁТ!",
    "D1": "НЕ ОРИ. ЭТО ГЕНА. ОН ТУТ ДО НАС ЖИЛ.", "A3": "ОН ЛЮДЕЙ ЕСТ!", "D2": "ЗАТО ЗА СВЕТ ПЛАТИТ ВОВРЕМЯ.",
    "G2": "И ПОСУДУ МОЮ.", "A4": "ДИМА, ОН С МЕНЯ МЕРКИ СНИМАЕТ!", "D3": "ЗНАЧИТ, ПОНРАВИЛСЯ. МНЕ ОН ШАРФ СВЯЗАЛ.",
    "G3": "ПОДВИНЬСЯ.", "A5": "ДИМА?", "D4": "ОН МЁРЗНЕТ. ПУСТИ.", "G4": "И СВЕТ НЕ ВЫКЛЮЧАЙ. Я ТЕМНОТЫ БОЮСЬ.",
}
WHO = {"A": ("АРТЁМ", "&H00A0E8B0&", "&H00406A50&"), "D": ("ДИМА", "&H00F5D49A&", "&H006A5A3A&"), "G": ("ГЕНА", "&H00E6E6E6&", "&H00404040&")}
# colours are ASS BGR: Artyom mint-green, Dima light blue, Gena white

# ---- shot list: (line or None for silent beat, image, beat_seconds, move)
# move: z0, z1, cx0, cy0, cx1, cy1, shake
S = [
    ("A1", "kitchen", 0, (1.0, 1.12, .5, .45, .6, .42, 0)),
    ("G1", "kitchen", 0, (1.9, 2.2, .28, .30, .28, .30, 0)),
    ("A2", "hall", 0, (1.9, 2.1, .18, .50, .18, .50, 1)),
    ("D1", "hall", 0, (1.9, 2.05, .83, .50, .83, .50, 0)),
    ("A3", "hall", 0, (1.0, 1.1, .5, .5, .5, .45, 1)),
    ("D2", "hall", 0, (2.0, 2.15, .83, .50, .83, .50, 0)),
    ("G2", "hall_plate", 0, (1.6, 1.8, .5, .36, .5, .34, 0)),
    ("A4", "hall_measure", 0, (1.0, 1.15, .55, .45, .6, .45, 1)),
    ("D3", "dima_scarf", 0, (1.0, 1.1, .5, .40, .5, .38, 0)),
    (None, "bed_dark", 1.4, (1.0, 1.1, .5, .45, .55, .45, 0)),
    ("G3", "bed_gena", 0, (1.2, 1.5, .6, .30, .62, .26, 0)),
    ("A5", "bed_dark", 0, (1.8, 2.0, .39, .55, .39, .55, 0)),
    ("D4", "black_eyes", 0, (1.0, 1.0, .5, .5, .5, .5, 0)),
    ("G4", "bed_lamp", 0, (1.0, 1.12, .5, .52, .45, .55, 0)),
]
GAP, TAIL = 0.22, 1.8

# ---- timeline
t = 0.35
timeline = []
for i, (line, img, beat, mv) in enumerate(S):
    st = t
    if line:
        f, a, b = SEG[line]
        dur = b - a
        timeline.append((line, st, dur))
        t = st + dur + GAP
    else:
        t = st + beat
    S[i] = (line, img, beat, mv, st)
END = t + TAIL

# ---- render shots
parts = []
for i, (line, img, beat, mv, st) in enumerate(S):
    st0 = 0.0 if i == 0 else st
    en = S[i + 1][4] if i + 1 < len(S) else END
    nf = round(en * FPS) - round(st0 * FPS)
    z0, z1, x0, y0, x1, y1, shake = mv
    p = f"(on/{max(nf-1,1)})"; ease = f"(1-pow(1-{p},2))"
    z = f"({z0}+({z1}-{z0})*{ease})"; cx = f"({x0}+({x1}-{x0})*{ease})"; cy = f"({y0}+({y1}-{y0})*{ease})"
    sh = f"+{shake*12}*sin(on*2.3)*max(0,1-on/12)" if shake else ""
    xs = f"max(0,min(iw-iw/zoom, iw*{cx}-iw/zoom/2{sh}))"
    ys = f"max(0,min(ih-ih/zoom, ih*{cy}-ih/zoom/2{sh.replace('sin','cos')}))"
    vf = f"zoompan=z='{z}':x='{xs}':y='{ys}':d={nf}:s={W}x{H}:fps={FPS},format=yuv420p"
    if i == len(S) - 1:
        vf += f",fade=t=out:st={nf/FPS-0.6:.2f}:d=0.6"
    fpath = f"{OUT}/shot{i:02d}.mp4"; parts.append(fpath)
    if "--keep" in sys.argv and os.path.exists(fpath):
        continue
    tmp = fpath + ".tmp.mp4"
    run(["ffmpeg", "-y", "-i", f"{ART}/{img}.png", "-vf", vf, "-frames:v", str(nf), *ENC, tmp])
    os.replace(tmp, fpath)
print("shots", len(parts), "end", round(END, 2))

# ---- dialogue track + ambience
def load(f):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{A}/{f}.mp3", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True)
    return np.frombuffer(r.stdout, dtype=np.float32)
src = {k: load(k) for k in ("artyom", "dima", "gena")}
n = int(END * SR); mix = np.zeros(n)
for line, st, dur in timeline:
    f, a, b = SEG[line]
    seg = src[f][int(a * SR):int(b * SR)].astype(np.float64)
    fade = int(0.02 * SR); seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
    gain = 1.0 if f != "gena" else 1.15
    i0 = int(st * SR); mix[i0:i0 + len(seg)] += seg[: n - i0] * gain
mix /= max(1e-6, np.abs(mix).max()); mix *= 0.85
rng = np.random.default_rng(3); tt = np.arange(n) / SR
amb = np.convolve(rng.standard_normal(n), np.ones(60) / 60, mode="same") * 0.6 + 0.08 * np.sin(2 * np.pi * 50 * tt)
amb /= np.abs(amb).max()
for line, st, dur in timeline:   # low stingers on Gena's first and whisper lines
    if line in ("G1", "G3"):
        i0 = int(st * SR); m = min(int(2.2 * SR), n - i0); x = np.arange(m) / SR
        amb[i0:i0 + m] += 2.0 * np.sin(2 * np.pi * 44 * x) * np.exp(-x * 1.8)
bed_start = [st for (line, img, beat, mv, st) in S if img == "bed_dark"][0]
lamp_start = [st for (line, img, beat, mv, st) in S if img == "bed_lamp"][0]
env = np.ones(n); env[int(bed_start * SR):int(lamp_start * SR)] = 0.45
final = np.clip(mix + 0.07 * amb * env, -1, 1)
with wave.open(f"{OUT}/mix.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((final * 32767).astype(np.int16).tobytes())

# ---- subtitles: POV label, speaker tag, chunked lines in speaker colour
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Sub,Montserrat Black,92,&H00FFFFFF,&H00FFFFFF,&H00111418,&H90000000,1,0,0,0,100,100,0,0,1,8,4,5,60,60,0",
       "Style: Tag,Montserrat Black,46,&H00111418,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,1,0,0,0,100,100,3,0,3,10,0,5,0,0,0",
       "Style: Pov,DejaVu Serif,44,&H00111418,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,1,0,0,0,100,100,0,0,3,16,0,8,0,0,190",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
ass.append(f"Dialogue: 3,{ts(0)},{ts(END)},Pov,,0,0,0,,POV: снял комнату за 9 тысяч")
for line, st, dur in timeline:
    name, col, tagbg = WHO[line[0]]
    words = TXT[line].split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w[-1] in ".!?,":
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    total = sum(len(" ".join(c)) for c in chunks)
    t0 = st
    ass.append(f"Dialogue: 2,{ts(st)},{ts(st+dur+0.15)},Tag,,0,0,0,,{{\\pos(540,1262)\\3c{tagbg}\\4c{tagbg}\\1c&HFFFFFF&}}{name}")
    for k, c in enumerate(chunks):
        d = dur * len(" ".join(c)) / total
        e = t0 + d + (0.15 if k == len(chunks) - 1 else 0)
        ass.append(f"Dialogue: 1,{ts(t0)},{ts(e)},Sub,,0,0,0,,{{\\pos(540,1370)\\1c{col}\\fscx85\\fscy85\\t(0,100,\\fscx100\\fscy100)}}{' '.join(c)}")
        t0 += d
open(f"{OUT}/subs.ass", "w").write("\n".join(ass) + "\n")

with open(f"{OUT}/list.txt", "w") as fh:
    for p_ in parts: fh.write(f"file '{p_}'\n")
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt", "-c", "copy", f"{OUT}/joined.mp4"])
if "--frames" in sys.argv: sys.exit(0)
tmp = f"{OUT}/final.tmp.mp4"
run(["ffmpeg", "-y", "-i", f"{OUT}/joined.mp4", "-i", f"{OUT}/mix.wav", "-filter_complex",
     f"[0:v]ass={OUT}/subs.ass[v];[1:a]loudnorm=I=-14:TP=-1.5:LRA=9[a]", "-map", "[v]", "-map", "[a]",
     *ENC, "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", "-t", f"{END:.2f}", tmp])
os.replace(tmp, f"{OUT}/final.mp4")
print("final ok")
