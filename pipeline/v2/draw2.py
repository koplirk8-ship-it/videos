"""v2 art: reference-style characters + better cartoon ER2 train and carriage."""
import os, subprocess, random
import chars
from chars import shaded, path, fillp, circle, ell, O

OUT = "/home/claude/v2/art2"
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920
SW = 6

C = dict(
    cream="#e2d6b4", creamS="#c9bc97", green="#5f7f6c", greenS="#4b6857", ceil="#ece6d2", ceilS="#d4ccb2",
    floor="#6d4f3a", floorS="#57402f", strip="#8a6a4f",
    wood="#c46a35", woodS="#9c4f24", woodL="#d98547", metal="#b7b9b2", metalS="#8d8f88",
    lamp="#fff4c2", glow="#ffe9a0", win="#141c2b", winL="#22304a", frame="#d8d0b4", frameS="#b4ab8c",
    night="#0d1320", navy="#141a2a", red="#d23a2f", green2="#3fae5a", yellow="#ffd23a",
    trainG="#3c6b4c", trainGS="#2c5039", trainR="#b8362b", trainRS="#8e271f", trainY="#e8c13a",
)

def svg(body, bg="#000"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="{bg}"/>{body}</svg>')

def save(name, s):
    p = f"{OUT}/{name}.svg"
    open(p, "w").write(s)
    subprocess.run(["rsvg-convert", "-w", str(W * 2), "-h", str(H * 2), p, "-o", f"{OUT}/{name}.png"], check=True)

def R(x, y, w, h, fill, rx=0, sw=SW, stroke=O, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def poly(pts, fill, sw=SW, stroke=O, extra=""):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>'

def T(x, y, text, size, fill="#fff", weight=900, anchor="middle", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="Montserrat" font-weight="{weight}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{text}</text>')

def G(inner, x=0, y=0, s=1, extra=""):
    return f'<g transform="translate({x},{y}) scale({s})" {extra}>{inner}</g>'

GRAIN = ('<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="4"/>'
         '<feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.09 0"/></filter>'
         f'<rect width="{W}" height="{H}" filter="url(#grain)"/>')
VIG = ('<defs><radialGradient id="vig" cx="50%" cy="45%" r="75%"><stop offset="55%" stop-color="#000" stop-opacity="0"/>'
       '<stop offset="100%" stop-color="#000" stop-opacity="0.5"/></radialGradient></defs>'
       f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
FIN = VIG + GRAIN

def bubble(x, y, w, lines, tag=None, tail="down", size=46):
    """Speech bubble like the reference: white rounded box, small dark tag pill, tail."""
    h = 40 + size * 1.25 * len(lines)
    b = [R(x, y, w, h, "#fbf8f0", rx=26, sw=6)]
    tx = x + w * 0.5
    if tail == "down":
        b.append(poly([(tx - 26, y + h - 3), (tx + 26, y + h - 3), (tx + 4, y + h + 44)], "#fbf8f0", sw=0))
        b.append(path(f"M{tx-26} {y+h} L{tx+4} {y+h+44} L{tx+26} {y+h}", sw=6))
    for i, ln in enumerate(lines):
        b.append(T(x + w / 2, y + 22 + size * 1.05 + i * size * 1.25, ln, size, O, 800))
    if tag:
        tw = 26 * len(tag) + 50
        b.append(R(x + 26, y - 26, tw, 50, O, rx=25, sw=0))
        b.append(T(x + 26 + tw / 2, y + 10, tag, 30, "#fff", 900))
    return "".join(b)

def night_outside(x, y, w, h, seed=3, speed=True, moon=True):
    rnd = random.Random(seed)
    b = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C["win"]}"/>']
    if moon:
        b.append(f'<circle cx="{x+w*0.76}" cy="{y+h*0.22}" r="{max(10,w*0.06)}" fill="#dfe0cf" opacity="0.85"/>')
    for i in range(18):
        tx = x + i * w / 14 + rnd.uniform(-15, 15)
        th = h * rnd.uniform(0.3, 0.55); tw = w * 0.07
        b.append(f'<polygon points="{tx},{y+h-th} {tx-tw},{y+h} {tx+tw},{y+h}" fill="#070b13"/>')
    if speed:
        for i in range(6):
            yy = y + h * (0.12 + 0.12 * i)
            b.append(f'<line x1="{x+rnd.uniform(0,w*.4)}" y1="{yy}" x2="{x+rnd.uniform(w*.6,w)}" y2="{yy}" stroke="#3b4762" stroke-width="3" opacity="0.5"/>')
    return "".join(b)

# =========================================================== CARRIAGE INTERIOR (1-point perspective)
VPX, VPY = 540, 760
FW, FH = 150, 190          # half-size of far end section

def sec(t):
    """Cross-section rectangle at depth t (0 far .. 1 near): L, R, Top, Bottom."""
    L = VPX - FW + (0 - (VPX - FW)) * t
    Rr = VPX + FW + (W - (VPX + FW)) * t
    Tp = VPY - FH + (0 - (VPY - FH)) * t
    B = VPY + FH + (H - (VPY + FH)) * t
    return L, Rr, Tp, B

def at(t, u, v):
    """Point in section t at fractional (u across 0..1 left->right, v down 0..1 top->bottom)."""
    L, Rr, Tp, B = sec(t)
    return L + (Rr - L) * u, Tp + (B - Tp) * v

def interior(lamps="on", katya_seat=None, man_far=False, man_aisle=None, dim=0.0):
    b = []
    # shells
    b.append(poly([at(0, 0, 0), at(0, 1, 0), at(1, 1, 0), at(1, 0, 0)], C["ceil"], sw=0))
    b.append(poly([at(0, 0, 1), at(0, 1, 1), at(1, 1, 1), at(1, 0, 1)], C["floor"], sw=0))
    b.append(poly([at(0, .44, 1), at(0, .56, 1), at(1, .62, 1), at(1, .38, 1)], C["strip"], sw=0))
    for side in (0, 1):
        b.append(poly([at(0, side, 0), at(1, side, 0), at(1, side, 1), at(0, side, 1)], C["cream"], sw=0))
        b.append(poly([at(0, side, .55), at(1, side, .55), at(1, side, 1), at(0, side, 1)], C["green"], sw=0))
        b.append(f'<line x1="{at(0,side,.55)[0]}" y1="{at(0,side,.55)[1]}" x2="{at(1,side,.55)[0]}" y2="{at(1,side,.55)[1]}" stroke="{O}" stroke-width="4"/>')
    # ceiling ribs
    for t in (0.1, 0.25, 0.42, 0.62, 0.85):
        b.append(f'<line x1="{at(t,0,0)[0]}" y1="{at(t,0,0)[1]}" x2="{at(t,1,0)[0]}" y2="{at(t,1,0)[1]}" stroke="{C["ceilS"]}" stroke-width="{2+6*t}"/>')
    # far end: door with window into next car
    L, Rr, Tp, B = sec(0)
    b.append(poly([at(0, 0, 0), at(0, 1, 0), at(0, 1, 1), at(0, 0, 1)], C["creamS"], sw=4))
    b.append(R(VPX - 58, Tp + 40, 116, B - Tp - 40, C["greenS"], rx=6, sw=4))
    b.append(R(VPX - 40, Tp + 60, 80, 110, C["win"], rx=6, sw=3))
    if man_far:
        b.append(G(chars.man("stare", "stand"), VPX, Tp + 250, 0.24))
    # floor boards
    for k in range(-5, 6):
        x0 = VPX + k * 26; x1 = W / 2 + k * 200
        b.append(f'<line x1="{x0}" y1="{VPY+FH}" x2="{x1}" y2="{H}" stroke="{C["floorS"]}" stroke-width="3" opacity="0.6"/>')

    # windows + racks on both walls
    bays = [0.05, 0.17, 0.32, 0.5, 0.72, 0.98]
    for side in (0, 1):
        for i in range(len(bays) - 1):
            t0, t1 = bays[i] + 0.02, bays[i + 1] - 0.02
            p = [at(t0, side, .2), at(t1, side, .2), at(t1, side, .5), at(t0, side, .5)]
            b.append(poly(p, C["win"], sw=0))
            # glass sheen
            b.append(poly([at(t0 + (t1 - t0) * .1, side, .22), at(t0 + (t1 - t0) * .25, side, .22), at(t0 + (t1 - t0) * .15, side, .48), at(t0, side, .48)], C["winL"], sw=0, extra='opacity="0.7"'))
            b.append(poly(p, "none", sw=4 + 14 * t1, stroke=C["frame"]))
            b.append(poly(p, "none", sw=3))
            mid = [at(t0, side, .29), at(t1, side, .29)]
            b.append(f'<line x1="{mid[0][0]}" y1="{mid[0][1]}" x2="{mid[1][0]}" y2="{mid[1][1]}" stroke="{C["frame"]}" stroke-width="{3+10*t1}"/>')
        # luggage rack: rail along wall + front bar
        for v, u_in in ((.14, 0.0), (.15, 0.09)):
            u = side + (u_in if side == 0 else -u_in)
            a0 = at(0.03, u, v); a1 = at(1.0, u, v)
            b.append(f'<line x1="{a0[0]}" y1="{a0[1]}" x2="{a1[0]}" y2="{a1[1]}" stroke="{C["metalS"]}" stroke-width="10"/>')
            b.append(f'<line x1="{a0[0]}" y1="{a0[1]}" x2="{a1[0]}" y2="{a1[1]}" stroke="{C["metal"]}" stroke-width="5"/>')
        for t in bays:
            u2 = 0.09 if side == 0 else 0.91
            p0, p1 = at(t, side, .12), at(t, u2, .15)
            b.append(f'<line x1="{p0[0]}" y1="{p0[1]}" x2="{p1[0]}" y2="{p1[1]}" stroke="{C["metalS"]}" stroke-width="{2+6*t}"/>')

    # lamps (dome lights along the centre)
    for t in (0.08, 0.22, 0.4, 0.62, 0.9):
        cx, cy = at(t, .5, .035)
        rw = 22 + 150 * t; rh = 6 + 26 * t
        on = lamps == "on" or (lamps == "flicker" and t not in (0.4,))
        col = C["lamp"] if on else "#8b8771"
        if on:
            b.append(f'<ellipse cx="{cx}" cy="{cy+rh}" rx="{rw*2.2}" ry="{rh*6}" fill="{C["glow"]}" opacity="0.16"/>')
        b.append(ell(cx, cy, rw, rh, col, sw=2 + 4 * t))

    # benches: each bay has a back panel at far edge (seat faces viewer) and one at near edge (faces away)
    def bench(t_back, t_seat, side, facing_viewer):
        u0, u1 = (0.0, 0.36) if side == 0 else (0.64, 1.0)
        g = []
        # seat slab (horizontal, at v=.80) between t_back and t_seat
        sa, sb = sorted((t_back, t_seat))
        g.append(poly([at(sa, u0, .8), at(sa, u1, .8), at(sb, u1, .8), at(sb, u0, .8)], C["woodL"], sw=2 + 4 * sb))
        # seat front edge (only visible on near side)
        g.append(poly([at(sb, u0, .8), at(sb, u1, .8), at(sb, u1, .84), at(sb, u0, .84)], C["woodS"], sw=2 + 4 * sb))
        # legs
        for uu in ((u0 + 0.06, u1 - 0.04) if side == 0 else (u0 + 0.04, u1 - 0.06)):
            p0 = at(sb, uu, .84); p1 = at(sb, uu, 1.0)
            g.append(f'<line x1="{p0[0]}" y1="{p0[1]}" x2="{p1[0]}" y2="{p1[1]}" stroke="{O}" stroke-width="{3+8*sb}"/>')
        # back panel (frontal rect at t_back) from v .52 to .8, rounded top, slats
        x0, y0 = at(t_back, u0, .56); x1, y1 = at(t_back, u1, .8)
        rr = 6 + 30 * t_back
        fill = C["wood"] if facing_viewer else C["woodS"]
        g.append(R(min(x0, x1), y0, abs(x1 - x0), y1 - y0, fill, rx=rr, sw=2 + 4 * t_back))
        for k in range(1, 4):
            yy = y0 + (y1 - y0) * k / 4
            g.append(f'<line x1="{min(x0,x1)+rr*.6}" y1="{yy}" x2="{max(x0,x1)-rr*.6}" y2="{yy}" stroke="{C["woodS"]}" stroke-width="{2+4*t_back}"/>')
        return "".join(g)

    for i in range(len(bays) - 1):
        ta, tb = bays[i], bays[i + 1]
        for side in (0, 1):
            b.append(bench(ta + 0.01, ta + (tb - ta) * 0.38, side, True))
            if katya_seat is not None and katya_seat[0] == i and katya_seat[1] == side:
                tk = ta + (tb - ta) * 0.25
                kx, ky = at(tk, 0.18 if side == 0 else 0.82, .8)
                sc = (sec(tk)[1] - sec(tk)[0]) / 1080 * 0.55
                b.append(G(chars.katya(katya_seat[2], katya_seat[3]), kx, ky - 30 * sc, sc))
            if not (katya_seat is not None and katya_seat[0] == i and katya_seat[1] == side):
                b.append(bench(tb - 0.01, tb - (tb - ta) * 0.38, side, False))

    if man_aisle:
        t, expr = man_aisle
        mx, my = at(t, .5, 1.0)
        sc = (sec(t)[1] - sec(t)[0]) / 1080 * 0.9
        b.append(G(chars.man(expr, "stand"), mx, my - 470 * sc, sc))
    if dim:
        b.append(f'<rect width="{W}" height="{H}" fill="#05070c" opacity="{dim}"/>')
    return "".join(b)

# =========================================================== SIDE VIEW (two-shot & close-ups)
def side_wall(win_x=70, win_y=300, win_w=940, win_h=560, rack=True, refl=None, dim=0.0):
    b = [f'<rect width="{W}" height="{H}" fill="{C["cream"]}"/>',
         f'<rect y="980" width="{W}" height="700" fill="{C["green"]}"/>',
         f'<line x1="0" y1="980" x2="{W}" y2="980" stroke="{O}" stroke-width="5"/>',
         f'<rect width="{W}" height="120" fill="{C["ceil"]}"/>',
         f'<line x1="0" y1="120" x2="{W}" y2="120" stroke="{O}" stroke-width="5"/>']
    # wall panel seams + rivets
    for x in (40, W - 40):
        b.append(f'<line x1="{x}" y1="120" x2="{x}" y2="980" stroke="{C["creamS"]}" stroke-width="4"/>')
    if rack:
        b.append(R(30, 175, W - 60, 22, C["metal"], rx=11, sw=5))
        b.append(R(30, 225, W - 60, 16, C["metal"], rx=8, sw=4))
        for x in range(90, W - 60, 180):
            b.append(f'<line x1="{x}" y1="186" x2="{x}" y2="233" stroke="{C["metalS"]}" stroke-width="6"/>')
        b.append(path("M60 186 L60 290 L40 290", sw=6, stroke=C["metalS"]))
        b.append(path(f"M{W-60} 186 L{W-60} 290 L{W-40} 290", sw=6, stroke=C["metalS"]))
    # window: frame, glass, upper sliding pane
    cid = chars.uid("w")
    b.append(f'<clipPath id="{cid}"><rect x="{win_x}" y="{win_y}" width="{win_w}" height="{win_h}" rx="30"/></clipPath>')
    b.append(f'<g clip-path="url(#{cid})">{night_outside(win_x, win_y, win_w, win_h)}')
    if refl:
        b.append(f'<g opacity="0.32">{refl}</g>')
    b.append(f'<polygon points="{win_x+60},{win_y} {win_x+170},{win_y} {win_x+40},{win_y+win_h} {win_x-70},{win_y+win_h}" fill="#ffffff" opacity="0.05"/>')
    b.append('</g>')
    b.append(R(win_x, win_y, win_w, win_h, "none", rx=30, sw=28, stroke=C["frame"]))
    b.append(R(win_x - 14, win_y - 14, win_w + 28, win_h + 28, "none", rx=42, sw=6))
    b.append(R(win_x + 14, win_y + 14, win_w - 28, win_h - 28, "none", rx=18, sw=4))
    b.append(R(win_x + 10, win_y + win_h * 0.3 - 10, win_w - 20, 20, C["frame"], sw=4))
    b.append(R(win_x + win_w / 2 - 40, win_y + win_h * 0.3 - 22, 80, 22, C["metal"], rx=6, sw=4))
    b.append(R(win_x - 30, win_y + win_h + 14, win_w + 60, 26, C["frameS"], rx=8, sw=5))
    # lamp glow
    b.append(f'<ellipse cx="540" cy="110" rx="520" ry="140" fill="{C["glow"]}" opacity="0.15"/>')
    b.append(ell(540, 108, 170, 22, C["lamp"], sw=5))
    b.append(f'<rect y="1680" width="{W}" height="240" fill="{C["floor"]}"/>')
    b.append(f'<line x1="0" y1="1680" x2="{W}" y2="1680" stroke="{O}" stroke-width="5"/>')
    return "".join(b)

def bench_front(x0, x1, y_seat):
    """Wooden bench seen from the front (seat edge + slatted back behind sitter)."""
    b = [R(x0, y_seat - 420, x1 - x0, 420, C["wood"], rx=30)]
    for k in range(1, 6):
        yy = y_seat - 420 + k * 70
        b.append(f'<line x1="{x0+14}" y1="{yy}" x2="{x1-14}" y2="{yy}" stroke="{C["woodS"]}" stroke-width="6"/>')
    return "".join(b)

def bench_seat(x0, x1, y_seat):
    b = [R(x0 - 16, y_seat, x1 - x0 + 32, 46, C["woodL"], rx=14),
         R(x0 - 10, y_seat + 46, x1 - x0 + 20, 30, C["woodS"], rx=8)]
    for xx in (x0 + 30, x1 - 50):
        b.append(R(xx, y_seat + 76, 22, 1680 - y_seat - 76, C["metalS"], sw=4))
    return "".join(b)

scenes = {}

def two_shot(man_expr="smile", k_expr="worried", hands="lap", dim=0.0, bub=None):
    b = [side_wall()]
    b.append(bench_front(20, 520, 1330)); b.append(bench_front(560, 1060, 1330))
    b.append(G(chars.man(man_expr, "sit"), 275, 1300, 0.9))
    b.append(G(chars.katya(k_expr, hands), 805, 1300, 0.9))
    b.append(bench_seat(20, 520, 1330)); b.append(bench_seat(560, 1060, 1330))
    if dim:
        b.append(f'<rect width="{W}" height="{H}" fill="#05070c" opacity="{dim}"/>')
    if bub:
        b.append(bub)
    b.append(FIN)
    return svg("".join(b))

scenes["two_shot"] = two_shot()
scenes["two_shot_grin"] = two_shot("grin", "scared", "bag")
scenes["two_shot_stare"] = two_shot("stare", "worried", "bag", dim=0.3)

def man_close(expr="smile", dim=0.0, bub=None):
    b = [side_wall(win_x=-40, win_y=230, win_w=1160, win_h=760, rack=False)]
    b.append(G(chars.man(expr, "sit"), 540, 1960, 2.05))
    if dim:
        b.append(f'<rect width="{W}" height="{H}" fill="#05070c" opacity="{dim}"/>')
    if bub:
        b.append(bub)
    b.append(FIN)
    return svg("".join(b))

scenes["man_close"] = man_close("smile")
scenes["man_close_grin"] = man_close("grin")
scenes["man_close_grin_q"] = man_close("grin", bub=bubble(150, 230, 780, ["До какой едешь,", "дочка?"], tag="ОН", size=54))
scenes["man_close_grin_me"] = man_close("smile", bub=bubble(200, 260, 680, ["Надо же. И я."], tag="ОН", size=58))
scenes["man_close_stare"] = man_close("stare", dim=0.4)

def katya_close(expr="worried", bub=None):
    b = [side_wall(win_x=-40, win_y=230, win_w=1160, win_h=760, rack=False)]
    b.append(G(chars.katya(expr, "lap"), 540, 1990, 2.1))
    if bub:
        b.append(bub)
    b.append(FIN)
    return svg("".join(b))

scenes["katya_close_worried"] = katya_close("worried")
scenes["katya_close_scared"] = katya_close("scared")
scenes["katya_close_calm"] = katya_close("calm")
scenes["katya_close_lie"] = katya_close("worried", bub=bubble(240, 260, 600, ["До конечной."], tag="ТЫ", size=56))

def corridor(man_far=False):
    return svg(interior(katya_seat=(4, 1, "calm", "bag"), man_far=man_far) + FIN)

scenes["corridor_empty"] = corridor()
scenes["corridor_man"] = corridor(True)

def seats60():
    b = [interior(man_far=True), f'<rect width="{W}" height="{H}" fill="#000" opacity="0.25"/>']
    b.append(R(290, 230, 500, 240, "#fbf8f0", rx=30))
    b.append(T(540, 385, "60", 170, O)); b.append(T(540, 440, "СВОБОДНЫХ МЕСТ", 40, O))
    b.append(FIN)
    return svg("".join(b))
scenes["seats60"] = seats60()

scenes["man_stands"] = svg(interior(lamps="flicker", man_aisle=(0.62, "stare"), dim=0.3) + FIN)

def reflection():
    refl = G(chars.man("stare", "sit"), 560, 1900, 2.0)
    b = [side_wall(win_x=50, win_y=200, win_w=980, win_h=1380, rack=False, refl=refl)]
    b.append(FIN)
    return svg("".join(b))
scenes["reflection"] = reflection()

# =========================================================== TRAIN EXTERIORS
def train_front():
    """ER2 commuter train approaching at night along a platform, headlights on."""
    rnd = random.Random(11)
    b = ['<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0f1d"/>'
         '<stop offset="1" stop-color="#1e2b45"/></linearGradient>'
         '<radialGradient id="beam" cx="50%" cy="0%" r="100%"><stop offset="0" stop-color="#fff6c8" stop-opacity="0.55"/>'
         '<stop offset="1" stop-color="#fff6c8" stop-opacity="0"/></radialGradient></defs>']
    b.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    for i in range(70):
        b.append(f'<circle cx="{rnd.uniform(0,W)}" cy="{rnd.uniform(0,620)}" r="{rnd.uniform(1.2,3.2)}" fill="#d6dcea" opacity="{rnd.uniform(.3,.9)}"/>')
    b.append(circle(860, 260, 80, "#e8e6d2", sw=0))
    b.append(circle(832, 240, 15, "#d0ccb3", sw=0)); b.append(circle(885, 290, 11, "#d0ccb3", sw=0))
    # forest
    for i in range(30):
        tx = i * 40 + rnd.uniform(-10, 10); th = rnd.uniform(260, 460)
        b.append(f'<polygon points="{tx},{900-th} {tx-50},900 {tx+50},900" fill="#070b13"/>')
    # ground + rails converging
    b.append(f'<rect y="900" width="{W}" height="1020" fill="#11151d"/>')
    for x0, x1 in ((380, -200), (700, 1280)):
        b.append(f'<line x1="{x0}" y1="900" x2="{x1}" y2="{H}" stroke="#4a4f5a" stroke-width="12"/>')
    # headlight beam on ground
    b.append(f'<polygon points="440,1400 640,1400 1080,1920 0,1920" fill="url(#beam)"/>')
    # platform on the right with lamp post (one dead lamp)
    b.append(poly([(800, 900), (W, 900), (W, H), (1000, H)], "#2a2e36", sw=0))
    b.append(f'<line x1="800" y1="900" x2="1000" y2="{H}" stroke="#d4c15a" stroke-width="10"/>')
    b.append(R(930, 420, 14, 500, "#20242c", sw=0))
    b.append(path("M937 420 Q980 400 1000 430", sw=12, stroke="#20242c"))
    b.append(ell(1004, 440, 22, 12, "#2c313a", sw=0))
    # train body (front, slightly perspective) ------------------------------------------
    cx = 540
    body = ("M300 1420 L300 760 C300 640 360 560 540 548 C720 560 780 640 780 760 L780 1420 Z")
    b.append(shaded(body, C["trainG"], [("M600 520 L820 520 L820 1440 L600 1440 Z", C["trainGS"])], sw=7))
    # roof + pantograph
    b.append(path("M430 556 L470 470 L610 470 L650 556", sw=6, stroke="#8d8f88"))
    b.append(path("M470 470 L540 430 L610 470", sw=5, stroke="#8d8f88"))
    b.append(R(450, 420, 180, 12, "#8d8f88", rx=6, sw=4))
    # destination board
    b.append(R(420, 590, 240, 56, "#111", rx=10, sw=5))
    b.append(T(540, 632, "ТАЙЦЫ", 38, "#ffcf5a", 800))
    # cab windows (lit warm, driver silhouette in left)
    for x in (330, 552):
        b.append(R(x, 670, 198, 230, "#ffe5a3", rx=22, sw=7))
        b.append(f'<rect x="{x+8}" y="{678}" width="182" height="214" rx="18" fill="#fff3cf" opacity="0.4"/>')
    b.append(R(522, 660, 36, 250, C["trainGS"], rx=8, sw=5))
    b.append(G('<path d="M-60 0 C-60 -80 -40 -110 0 -112 C40 -110 60 -80 60 0 Z" fill="#2a2420"/><circle cx="0" cy="-150" r="42" fill="#2a2420"/>'
               '<path d="M-56 -170 Q0 -215 56 -170 Q60 -160 -56 -160 Z" fill="#2a2420"/>', 430, 900, 1.0))
    # wipers
    b.append(path("M360 890 L470 760", sw=5)); b.append(path("M580 890 L690 760", sw=5))
    # red lower front with yellow whiskers
    b.append(shaded("M300 960 L780 960 L780 1300 L300 1300 Z", C["trainR"], [("M600 940 L820 940 L820 1320 L600 1320 Z", C["trainRS"])], sw=7))
    for k in range(3):
        y = 1000 + k * 46
        b.append(path(f"M310 {y+60} L540 {y} L770 {y+60}", sw=16, stroke=C["trainY"]))
    b.append(R(476, 1020, 128, 70, "#f3efe0", rx=8, sw=5))
    b.append(T(540, 1068, "ЭР2", 38, O, 900))
    # headlights: top + two lower with glow
    for (hx, hy, r) in ((540, 586 - 20, 0), (360, 1240, 34), (720, 1240, 34)):
        if r:
            b.append(f'<circle cx="{hx}" cy="{hy}" r="{r*3}" fill="#fff6c8" opacity="0.25"/>')
            b.append(circle(hx, hy, r, "#fffbe8", sw=6))
    b.append(f'<circle cx="540" cy="520" r="70" fill="#fff6c8" opacity="0.3"/>')
    b.append(circle(540, 520, 24, "#fffbe8", sw=6))
    # buffer beam, coupler
    b.append(R(290, 1300, 500, 70, "#2a2a2a", rx=10, sw=6))
    b.append(R(500, 1320, 80, 80, "#3a3a3a", rx=8, sw=5))
    b.append(R(320, 1370, 440, 60, "#1b1b1b", sw=5))
    b.append(FIN)
    return svg("".join(b))

scenes["exterior"] = train_front()

def train_side(braking=True):
    rnd = random.Random(5)
    b = ['<defs><linearGradient id="sky2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0f1d"/>'
         '<stop offset="1" stop-color="#1c2840"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#sky2)"/>']
    for i in range(50):
        b.append(f'<circle cx="{rnd.uniform(0,W)}" cy="{rnd.uniform(0,700)}" r="{rnd.uniform(1.2,3)}" fill="#d6dcea" opacity="{rnd.uniform(.3,.9)}"/>')
    for i in range(30):
        tx = i * 40 + rnd.uniform(-10, 10); th = rnd.uniform(300, 520)
        b.append(f'<polygon points="{tx},{1050-th} {tx-55},1050 {tx+55},1050" fill="#070b13"/>')
    b.append(f'<rect y="1050" width="{W}" height="870" fill="#0e1218"/>')
    # dark platform in front (no lamps)
    b.append(R(-10, 1560, W + 20, 380, "#1b1f27", sw=0))
    b.append(f'<line x1="0" y1="1560" x2="{W}" y2="1560" stroke="#6b6332" stroke-width="10"/>')
    b.append(R(120, 1100, 16, 470, "#171a21", sw=0)); b.append(ell(150, 1110, 30, 14, "#22262e", sw=0))
    # car body
    b.append(shaded("M-40 900 L1120 900 L1120 1500 L-40 1500 Z", C["trainG"], [("M-60 1380 L1140 1380 L1140 1520 L-60 1520 Z", C["trainGS"])], sw=7))
    b.append(R(-40, 860, 1160, 60, "#7f8a85", rx=24, sw=6))
    b.append(R(-40, 1310, 1160, 34, C["trainR"], sw=5))
    b.append(R(-40, 1346, 1160, 10, C["trainY"], sw=0))
    # pantograph
    b.append(path("M600 860 L660 760 L760 760 L820 860", sw=6, stroke="#8d8f88"))
    b.append(R(640, 744, 140, 12, "#8d8f88", rx=6, sw=4))
    # windows: lit except one (where they sit, lamps dimmer)
    for i, x in enumerate((40, 250, 640, 850)):
        lit = i != 2
        if lit:
            b.append(f'<rect x="{x-20}" y="960" width="210" height="230" fill="{C["glow"]}" opacity="0.2"/>')
        b.append(R(x, 980, 170, 190, "#ffe5a3" if lit else "#b9a26a", rx=18, sw=6))
        b.append(R(x, 980, 170, 40, C["frame"], rx=12, sw=5))
    # two silhouettes in window 3
    b.append(G('<path d="M-60 0 C-60 -70 -40 -100 0 -102 C40 -100 60 -70 60 0 Z" fill="#2a2420"/><circle cx="0" cy="-135" r="36" fill="#2a2420"/>'
               '<path d="M-62 -150 Q0 -185 62 -150 Q0 -140 -62 -150 Z" fill="#2a2420"/>', 690, 1172, 1.0))
    b.append(G('<path d="M-50 0 C-50 -60 -35 -86 0 -88 C35 -86 50 -60 50 0 Z" fill="#2a2420"/><circle cx="0" cy="-118" r="34" fill="#2a2420"/>'
               '<path d="M-38 -138 Q0 -166 44 -140 Z" fill="#2a2420"/>', 775, 1172, 1.0))
    # doors
    b.append(R(450, 940, 160, 380, "#4b7d5d", rx=8, sw=6)); b.append(f'<line x1="530" y1="940" x2="530" y2="1320" stroke="{O}" stroke-width="5"/>')
    b.append(R(470, 980, 50, 130, "#b9a26a", rx=6, sw=4)); b.append(R(540, 980, 50, 130, "#b9a26a", rx=6, sw=4))
    b.append(T(1000, 1290, "ЭР2-1043", 34, "#e8e2c4", 800))
    # bogies + wheels, sparks if braking
    for bx in (170, 900):
        b.append(R(bx - 140, 1500, 280, 50, "#222", rx=10, sw=6))
        for wx in (bx - 80, bx + 80):
            b.append(circle(wx, 1550, 48, "#2d2d2d", sw=6)); b.append(circle(wx, 1550, 16, "#666", sw=4))
            if braking:
                for k in range(6):
                    a = rnd.uniform(-0.3, 0.6)
                    b.append(f'<line x1="{wx+40}" y1="{1580}" x2="{wx+40+rnd.uniform(40,110)}" y2="{1580-rnd.uniform(0,60)}" stroke="#ffcf5a" stroke-width="4" stroke-linecap="round"/>')
    b.append(FIN)
    return svg("".join(b))

scenes["exterior_side"] = train_side()

# =========================================================== props (kept from v1, tuned)
def door_locked():
    b = [f'<rect width="{W}" height="{H}" fill="{C["greenS"]}"/>']
    b.append(R(160, 180, 760, 1560, C["green"], rx=20))
    b.append(R(250, 290, 580, 520, C["win"], rx=16))
    b.append(f'<polygon points="300,780 780,780 640,540 440,540" fill="#0b111c"/>')
    b.append(f'<rect x="250" y="290" width="580" height="520" rx="16" fill="#ffffff" opacity="0.04"/>')
    b.append(R(250, 290, 580, 520, "none", rx=16))
    for y in (900, 1560):
        b.append(R(200, y, 680, 18, C["greenS"], rx=8, sw=4))
    b.append(R(760, 980, 70, 220, C["metal"], rx=20))
    b.append(chars.hand(820, 1060, 1.6, -1, chars.KAT["skin"], chars.KAT["skinS"], "grip"))
    b.append(shaded("M880 1040 L1100 980 L1100 1200 L880 1150 Z", chars.KAT["coat"], [("M880 1110 L1100 1110 L1100 1210 L880 1210 Z", chars.KAT["coatS"])]))
    b.append(f'<g transform="rotate(-8 540 1350)">{R(250, 1280, 580, 150, C["red"], rx=14)}{T(540, 1385, "ЗАПЕРТО", 86)}</g>')
    b.append(FIN)
    return svg("".join(b))
scenes["door_locked"] = door_locked()

def bag_pass():
    b = [f'<rect width="{W}" height="{H}" fill="{C["woodL"]}"/>']
    for i in range(0, H, 140):
        b.append(f'<line x1="0" y1="{i}" x2="{W}" y2="{i}" stroke="{C["wood"]}" stroke-width="8"/>')
    k = chars.KAT
    b.append(path("M190 880 C190 600 890 600 890 880", sw=34))
    b.append(path("M190 880 C190 600 890 600 890 880", sw=20, stroke=k["bagS"]))
    b.append(f'<g transform="rotate(-7 540 560)">')
    b.append(shaded("M230 300 L830 300 L830 720 L230 720 Z", "#f3ecd6", [("M230 300 L830 300 L830 395 L230 395 Z", C["trainG"])]))
    b.append(T(530, 368, "ПРОЕЗДНОЙ", 56))
    b.append(T(280, 470, "ОКТЯБРЬСКАЯ Ж.Д.", 32, O, 700, "start"))
    b.append(T(280, 535, "ЛЕНИНГРАД —", 50, O, 900, "start"))
    b.append(f'<rect x="270" y="565" width="470" height="80" fill="{C["yellow"]}" opacity="0.9"/>')
    b.append(T(285, 628, "ст. ТАЙЦЫ", 62, C["red"], 900, "start"))
    b.append('</g>')
    bag = "M120 820 L960 820 C990 820 1000 840 1000 870 L990 1560 C990 1590 970 1610 940 1610 L140 1610 C110 1610 90 1590 90 1560 L80 870 C80 840 90 820 120 820 Z"
    b.append(shaded(bag, k["bag"], [("M700 800 L1020 800 L1020 1620 L700 1620 Z", k["bagS"])], sw=8,
                    lines=[("M100 1010 L980 1010", 6), ("M130 1560 L950 1560", 4)]))
    b.append(shaded("M470 960 L610 960 L610 1080 L470 1080 Z", "#c8a560", sw=7, lines=[("M500 1020 L580 1020", 6)]))
    b.append(FIN)
    return svg("".join(b))
scenes["bag_pass"] = bag_pass()

def intercom(pressed=False):
    b = [f'<rect width="{W}" height="{H}" fill="{C["cream"]}"/>']
    b.append(R(190, 360, 700, 1100, "#c9c3aa", rx=30))
    b.append(R(250, 420, 580, 120, C["red"], rx=14))
    b.append(T(540, 475, "СВЯЗЬ", 56)); b.append(T(540, 525, "С МАШИНИСТОМ", 40))
    for r in range(6):
        for c_ in range(8):
            b.append(f'<circle cx="{330 + c_*60}" cy="{650 + r*55}" r="13" fill="{O}"/>')
    b.append(ell(540, 1150, 150, 150, "#9b1d16" if pressed else C["red"]))
    b.append(ell(540, 1150, 110, 110, "#b5281f" if pressed else "#ec5a4d", sw=5))
    if pressed:
        b.append(G(chars.hand(0, 0, 1, 1, chars.KAT["skin"], chars.KAT["skinS"], "rest"), 600, 1040, 2.6, extra='transform-origin="0 0"'))
        b.append(shaded("M700 1150 L1100 1300 L1100 1700 L760 1480 Z", chars.KAT["coat"], [("M900 1150 L1120 1150 L1120 1720 L900 1720 Z", chars.KAT["coatS"])]))
    b.append(FIN)
    return svg("".join(b))
scenes["intercom"] = intercom()
scenes["intercom_press"] = intercom(True)

def silhouette_man():
    return ('<path d="M-150 0 C-150 -200 -120 -300 -70 -320 L70 -320 C120 -300 150 -200 150 0 Z" fill="#101010"/>'
            '<ellipse cx="0" cy="-410" rx="70" ry="95" fill="#101010"/>'
            '<path d="M-150 -460 Q0 -420 150 -460 Q150 -440 0 -428 Q-150 -440 -150 -460 Z" fill="#101010"/>'
            '<path d="M-82 -458 C-90 -560 82 -560 82 -458 Z" fill="#101010"/>')

def platform(man_in_door=False):
    b = [f'<rect width="{W}" height="{H}" fill="{C["cream"]}"/>']
    b.append(f'<rect x="200" y="260" width="680" height="1360" fill="#04060a"/>')
    b.append(f'<polygon points="200,1300 880,1300 880,1620 200,1620" fill="#0b0e14"/>')
    b.append(f'<line x1="200" y1="1300" x2="880" y2="1300" stroke="#3a3720" stroke-width="10"/>')
    b.append(f'<rect x="700" y="560" width="14" height="740" fill="#151920"/>')
    b.append(f'<path d="M707 560 q40 -10 60 20" stroke="#151920" stroke-width="12" fill="none"/>')
    b.append(R(40, 240, 170, 1400, C["green"], rx=10)); b.append(R(870, 240, 170, 1400, C["green"], rx=10))
    b.append(R(70, 320, 110, 420, C["win"], rx=10)); b.append(R(900, 320, 110, 420, C["win"], rx=10))
    b.append(R(200, 260, 680, 1360, "none"))
    b.append(f'<rect y="1620" width="{W}" height="300" fill="{C["floor"]}"/>')
    b.append(f'<line x1="0" y1="1620" x2="{W}" y2="1620" stroke="{O}" stroke-width="{SW}"/>')
    if man_in_door:
        b.append(G(silhouette_man(), 540, 1180, 1.25))
        b.append(circle(510, 668, 9, "#e8e3c9", sw=0)); b.append(circle(570, 668, 9, "#e8e3c9", sw=0))
    b.append(FIN)
    return svg("".join(b))
scenes["platform"] = platform()
scenes["platform_man"] = platform(True)

# rule cards and choice end card (unchanged design)
def rule_card(n, title, bad, good, reveal):
    b = [f'<rect width="{W}" height="{H}" fill="{C["navy"]}"/>']
    b.append(R(90, 230, 900, 110, "#262f47", rx=26, sw=5))
    b.append(circle(160, 285, 34, C["yellow"], sw=5)); b.append(T(160, 300, str(n), 42, O))
    b.append(T(215, 302, title, 40, "#fff", 900, "start"))
    def row(y, ok, txt, show):
        col = C["green2"] if ok else C["red"]
        g = [R(90, y, 900, 300, "#1d2438", rx=26, sw=5)]
        if show:
            g.append(R(90, y, 900, 70, col, rx=26, sw=5))
            g.append(f'<rect x="94" y="{y+40}" width="892" height="30" fill="{col}"/>')
            g.append(T(540, y + 50, "МОЖНО" if ok else "НЕЛЬЗЯ", 38))
            g.append(T(470, y + 190, txt, 50, "#fff"))
            mx = 900
            g.append(circle(mx, y + 220, 48, col, sw=5))
            if ok:
                g.append(path(f"M{mx-22} {y+220} l15 17 l30 -35", sw=10, stroke="#fff"))
            else:
                g.append(path(f"M{mx-20} {y+200} l40 40 M{mx+20} {y+200} l-40 40", sw=10, stroke="#fff"))
        else:
            g.append(f'<rect x="150" y="{y+130}" width="700" height="40" rx="20" fill="#2c3550"/>')
        return "".join(g)
    b.append(row(400, False, bad, reveal >= 1))
    b.append(row(740, True, good, reveal >= 2))
    b.append(GRAIN)
    return svg("".join(b))

rules = [
    (1, "ПУСТОЙ ВАГОН — ИДИ К ЛЮДЯМ", "Сидеть с чужим вдвоём", "Перейти туда, где люди"),
    (2, "НЕ НАЗЫВАЙ СВОЮ СТАНЦИЮ", "«До Тайцев. Одна»", "«До конечной»"),
    (3, "РАСКРЫЛИ — ЗОВИ МАШИНИСТА", "Молча ждать", "Кнопка связи в тамбуре"),
]
for n, title, bad, good in rules:
    for rv in (0, 1, 2):
        scenes[f"rule{n}_{rv}"] = rule_card(n, title, bad, good, rv)

def choice():
    inner = platform(True).split(">", 1)[1].rsplit("</svg>", 1)[0]
    b = [inner, f'<rect width="{W}" height="{H}" fill="#000" opacity="0.5"/>']
    b.append(R(80, 1340, 440, 220, C["red"], rx=30))
    b.append(T(300, 1430, "ВЫЙТИ", 64)); b.append(T(300, 1500, "В ТЕМНОТУ", 46))
    b.append(R(560, 1340, 440, 220, "#2f3a5c", rx=30))
    b.append(T(780, 1430, "ОСТАТЬСЯ", 60)); b.append(T(780, 1500, "С НИМ", 46))
    b.append(T(540, 1650, "ПИШИ В КОММЕНТАХ", 50, C["yellow"]))
    return svg("".join(b))
scenes["choice"] = choice()

if __name__ == "__main__":
    import sys
    want = set(sys.argv[1:])
    for k, v in scenes.items():
        if want and k not in want:
            continue
        save(k, v)
        print(k)
