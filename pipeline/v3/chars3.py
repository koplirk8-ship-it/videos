"""Characters for 'POV: снял комнату за 9 тысяч': Artyom, Dima (normal young guys) and Gena (wardrobe monster).
Same style as chars.py: flat colours + cel shading + dark outlines. Origins at FEET centre (standing)."""
import sys
sys.path.insert(0, "/home/claude/v2")
from chars import shaded, path, fillp, circle, ell, hand, O, uid

SK = dict(skin="#efd2b6", skinS="#d4ad8e")

def eyes(expr, ex=(-34, 34), y=0, iris="#4a3a2a"):
    b = []
    for x in ex:
        if expr in ("deadpan", "deadpan_r"):
            b.append(ell(x, y, 15, 15, "#fbf7ef", sw=4))
            b.append(circle(x + (4 if expr == "deadpan_r" else 0), y + 3, 7, O, sw=0))
            b.append(fillp(f"M{x-19} {y-2} L{x+19} {y-2} L{x+19} {y-20} L{x-19} {y-20} Z", SK["skin"]))
            b.append(path(f"M{x-17} {y-2} L{x+17} {y-2}", sw=6))
        elif expr == "sleepy":
            b.append(path(f"M{x-16} {y} Q{x} {y+10} {x+16} {y}", sw=6))
        elif expr in ("shout", "panic", "scared"):
            r = 19 if expr != "shout" else 17
            b.append(ell(x, y, r, r + 2, "#fbf7ef", sw=4))
            b.append(circle(x, y, 4.5, O, sw=0))
        else:  # normal
            b.append(ell(x, y, 15, 17, "#fbf7ef", sw=4))
            b.append(circle(x + 1, y + 2, 8, iris, sw=0)); b.append(circle(x + 1, y + 2, 4.5, O, sw=0))
            b.append(circle(x + 4, y - 2, 2.5, "#fff", sw=0))
    return "".join(b)

def brows(expr, y=-32):
    if expr in ("shout",):
        return path(f"M-54 {y+4} L-16 {y-10}", sw=8) + path(f"M16 {y-10} L54 {y+4}", sw=8)
    if expr in ("panic", "scared"):
        return path(f"M-54 {y-6} Q-34 {y-22} -16 {y-14}", sw=7) + path(f"M16 {y-14} Q34 {y-22} 54 {y-6}", sw=7)
    if expr in ("deadpan", "deadpan_r", "sleepy"):
        return path(f"M-54 {y} L-16 {y}", sw=7) + path(f"M16 {y} L54 {y}", sw=7)
    return path(f"M-52 {y} Q-34 {y-8} -16 {y-2}", sw=6) + path(f"M16 {y-2} Q34 {y-8} 52 {y}", sw=6)

def mouth(expr, y=70):
    if expr == "shout":
        return (shaded(f"M-34 {y-14} Q0 {y-24} 34 {y-14} Q36 {y+40} 0 {y+46} Q-36 {y+40} -34 {y-14} Z", "#5c1f1a",
                       [(f"M-30 {y+20} Q0 {y+6} 30 {y+20} L30 {y+60} L-30 {y+60} Z", "#c4544a")])
                + fillp(f"M-24 {y-14} L24 {y-14} L22 {y-4} L-22 {y-4} Z", "#f6f1e4"))
    if expr == "panic":
        return path(f"M-26 {y} q9 -10 17 0 q9 10 17 0 q9 -10 18 0", sw=5)
    if expr == "scared":
        return ell(0, y, 11, 14, "#5c1f1a", sw=4)
    if expr in ("deadpan", "deadpan_r"):
        return path(f"M-20 {y} L20 {y}", sw=5)
    if expr == "sleepy":
        return path(f"M-12 {y} Q0 {y+6} 12 {y}", sw=4)
    return path(f"M-18 {y-2} Q0 {y+8} 18 {y-2}", sw=4)


def guy_head(who, expr):
    """Head centred at (0,0)."""
    b = []
    if who == "artyom":
        hair, hairS = "#8a6a43", "#6c512f"
    else:
        hair, hairS = "#2b2522", "#1b1715"
    # ears + neck
    b.append(shaded("M-80 -6 C-104 -14 -108 30 -86 40 Z", SK["skin"], [("M-110 -20 L-84 -20 L-84 50 L-110 50 Z", SK["skinS"])]))
    b.append(shaded("M80 -6 C104 -14 108 30 86 40 Z", SK["skin"], [("M70 -20 L120 -20 L120 50 L70 50 Z", SK["skinS"])]))
    face = "M-80 -50 C-86 10 -78 70 -56 100 C-36 124 -16 132 0 132 C16 132 36 124 56 100 C78 70 86 10 80 -50 C70 -110 -70 -110 -80 -50 Z"
    b.append(shaded(face, SK["skin"], [("M40 -120 C90 -60 86 60 40 130 L140 130 L140 -120 Z", SK["skinS"])]))
    # hair
    if who == "artyom":   # messy fringe
        b.append(shaded("M-92 -30 C-104 -110 -40 -150 10 -146 C70 -144 108 -110 94 -28 C84 -50 70 -62 56 -60 L48 -40 C36 -62 20 -66 8 -58 L-4 -34 C-16 -60 -34 -66 -50 -56 L-62 -36 C-70 -48 -82 -46 -92 -30 Z",
                        hair, [("M30 -160 L120 -160 L120 -20 L30 -20 Z", hairS)],
                        lines=[("M-60 -110 Q-50 -80 -50 -56 M-10 -130 Q-6 -90 8 -58 M40 -128 Q50 -90 48 -40", 3)]))
        b.append(path("M-20 -146 q10 -24 26 -18 M10 -146 q20 -20 30 -4", sw=6, stroke=hair))
    else:                 # short neat dark hair
        b.append(shaded("M-88 -20 C-96 -110 -40 -140 6 -138 C64 -136 100 -104 90 -20 C80 -44 60 -66 20 -70 C-20 -70 -60 -60 -88 -20 Z",
                        hair, [("M30 -150 L120 -150 L120 -10 L30 -10 Z", hairS)],
                        lines=[("M-60 -90 Q-30 -110 0 -100 M10 -112 Q40 -116 66 -96", 3)]))
    b.append(eyes(expr, y=6))
    b.append(brows(expr, y=-30))
    if who == "dima":  # glasses
        for x in (-34, 34):
            b.append(f'<rect x="{x-27}" y="-16" width="54" height="42" rx="12" fill="#cfe3ef" fill-opacity="0.18" stroke="{O}" stroke-width="5"/>')
        b.append(path("M-7 2 L7 2", sw=5)); b.append(path("M-61 0 L-82 -6 M61 0 L82 -6", sw=5))
    b.append(path("M-2 18 C2 38 10 50 8 58 C4 64 -6 64 -10 60", sw=4))
    if who == "artyom":
        b.append(path("M-50 90 l6 4 M50 90 l-6 4", sw=3))  # dimples
    else:
        b.append(f'<path d="M-60 80 C-40 120 40 120 60 80 C40 104 -40 104 -60 80 Z" fill="#2b2522" opacity="0.18"/>')  # light stubble
    b.append(mouth(expr, y=88))
    if expr == "panic":
        b.append(shaded("M96 -60 C106 -40 110 -26 100 -18 C90 -12 82 -24 86 -40 Z", "#bfe3f5"))  # sweat drop
    return "".join(b)


def guy(who, expr="normal", arms="down", prop=None, scarf=False):
    """Standing young guy, origin at feet centre, ~1120 units tall."""
    if who == "artyom":
        top, topS, topL, pants, pantsS, shoe = "#4f6f66", "#3c5750", "#5f8278", "#3a3f4a", "#2c3038", "#d9d4c8"
    else:
        top, topS, topL, pants, pantsS, shoe = "#8a8f96", "#6f747b", "#a1a6ad", "#2f3a52", "#232c40", "#3a2c24"
    b = []
    # legs + shoes
    for sx in (-48, 48):
        b.append(shaded(f"M{sx-40} -470 L{sx-36} -40 L{sx+36} -40 L{sx+40} -470 Z", pants,
                        [(f"M{sx+8} -480 L{sx+60} -480 L{sx+60} -30 L{sx+8} -30 Z", pantsS)],
                        lines=[(f"M{sx-20} -200 q10 8 24 4", 3)]))
        b.append(shaded(f"M{sx-46} -44 L{sx+40} -44 C{sx+70} -40 {sx+72} 0 {sx+52} 0 L{sx-50} 0 C{sx-56} -14 {sx-54} -34 {sx-46} -44 Z", shoe,
                        lines=[(f"M{sx-48} -12 L{sx+66} -12", 4)]))
    # torso
    if who == "artyom":  # hoodie
        torso = "M-40 -852 C-110 -848 -138 -826 -146 -770 C-152 -660 -146 -540 -132 -430 L132 -430 C146 -540 152 -660 146 -770 C138 -826 110 -848 40 -852 Z"
        b.append(shaded(torso, top, [("M20 -850 L170 -850 L170 -420 L20 -420 Z", topS)],
                        lines=[("M-128 -470 L128 -470", 4)]))
        b.append(shaded("M-70 -600 L70 -600 L84 -490 L-84 -490 Z", topS, lines=[("M0 -600 L0 -490", 3)]))  # pocket
        b.append(shaded("M-96 -850 C-60 -800 60 -800 96 -850 C80 -880 -80 -880 -96 -850 Z", topL))  # hood rim
        b.append(path("M-26 -820 L-30 -720 M26 -820 L30 -720", sw=5, stroke="#e8e2d2"))
    else:  # t-shirt over long sleeve
        torso = "M-40 -852 C-108 -848 -136 -826 -142 -770 C-146 -660 -142 -540 -128 -430 L128 -430 C142 -540 146 -660 142 -770 C136 -826 108 -848 40 -852 Z"
        b.append(shaded(torso, top, [("M20 -850 L170 -850 L170 -420 L20 -420 Z", topS)],
                        lines=[("M-50 -830 Q0 -790 50 -830", 5)]))
        b.append(shaded("M-150 -540 L150 -540 L150 -440 L-150 -440 Z", "#3d4b63", lines=[("M-140 -500 l20 0", 0)]) if False else "")
    # neck
    b.append(shaded("M-30 -880 L-32 -822 L32 -822 L30 -880 Z", SK["skin"], [("M-40 -890 L40 -890 L40 -850 L-40 -850 Z", SK["skinS"])]))
    if scarf:
        b.append(shaded("M-80 -850 Q0 -800 80 -850 L84 -810 Q0 -760 -84 -810 Z", "#b8362b",
                        lines=[("M-40 -836 L-44 -790 M0 -824 L0 -778 M40 -836 L44 -790", 10)]))
        b.append(shaded("M30 -800 L70 -560 L20 -552 L-6 -790 Z", "#b8362b",
                        lines=[("M20 -740 L56 -746 M28 -680 L64 -686 M36 -620 L70 -626", 12), ("M26 -560 l0 20 M42 -560 l0 20 M58 -562 l0 20", 4)]))
    # arms
    sleeve, sleeveS = (top, topS) if who == "artyom" else ("#3d4b63", "#2e3a4f")
    def arm(side, kind):
        s = side
        if kind == "down":
            d = f"M{120*s} -820 C{170*s} -760 {182*s} -600 {176*s} -470 L{132*s} -468 C{136*s} -600 {130*s} -720 {100*s} -790 Z"
            return shaded(d, sleeve if s < 0 else sleeveS) + hand(176 * s - 22 * s, -478, 1.0, -s if s > 0 else 1, SK["skin"], SK["skinS"])
        if kind == "head":  # hands on head (panic)
            d = f"M{120*s} -820 C{190*s} -840 {210*s} -940 {150*s} -1040 L{112*s} -1010 C{150*s} -930 {140*s} -860 {100*s} -790 Z"
            return shaded(d, sleeve if s < 0 else sleeveS) + hand(138 * s, -1080, 1.0, -s if s > 0 else 1, SK["skin"], SK["skinS"], "grip")
        if kind == "point":  # pointing outward
            d = f"M{120*s} -820 C{200*s} -800 {280*s} -760 {330*s} -740 L{320*s} -700 C{260*s} -712 {180*s} -740 {110*s} -770 Z"
            g = shaded(d, sleeve if s < 0 else sleeveS)
            fx = 330 * s
            g += shaded(f"M{fx} -748 L{fx+80*s} -738 C{fx+92*s} -736 {fx+92*s} -722 {fx+80*s} -720 L{fx+30*s} -716 C{fx+34*s} -700 {fx+20*s} -690 {fx} -694 Z", SK["skin"])
            return g
        if kind == "mug":
            d = f"M{120*s} -820 C{170*s} -760 {180*s} -660 {150*s} -600 L{60*s} -610 L{70*s} -650 L{120*s} -650 C{130*s} -700 {126*s} -740 {100*s} -790 Z"
            g = shaded(d, sleeve if s < 0 else sleeveS)
            g += shaded(f"M{20*s} -700 L{100*s} -700 L{96*s} -590 L{24*s} -590 Z", "#d8d2c2", lines=[(f"M{30*s} -680 L{90*s} -680", 3)])
            g += path(f"M{100*s} -680 C{130*s} -680 {130*s} -620 {98*s} -620", sw=7)
            g += path(f"M{50*s} -730 q-10 -20 0 -40 M{74*s} -730 q-10 -20 0 -40", sw=4, stroke="#9aa6b3")
            g += hand(80 * s, -640, 0.9, -s if s > 0 else 1, SK["skin"], SK["skinS"], "grip")
            return g
        return ""
    la, ra = {"down": ("down", "down"), "head": ("head", "head"), "point": ("point", "down"),
              "mug": ("down", "mug"), "point_r": ("down", "point")}[arms]
    b.append(arm(-1, la)); b.append(arm(1, ra))
    b.append(f'<g transform="translate(0,-990)">{guy_head(who, expr)}</g>')
    return "".join(b)


def guy_in_bed(expr="scared"):
    """Artyom's head on a pillow (for bed shots), centred at (0,0)."""
    return f'<g transform="translate(0,0)">{guy_head("artyom", expr)}</g>'


# ------------------------------------------------------------------ Gena, the wardrobe monster
GN = dict(body="#9aa1a6", bodyS="#7b8287", dark="#5d6368")

def gena_head(expr="grin"):
    b = []
    head = "M-90 -40 C-100 -180 -60 -260 0 -262 C60 -260 100 -180 90 -40 C80 40 40 80 0 82 C-40 80 -80 40 -90 -40 Z"
    b.append(shaded(head, GN["body"], [("M30 -280 C90 -180 100 0 30 90 L140 90 L140 -280 Z", GN["bodyS"])],
                    lines=[("M-60 -200 l14 10 M-40 -224 l6 16 M50 -210 l-12 10", 3)]))
    # stitches across the forehead
    b.append(path("M-50 -170 Q0 -190 50 -168", sw=4))
    for x in (-40, -20, 0, 20, 40):
        b.append(path(f"M{x-4} -188 l8 22", sw=3))
    # hollow eye sockets with tiny white pupils
    for x in (-38, 38):
        b.append(ell(x, -88, 30, 40, "#111316", sw=5))
        if expr != "closed":
            b.append(circle(x + 4, -84, 6, "#f4f1e6", sw=0))
    # wide stitched grin
    if expr in ("grin", "eat"):
        b.append(shaded("M-70 -10 Q0 40 70 -10 Q0 10 -70 -10 Z", "#1a1a1c"))
        for k in range(-5, 6):
            x = k * 12
            b.append(fillp(f"M{x-5} {-2 + abs(k)*-0.5} L{x+5} {-2 + abs(k)*-0.5} L{x} {12 - abs(k)} Z", "#efeadc"))
        b.append(path("M-70 -10 Q0 40 70 -10", sw=5))
        for x in (-80, 80):
            b.append(path(f"M{x} -20 l{-8 if x<0 else 8} 14", sw=3))
    elif expr == "shy":
        b.append(path("M-30 10 Q0 0 30 10", sw=5))
        b.append(ell(-60, -30, 16, 8, "#c98d9a", sw=0, extra='opacity="0.6"'))
        b.append(ell(60, -30, 16, 8, "#c98d9a", sw=0, extra='opacity="0.6"'))
    return "".join(b)


def gena(expr="grin", arms="down", prop=None, beanie=False):
    """Tall gaunt monster, origin at feet centre, ~1500 units tall (taller than the guys)."""
    b = []
    for sx in (-40, 40):
        b.append(shaded(f"M{sx-22} -620 L{sx-18} -30 L{sx+18} -30 L{sx+22} -620 Z", GN["body"], [(f"M{sx+4} -640 L{sx+40} -640 L{sx+40} -20 L{sx+4} -20 Z", GN["bodyS"])]))
        b.append(shaded(f"M{sx-30} -34 C{sx-40} 0 {sx+70} 4 {sx+60} -20 L{sx+20} -40 Z", GN["dark"]))
    # ragged long coat/skin-sack torso, hunched
    torso = "M-110 -1180 C-150 -1000 -140 -800 -120 -600 L-90 -560 L-60 -610 L-30 -560 L0 -600 L30 -560 L60 -610 L90 -560 L120 -600 C140 -800 150 -1000 110 -1180 Z"
    b.append(shaded(torso, "#4c5257", [("M20 -1200 L170 -1200 L170 -540 L20 -540 Z", "#3c4145")],
                    lines=[("M-60 -1100 Q-50 -900 -70 -700 M50 -1080 Q40 -880 60 -680", 3)]))
    # long neck
    b.append(shaded("M-24 -1280 L-28 -1170 L28 -1170 L24 -1280 Z", GN["body"], [("M4 -1290 L40 -1290 L40 -1160 L4 -1160 Z", GN["bodyS"])]))
    def arm(s, kind):
        if kind == "down":
            d = f"M{100*s} -1170 C{170*s} -1100 {200*s} -900 {196*s} -620 L{168*s} -620 C{168*s} -880 {140*s} -1060 {80*s} -1140 Z"
            g = shaded(d, GN["body"] if s < 0 else GN["bodyS"])
            fx, fy = 182 * s, -620
            for k in range(4):
                g += path(f"M{fx + (k-1.5)*10} {fy} q{6*s} 80 {(k-1.5)*14} 150", sw=9, stroke=O)
                g += path(f"M{fx + (k-1.5)*10} {fy} q{6*s} 80 {(k-1.5)*14} 150", sw=4, stroke=GN["body"])
            return g
        if kind == "reach":  # arm reaching forward/up holding something at chest level
            d = f"M{100*s} -1170 C{170*s} -1100 {190*s} -980 {150*s} -900 L{40*s} -880 L{40*s} -920 L{120*s} -940 C{140*s} -1000 {120*s} -1100 {80*s} -1140 Z"
            return shaded(d, GN["body"] if s < 0 else GN["bodyS"])
        return ""
    if arms == "down":
        b.append(arm(-1, "down")); b.append(arm(1, "down"))
    elif arms == "pot":
        b.append(arm(-1, "reach")); b.append(arm(1, "reach"))
        b.append(shaded("M-120 -960 L120 -960 L110 -820 C108 -800 -108 -800 -110 -820 Z", "#8b8f86", [("M40 -970 L130 -970 L130 -800 L40 -800 Z", "#6f736b")],
                        lines=[("M-120 -940 L120 -940", 4)]))
        b.append(f'<ellipse cx="0" cy="-960" rx="120" ry="20" fill="#9b2f2a" stroke="{O}" stroke-width="5"/>')
        b.append(path("M-150 -950 L-120 -950 M120 -950 L150 -950", sw=10))
        b.append(path("M60 -1000 L-10 -1080", sw=8, stroke="#c9c4b4"))  # ladle handle up to mouth
    elif arms == "plate":  # pink rubber gloves + clean plate
        b.append(arm(-1, "reach")); b.append(arm(1, "reach"))
        b.append(f'<ellipse cx="0" cy="-930" rx="140" ry="44" fill="#eef2f4" stroke="{O}" stroke-width="6"/>')
        b.append(f'<ellipse cx="0" cy="-930" rx="90" ry="26" fill="none" stroke="#c7d0d6" stroke-width="5"/>')
        b.append(path("M-50 -960 l10 -14 M40 -950 l14 -10", sw=4, stroke="#ffffff"))
        for s in (-1, 1):
            b.append(shaded(f"M{120*s} -960 C{160*s} -960 {170*s} -900 {130*s} -880 L{80*s} -880 L{70*s} -950 Z", "#e77fa6", [(f"M{110*s} -990 L{180*s} -990 L{180*s} -870 L{110*s} -870 Z", "#c95f87")]))
    elif arms == "measure":  # holding tape measure stretched out to the right
        b.append(arm(-1, "reach")); b.append(arm(1, "reach"))
        b.append(f'<rect x="-40" y="-950" width="520" height="34" fill="#f2d24b" stroke="{O}" stroke-width="5"/>')
        for k in range(26):
            x = -30 + k * 20
            b.append(path(f"M{x} -950 L{x} {-934 if k % 5 else -924}", sw=3))
        b.append(shaded("M-110 -990 L-20 -990 L-20 -880 L-110 -880 Z", "#d6b235", lines=[("M-90 -935 l50 0", 4)]))
    elif arms == "blanket":
        pass
    b.append(f'<g transform="translate(0,-1290)">{gena_head(expr)}</g>')
    if beanie:
        b.append(f'<g transform="translate(0,-1290)">' +
                 shaded("M-96 -170 C-100 -280 100 -280 96 -170 Z", "#b8362b", lines=[("M-60 -180 L-60 -250 M-20 -176 L-20 -264 M20 -176 L20 -264 M60 -180 L60 -250", 6)]) +
                 shaded("M-104 -190 L104 -190 L104 -150 L-104 -150 Z", "#e8e2d2") + circle(0, -276, 28, "#e8e2d2") + '</g>')
    return "".join(b)


if __name__ == "__main__":
    import subprocess
    W, H = 2000, 1300
    body = (f'<rect width="{W}" height="{H}" fill="#2a3440"/>'
            f'<g transform="translate(250,1240) scale(0.95)">{guy("artyom","shout","point")}</g>'
            f'<g transform="translate(600,1240) scale(0.95)">{guy("artyom","panic","head")}</g>'
            f'<g transform="translate(950,1240) scale(0.95)">{guy("dima","deadpan","mug")}</g>'
            f'<g transform="translate(1250,1240) scale(0.95)">{guy("dima","deadpan_r","down", scarf=True)}</g>'
            f'<g transform="translate(1700,1240) scale(0.75)">{gena("grin","pot")}</g>')
    open("/tmp/c3.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{body}</svg>')
    subprocess.run(["rsvg-convert", "/tmp/c3.svg", "-o", "/home/claude/v3/chars_test.png"], check=True)
    body2 = (f'<rect width="{W}" height="{H}" fill="#2a3440"/>'
             f'<g transform="translate(300,1240) scale(0.75)">{gena("grin","plate")}</g>'
             f'<g transform="translate(800,1240) scale(0.75)">{gena("grin","measure")}</g>'
             f'<g transform="translate(1400,1240) scale(0.75)">{gena("shy","down",beanie=True)}</g>'
             f'<g transform="translate(1800,700) scale(1.2)">{guy_in_bed("scared")}</g>')
    open("/tmp/c4.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{body2}</svg>')
    subprocess.run(["rsvg-convert", "/tmp/c4.svg", "-o", "/home/claude/v3/chars_test2.png"], check=True)
