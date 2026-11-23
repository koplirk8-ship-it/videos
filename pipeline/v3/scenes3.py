"""Scenes for 'POV: снял комнату за 9 тысяч'. Dark, desaturated blue-grey night palette."""
import os, subprocess, random, sys
sys.path.insert(0, "/home/claude/v2")
from chars import shaded, path, fillp, circle, ell, O
import chars3 as c3

OUT = "/home/claude/v3/art"
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920

P = dict(wall="#36434d", wallS="#2b363f", wallL="#43525d", floor="#3b3330", floorS="#2e2826",
         cab="#4a5862", cabS="#3a464f", top="#5e6b73", tile="#3f4c56", win="#0e141d", moon="#d9dccd")

def svg(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{body}</svg>'

def save(name, s):
    p = f"{OUT}/{name}.svg"
    open(p, "w").write(s)
    subprocess.run(["rsvg-convert", "-w", str(W * 2), "-h", str(H * 2), p, "-o", f"{OUT}/{name}.png"], check=True)

def R(x, y, w, h, fill, rx=0, sw=6, stroke=O, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def G(inner, x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})">{inner}</g>'

GRAIN = ('<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="9"/>'
         '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.10 0"/></filter>'
         f'<rect width="{W}" height="{H}" filter="url(#grain)"/>')
VIG = ('<defs><radialGradient id="vig" cx="50%" cy="45%" r="75%"><stop offset="50%" stop-color="#000" stop-opacity="0"/>'
       '<stop offset="100%" stop-color="#000" stop-opacity="0.6"/></radialGradient></defs>'
       f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
FIN = VIG + GRAIN

def window(x, y, w, h):
    b = [R(x, y, w, h, P["win"], rx=8)]
    b.append(circle(x + w * 0.7, y + h * 0.3, w * 0.12, P["moon"], sw=0))
    rnd = random.Random(2)
    for i in range(6):
        bx = x + i * w / 6
        bh = rnd.uniform(0.2, 0.45) * h
        b.append(f'<rect x="{bx}" y="{y+h-bh}" width="{w/6-6}" height="{bh}" fill="#070a10"/>')
        for k in range(3):
            if rnd.random() < 0.35:
                b.append(f'<rect x="{bx+12}" y="{y+h-bh+20+k*30}" width="14" height="14" fill="#e8c96a" opacity="0.7"/>')
    b.append(R(x, y, w, h, "none", rx=8, sw=16, stroke="#5b6870"))
    b.append(R(x - 8, y - 8, w + 16, h + 16, "none", rx=12, sw=6))
    b.append(f'<line x1="{x+w/2}" y1="{y}" x2="{x+w/2}" y2="{y+h}" stroke="#5b6870" stroke-width="12"/>')
    b.append(R(x - 30, y + h + 8, w + 60, 26, "#5b6870", rx=6, sw=5))
    return "".join(b)

# ------------------------------------------------------------ KITCHEN
def kitchen_bg():
    b = [f'<rect width="{W}" height="{H}" fill="{P["wall"]}"/>']
    # tiles band
    for yy in range(700, 1200, 60):
        for xx in range(0 if (yy // 60) % 2 else -30, W, 60):
            b.append(f'<rect x="{xx}" y="{yy}" width="58" height="58" fill="{P["tile"]}" stroke="{P["wallS"]}" stroke-width="2"/>')
    # upper cabinets
    for x in (420, 640, 860):
        b.append(R(x, 250, 210, 380, P["cab"], rx=8)); b.append(R(x + 175, 420, 12, 60, "#a9b1b6", rx=6, sw=3))
    b.append(window(430, 720, 300, 330) if False else "")
    # counter + lower cabinets
    b.append(R(380, 1200, 720, 40, P["top"], rx=6))
    for x in (400, 620, 840):
        b.append(R(x, 1240, 210, 470, P["cab"], rx=6)); b.append(R(x + 90, 1270, 40, 12, "#a9b1b6", rx=6, sw=3))
    # stove kettle
    b.append(shaded("M560 1120 C560 1080 660 1080 660 1120 L670 1200 L550 1200 Z", "#6c7a83", lines=[("M570 1140 L650 1140", 3)]))
    b.append(path("M660 1130 q40 -10 50 -40", sw=8))
    # fridge (open) on the left
    b.append(R(20, 380, 330, 1330, "#c9cfd2", rx=20))
    b.append(f'<rect x="36" y="396" width="298" height="1298" rx="12" fill="#fff6d2"/>')
    for y in (700, 980, 1260):
        b.append(f'<line x1="40" y1="{y}" x2="330" y2="{y}" stroke="#d8cfa8" stroke-width="10"/>')
    b.append(R(70, 1180, 90, 80, "#d36b4c", rx=10, sw=4)); b.append(R(190, 900, 60, 80, "#7bb36a", rx=10, sw=4))
    # light spill on floor
    b.append(f'<polygon points="20,1710 350,1710 760,1920 0,1920" fill="#fff3c4" opacity="0.18"/>')
    b.append(f'<polygon points="350,400 350,1710 700,1500 640,500" fill="#fff3c4" opacity="0.06"/>')
    # floor
    b.append(f'<rect y="1710" width="{W}" height="210" fill="{P["floor"]}"/>')
    b.append(f'<line x1="0" y1="1710" x2="{W}" y2="1710" stroke="{O}" stroke-width="6"/>')
    # wall clock 03:12
    b.append(circle(300, 200, 56, "#d9d6cb", sw=6)); b.append(path("M300 200 L300 160 M300 200 L322 206", sw=5))
    return "".join(b)

def kitchen(art_expr="shout"):
    b = [kitchen_bg()]
    b.append(G(c3.gena("grin", "pot"), 300, 1800, 0.95))
    b.append(G(c3.guy("artyom", art_expr, "point"), 800, 1840, 1.12))
    b.append(FIN)
    return svg("".join(b))

# ------------------------------------------------------------ HALLWAY with wardrobe
def hall_bg():
    b = [f'<rect width="{W}" height="{H}" fill="#3a3f4f"/>']
    # diamond wallpaper
    for yy in range(0, 1700, 90):
        for xx in range(0, W + 90, 90):
            ox = 45 if (yy // 90) % 2 else 0
            b.append(f'<path d="M{xx+ox} {yy} l20 30 l-20 30 l-20 -30 Z" fill="#454b5d"/>')
    b.append(f'<rect y="1200" width="{W}" height="510" fill="#2f3a3f"/>')
    b.append(f'<line x1="0" y1="1200" x2="{W}" y2="1200" stroke="{O}" stroke-width="5"/>')
    # wardrobe, doors open, dark inside
    b.append(R(300, 260, 480, 1450, "#5a4636", rx=10))
    b.append(f'<rect x="330" y="300" width="420" height="1380" fill="#0b0c0f"/>')
    b.append(path("M340 360 L740 360", sw=8, stroke="#6c6a63"))
    for x in (380, 470, 640):
        b.append(path(f"M{x} 360 l-26 40 l52 0 Z", sw=4, stroke="#6c6a63"))
    b.append(R(150, 280, 160, 1420, "#6a5442", rx=8)); b.append(R(770, 280, 160, 1420, "#6a5442", rx=8))
    b.append(circle(290, 1000, 10, "#c9b37a", sw=3)); b.append(circle(790, 1000, 10, "#c9b37a", sw=3))
    # ceiling bulb
    b.append(path("M540 0 L540 90", sw=4))
    b.append(circle(540, 120, 34, "#f3e3a6", sw=5))
    b.append(f'<circle cx="540" cy="120" r="320" fill="#f3e3a6" opacity="0.07"/>')
    # runner rug + floor
    b.append(f'<rect y="1710" width="{W}" height="210" fill="{P["floor"]}"/>')
    b.append(f'<line x1="0" y1="1710" x2="{W}" y2="1710" stroke="{O}" stroke-width="6"/>')
    b.append(f'<polygon points="380,1710 700,1710 820,1920 260,1920" fill="#6e2e2b" stroke="{O}" stroke-width="5"/>')
    b.append(f'<polygon points="410,1730 670,1730 770,1900 310,1900" fill="none" stroke="#b9a061" stroke-width="5"/>')
    return "".join(b)

def hall(gena_arms="down", art_expr="panic", dima=True, gena_expr="grin"):
    b = [hall_bg()]
    b.append(G(c3.gena(gena_expr, gena_arms), 540, 1730, 0.95))
    b.append(G(c3.guy("artyom", art_expr, "head"), 180, 1880, 1.05))
    if dima:
        b.append(G(c3.guy("dima", "deadpan", "mug"), 900, 1880, 1.05))
    b.append(FIN)
    return svg("".join(b))

def hall_measure():
    b = [hall_bg()]
    b.append(G(c3.gena("grin", "measure"), 330, 1730, 0.95))
    b.append(G(c3.guy("artyom", "panic", "down"), 840, 1880, 1.05))
    b.append(FIN)
    return svg("".join(b))

def dima_scarf():
    b = [hall_bg()]
    b.append(f'<rect width="{W}" height="{H}" fill="#000" opacity="0.15"/>')
    b.append(G(c3.guy("dima", "deadpan_r", "mug", scarf=True), 540, 2600, 2.05))
    b.append(FIN)
    return svg("".join(b))

# ------------------------------------------------------------ BEDROOM
def bedroom(state="dark"):
    b = [f'<rect width="{W}" height="{H}" fill="#1f2731"/>']
    b.append(window(110, 260, 300, 380))
    # wardrobe right with door ajar
    b.append(R(640, 200, 420, 1300, "#3b3029", rx=10))
    b.append(f'<rect x="660" y="230" width="380" height="1250" fill="#050608"/>')
    b.append(R(700, 220, 360, 1270, "#4a3c32", rx=8))
    b.append(f'<polygon points="660,230 720,226 720,1486 660,1480" fill="#050608"/>')
    if state == "dark":
        b.append(circle(686, 620, 6, "#f4f1e6", sw=0)); b.append(circle(706, 622, 6, "#f4f1e6", sw=0))
        b.append(f'<circle cx="696" cy="620" r="30" fill="#f4f1e6" opacity="0.08"/>')
    # floor
    b.append(f'<rect y="1500" width="{W}" height="420" fill="#2a2321"/>')
    # bed: headboard, mattress, pillow, blanket (seen from foot, tilted)
    b.append(R(40, 860, 760, 260, "#5a4636", rx=20))
    b.append(R(30, 1080, 780, 560, "#d9d4c8", rx=30))
    if state == "lamp":
        # bedside lamp glow
        b.append(f'<circle cx="930" cy="1000" r="420" fill="#ffd98a" opacity="0.18"/>')
        b.append(R(860, 1100, 150, 400, "#4a3c32", rx=8))
        b.append(shaded("M880 960 L990 960 L1010 1040 L860 1040 Z", "#f1c96b"))
        b.append(R(925, 1040, 20, 60, "#3b3029", sw=4))
    pillow_y = 1060
    b.append(f'<ellipse cx="{260 if state == "lamp" else 420}" cy="{pillow_y}" rx="190" ry="70" fill="#eeeae0" stroke="{O}" stroke-width="6"/>')
    if state == "lamp":
        b.append(f'<ellipse cx="590" cy="{pillow_y}" rx="190" ry="70" fill="#eeeae0" stroke="{O}" stroke-width="6"/>')
    # heads on pillows
    if state in ("dark", "gena"):
        b.append(G(c3.guy_in_bed("scared"), 420, 1010, 1.1))
    elif state == "lamp":
        b.append(G(c3.guy_in_bed("deadpan"), 260, 1010, 1.05))
        b.append(G(c3.gena_head("shy"), 590, 1100, 0.95))
        b.append(G(c3.shaded("M-96 -170 C-100 -280 100 -280 96 -170 Z", "#b8362b", lines=[("M-60 -180 L-60 -250 M-20 -176 L-20 -264 M20 -176 L20 -264 M60 -180 L60 -250", 6)])
                   + c3.shaded("M-104 -190 L104 -190 L104 -150 L-104 -150 Z", "#e8e2d2") + c3.circle(0, -276, 28, "#e8e2d2"), 590, 1100, 0.95))
    # blanket
    b.append(shaded("M20 1150 C200 1120 640 1120 820 1150 L830 1650 L10 1650 Z", "#55708a",
                    [("M500 1100 L860 1100 L860 1660 L500 1660 Z", "#46607a")],
                    lines=[("M120 1300 Q300 1270 480 1310 M200 1480 Q420 1440 700 1490", 4)]))
    if state == "gena":
        # Gena leans out of the wardrobe over the bed
        b.append(G(c3.gena("grin", "down"), 700, 1900, 1.1))
    if state != "lamp":
        b.append(f'<rect width="{W}" height="{H}" fill="#03050a" opacity="0.45"/>')
        if state == "dark":
            b.append(circle(686, 620, 6, "#f4f1e6", sw=0)); b.append(circle(706, 622, 6, "#f4f1e6", sw=0))
    b.append(FIN)
    return svg("".join(b))

def black_eyes():
    b = [f'<rect width="{W}" height="{H}" fill="#020305"/>']
    b.append(circle(510, 820, 9, "#f4f1e6", sw=0)); b.append(circle(570, 822, 9, "#f4f1e6", sw=0))
    b.append(f'<circle cx="540" cy="820" r="80" fill="#f4f1e6" opacity="0.05"/>')
    b.append(GRAIN)
    return svg("".join(b))

scenes = {
    "kitchen": kitchen("shout"),
    "hall": hall(),
    "hall_plate": hall("plate"),
    "hall_measure": hall_measure(),
    "dima_scarf": dima_scarf(),
    "bed_dark": bedroom("dark"),
    "bed_gena": bedroom("gena"),
    "black_eyes": black_eyes(),
    "bed_lamp": bedroom("lamp"),
}

if __name__ == "__main__":
    want = set(sys.argv[1:])
    for k, v in scenes.items():
        if want and k not in want:
            continue
        save(k, v); print(k)
