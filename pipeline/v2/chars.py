"""Characters in the reference style: realistic proportions, flat colours with cel shading,
dark-brown outlines, big round eyes with ring, defined nose/brows, stubble, fingers, clothing folds."""
import itertools

O = "#2a1c17"
SW = 5
_uid = itertools.count()

def uid(p="c"):
    return f"{p}{next(_uid)}"

def path(d, fill="none", sw=SW, stroke=O, extra=""):
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linejoin="round" stroke-linecap="round" {extra}/>')

def fillp(d, fill, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="none" {extra}/>'

def shaded(d, fill, shades=(), sw=SW, lines=()):
    """Base shape + clipped cel-shade shapes + inner fold lines + outline on top."""
    cid = uid("clip")
    out = [f'<clipPath id="{cid}"><path d="{d}"/></clipPath>', fillp(d, fill)]
    if shades or lines:
        out.append(f'<g clip-path="url(#{cid})">')
        for sd, sf, *op in shades:
            out.append(fillp(sd, sf, f'opacity="{op[0]}"' if op else ""))
        for ld, lw in lines:
            out.append(path(ld, sw=lw))
        out.append("</g>")
    out.append(path(d, sw=sw))
    return "".join(out)

def circle(cx, cy, r, fill, sw=SW, stroke=O):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def ell(cx, cy, rx, ry, fill, sw=SW, stroke=O, extra=""):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def hand(x, y, s=1.0, flip=1, skin="#e9cfb3", shade="#cfae8f", pose="rest"):
    """Simple cartoon hand with 4 fingers + thumb, origin at wrist."""
    f = flip
    if pose == "rest":  # hand lying flat/down, fingers pointing down-in
        d = (f"M0 0 C{-22*f} 4 {-34*f} 22 {-34*f} 46 L{-36*f} 78 C{-36*f} 90 {-22*f} 92 {-20*f} 80 "
             f"L{-18*f} 92 C{-16*f} 104 {-2*f} 104 {-2*f} 92 L{0} 98 C{2*f} 110 {16*f} 108 {16*f} 96 "
             f"L{18*f} 88 C{22*f} 98 {34*f} 94 {32*f} 82 L{30*f} 50 C{40*f} 44 {44*f} 30 {36*f} 22 C{26*f} 12 {14*f} 0 0 0 Z")
        lines = [(f"M{-20*f} 62 L{-20*f} 80 M{-2*f} 66 L{-2*f} 92 M{16*f} 64 L{16*f} 94", 3)]
    else:  # fist / grip
        d = (f"M0 0 C{-28*f} 0 {-40*f} 20 {-38*f} 44 C{-36*f} 68 {-18*f} 76 {4*f} 74 C{26*f} 72 {40*f} 60 {38*f} 38 "
             f"C{36*f} 16 {22*f} 0 0 0 Z")
        lines = [(f"M{-30*f} 40 C{-10*f} 46 {10*f} 46 {30*f} 40 M{-28*f} 56 C{-8*f} 62 {12*f} 60 {28*f} 54", 3)]
    sh = [(f"M{10*f} -10 L{60*f} -10 L{60*f} 120 L{14*f} 120 Z", shade)]
    return f'<g transform="translate({x},{y}) scale({s})">{shaded(d, skin, sh, lines=lines)}</g>'


# ------------------------------------------------------------------ the man
MAN = dict(coat="#8a8c84", coatS="#6d6f68", coatL="#a2a49b", hat="#4d4f49", hatS="#393b36", band="#25231f",
           skin="#e2cdb2", skinS="#c4a98c", stub="#6d6458", trousers="#3b3b39", trousersS="#2c2c2a", shoe="#1e1b19")

def man_head(expr="smile", look=0):
    c = MAN
    b = []
    # ears
    b.append(shaded("M-74 -478 C-96 -484 -100 -446 -80 -432 C-74 -428 -70 -432 -70 -440 Z", c["skin"], [("M-100 -470 L-80 -470 L-80 -420 L-100 -420 Z", c["skinS"])]))
    b.append(shaded("M74 -478 C96 -484 100 -446 80 -432 C74 -428 70 -432 70 -440 Z", c["skin"], [("M60 -490 L110 -490 L110 -420 L60 -420 Z", c["skinS"])]))
    # neck
    b.append(shaded("M-34 -380 L-38 -318 L38 -318 L34 -380 Z", c["skin"], [("M-40 -390 L40 -390 L40 -350 L-40 -350 Z", c["skinS"])]))
    # long face
    face = "M-72 -560 C-78 -500 -76 -440 -62 -400 C-48 -362 -24 -346 0 -344 C24 -346 48 -362 62 -400 C76 -440 78 -500 72 -560 Z"
    stub = "M-66 -420 C-50 -370 -24 -352 0 -350 C24 -352 50 -370 66 -420 C50 -400 28 -392 0 -394 C-28 -392 -50 -400 -66 -420 Z"
    b.append(shaded(face, c["skin"], [
        ("M30 -600 C70 -560 90 -480 70 -400 C60 -370 40 -350 20 -340 L120 -340 L120 -600 Z", c["skinS"]),
        (stub, c["stub"], 0.35),
        ("M-90 -560 L90 -560 L90 -528 Q0 -508 -90 -528 Z", c["skinS"], 0.9),
        ("M-56 -430 C-50 -405 -40 -396 -30 -392 M56 -430 C50 -405 40 -396 30 -392", "none"),
    ], lines=[("M-50 -410 C-46 -398 -40 -392 -34 -390", 3), ("M50 -410 C46 -398 40 -392 34 -390", 3)]))
    # eyes: white with dark ring, small pupils (creepy)
    for ex in (-30, 30):
        if expr == "grin":
            b.append(path(f"M{ex-17} -470 Q{ex} -486 {ex+17} -470", sw=6))
            continue
        r = 17 if expr == "stare" else 15
        b.append(circle(ex, -472, r, "#f7f2e6", sw=5))
        pr = 4 if expr == "stare" else 6
        b.append(circle(ex + look * 5, -470, pr, O, sw=0))
        b.append(path(f"M{ex-16} -452 Q{ex} -446 {ex+16} -452", sw=3))   # eye bags
    # brows: thick, inner ends low
    if expr == "grin":
        b.append(path("M-52 -500 L-14 -494", sw=9)); b.append(path("M14 -494 L52 -500", sw=9))
    else:
        b.append(path("M-54 -502 L-14 -492", sw=9)); b.append(path("M14 -492 L54 -502", sw=9))
    # nose
    b.append(path("M-4 -466 C-2 -446 8 -428 10 -420 C6 -412 -6 -410 -12 -416", sw=4))
    # mouth
    if expr == "smile":
        b.append(path("M-30 -384 Q0 -370 30 -386", sw=5))
        b.append(path("M-34 -388 L-28 -382 M34 -390 L28 -384", sw=3))
    elif expr == "stare":
        b.append(path("M-22 -382 L22 -382", sw=5))
    elif expr == "grin":
        b.append(shaded("M-38 -392 Q0 -350 38 -392 Q0 -380 -38 -392 Z", "#f4efe2", lines=[("M-20 -386 L-18 -372 M0 -383 L0 -366 M20 -386 L18 -372", 3)]))
    # mole above right brow
    b.append(circle(44, -516, 4.5, "#4d3426", sw=0))
    # fedora
    b.append(shaded("M-150 -540 Q-140 -556 -100 -560 Q0 -572 100 -560 Q140 -556 150 -540 Q120 -522 0 -522 Q-120 -522 -150 -540 Z",
                    c["hatS"], [("M-160 -560 L160 -560 L160 -546 Q0 -566 -160 -546 Z", c["hat"])]))
    b.append(shaded("M-86 -556 C-92 -620 -70 -656 -30 -660 Q0 -648 30 -660 C70 -656 92 -620 86 -556 Q0 -570 -86 -556 Z",
                    c["hat"], [("M30 -680 L110 -680 L110 -540 L40 -540 Z", c["hatS"])],
                    lines=[("M0 -650 Q-6 -620 0 -596", 4)]))
    b.append(shaded("M-88 -574 Q0 -588 88 -574 L87 -556 Q0 -570 -87 -556 Z", c["band"]))
    return "".join(b)


def man(expr="smile", pose="sit", look=0):
    c = MAN
    b = []
    if pose == "sit":
        for sx in (-58, 58):
            b.append(shaded(f"M{sx-34} 70 L{sx-36} 240 L{sx+36} 240 L{sx+34} 70 Z", c["trousers"], [(f"M{sx+8} 50 L{sx+60} 50 L{sx+60} 250 L{sx+8} 250 Z", c["trousersS"])]))
            b.append(shaded(f"M{sx-44} 236 C{sx-48} 268 {sx+58} 272 {sx+54} 244 L{sx+38} 230 Z", c["shoe"]))
            # knees/thighs foreshortened under coat skirt
        coat = ("M-140 -300 C-150 -220 -150 -120 -134 -30 L-136 40 C-136 76 -110 92 -70 92 C-40 92 -14 84 0 72 "
                "C14 84 40 92 70 92 C110 92 136 76 136 40 L134 -30 C150 -120 150 -220 140 -300 Z")
        b.append(shaded(coat, c["coat"], [("M20 -320 L200 -320 L200 120 L20 120 Z", c["coatS"])],
                        lines=[("M0 -40 L0 70", 4), ("M-128 -24 Q-60 -6 0 -20 Q60 -6 128 -24", 3), ("M-70 92 Q-72 60 -60 30 M70 92 Q72 60 60 30", 3)]))
    else:
        for sx in (-50, 50):
            b.append(shaded(f"M{sx-34} 220 L{sx-36} 470 L{sx+36} 470 L{sx+34} 220 Z", c["trousers"], [(f"M{sx+8} 200 L{sx+60} 200 L{sx+60} 480 L{sx+8} 480 Z", c["trousersS"])]))
            b.append(shaded(f"M{sx-44} 466 C{sx-48} 500 {sx+62} 504 {sx+56} 474 L{sx+38} 460 Z", c["shoe"]))
        coat = "M-140 -300 C-155 -150 -160 80 -150 290 L150 290 C160 80 155 -150 140 -300 Z"
        b.append(shaded(coat, c["coat"], [("M20 -320 L230 -320 L230 320 L20 320 Z", c["coatS"])],
                        lines=[("M-8 -40 L-8 290", 4), ("M-120 120 Q-110 200 -130 286", 3), ("M110 140 Q100 220 120 286", 3)]))
    # torso detail: lapels, double-breasted buttons, belt, pockets
    b.append(shaded("M-40 -318 L-112 -300 L-60 -130 L0 -200 Z", c["coatL"], [("M-30 -330 L0 -330 L0 -190 L-30 -190 Z", c["coat"])]))
    b.append(shaded("M40 -318 L112 -300 L60 -130 L0 -200 Z", c["coatS"]))
    b.append(shaded("M-34 -322 L0 -200 L34 -322 Z", "#d9d4c6", lines=[("M0 -300 L0 -210", 3)]))  # shirt
    b.append(shaded("M-12 -300 L12 -300 L8 -220 L0 -205 L-8 -220 Z", "#3b3f46"))  # tie
    for bx in (-36, 36):
        for by in (-150, -95):
            b.append(circle(bx, by, 9, "#4a4b46", sw=4))
    b.append(shaded("M-140 -50 L140 -50 L140 -18 L-140 -18 Z", c["coatS"]))
    b.append(shaded("M-22 -56 L22 -56 L22 -12 L-22 -12 Z", "#b9a061", lines=[("M-10 -24 L10 -24", 4)]))
    b.append(path("M-150 40 L-70 40 M70 40 L150 40", sw=4) if pose == "stand" else "")
    # arms
    if pose == "sit":
        la = "M-140 -296 C-176 -270 -186 -200 -180 -130 C-176 -70 -150 -30 -110 -6 L-82 -40 C-114 -64 -132 -100 -134 -150 C-136 -200 -128 -250 -112 -280 Z"
        b.append(shaded(la, c["coat"], [("M-150 -310 L-120 -310 L-120 0 L-150 0 Z", c["coatS"], 0.55)], lines=[("M-176 -140 Q-160 -128 -146 -112", 3)]))
        ra = "M140 -296 C176 -270 186 -200 180 -130 C176 -70 150 -30 110 -6 L82 -40 C114 -64 132 -100 134 -150 C136 -200 128 -250 112 -280 Z"
        b.append(shaded(ra, c["coatS"], lines=[("M176 -140 Q160 -128 146 -112", 3)]))
        b.append(hand(-92, -24, 0.95, 1, c["skin"], c["skinS"]))
        b.append(hand(92, -24, 0.95, -1, c["skin"], c["skinS"]))
    else:
        la = "M-136 -296 C-172 -250 -182 -100 -176 140 L-130 142 C-134 0 -128 -150 -108 -270 Z"
        b.append(shaded(la, c["coat"], [("M-150 -310 L-132 -310 L-132 150 L-150 150 Z", c["coatS"], 0.6)], lines=[("M-178 40 Q-162 50 -140 44", 3)]))
        ra = "M136 -296 C172 -250 182 -100 176 140 L130 142 C134 0 128 -150 108 -270 Z"
        b.append(shaded(ra, c["coatS"], lines=[("M178 40 Q162 50 140 44", 3)]))
        b.append(hand(-152, 138, 1.0, 1, c["skin"], c["skinS"]))
        b.append(hand(152, 138, 1.0, -1, c["skin"], c["skinS"]))
    # raised collar behind head
    b.append(shaded("M-104 -300 L-122 -366 L-56 -330 L-40 -318 Z", c["coat"], [("M-160 -390 L-110 -390 L-110 -300 L-160 -300 Z", c["coatL"], 0.6)]))
    b.append(shaded("M104 -300 L122 -366 L56 -330 L40 -318 Z", c["coatS"]))
    b.append(man_head(expr, look))
    return "".join(b)


# ------------------------------------------------------------------ Katya
KAT = dict(coat="#c0392f", coatS="#922620", coatL="#d65a47", skin="#f3d0b0", skinS="#e0ad8a", hair="#5a3420", hairS="#3f2214",
           beret="#2d3757", beretS="#1f2740", scarf="#efe4c4", scarfS="#d4c59c", stripe="#2d3757", tights="#36384a", shoe="#2a1f1a",
           bag="#7a4f2c", bagS="#5c3a1f")

def katya_head(expr="calm"):
    c = KAT
    b = []
    # back hair (bob)
    b.append(shaded("M-104 -470 C-112 -390 -100 -350 -86 -330 C-60 -318 60 -318 86 -330 C100 -350 112 -390 104 -470 Z",
                    c["hair"], [("M20 -480 L130 -480 L130 -300 L20 -300 Z", c["hairS"])],
                    lines=[("M-80 -400 Q-84 -360 -76 -336 M70 -400 Q78 -360 72 -334", 3)]))
    b.append(shaded("M-26 -360 L-28 -300 L28 -300 L26 -360 Z", c["skin"], [("M-30 -370 L30 -370 L30 -335 L-30 -335 Z", c["skinS"])]))
    face = "M-80 -500 C-86 -440 -78 -400 -60 -376 C-42 -352 -20 -342 0 -342 C20 -342 42 -352 60 -376 C78 -400 86 -440 80 -500 Z"
    b.append(shaded(face, c["skin"], [("M40 -520 C80 -470 76 -400 40 -350 L120 -350 L120 -520 Z", c["skinS"])]))
    # eyes
    for ex in (-32, 32):
        if expr == "scared":
            b.append(ell(ex, -446, 17, 20, "#fbf7ef", sw=4)); b.append(circle(ex, -446, 5, O, sw=0))
        else:
            b.append(ell(ex, -446, 15, 18, "#fbf7ef", sw=4))
            b.append(circle(ex + 1, -443, 10, "#5b3b22", sw=0)); b.append(circle(ex + 1, -443, 5.5, O, sw=0))
            b.append(circle(ex + 5, -448, 3, "#fff", sw=0))
        b.append(path(f"M{ex-17} -458 Q{ex} -470 {ex+17} -458", sw=6))  # upper lid
        b.append(path(f"M{ex + (17 if ex > 0 else -17)} -458 l{6 if ex > 0 else -6} -5", sw=3))  # lash
    # brows
    if expr == "calm":
        b.append(path("M-50 -484 Q-32 -492 -14 -486", sw=5)); b.append(path("M14 -486 Q32 -492 50 -484", sw=5))
    else:
        b.append(path("M-50 -478 Q-32 -484 -14 -496", sw=5)); b.append(path("M14 -496 Q32 -484 50 -478", sw=5))
    # nose, freckles, cheeks
    b.append(path("M2 -436 C4 -420 8 -412 2 -406", sw=3.5))
    for fx, fy in ((-46, -416), (-38, -410), (-52, -406), (46, -416), (38, -410), (52, -406)):
        b.append(circle(fx, fy, 2.4, "#c98a66", sw=0))
    b.append(ell(-50, -400, 15, 8, "#ef9f95", sw=0, extra='opacity="0.45"'))
    b.append(ell(50, -400, 15, 8, "#ef9f95", sw=0, extra='opacity="0.45"'))
    # mouth
    if expr == "calm":
        b.append(path("M-14 -380 Q0 -374 14 -380", sw=4))
    elif expr == "worried":
        b.append(path("M-14 -376 Q0 -384 14 -376", sw=4))
    else:
        b.append(shaded("M-12 -390 Q0 -394 12 -390 Q14 -370 0 -366 Q-14 -370 -12 -390 Z", "#7a2c25"))
    # bangs with strands
    b.append(shaded("M-92 -470 C-96 -540 -40 -560 0 -556 C50 -556 98 -536 94 -466 C80 -480 60 -492 40 -490 C30 -476 10 -472 -4 -486 C-20 -470 -50 -470 -60 -486 C-72 -478 -84 -474 -92 -470 Z",
                    c["hair"], [("M40 -570 L110 -570 L110 -460 L40 -460 Z", c["hairS"])],
                    lines=[("M-50 -540 Q-56 -510 -60 -486 M0 -550 Q-2 -515 -4 -486 M44 -542 Q44 -515 40 -490", 3)]))
    # beret tilted
    b.append(shaded("M-108 -516 C-116 -572 -40 -600 24 -596 C90 -592 124 -566 114 -528 C70 -542 -56 -544 -108 -516 Z",
                    c["beret"], [("M40 -620 L150 -620 L150 -520 L40 -520 Z", c["beretS"])]))
    b.append(path("M-4 -606 l6 -18", sw=7))
    return "".join(b)


def katya(expr="calm", hands="lap"):
    c = KAT
    b = []
    for sx in (-46, 46):
        b.append(shaded(f"M{sx-26} 40 L{sx-28} 220 L{sx+28} 220 L{sx+26} 40 Z", c["tights"], [(f"M{sx+6} 20 L{sx+50} 20 L{sx+50} 230 L{sx+6} 230 Z", "#272938")]))
        b.append(shaded(f"M{sx-34} 214 C{sx-38} 246 {sx+48} 250 {sx+44} 222 L{sx+30} 208 Z", c["shoe"]))
    coat = ("M-112 -300 C-124 -220 -122 -120 -110 -30 L-114 40 C-114 72 -92 88 -58 88 C-32 88 -12 80 0 70 "
            "C12 80 32 88 58 88 C92 88 114 72 114 40 L110 -30 C122 -120 124 -220 112 -300 Z")
    b.append(shaded(coat, c["coat"], [("M16 -320 L200 -320 L200 120 L16 120 Z", c["coatS"])],
                    lines=[("M0 -260 L0 70", 4), ("M-108 -26 Q-50 -8 0 -22 Q50 -8 108 -26", 3), ("M-58 88 Q-60 58 -50 30 M58 88 Q60 58 50 30", 3)]))
    for by in (-220, -160, -100):
        b.append(circle(-18, by, 8, "#f0d27a", sw=4))
    # collar
    b.append(shaded("M-30 -312 L-104 -296 L-64 -236 L0 -270 Z", c["coatL"]))
    b.append(shaded("M30 -312 L104 -296 L64 -236 L0 -270 Z", c["coat"]))
    # scarf with stripes
    sc = "M-56 -320 Q0 -290 56 -320 L60 -296 Q0 -264 -60 -296 Z"
    b.append(shaded(sc, c["scarf"], [("M0 -330 L80 -330 L80 -250 L0 -250 Z", c["scarfS"])], lines=[("M-50 -306 Q0 -280 50 -306", 6)]))
    tail = "M20 -286 L52 -150 L14 -144 L-4 -280 Z"
    b.append(shaded(tail, c["scarf"], [("M30 -300 L70 -300 L70 -140 L30 -140 Z", c["scarfS"])],
                    lines=[(f"M{8} -230 L46 -236 M14 -200 L50 -206", 7), ("M18 -150 l0 14 M30 -150 l0 14 M42 -152 l0 14", 3)]))
    # arms
    la = "M-112 -296 C-146 -268 -154 -200 -150 -130 C-146 -74 -124 -34 -90 -10 L-66 -44 C-92 -64 -108 -100 -108 -150 C-108 -200 -102 -250 -88 -280 Z"
    b.append(shaded(la, c["coat"], [("M-124 -310 L-98 -310 L-98 0 L-124 0 Z", c["coatS"], 0.5)], lines=[("M-146 -140 Q-132 -128 -120 -112", 3)]))
    ra = "M112 -296 C146 -268 154 -200 150 -130 C146 -74 124 -34 90 -10 L66 -44 C92 -64 108 -100 108 -150 C108 -200 102 -250 88 -280 Z"
    b.append(shaded(ra, c["coatS"], lines=[("M146 -140 Q132 -128 120 -112", 3)]))
    if hands == "bag":
        bag = "M-104 -100 L104 -100 C114 -100 120 -90 120 -78 L116 26 C116 38 106 46 94 46 L-94 46 C-106 46 -116 38 -116 26 L-120 -78 C-120 -90 -114 -100 -104 -100 Z"
        b.append(path("M-70 -100 C-70 -180 70 -180 70 -100", sw=14))
        b.append(path("M-70 -100 C-70 -180 70 -180 70 -100", sw=7, stroke=c["bagS"]))
        b.append(shaded(bag, c["bag"], [("M40 -120 L150 -120 L150 50 L40 50 Z", c["bagS"])],
                        lines=[("M-130 -60 L130 -60", 4)]))
        b.append(shaded("M-26 -70 L26 -70 L26 -30 L-26 -30 Z", "#c8a560"))
        b.append(hand(-92, -66, 0.85, 1, c["skin"], c["skinS"], "grip"))
        b.append(hand(92, -66, 0.85, -1, c["skin"], c["skinS"], "grip"))
    else:
        b.append(hand(-74, -30, 0.85, 1, c["skin"], c["skinS"]))
        b.append(hand(74, -30, 0.85, -1, c["skin"], c["skinS"]))
    b.append(katya_head(expr))
    return "".join(b)


if __name__ == "__main__":
    import subprocess
    W, H = 1600, 1100
    body = (f'<rect width="{W}" height="{H}" fill="#6f8c7b"/>'
            f'<g transform="translate(230,760) scale(0.95)">{man("smile")}</g>'
            f'<g transform="translate(620,760) scale(0.95)">{man("grin")}</g>'
            f'<g transform="translate(1000,760) scale(0.95)">{katya("worried","bag")}</g>'
            f'<g transform="translate(1370,760) scale(0.95)">{katya("scared")}</g>'
            f'<g transform="translate(230,560) scale(0.6)">{man("stare","stand")}</g>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{body}</svg>'
    open("/tmp/chars.svg", "w").write(svg)
    subprocess.run(["rsvg-convert", "/tmp/chars.svg", "-o", "/home/claude/v2/chars_test.png"], check=True)
