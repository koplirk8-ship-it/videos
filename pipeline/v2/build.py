import json, os, subprocess, sys

ART = "/home/claude/v2/art2"
A = "/home/claude/v2/assets"
OUT = "/home/claude/v2/out2"
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
ENC = ["-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS)]
END = 69.2

# (start, image, label, move) ; move: (z0, z1, cx0, cy0, cx1, cy1, shake)
S = [
    (0.00, "man_close", None, (1.10, 1.30, .5, .46, .5, .46, 0)),
    (2.88, "katya_close_worried", None, (1.10, 1.25, .5, .50, .5, .50, 0)),
    (4.24, "exterior", "ЛЕНИНГРАД · ОСЕНЬ 1979", (1.00, 1.18, .5, .45, .5, .42, 0)),
    (6.80, "katya_close_calm", "КАТЯ · 16 ЛЕТ", (1.05, 1.15, .5, .52, .5, .50, 0)),
    (8.88, "corridor_empty", "ПОСЛЕДНЯЯ ЭЛЕКТРИЧКА", (1.00, 1.12, .5, .5, .55, .5, 0)),
    (11.68, "corridor_man", "ПОЧТИ ПУСТОЙ", (1.6, 2.6, .5, .38, .5, .37, 1)),
    (13.50, "corridor_man", None, (1.15, 1.35, .5, .45, .5, .42, 0)),
    (15.04, "seats60", None, (1.00, 1.08, .5, .4, .5, .4, 0)),
    (16.48, "two_shot", "НАПРОТИВ ТЕБЯ", (1.05, 1.18, .5, .62, .5, .62, 0)),
    (18.32, "rule1_0", None, (1.0, 1.0, .5, .5, .5, .5, 0)),
    (19.52, "rule1_1", None, (1.0, 1.0, .5, .5, .5, .5, 0)),
    (21.84, "rule1_2", None, (1.0, 1.0, .5, .5, .5, .5, 0)),
    (23.41, "corridor_empty", None, (1.2, 1.9, .5, .45, .5, .40, 0)),
    (25.92, "door_locked", "СОСЕДНИЙ ВАГОН", (1.0, 1.12, .5, .5, .55, .55, 1)),
    (27.01, "man_close", "ОН УЛЫБАЕТСЯ", (1.15, 1.35, .5, .46, .5, .44, 0)),
    (29.60, "man_close_grin_q", None, (1.00, 1.06, .5, .5, .5, .5, 0)),
    (31.28, "rule2_0", None, (1.0, 1.0, .5, .5, .5, .5, 0)),
    (32.40, "rule2_1", None, (1.0, 1.0, .5, .5, .5, .5, 0)),
    (33.76, "rule2_2", None, (1.0, 1.0, .5, .5, .5, .5, 0)),
    (34.64, "katya_close_lie", None, (1.00, 1.06, .5, .5, .5, .5, 0)),
    (36.32, "man_close_grin_me", None, (1.00, 1.08, .5, .5, .5, .5, 0)),
    (38.08, "reflection", "В СТЕКЛЕ", (1.0, 1.3, .5, .5, .5, .38, 0)),
    (41.12, "man_close_stare", None, (1.5, 1.8, .5, .45, .5, .44, 0)),
    (42.16, "two_shot_stare", "ОН СМОТРИТ НА СУМКУ", (1.10, 1.30, .5, .62, .65, .62, 0)),
    (43.84, "bag_pass", "ТВОЯ СТАНЦИЯ", (1.0, 1.25, .5, .4, .45, .28, 0)),
    (46.88, "rule3_0", None, (1.0, 1.0, .5, .5, .5, .5, 0)),
    (48.00, "rule3_1", None, (1.0, 1.0, .5, .5, .5, .5, 0)),
    (49.12, "rule3_2", None, (1.0, 1.0, .5, .5, .5, .5, 0)),
    (51.68, "intercom", "ТАМБУР", (1.0, 1.1, .5, .5, .5, .55, 0)),
    (52.08, "intercom_press", None, (1.1, 1.2, .5, .58, .5, .6, 1)),
    (53.92, "katya_close_scared", "ТИШИНА", (1.2, 1.4, .5, .5, .5, .49, 0)),
    (54.80, "exterior_side", None, (1.15, 1.0, .55, .6, .5, .58, 1)),
    (56.13, "platform", "НИ ОДНОГО ФОНАРЯ", (1.0, 1.15, .5, .45, .5, .45, 0)),
    (60.08, "man_stands", None, (1.0, 1.25, .5, .40, .5, .32, 0)),
    (61.20, "platform_man", None, (1.0, 1.2, .5, .45, .5, .42, 0)),
    (63.20, "choice", "ЧТО ВЫБЕРЕШЬ?", (1.0, 1.05, .5, .5, .5, .5, 0)),
]

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(" ".join(cmd)[:400]); print(r.stderr[-3000:]); sys.exit(1)

only = set(a for a in sys.argv[1:] if a.isdigit())
parts = []
for i, (s, img, label, mv) in enumerate(S):
    e = S[i + 1][0] if i + 1 < len(S) else END
    f0, f1 = round(s * FPS), round(e * FPS)
    nf = f1 - f0
    z0, z1, x0, y0, x1, y1, shake = mv
    p = f"(on/{max(nf-1,1)})"
    ease = f"(1-pow(1-{p},2))"
    z = f"({z0}+({z1}-{z0})*{ease})"
    cx = f"({x0}+({x1}-{x0})*{ease})"
    cy = f"({y0}+({y1}-{y0})*{ease})"
    sh = f"+{shake*14}*sin(on*2.1)*(1-{p})" if shake else ""
    xs = f"max(0,min(iw-iw/zoom, iw*{cx}-iw/zoom/2{sh}))"
    ys = f"max(0,min(ih-ih/zoom, ih*{cy}-ih/zoom/2{sh.replace('sin','cos')}))"
    vf = f"zoompan=z='{z}':x='{xs}':y='{ys}':d={nf}:s={W}x{H}:fps={FPS},format=yuv420p"
    if i == len(S) - 1:
        vf += f",fade=t=out:st={nf/FPS-0.5:.2f}:d=0.5"
    f = f"{OUT}/shot{i:02d}.mp4"
    parts.append(f)
    if (only and str(i) not in only and os.path.exists(f)) or ("--keep" in sys.argv and os.path.exists(f)):
        continue
    tmp = f"{OUT}/shot{i:02d}.tmp.mp4"
    run(["ffmpeg", "-y", "-i", f"{ART}/{img}.png", "-vf", vf, "-frames:v", str(nf), *ENC, tmp])
    os.replace(tmp, f)
print("shots ok", len(parts))

# ---------- subtitles
words = [w for w in json.load(open(f"{A}/words.json"))["words"] if w["type"] == "word"]
clean, skip = [], False
for w in words:
    t = w["text"]
    if skip or t.startswith("["):
        skip = not t.endswith("]")
        continue
    if t == "—":
        continue
    clean.append(w)

NUMS = {"семьдесят": None}
for i in range(len(clean) - 1):
    if clean[i]["text"] == "семьдесят" and clean[i + 1]["text"].startswith("девятого"):
        clean[i:i + 2] = [{"text": "79-го.", "start": clean[i]["start"], "end": clean[i + 1]["end"]}]
        break
for w in clean:
    if w["text"].startswith("шестьдесят"):
        w["text"] = "60."
    if w["text"].startswith("шестнадцать"):
        w["text"] = "16."

chunks, cur = [], []
for w in clean:
    cur.append(w)
    t = w["text"]
    if len(cur) >= 3 or t[-1] in ".,?!:»" or t.endswith("?»"):
        chunks.append(cur); cur = []
if cur: chunks.append(cur)

RED = {"НАПРОТИВ", "ЗАПЕРТА", "ДОЧКА", "ОТРАЖЕНИЕ", "МОРГАЕТ", "СТАНЦИЕЙ", "ТИШИНА", "ВСТАЁТ", "ТЕМНОТУ", "ВДВОЁМ", "ПОЧТИ", "ЗАСЫПАЙ", "ЛЮДИ", "СТАНЦИЮ", "МАШИНИСТА", "Я"}

def ts(x):
    return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"

def clean_txt(t):
    return t.replace("«", "").replace("»", "").rstrip(".,:").upper()

ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Sub,Montserrat Black,96,&H00FFFFFF,&H00FFFFFF,&H00171A23,&H90000000,1,0,0,0,100,100,0,0,1,8,4,5,70,70,0",
       "Style: Label,Montserrat Black,62,&H00FFFFFF,&H00FFFFFF,&H00171A23,&H00171A23,1,0,0,0,100,100,2,0,3,16,0,8,60,60,250",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]

for i, (s, img, label, mv) in enumerate(S):
    if label:
        e = S[i + 1][0] if i + 1 < len(S) else END
        ass.append(f"Dialogue: 2,{ts(s)},{ts(e)},Label,,0,0,0,,{label}")

for k, c in enumerate(chunks):
    s = c[0]["start"]
    e = chunks[k + 1][0]["start"] if k + 1 < len(chunks) else c[-1]["end"] + 1.2
    e = min(e, c[-1]["end"] + 0.5)
    parts_txt = []
    for w in c:
        t = clean_txt(w["text"])
        d = int((w["start"] - s) * 1000)
        hi = "&H3A3AE6&" if t in RED else "&H00D7FF&"
        parts_txt.append(f"{{\\1c&HFFFFFF&\\t({d},{d+1},\\1c{hi})}}{t}")
    shot_img = [im for (st, im, lb, mv) in S if st <= s + 1e-6][-1]
    ypos = 1200 if shot_img == "choice" or shot_img.startswith("rule") else 1430
    body = "{\\pos(540," + str(ypos) + ")\\fscx85\\fscy85\\t(0,110,\\fscx100\\fscy100)}" + " ".join(parts_txt)
    ass.append(f"Dialogue: 1,{ts(s)},{ts(e)},Sub,,0,0,0,,{body}")
open(f"{OUT}/subs.ass", "w").write("\n".join(ass) + "\n")

with open(f"{OUT}/list.txt", "w") as fh:
    for p in parts: fh.write(f"file '{p}'\n")
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt", "-c", "copy", f"{OUT}/joined.mp4"])
if "--frames" in sys.argv:
    sys.exit(0)

# ---------- sound bed (numpy): train rumble + wheel clacks, braking, stingers, hiss
import numpy as np, wave
SR = 44100
n = int(END * SR); t = np.arange(n) / SR
rng = np.random.default_rng(1)
BRAKE = 54.8
brown = np.cumsum(rng.standard_normal(n)); brown -= np.convolve(brown, np.ones(4410)/4410, mode="same")
brown /= np.abs(brown).max()
env = np.where(t < BRAKE, 1.0, np.clip(1 - (t - BRAKE) / 3.5, 0, 1))
bed = 0.5 * brown * env
per = 0.92
for k in range(int(BRAKE / per) + 2):
    for off in (0.0, 0.14):
        t0 = k * per + off
        if t0 > BRAKE + 1.2: break
        i0 = int(t0 * SR); m = min(int(0.12 * SR), n - i0)
        tt = np.arange(m) / SR
        bed[i0:i0+m] += 0.35 * np.sin(2*np.pi*95*tt) * np.exp(-tt*35) + 0.15 * rng.standard_normal(m) * np.exp(-tt*60)
for x in (11.68, 25.92, 41.12, 60.08, 61.2):
    i0 = int(x * SR); m = min(int(2.5 * SR), n - i0); tt = np.arange(m) / SR
    bed[i0:i0+m] += 0.9 * np.sin(2*np.pi*46*tt) * np.exp(-tt*1.8) + 0.25 * rng.standard_normal(m) * np.exp(-tt*12)
i0, i1 = int(52.9 * SR), int(53.9 * SR)
hiss = rng.standard_normal(i1 - i0); hiss = hiss - np.convolve(hiss, np.ones(8)/8, mode="same")
bed[i0:i1] += 0.5 * hiss * np.hanning(i1 - i0)
bed = np.clip(bed / np.abs(bed).max() * 0.8, -1, 1)
with wave.open(f"{OUT}/bed.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((bed * 32767).astype(np.int16).tobytes())
fc = (f"[1:a]apad,atrim=0:{END},loudnorm=I=-15:TP=-1.5:LRA=9[v];"
      f"[2:a]volume=0.22[bed];"
      f"[v][bed]amix=inputs=2:normalize=0,alimiter=limit=0.95[a];"
      f"[0:v]ass={OUT}/subs.ass[vv]")
tmp = f"{OUT}/final.tmp.mp4"
run(["ffmpeg", "-y", "-i", f"{OUT}/joined.mp4", "-i", f"{A}/voice.mp3", "-i", f"{OUT}/bed.wav", "-filter_complex", fc,
     "-map", "[vv]", "-map", "[a]", *ENC, "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
     "-movflags", "+faststart", "-t", str(END), tmp])
os.replace(tmp, f"{OUT}/final.mp4")
print("final ok")
