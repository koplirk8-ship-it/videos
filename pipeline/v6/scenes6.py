"""Scenes for 'POV: попросил соседа-монстра разбудить в 7 утра'."""
import math

def make(ns):
    """Inject scene functions into anim namespace ns (needs W,H,G,P,artyom,dima,gena,blink_of,s3,c4,shaded,path,circle,O)."""
    W, H, G, P, s3, c4 = ns["W"], ns["H"], ns["G"], ns["P"], ns["s3"], ns["c4"]
    shaded, path, circle, O = ns["shaded"], ns["path"], ns["circle"], ns["O"]
    artyom, dima, blink_of = ns["artyom"], ns["dima"], ns["blink_of"]

    def clock(x, y, s=1.0, hh=7, mm=0, digital=False):
        g = [f'<g transform="translate({x},{y}) scale({s})">']
        if digital:
            g.append(s3.R(-110, -60, 220, 120, "#1b1d22", rx=18, sw=6))
            g.append(f'<text x="0" y="26" font-family="DejaVu Sans Mono" font-weight="bold" font-size="74" fill="#ff3b30" text-anchor="middle">{hh:02d}:{mm:02d}</text>')
            g.append(f'<ellipse cx="0" cy="0" rx="170" ry="110" fill="#ff3b30" opacity="0.10"/>')
        else:
            for sx in (-1, 1):
                g.append(f'<circle cx="{sx*62}" cy="-78" r="34" fill="#c9c4b4" stroke="{O}" stroke-width="5"/>')
            g.append(path("M-50 80 l-20 30 M50 80 l20 30", sw=8))
            g.append(shaded("M-88 0 A88 88 0 1 1 88 0 A88 88 0 1 1 -88 0 Z", "#c7362b", [("M20 -100 L110 -100 L110 100 L20 100 Z", "#a52a21")]))
            g.append(f'<circle r="66" fill="#f4efe3" stroke="{O}" stroke-width="5"/>')
            for k in range(12):
                a = k * math.pi / 6
                g.append(path(f"M{58*math.sin(a):.1f} {-58*math.cos(a):.1f} L{50*math.sin(a):.1f} {-50*math.cos(a):.1f}", sw=4))
            ah = (hh % 12 + mm / 60) * math.pi / 6; am = mm * math.pi / 30
            g.append(path(f"M0 0 L{32*math.sin(ah):.1f} {-32*math.cos(ah):.1f}", sw=7))
            g.append(path(f"M0 0 L{48*math.sin(am):.1f} {-48*math.cos(am):.1f}", sw=5))
            g.append(circle(0, 0, 6, "#2a2420", sw=0))
        g.append("</g>")
        return "".join(g)

    def bedroom_bg(tt, night=False):
        b = [f'<rect width="{W}" height="{H}" fill="{"#1a2029" if night else "#56606b"}"/>']
        # ceiling band + cornice
        b.append(f'<rect width="{W}" height="120" fill="{"#141920" if night else "#6b7580"}"/>')
        b.append(f'<line x1="0" y1="120" x2="{W}" y2="120" stroke="{O}" stroke-width="6"/>')
        # window with morning light / night
        b.append(s3.R(700, 300, 300, 420, "#0e141d" if night else "#f3d9a4", rx=8))
        if not night:
            b.append(f'<rect x="700" y="300" width="300" height="420" fill="#ffe9b8" opacity="0.6"/>')
            b.append(f'<polygon points="700,720 1000,720 760,1500 260,1500" fill="#ffe9b8" opacity="0.10"/>')
        else:
            b.append(circle(910, 400, 30, "#d9dccd", sw=0))
        b.append(s3.R(700, 300, 300, 420, "none", rx=8, sw=16, stroke="#5b6870"))
        b.append(f'<line x1="850" y1="300" x2="850" y2="720" stroke="#5b6870" stroke-width="12"/>')
        # nightstand
        b.append(s3.R(820, 1180, 230, 520, "#4a3c32", rx=8))
        b.append(s3.R(840, 1260, 190, 12, "#3b3029", rx=4, sw=3))
        b.append(f'<rect y="1700" width="{W}" height="220" fill="#2a2321"/>')
        b.append(f'<line x1="0" y1="1700" x2="{W}" y2="1700" stroke="{O}" stroke-width="6"/>')
        # bed headboard + mattress
        b.append(s3.R(40, 860, 760, 260, "#5a4636", rx=20))
        b.append(s3.R(30, 1080, 780, 620, "#d9d4c8", rx=30))
        return "".join(b)

    def blanket(night=False):
        return shaded("M20 1150 C200 1120 640 1120 820 1150 L830 1700 L10 1700 Z", "#55708a",
                      [("M500 1100 L860 1100 L860 1710 L500 1710 Z", "#46607a")],
                      lines=[("M120 1300 Q300 1270 480 1310 M200 1480 Q420 1440 700 1490", 4)])

    def hanging_gena(tt, x, y0, s, eyes_glow=False):
        p = P("gena", tt, "grin", "grin")
        sway = 4 * math.sin(tt * 0.7)
        inner = c4.gena("grin", "down", p["mouth"] if p["talking"] else 0.0, p["blink"], p["breath"], lean=0)
        g = f'<g transform="translate({x},{y0}) rotate({180+sway:.2f}) scale({s})">{inner}</g>'
        # fingers/toes gripping the ceiling
        g += path(f"M{x-40} 120 q-10 -14 -2 -24 M{x+40} 120 q10 -14 2 -24 M{x-20} 120 l-4 -18 M{x+20} 120 l4 -18", sw=6, stroke="#5c645e")
        return g

    def scene(name, tt):
        if name == "ceiling":
            pa = P("artyom", tt, "shout", "scared")
            b = [bedroom_bg(tt)]
            b.append(clock(935, 1120, 0.75, 7, 0))
            b.append(f'<ellipse cx="330" cy="1130" rx="190" ry="70" fill="#eeeae0" stroke="{O}" stroke-width="6"/>')
            b.append(G(c4.guy_head("artyom", pa["expr"], pa["mouth"], pa["blink"], look=1), 330 + pa["shake"][0], 1080 + 3 * pa["breath"], 1.1))
            b.append(blanket())
            b.append(hanging_gena(tt, 660, 110, 0.6))
            return "".join(b)
        if name == "kitchen":
            return (s3.kitchen_bg() + artyom(tt, "head", 330, 1880, 1.02, "panic", "panic", look=1) +
                    dima(tt, "mug", 820, 1880, 1.02, look=-1))
        if name == "dima_close":
            return s3.kitchen_bg() + f'<rect width="{W}" height="{H}" fill="#000" opacity="0.15"/>' + dima(tt, "mug", 540, 2600, 2.05, look=0)
        if name == "gift":
            pg = P("gena", tt, "grin", "grin")
            b = [s3.hall_bg()]
            inner = c4.gena("grin", "clock", pg["mouth"] if pg["talking"] else 0.0, pg["blink"], pg["breath"], lean=0.12 * math.sin(tt * 0.9))
            inner += c4._bony_hand(-120, -950, 0.8, -1, "grip") + c4._bony_hand(120, -950, 0.8, 1, "grip")
            inner += clock(0, -950, 1.2, 3, 0)
            b.append(G(inner, 540, 1730, 0.95))
            b.append(artyom(tt, "head", 180, 1880, 1.0, "shout", "panic", look=1))
            b.append(dima(tt, "mug", 900, 1880, 1.0, look=-1))
            return "".join(b)
        if name == "night3":
            b = [bedroom_bg(tt, night=True)]
            b.append(f'<ellipse cx="330" cy="1130" rx="190" ry="70" fill="#eeeae0" stroke="{O}" stroke-width="6"/>')
            b.append(G(c4.guy_head("artyom", "deadpan", 0, 1.0, look=0), 330, 1080, 1.1))  # asleep
            b.append(blanket())
            b.append(hanging_gena(tt, 660, 110, 0.6))
            b.append(f'<rect width="{W}" height="{H}" fill="#03050a" opacity="0.55"/>')
            b.append(clock(935, 1110, 0.9, 3, 0, digital=True))
            if blink_of("gena", tt) < 0.5:   # glowing eyes (upside-down head ~ y 760)
                sway = 4 * math.sin(tt * 0.7)
                b.append(f'<g transform="translate(660,110) rotate({180+sway:.2f}) scale(0.6)">'
                         + circle(-38, -1418, 15, "#f2e7b0", sw=0) + circle(38, -1418, 15, "#f2e7b0", sw=0)
                         + '<circle cx="0" cy="-1418" r="150" fill="#f2e7b0" opacity="0.08"/></g>')
            return "".join(b)
        raise ValueError(name)
    return scene
