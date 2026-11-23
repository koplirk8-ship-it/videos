"""Detailed, animatable characters. Each takes animation params:
mouth: 0 closed .. 1 half .. 2 wide (lip-sync), blink: 0..1 (1 = eyes shut), breath: -1..1 (idle cycle)."""
import sys, itertools
sys.path.insert(0, "/home/claude/v2")
from chars import shaded, path, fillp, circle, ell, hand, O

SK = dict(skin="#efd2b6", skinS="#d4ad8e", skinD="#b98d70", lip="#c98579", lipS="#a86257")

# ======================================================================= guys
def _eye(x, y, expr, blink, iris, look=0):
    b = []
    wide = expr in ("shout", "panic", "scared")
    rx, ry = (19, 21) if wide else (16, 17)
    lid_cover = {"deadpan": 0.48, "tired": 0.35}.get(expr, 0.0)
    lid_cover = max(lid_cover, blink)
    cid = f"e{abs(hash((x, y, expr, round(blink, 2), look))) % 10**8}"
    b.append(f'<clipPath id="{cid}"><ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}"/></clipPath>')
    b.append(ell(x, y, rx, ry, "#fbf8f1", sw=0))
    b.append(f'<g clip-path="url(#{cid})">')
    ir = 7 if wide else 10
    ix = x + look * 5
    b.append(circle(ix, y + 1, ir, iris, sw=0))
    b.append(f'<circle cx="{ix}" cy="{y+1}" r="{ir}" fill="none" stroke="#2a1c17" stroke-width="2" opacity="0.6"/>')
    b.append(circle(ix, y + 1, ir * 0.5, "#140e0b", sw=0))
    b.append(circle(ix + ir * 0.45, y - ir * 0.35, ir * 0.28, "#ffffff", sw=0))
    b.append(circle(ix - ir * 0.4, y + ir * 0.45, ir * 0.13, "#ffffff", sw=0))
    b.append(f'<rect x="{x-rx}" y="{y-ry}" width="{2*rx}" height="{ry*0.5}" fill="#000" opacity="0.10"/>')  # lid shadow
    if lid_cover > 0:
        h = 2 * ry * lid_cover
        b.append(f'<rect x="{x-rx-2}" y="{y-ry-2}" width="{2*rx+4}" height="{h+2}" fill="{SK["skin"]}"/>')
    b.append('</g>')
    b.append(ell(x, y, rx, ry, "none", sw=3.5))
    ly = y - ry + 2 * ry * lid_cover
    b.append(path(f"M{x-rx-3} {ly+2} Q{x} {ly-6 if lid_cover < .9 else ly+4} {x+rx+3} {ly+2}", sw=5.5))  # upper lid line
    if lid_cover < 0.9:
        b.append(path(f"M{x-rx+4} {y-ry-9} Q{x} {y-ry-15} {x+rx-4} {y-ry-9}", sw=2.2))  # crease
        b.append(path(f"M{x-rx+5} {y+ry+3} Q{x} {y+ry+7} {x+rx-5} {y+ry+3}", sw=1.8))  # lower lash
    return "".join(b)

def _brow(side, expr, y):
    s = side
    shapes = {
        "shout": f"M{18*s} {y-12} Q{38*s} {y-6} {58*s} {y+6} L{56*s} {y+14} Q{36*s} {y+2} {16*s} {y-2} Z",
        "panic": f"M{16*s} {y-4} Q{36*s} {y-24} {58*s} {y-10} L{56*s} {y-2} Q{36*s} {y-14} {18*s} {y+6} Z",
        "scared": f"M{16*s} {y-4} Q{36*s} {y-24} {58*s} {y-10} L{56*s} {y-2} Q{36*s} {y-14} {18*s} {y+6} Z",
        "deadpan": f"M{16*s} {y-3} L{58*s} {y-3} L{58*s} {y+6} L{16*s} {y+6} Z",
    }
    d = shapes.get(expr, f"M{16*s} {y} Q{36*s} {y-12} {58*s} {y-2} L{57*s} {y+6} Q{36*s} {y-3} {17*s} {y+8} Z")
    return f'<path d="{d}" fill="#2b2220" stroke="#2b2220" stroke-width="2" stroke-linejoin="round"/>'

def _mouth(expr, mouth, y):
    b = []
    if mouth < 0.25:
        if expr in ("panic",):
            b.append(path(f"M-24 {y} q8 -8 16 0 q8 8 16 0 q8 -8 16 0", sw=4.5))
        elif expr == "scared":
            b.append(ell(0, y, 10, 12, "#5a201b", sw=4))
        elif expr in ("deadpan", "tired"):
            b.append(path(f"M-20 {y} Q0 {y+2} 20 {y}", sw=4.5))
            b.append(path(f"M-12 {y+12} Q0 {y+16} 12 {y+12}", sw=2, stroke=SK["skinD"]))
        else:
            b.append(path(f"M-20 {y-2} Q0 {y+8} 20 {y-2}", sw=4.5))
            b.append(path(f"M-12 {y+14} Q0 {y+18} 12 {y+14}", sw=2, stroke=SK["skinD"]))
        return "".join(b)
    w = 22 + 8 * min(mouth, 2)
    h = 8 + 20 * min(mouth, 2)
    d = f"M{-w} {y-4} Q0 {y-10} {w} {y-4} Q{w*0.9} {y+h} 0 {y+h+4} Q{-w*0.9} {y+h} {-w} {y-4} Z"
    cid = f"m{abs(hash((expr, round(mouth, 2), y))) % 10**8}"
    b.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    b.append(fillp(d, "#4a1712"))
    b.append(f'<g clip-path="url(#{cid})">')
    b.append(f'<rect x="{-w}" y="{y-12}" width="{2*w}" height="{6+2*mouth}" fill="#f4efe3"/>')  # upper teeth
    b.append(ell(0, y + h + 4, w * 0.6, h * 0.45, "#c55a52", sw=0))  # tongue
    b.append('</g>')
    b.append(path(d, sw=4.5))
    b.append(path(f"M{-w*0.6} {y+h+16} Q0 {y+h+22} {w*0.6} {y+h+16}", sw=2, stroke=SK["skinD"]))
    return "".join(b)

def guy_head(who, expr="normal", mouth=0.0, blink=0.0, look=0):
    if who == "artyom":
        hair, hairS, hairL, iris = "#8a6a43", "#6c512f", "#a8855a", "#5a7d4f"
    else:
        hair, hairS, hairL, iris = "#2b2522", "#1b1715", "#4a403b", "#5b4433"
    b = []
    # neck shadow under jaw is drawn by body; ears
    for s in (-1, 1):
        ear = f"M{80*s} -8 C{106*s} -18 {112*s} 30 {88*s} 44 C{84*s} 46 {80*s} 40 {80*s} 34 Z"
        b.append(shaded(ear, SK["skin"], [(f"M{94*s} -20 L{120*s} -20 L{120*s} 50 L{94*s} 50 Z", SK["skinS"])],
                        lines=[(f"M{88*s} 4 C{100*s} 6 {100*s} 24 {90*s} 30", 2.5)]))
    face = "M-80 -50 C-86 10 -78 70 -56 100 C-36 124 -16 132 0 132 C16 132 36 124 56 100 C78 70 86 10 80 -50 C70 -110 -70 -110 -80 -50 Z"
    b.append(shaded(face, SK["skin"], [
        ("M40 -120 C90 -60 86 60 40 130 L140 130 L140 -120 Z", SK["skinS"]),
        ("M-70 60 C-60 90 -40 110 -20 120 L-70 120 Z", SK["skinS"], 0.5),
        ("M-60 -14 Q-34 -30 -8 -14 L-8 -6 Q-34 -20 -60 -6 Z", SK["skinS"], 0.35),
        ("M8 -14 Q34 -30 60 -14 L60 -6 Q34 -20 8 -6 Z", SK["skinS"], 0.45),
    ]))
    if who == "dima":
        b.append(f'<path d="M-62 74 C-46 120 46 120 62 74 C40 104 -40 104 -62 74 Z" fill="#2b2522" opacity="0.16"/>')
        b.append(f'<path d="M-30 74 Q0 66 30 74 Q0 80 -30 74 Z" fill="#2b2522" opacity="0.18"/>')
    # cheeks
    b.append(ell(-50, 56, 16, 9, "#e59a8c", sw=0, extra='opacity="0.35"'))
    b.append(ell(50, 56, 16, 9, "#e59a8c", sw=0, extra='opacity="0.35"'))
    if who == "artyom":
        for fx, fy in ((-44, 44), (-52, 50), (-38, 52), (44, 44), (52, 50), (38, 52)):
            b.append(circle(fx, fy, 2, "#c48a69", sw=0))
    # eyes, brows
    b.append(_eye(-34, 6, expr, blink, iris, look)); b.append(_eye(34, 6, expr, blink, iris, look))
    b.append(_brow(-1, expr, -30)); b.append(_brow(1, expr, -30))
    # nose
    b.append(path("M-2 14 C0 34 8 46 10 56", sw=3.5))
    b.append(path("M-12 60 Q-6 66 0 62 Q6 66 12 60", sw=3))
    b.append(f'<path d="M-14 66 Q0 74 14 66 Q0 70 -14 66 Z" fill="{SK["skinD"]}" opacity="0.5"/>')
    b.append(_mouth(expr, mouth, 88))
    # hair
    if who == "artyom":
        h = ("M-92 -30 C-104 -110 -40 -150 10 -146 C70 -144 108 -110 94 -28 C84 -50 70 -62 56 -60 L48 -40 C36 -62 20 -66 8 -58 "
             "L-4 -34 C-16 -60 -34 -66 -50 -56 L-62 -36 C-70 -48 -82 -46 -92 -30 Z")
        b.append(shaded(h, hair, [("M30 -160 L120 -160 L120 -20 L30 -20 Z", hairS), ("M-70 -130 Q-30 -150 10 -140 L10 -128 Q-30 -136 -66 -118 Z", hairL, 0.9)],
                        lines=[("M-60 -110 Q-50 -80 -50 -56 M-30 -128 Q-24 -96 -20 -62 M-10 -136 Q-6 -96 8 -58 M20 -134 Q30 -100 30 -60 M40 -128 Q50 -90 48 -40 M66 -112 Q74 -80 70 -54", 2.5)]))
        b.append(path("M-20 -146 q10 -24 26 -18 M10 -146 q20 -20 30 -4", sw=6, stroke=hair))
    else:
        h = "M-88 -20 C-96 -110 -40 -140 6 -138 C64 -136 100 -104 90 -20 C80 -44 60 -66 20 -70 C-20 -70 -60 -60 -88 -20 Z"
        b.append(shaded(h, hair, [("M30 -150 L120 -150 L120 -10 L30 -10 Z", hairS), ("M-60 -110 Q-20 -130 30 -124 L28 -114 Q-20 -118 -56 -100 Z", hairL, 0.9)],
                        lines=[("M-60 -90 Q-30 -110 0 -100 M10 -112 Q40 -116 66 -96 M-74 -60 Q-60 -80 -40 -84", 2.5)]))
        for x in (-34, 34):   # glasses
            b.append(f'<rect x="{x-28}" y="-18" width="56" height="44" rx="13" fill="#d6e8f2" fill-opacity="0.16" stroke="{O}" stroke-width="5"/>')
            b.append(f'<path d="M{x+4} -12 l14 0 l-24 34 l-14 0 Z" fill="#ffffff" opacity="0.22"/>')
        b.append(path("M-6 0 Q0 -6 6 0", sw=5)); b.append(path("M-62 -2 L-84 -8 M62 -2 L84 -8", sw=5))
    if expr == "panic":
        b.append(shaded("M96 -60 C106 -40 110 -26 100 -18 C90 -12 82 -24 86 -40 Z", "#bfe3f5"))
        b.append(shaded("M-100 -30 C-94 -16 -92 -6 -100 0 C-108 -4 -108 -14 -100 -30 Z", "#bfe3f5"))
    return "".join(b)


def guy(who, expr="normal", arms="down", mouth=0.0, blink=0.0, breath=0.0, scarf=False, look=0, shake=(0, 0)):
    if who == "artyom":
        top, topS, topL, pants, pantsS, shoe = "#4f6f66", "#3c5750", "#5f8278", "#3a3f4a", "#2c3038", "#d9d4c8"
    else:
        top, topS, topL, pants, pantsS, shoe = "#8a8f96", "#6f747b", "#a1a6ad", "#2f3a52", "#232c40", "#3a2c24"
    b = []
    for sx in (-48, 48):
        b.append(shaded(f"M{sx-40} -470 L{sx-36} -40 L{sx+36} -40 L{sx+40} -470 Z", pants,
                        [(f"M{sx+8} -480 L{sx+60} -480 L{sx+60} -30 L{sx+8} -30 Z", pantsS)],
                        lines=[(f"M{sx-20} -200 q10 8 24 4 M{sx-8} -120 q8 6 18 2", 2.5)]))
        b.append(shaded(f"M{sx-46} -44 L{sx+40} -44 C{sx+70} -40 {sx+72} 0 {sx+52} 0 L{sx-50} 0 C{sx-56} -14 {sx-54} -34 {sx-46} -44 Z", shoe,
                        lines=[(f"M{sx-48} -12 L{sx+66} -12", 4), (f"M{sx-10} -40 l10 10 M{sx+4} -40 l10 10", 2)]))
    up = -6 * breath   # chest rise
    b.append(f'<g transform="translate({shake[0]},{shake[1]+up})">')
    if who == "artyom":
        torso = "M-40 -852 C-110 -848 -138 -826 -146 -770 C-152 -660 -146 -540 -132 -430 L132 -430 C146 -540 152 -660 146 -770 C138 -826 110 -848 40 -852 Z"
        b.append(shaded(torso, top, [("M20 -870 L170 -870 L170 -420 L20 -420 Z", topS), ("M-140 -800 Q-150 -700 -136 -600 L-120 -600 Q-134 -700 -124 -800 Z", topL, 0.6)],
                        lines=[("M-128 -470 L128 -470", 4), ("M-90 -700 Q-70 -660 -86 -620 M80 -720 Q96 -680 84 -640", 2.5)]))
        b.append(shaded("M-70 -600 L70 -600 L84 -490 L-84 -490 Z", topS, lines=[("M0 -600 L0 -490", 3), ("M-64 -592 L64 -592", 2)]))
        b.append(shaded("M-96 -850 C-60 -800 60 -800 96 -850 C80 -880 -80 -880 -96 -850 Z", topL))
        b.append(path("M-26 -820 L-30 -720 M26 -820 L30 -720", sw=5, stroke="#e8e2d2"))
        b.append(circle(-30, -716, 5, "#c8c2b2", sw=2)); b.append(circle(30, -716, 5, "#c8c2b2", sw=2))
    else:
        torso = "M-40 -852 C-108 -848 -136 -826 -142 -770 C-146 -660 -142 -540 -128 -430 L128 -430 C142 -540 146 -660 142 -770 C136 -826 108 -848 40 -852 Z"
        b.append(shaded(torso, top, [("M20 -870 L170 -870 L170 -420 L20 -420 Z", topS)],
                        lines=[("M-50 -846 Q0 -806 50 -846", 5), ("M-100 -700 Q-80 -640 -96 -580 M90 -720 Q104 -660 92 -600", 2.5)]))
    # neck + chin shadow
    b.append(shaded("M-30 -880 L-32 -822 L32 -822 L30 -880 Z", SK["skin"], [("M-40 -890 L40 -890 L40 -846 L-40 -846 Z", SK["skinS"])]))
    if scarf:
        b.append(shaded("M-80 -850 Q0 -800 80 -850 L84 -810 Q0 -760 -84 -810 Z", "#b8362b",
                        lines=[("M-40 -836 L-44 -790 M0 -824 L0 -778 M40 -836 L44 -790", 10)]))
        b.append(shaded("M30 -800 L70 -560 L20 -552 L-6 -790 Z", "#b8362b",
                        lines=[("M20 -740 L56 -746 M28 -680 L64 -686 M36 -620 L70 -626", 12), ("M26 -560 l0 20 M42 -560 l0 20 M58 -562 l0 20", 4)]))
    sleeve, sleeveS = (top, topS) if who == "artyom" else ("#3d4b63", "#2e3a4f")
    def arm(s, kind):
        if kind == "down":
            d = f"M{120*s} -820 C{170*s} -760 {182*s} -600 {176*s} -470 L{132*s} -468 C{136*s} -600 {130*s} -720 {100*s} -790 Z"
            return shaded(d, sleeve if s < 0 else sleeveS, lines=[(f"M{160*s} -640 Q{150*s} -630 {154*s} -610", 2.5)]) + hand(154 * s, -478, 1.0, -s if s > 0 else 1, SK["skin"], SK["skinS"])
        if kind == "head":
            d = f"M{120*s} -820 C{190*s} -840 {210*s} -940 {150*s} -1040 L{112*s} -1010 C{150*s} -930 {140*s} -860 {100*s} -790 Z"
            return shaded(d, sleeve if s < 0 else sleeveS) + hand(138 * s, -1080, 1.0, -s if s > 0 else 1, SK["skin"], SK["skinS"], "grip")
        if kind == "point":
            d = f"M{120*s} -820 C{200*s} -800 {280*s} -760 {330*s} -740 L{320*s} -700 C{260*s} -712 {180*s} -740 {110*s} -770 Z"
            g = shaded(d, sleeve if s < 0 else sleeveS)
            fx = 330 * s
            g += shaded(f"M{fx} -748 L{fx+80*s} -738 C{fx+92*s} -736 {fx+92*s} -722 {fx+80*s} -720 L{fx+30*s} -716 C{fx+34*s} -700 {fx+20*s} -690 {fx} -694 Z", SK["skin"], lines=[(f"M{fx+10*s} -716 l20 0", 2)])
            return g
        if kind == "mug":
            d = f"M{120*s} -820 C{170*s} -760 {180*s} -660 {150*s} -600 L{60*s} -610 L{70*s} -650 L{120*s} -650 C{130*s} -700 {126*s} -740 {100*s} -790 Z"
            g = shaded(d, sleeve if s < 0 else sleeveS)
            g += shaded(f"M{20*s} -700 L{100*s} -700 L{96*s} -590 L{24*s} -590 Z", "#d8d2c2", [(f"M{70*s} -710 L{110*s} -710 L{110*s} -580 L{70*s} -580 Z", "#bdb6a4")], lines=[(f"M{30*s} -680 L{90*s} -680", 3)])
            g += path(f"M{100*s} -680 C{130*s} -680 {130*s} -620 {98*s} -620", sw=7)
            g += path(f"M{50*s} -730 q-10 -20 0 -40 M{74*s} -730 q-10 -20 0 -40", sw=4, stroke="#9aa6b3")
            g += hand(80 * s, -640, 0.9, -s if s > 0 else 1, SK["skin"], SK["skinS"], "grip")
            return g
        return ""
    la, ra = {"down": ("down", "down"), "head": ("head", "head"), "point": ("point", "down"), "mug": ("down", "mug")}[arms]
    b.append(arm(-1, la)); b.append(arm(1, ra))
    b.append(f'<path d="M-46 -880 Q0 -850 46 -880 L40 -864 Q0 -840 -40 -864 Z" fill="{SK["skinD"]}" opacity="0.55"/>')
    b.append(f'<g transform="translate(0,{-990 - 2*breath})">{guy_head(who, expr, mouth, blink, look)}</g>')
    b.append('</g>')
    return "".join(b)


# ======================================================================= Gena (detailed, creepy)
GN = dict(skin="#9ea79f", skinS="#7c857e", skinD="#5c645e", skinL="#b9c1b8", vein="#6d6a8c",
          sock="#1a1c1f", eye="#e8dcb4", knit="#3e4a44", knitS="#2f3934", knitL="#4f5c55", nail="#3a3530", tooth="#e3d6a6", toothS="#b8a877")

def gena_head(expr="grin", mouth=0.0, blink=0.0, look=0):
    b = []
    # stringy hair behind
    for i, x in enumerate(range(-70, 80, 18)):
        b.append(path(f"M{x} -230 q{(-1)**i*14} 90 {(-1)**i*8} {150 + (i % 3) * 30}", sw=3, stroke="#2a2724"))
    # pointed torn ears
    for s in (-1, 1):
        ear = f"M{84*s} -120 L{140*s} -170 L{120*s} -100 C{112*s} -70 {98*s} -60 {86*s} -60 Z"
        b.append(shaded(ear, GN["skin"], [(f"M{100*s} -180 L{150*s} -180 L{150*s} -50 L{100*s} -50 Z", GN["skinS"])],
                        lines=[(f"M{96*s} -110 L{124*s} -140", 2.5), (f"M{128*s} -150 l{-8*s} 10", 3)]))
    # elongated skull with sunken cheeks
    head = ("M-88 -150 C-96 -230 -50 -270 0 -272 C50 -270 96 -230 88 -150 C84 -100 70 -80 64 -40 C60 0 46 60 0 70 "
            "C-46 60 -60 0 -64 -40 C-70 -80 -84 -100 -88 -150 Z")
    b.append(shaded(head, GN["skin"], [
        ("M30 -290 C100 -220 96 -100 60 -20 C50 30 30 70 0 80 L140 80 L140 -290 Z", GN["skinS"]),
        ("M-62 -60 C-56 -20 -40 10 -30 20 C-44 0 -50 -30 -48 -60 Z", GN["skinD"], 0.7),   # sunken cheek L
        ("M62 -60 C56 -20 40 10 30 20 C44 0 50 -30 48 -60 Z", GN["skinD"], 0.8),          # sunken cheek R
        ("M-70 -168 Q0 -186 70 -168 L70 -150 Q0 -166 -70 -150 Z", GN["skinD"], 0.45),      # brow ridge shadow
        ("M-60 -240 Q-20 -262 20 -254 L16 -244 Q-20 -250 -56 -230 Z", GN["skinL"], 0.8),   # skull highlight
        ("M-40 -210 C-30 -214 -22 -204 -30 -198 C-40 -196 -46 -204 -40 -210 Z", GN["skinD"], 0.5),  # blotches
        ("M40 -60 C50 -64 56 -54 50 -48 C42 -46 36 -54 40 -60 Z", GN["skinD"], 0.5),
    ]))
    # veins on temples
    b.append(path("M-78 -190 q10 16 4 30 q-6 12 2 26 M-74 -170 q-12 8 -10 20", sw=2, stroke=GN["vein"]))
    b.append(path("M76 -196 q-10 18 -4 34 q4 10 -2 22", sw=2, stroke=GN["vein"]))
    # forehead scar with cross stitches + cheek scar
    b.append(path("M-56 -222 Q-10 -244 52 -214", sw=5, stroke="#6a4b4b"))
    for k in range(7):
        x = -48 + k * 16
        y = -230 + (x * x) / 220 - 6
        b.append(path(f"M{x-6} {y-9} L{x+6} {y+9}", sw=3)); b.append(path(f"M{x+6} {y-9} L{x-6} {y+9}", sw=2))
    b.append(path("M48 -100 Q58 -60 50 -20", sw=4, stroke="#6a4b4b"))
    for y in (-90, -70, -50, -30):
        b.append(path(f"M{44} {y} L{60} {y+4}", sw=2.5))
    # deep eye sockets with bloodshot eyes
    for s in (-1, 1):
        x = 38 * s
        b.append(f'<ellipse cx="{x}" cy="-128" rx="36" ry="40" fill="{GN["sock"]}" opacity="0.95"/>')
        b.append(f'<ellipse cx="{x}" cy="-122" rx="26" ry="28" fill="{GN["sock"]}"/>')
        if blink < 0.8 and expr != "closed":
            b.append(ell(x, -124, 18, 18 * (1 - blink * 0.9), GN["eye"], sw=2.5))
            for a in range(4):
                b.append(path(f"M{x - 16 + a * 3} {-126 + (a % 2) * 6} q6 -2 {8 + a} 2", sw=1.2, stroke="#b04a3e"))
            px = x + look * 5
            b.append(circle(px, -122, 6.5, "#0d0d0e", sw=0))
            b.append(f'<circle cx="{px}" cy="-122" r="9" fill="none" stroke="#7a3b2c" stroke-width="3"/>')
            b.append(circle(px + 3, -126, 2.4, "#ffffff", sw=0))
        else:
            b.append(path(f"M{x-18} -122 Q{x} -114 {x+18} -122", sw=4, stroke="#8a8f88"))
        b.append(path(f"M{x-26} -96 Q{x} -84 {x+26} -96", sw=2.5, stroke=GN["skinD"]))  # under-eye bag
    # heavy brows (bony ridges)
    b.append(path("M-74 -160 Q-40 -176 -10 -160", sw=6)); b.append(path("M10 -160 Q40 -176 74 -160", sw=6))
    # skull nose: two slits
    b.append(path("M-8 -86 Q-14 -70 -10 -60 M8 -86 Q14 -70 10 -60", sw=4))
    b.append(f'<path d="M-16 -56 Q0 -48 16 -56 Q0 -52 -16 -56 Z" fill="{GN["skinD"]}"/>')
    # mouth: wide grin of crooked teeth, jaw opens with `mouth`
    if expr in ("grin", "eat", "closed"):
        o = 26 * min(mouth, 2)
        top = "M-70 -30 Q0 -6 70 -30"
        lip = f"M-70 -30 Q0 -6 70 -30 Q40 {-10 + o * 0.8} 0 {-4 + o} Q-40 {-10 + o * 0.8} -70 -30 Z"
        cid = f"g{abs(hash((expr, round(mouth, 2)))) % 10**8}"
        b.append(f'<clipPath id="{cid}"><path d="{lip}"/></clipPath>')
        b.append(fillp(lip, "#1a0f0e"))
        b.append(f'<g clip-path="url(#{cid})">')
        for k in range(-6, 7):   # upper teeth, uneven
            x = k * 10.5
            ty = -30 + 24 * (1 - (x / 70) ** 2) * 0.55
            ln = 12 + (k * 7 % 5)
            b.append(f'<path d="M{x-5} {ty-6} L{x+5} {ty-6} L{x+4} {ty+ln} Q{x} {ty+ln+3} {x-4} {ty+ln} Z" fill="{GN["tooth"] if k % 4 else GN["toothS"]}" stroke="#3a2e22" stroke-width="1.6"/>')
        if o > 4:
            for k in range(-5, 6):  # lower teeth
                x = k * 11
                by = -4 + o - 4
                b.append(f'<path d="M{x-5} {by+6} L{x+5} {by+6} L{x+4} {by-10} L{x-4} {by-10} Z" fill="{GN["toothS"]}" stroke="#3a2e22" stroke-width="1.4"/>')
        b.append('</g>')
        b.append(path(lip, sw=4.5))
        b.append(path(f"M-60 -24 Q0 0 60 -24", sw=2, stroke="#7a6a6a"))  # cracked lip line
        for s in (-1, 1):   # stitched mouth corners
            b.append(path(f"M{70*s} -30 L{92*s} -40", sw=3, stroke="#6a4b4b"))
            b.append(path(f"M{76*s} -42 L{80*s} -26 M{86*s} -46 L{90*s} -30", sw=2.5))
    elif expr == "timid":
        o = 18 * min(mouth, 2)
        lip = f"M-34 -20 Q0 -26 34 -20 Q20 {-14 + o} 0 {-12 + o} Q-20 {-14 + o} -34 -20 Z"
        b.append(fillp(lip, "#1a0f0e")); b.append(path(lip, sw=4))
        for k in range(-2, 3):
            x = k * 11
            b.append(f'<path d="M{x-4} -22 L{x+4} -22 L{x+3} -12 L{x-3} -12 Z" fill="{GN["tooth"]}" stroke="#3a2e22" stroke-width="1.4"/>')
    # jaw stubble/texture dots
    for x, y in ((-30, 30), (-16, 40), (0, 44), (18, 38), (32, 26), (-40, 14), (40, 10)):
        b.append(circle(x, y, 1.6, GN["skinD"], sw=0))
    return "".join(b)


def _knit(d, base, shade, rows=(), clip_id=None):
    """Knitted sweater: base shape + rows of little V stitches."""
    g = [shaded(d, base, [("M20 -1300 L200 -1300 L200 -500 L20 -500 Z", shade)])]
    cid = clip_id or f"k{abs(hash(d)) % 10**8}"
    g.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})" opacity="0.55">')
    for y in range(-1180, -560, 22):
        for x in range(-160, 170, 20):
            g.append(f'<path d="M{x} {y} l6 8 l6 -8" fill="none" stroke="{GN["knitS"]}" stroke-width="2"/>')
    g.append('</g>')
    g.append(path(d, sw=5))
    return "".join(g)


def _bony_hand(x, y, s=1.0, flip=1, pose="hang"):
    """Long bony fingers with knuckles and dark nails, origin at wrist."""
    f = flip
    g = [f'<g transform="translate({x},{y}) scale({s * f},{s})">']
    g.append(shaded("M-26 0 C-34 30 -30 60 -20 80 L22 80 C30 60 34 30 26 0 Z", GN["skin"], [("M6 -10 L40 -10 L40 90 L6 90 Z", GN["skinS"])]))
    if pose == "hang":
        for i, (dx, ln) in enumerate(((-18, 120), (-6, 140), (6, 136), (18, 112))):
            g.append(path(f"M{dx} 76 L{dx*1.2} {76+ln*0.5} L{dx*1.3} {76+ln}", sw=13))
            g.append(path(f"M{dx} 76 L{dx*1.2} {76+ln*0.5} L{dx*1.3} {76+ln}", sw=8, stroke=GN["skin"]))
            g.append(circle(dx * 1.2, 76 + ln * 0.5, 5.5, GN["skinL"], sw=2))
            g.append(f'<path d="M{dx*1.3-4} {76+ln-4} L{dx*1.3+4} {76+ln-4} L{dx*1.3} {76+ln+12} Z" fill="{GN["nail"]}"/>')
        g.append(path("M-26 30 L-46 70 L-50 100", sw=12)); g.append(path("M-26 30 L-46 70 L-50 100", sw=7, stroke=GN["skin"]))
    else:  # grip: curled fingers
        for dx in (-18, -6, 6, 18):
            g.append(path(f"M{dx} 70 Q{dx+2} 110 {dx-10} 120", sw=13)); g.append(path(f"M{dx} 70 Q{dx+2} 110 {dx-10} 120", sw=8, stroke=GN["skin"]))
            g.append(f'<circle cx="{dx-10}" cy="120" r="4" fill="{GN["nail"]}"/>')
    g.append('</g>')
    return "".join(g)


def gena(expr="grin", arms="down", mouth=0.0, blink=0.0, breath=0.0, beanie=False, look=0, lean=0.0):
    b = []
    for sx in (-40, 40):  # thin legs in torn trousers
        b.append(shaded(f"M{sx-28} -640 L{sx-22} -60 L{sx+22} -60 L{sx+28} -640 Z", "#2e3133", [(f"M{sx+4} -660 L{sx+40} -660 L{sx+40} -50 L{sx+4} -50 Z", "#232527")],
                        lines=[(f"M{sx-20} -260 l14 -10 l10 12 M{sx-10} -420 q8 6 16 0", 2.5)]))
        b.append(shaded(f"M{sx-20} -70 L{sx+20} -70 L{sx+18} -30 L{sx-18} -30 Z", GN["skin"], [(f"M{sx+4} -80 L{sx+30} -80 L{sx+30} -20 L{sx+4} -20 Z", GN["skinS"])]))
        b.append(shaded(f"M{sx-30} -34 C{sx-44} 0 {sx+80} 6 {sx+66} -18 L{sx+20} -40 Z", GN["skinD"],
                        lines=[(f"M{sx+30} -20 l6 -4 M{sx+46} -16 l6 -4 M{sx+60} -12 l6 -4", 2)]))
    up = -5 * breath
    b.append(f'<g transform="translate(0,{up}) rotate({lean*6} 0 -620)">')
    # knitted sweater, ragged hem with holes
    sweater = ("M-60 -1190 C-130 -1180 -150 -1130 -156 -1040 C-160 -900 -150 -760 -132 -620 L-110 -600 L-92 -632 L-70 -596 L-40 -628 "
               "L-12 -592 L16 -630 L44 -596 L70 -628 L96 -598 L132 -620 C150 -760 160 -900 156 -1040 C150 -1130 130 -1180 60 -1190 Z")
    b.append(_knit(sweater, GN["knit"], GN["knitS"]))
    b.append(shaded("M-60 -1196 Q0 -1160 60 -1196 L58 -1170 Q0 -1134 -58 -1170 Z", GN["knitL"], lines=[("M-50 -1180 l0 14 M-30 -1172 l0 14 M-10 -1168 l0 14 M10 -1168 l0 14 M30 -1172 l0 14 M50 -1180 l0 14", 2)]))
    for hx, hy, r in ((-70, -820, 16), (60, -930, 12), (20, -700, 10)):
        b.append(ell(hx, hy, r, r * 0.8, "#16191a", sw=3))
        b.append(path(f"M{hx-r} {hy} q-6 -8 -2 -16 M{hx+r} {hy} q6 8 2 16", sw=2, stroke=GN["knitL"]))
    b.append(path("M-90 -1000 q30 20 60 0 M40 -1060 q20 14 44 4", sw=2, stroke=GN["knitL"]))
    # long sinewy neck with tendons & adam's apple
    neck = "M-26 -1300 L-32 -1186 L32 -1186 L26 -1300 Z"
    b.append(shaded(neck, GN["skin"], [("M6 -1310 L40 -1310 L40 -1180 L6 -1180 Z", GN["skinS"])],
                    lines=[("M-16 -1296 L-20 -1196 M14 -1296 L18 -1196", 2.5), ("M-6 -1250 q6 -10 12 0", 3)]))
    # arms
    def arm(s, kind):
        if kind == "down":
            d = f"M{110*s} -1176 C{170*s} -1110 {196*s} -900 {190*s} -660 L{152*s} -660 C{156*s} -880 {136*s} -1060 {80*s} -1150 Z"
            return _knit(d, GN["knit"] if s < 0 else GN["knitS"], GN["knitS"]) + _bony_hand(171 * s, -668, 1.0, s, "hang")
        d = f"M{110*s} -1176 C{170*s} -1100 {190*s} -980 {150*s} -900 L{40*s} -880 L{40*s} -920 L{120*s} -940 C{140*s} -1000 {120*s} -1100 {80*s} -1150 Z"
        return _knit(d, GN["knit"] if s < 0 else GN["knitS"], GN["knitS"])
    if arms == "down":
        b.append(arm(-1, "down")); b.append(arm(1, "down"))
    else:
        b.append(arm(-1, "reach")); b.append(arm(1, "reach"))
        if arms == "pot":
            b.append(shaded("M-120 -960 L120 -960 L110 -820 C108 -800 -108 -800 -110 -820 Z", "#8b8f86", [("M40 -970 L130 -970 L130 -800 L40 -800 Z", "#6f736b")],
                            lines=[("M-120 -940 L120 -940", 4), ("M-80 -900 l10 30", 2)]))
            b.append(f'<ellipse cx="0" cy="-960" rx="120" ry="20" fill="#9b2f2a" stroke="{O}" stroke-width="5"/>')
            b.append(f'<ellipse cx="-30" cy="-962" rx="20" ry="5" fill="#c9574a"/>')
            b.append(path("M-150 -950 L-120 -950 M120 -950 L150 -950", sw=10))
            b.append(path("M60 -1000 L-10 -1150", sw=8, stroke="#c9c4b4"))
            b.append(_bony_hand(-120, -950, 0.8, -1, "grip")); b.append(_bony_hand(120, -950, 0.8, 1, "grip"))
        elif arms == "plate":
            b.append(f'<ellipse cx="0" cy="-930" rx="140" ry="44" fill="#eef2f4" stroke="{O}" stroke-width="6"/>')
            b.append(f'<ellipse cx="0" cy="-930" rx="90" ry="26" fill="none" stroke="#c7d0d6" stroke-width="5"/>')
            b.append(path("M-50 -960 l10 -14 M40 -950 l14 -10", sw=4, stroke="#ffffff"))
            for s in (-1, 1):
                b.append(shaded(f"M{120*s} -960 C{160*s} -960 {170*s} -900 {130*s} -880 L{80*s} -880 L{70*s} -950 Z", "#e77fa6",
                                [(f"M{110*s} -990 L{180*s} -990 L{180*s} -870 L{110*s} -870 Z", "#c95f87")], lines=[(f"M{96*s} -930 l{20*s} -6", 2)]))
        elif arms == "measure":
            b.append(f'<rect x="-40" y="-950" width="520" height="34" fill="#f2d24b" stroke="{O}" stroke-width="5"/>')
            for k in range(26):
                x = -30 + k * 20
                b.append(path(f"M{x} -950 L{x} {-934 if k % 5 else -924}", sw=3))
            b.append(shaded("M-110 -990 L-20 -990 L-20 -880 L-110 -880 Z", "#d6b235", lines=[("M-90 -935 l50 0", 4)]))
            b.append(_bony_hand(-100, -960, 0.75, -1, "grip"))
    b.append(f'<g transform="translate(0,{-1290 - 2*breath})">{gena_head(expr, mouth, blink, look)}')
    if beanie:
        b.append(shaded("M-96 -230 C-100 -340 100 -340 96 -230 Z", "#b8362b", lines=[("M-60 -240 L-60 -310 M-20 -236 L-20 -324 M20 -236 L20 -324 M60 -240 L60 -310", 6)]))
        b.append(shaded("M-104 -250 L104 -250 L104 -206 L-104 -206 Z", "#e8e2d2", lines=[("M-90 -228 l180 0", 2)]))
        b.append(circle(0, -336, 28, "#e8e2d2"))
    b.append('</g></g>')
    return "".join(b)


if __name__ == "__main__":
    import subprocess
    W, H = 2200, 1400
    body = (f'<rect width="{W}" height="{H}" fill="#2a3440"/>'
            f'<g transform="translate(260,1340)">{guy("artyom","shout","point",mouth=1.6)}</g>'
            f'<g transform="translate(640,1340)">{guy("artyom","panic","head")}</g>'
            f'<g transform="translate(1000,1340)">{guy("dima","deadpan","mug",mouth=0.8)}</g>'
            f'<g transform="translate(1340,1340)">{guy("dima","normal","down",scarf=True,blink=1)}</g>'
            f'<g transform="translate(1850,1340) scale(0.85)">{gena("grin","down",mouth=1.2)}</g>')
    open("/tmp/c5.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{body}</svg>')
    subprocess.run(["rsvg-convert", "/tmp/c5.svg", "-o", "/home/claude/v4/t1.png"], check=True)
    body = (f'<rect width="1400" height="900" fill="#2a3440"/>'
            f'<g transform="translate(350,1050) scale(2.4)">{guy_head("artyom","normal")}</g>'
            f'<g transform="translate(1000,1600) scale(2.2)">{gena_head("grin",0.0)}</g>')
    body = (f'<rect width="1400" height="900" fill="#2a3440"/>'
            f'<g transform="translate(330,430) scale(2.4)">{guy_head("artyom","normal")}</g>'
            f'<g transform="translate(1000,760) scale(2.2)">{gena_head("grin",0.0)}</g>')
    open("/tmp/c6.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900">{body}</svg>')
    subprocess.run(["rsvg-convert", "/tmp/c6.svg", "-o", "/home/claude/v4/t2.png"], check=True)
