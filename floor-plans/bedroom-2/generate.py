#!/usr/bin/env python3
"""Draw Bedroom 2 furniture layouts in the style of the builder's floor plan.

All geometry is in inches. The origin is the NW interior corner of Bedroom 2's
main rectangle; +x runs east (toward the study) and +y runs south (toward the
street). Wall positions were scaled off the builder's marketing plan and
calibrated so the main room is exactly its labeled 13'-4" x 16'-4".

    python3 generate.py     # writes the .svg sheets next to this script
    node render.cjs         # rasterizes every .svg here to .png
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent

FONT = "'Liberation Serif','Times New Roman',Times,serif"
LW = 1.1       # wall line weight
FIX = 0.55     # fixtures and furniture
THIN = 0.35    # door swings and dimension lines
VENEER = 5.5   # brick veneer outside the stud wall's outer line
PX_PER_IN = 4.5

# ---------------------------------------------------------------- architecture
# Room interiors. Context rooms run past the crop so their walls read as cut.
BEDROOM = [(0, 0), (117.65, 0), (117.65, -68.1), (160, -68.1), (160, 196),
           (122.25, 196), (122.25, 223), (37.75, 223), (37.75, 196), (0, 196)]
BATH2 = [(0, -68.1), (111.65, -68.1), (111.65, -6), (0, -6)]
WIC = [(40.1, -132.8), (111.65, -132.8), (111.65, -74.1), (40.1, -74.1)]
HALL = [(117.65, -400), (160, -400), (160, -74.1), (117.65, -74.1)]
STUDY = [(166, -70), (400, -70), (400, 91.3), (166, 91.3)]
STAIR = [(166, -400), (400, -400), (400, -76.1), (166, -76.1)]
MASTER = [(-400, -400), (111.65, -400), (111.65, -138.8), (34.1, -138.8),
          (34.1, -74.1), (-6, -74.1), (-6, -26.1), (-400, -26.1)]
ROOMS = [BEDROOM, BATH2, WIC, HALL, STUDY, STAIR, MASTER]

# Exterior face of the brick around this corner of the house.
OUTLINE = [(-400, -400), (400, -400), (400, 101.3), (171.5, 101.3),
           (171.5, 207.5), (133.75, 207.5), (133.75, 234.5), (26.25, 234.5),
           (26.25, 207.5), (-11.5, 207.5), (-11.5, -14.6), (-400, -14.6)]

NOOK = (37.75, 122.25, 196.0, 223.0)   # 84.5" wide x 27" deep

# Door openings: (axis of the wall, wall span, opening span).
OPENINGS = [
    ("h", (-74.1, -68.1), (123.7, 154.0)),    # bedroom door off the hall
    ("v", (111.65, 117.65), (-62.6, -35.6)),  # Bath 2 door
    ("h", (-74.1, -68.1), (61.6, 91.1)),      # WIC door
]
# Windows: (axis, inner face, outward sign, span, twin unit?)
WINDOWS = [
    ("v", 0.0, -1, (9.5, 43.5), False),       # west wall, north window
    ("v", 0.0, -1, (152.5, 186.5), False),    # west wall, south window
    ("h", 223.0, 1, (48.25, 111.75), True),   # nook, twin window
]
# Doors: (hinge, closed tip, open tip, sweep flag). Leaves drawn 45 deg open.
DOORS = [
    ((154.0, -68.1), (123.7, -68.1), (132.57, -46.67), 0),
    ((111.65, -62.6), (111.65, -35.6), (92.56, -43.51), 1),
    ((91.1, -74.1), (61.6, -74.1), (70.24, -94.96), 1),
]

CROP = (-40, -152, 215, 252)   # x0, y0, x1, y1 of the plan view

# ------------------------------------------------------------------- furniture
BED_LEN, BED_W = 86, 80        # king frame incl. headboard (76x80 mattress)
NS_W, NS_D = 22, 16            # nightstands
TV_LEN, TV_D = 84, 18          # TV console
SOFA_W, SOFA_D = 86, 38        # sofa (depth assumed)

OPTIONS = {
    "a": dict(
        file="option-a-sofa-at-nook",
        title="Option A",
        subtitle="SOFA CENTERED ON THE FRONT NOOK",
        bed_y=48, sofa=(37, 158, "south"),
        label_y=80, dims=[("v", 64, 128, 158, "2'-6\""),
                          ("h", 112, 86, 142, "4'-8\"")],
        notes=[
            "NOOK IS ABOUT 7'-0½\" WIDE x 2'-3\" DEEP (84½\" x 27\"), "
            "SCALED FROM THE BUILDER PLAN.",
            "AN 86\" SOFA IS ~1½\" WIDER THAN THE NOOK, SO IT CAN'T SLIDE "
            "IN. IT SITS ACROSS THE OPENING AND",
            "STICKS 3'-2\" INTO THE ROOM. A SOFA 82\" OR NARROWER FITS "
            "INSIDE (AND STILL STICKS OUT ~11\").",
        ],
    ),
    "b": dict(
        file="option-b-sofa-on-bath-wall",
        title="Option B",
        subtitle="SOFA ON THE BATH 2 WALL BY THE ENTRY",
        bed_y=68, sofa=(24, 0, "north"),
        label_y=100, dims=[("v", 64, 38, 68, "2'-6\""),
                           ("h", 132, 86, 142, "4'-8\""),
                           ("v", 64, 148, 196, "4'-0\"")],
        notes=[
            "SOFA SITS ON THE 9'-10\" BATH 2 WALL WITH A 2'-6\" WALKWAY TO THE "
            "BED AND 4'-8\" BETWEEN THE BED AND TV.",
            "THE WINDOW NOOK (7'-0½\" x 2'-3\") STAYS OPEN FOR A READING "
            "CHAIR OR A SMALL DESK.",
        ],
    ),
}
SIZES_NOTE = ("SIZES: KING BED 80\" x 86\" (76\" x 80\" MATTRESS) · "
              "NIGHTSTANDS 22\" x 16\" · TV CONSOLE 84\" x 18\" · "
              "SOFA 86\" x 38\" DEEP (ASSUMED)")


# ------------------------------------------------------------------- svg bits
def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def pts(poly):
    return " ".join(f"{f(x)},{f(y)}" for x, y in poly)


def rect(x, y, w, h, fill="#fff", stroke="#000", sw=FIX, rx=0, extra=""):
    r = f' rx="{f(rx)}"' if rx else ""
    return (f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{r} '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{f(sw)}"{extra}/>')


def box(x0, y0, x1, y1, fill):
    return f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="{fill}"/>'


def line(x1, y1, x2, y2, sw=FIX, stroke="#000", extra=""):
    return (f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" '
            f'stroke="{stroke}" stroke-width="{f(sw)}"{extra}/>')


def ellipse(cx, cy, rx, ry, sw=FIX, fill="#fff"):
    return (f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" '
            f'fill="{fill}" stroke="#000" stroke-width="{f(sw)}"/>')


def text(x, y, s, size, weight="normal", anchor="middle", fill="#000",
         rotate=0, halo=False, underline=False, spacing=0):
    s = s.replace("&", "&amp;").replace("<", "&lt;")
    attrs = [f'x="{f(x)}"', f'y="{f(y)}"', f'font-size="{f(size)}"',
             f'font-family="{FONT}"', f'text-anchor="{anchor}"',
             f'fill="{fill}"']
    if weight != "normal":
        attrs.append(f'font-weight="{weight}"')
    if spacing:
        attrs.append(f'letter-spacing="{f(spacing)}"')
    if rotate:
        attrs.append(f'transform="rotate({rotate} {f(x)} {f(y)})"')
    if underline:
        attrs.append('text-decoration="underline"')
    if halo:
        attrs.append(f'stroke="#fff" stroke-width="{f(size * 0.32)}" '
                     'stroke-linejoin="round" paint-order="stroke"')
    return f'<text {" ".join(attrs)}>{s}</text>'


def inside(poly, x, y):
    hit = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def shrink(poly, d):
    """Offset an orthogonal polygon inward by d (miter corners)."""
    edges = []
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if x1 == x2:   # vertical edge -> moves in x
            step = 0.01 if inside(poly, mx + 0.01, my) else -0.01
            edges.append(("v", x1 + (d if step > 0 else -d)))
        else:
            step = 0.01 if inside(poly, mx, my + 0.01) else -0.01
            edges.append(("h", y1 + (d if step > 0 else -d)))
    out = []
    for i, (kind, val) in enumerate(edges):
        pkind, pval = edges[i - 1]
        out.append((val, pval) if kind == "v" else (pval, val))
    return out


# ------------------------------------------------------------- architecture
def walls():
    g = [f'<polygon points="{pts(OUTLINE)}" fill="#000"/>',
         f'<polygon points="{pts(shrink(OUTLINE, LW))}" fill="#fff"/>',
         f'<polygon points="{pts(shrink(OUTLINE, VENEER))}" fill="#000"/>',
         f'<polygon points="{pts(shrink(OUTLINE, VENEER + LW))}" fill="#fff"/>']
    # Each room's face line sits just outside its interior; white between
    # neighbouring rooms' lines is the wall core, so junctions clean up.
    for room in ROOMS:
        g.append(f'<polygon points="{pts(room)}" fill="#fff" stroke="#000" '
                 f'stroke-width="{f(2 * LW)}" stroke-linejoin="miter" '
                 'paint-order="stroke"/>')
    for axis, (w0, w1), (o0, o1) in OPENINGS:
        if axis == "h":
            g.append(box(o0, w0 - 0.05, o1, w1 + 0.05, "#fff"))
            g.append(box(o0 - LW, w0, o0, w1, "#000"))
            g.append(box(o1, w0, o1 + LW, w1, "#000"))
        else:
            g.append(box(w0 - 0.05, o0, w1 + 0.05, o1, "#fff"))
            g.append(box(w0, o0 - LW, w1, o0, "#000"))
            g.append(box(w0, o1, w1, o1 + LW, "#000"))
    for axis, face, sign, (s0, s1), twin in WINDOWS:
        # glass band between the face line and the stud wall's outer line
        a, b = sorted((face + sign * LW, face + sign * (6 - LW)))
        va, vb = sorted((face + sign * 6, face + sign * (11.5 - LW)))
        mid = (a + b) / 2
        marks = [s0 + 1.8, s1 - 1.8] + ([(s0 + s1) / 2 - 1.5, (s0 + s1) / 2 + 1.5] if twin else [])
        if axis == "v":
            g.append(box(a, s0, b, s1, "#000"))
            for s in (s0, s1):
                g.append(box(va, s - 1.3, vb, s + 1.3, "#000"))
            for m in marks:
                g.append(box(mid - 0.65, m - 0.65, mid + 0.65, m + 0.65, "#fff"))
        else:
            g.append(box(s0, a, s1, b, "#000"))
            for s in (s0, s1):
                g.append(box(s - 1.3, va, s + 1.3, vb, "#000"))
            for m in marks:
                g.append(box(m - 0.65, mid - 0.65, m + 0.65, mid + 0.65, "#fff"))
    return g


def doors():
    g = []
    for (hx, hy), (cx, cy), (tx, ty), sweep in DOORS:
        r = ((cx - hx) ** 2 + (cy - hy) ** 2) ** 0.5
        g.append(f'<path d="M{f(cx)},{f(cy)} A{f(r)},{f(r)} 0 0 {sweep} {f(tx)},{f(ty)}" '
                 f'fill="none" stroke="#000" stroke-width="{f(THIN)}"/>')
        g.append(line(hx, hy, tx, ty, sw=1.5))
    return g


def fixtures():
    g = []
    # tub
    g.append(rect(0, -68.1, 32, 62.1, fill="none"))
    g.append('<path d="M6,-65.5 H26 A3,3 0 0 1 29,-62.5 V-18.5 A9,9 0 0 1 20,-9.5 '
             'H12 A9,9 0 0 1 3,-18.5 V-62.5 A3,3 0 0 1 6,-65.5 Z" fill="#fff" '
             f'stroke="#000" stroke-width="{f(FIX)}"/>')
    g.append('<circle cx="16" cy="-13" r="1.2" fill="#000"/>')
    # toilet
    g.append(ellipse(54, -26, 7, 10.5))
    g.append(ellipse(54, -26.8, 4.8, 7.6, sw=THIN))
    g.append(rect(43.3, -15.5, 21.5, 9.5, rx=1))
    # vanity + sink
    g.append(rect(72, -27.6, 39.65, 21.6))
    g.append(ellipse(92, -17.4, 9, 7.2))
    g.append(ellipse(92, -17.4, 7, 5.4, sw=THIN))
    g.append('<circle cx="92" cy="-17.4" r="0.9" fill="#000"/>')
    g.append(rect(90.6, -11.4, 2.8, 3, sw=THIN))
    # WIC shelf + rod
    g.append(f'<polyline points="53.1,-74.1 53.1,-119.8 98.65,-119.8 98.65,-74.1" '
             f'fill="none" stroke="#000" stroke-width="{f(FIX)}"/>')
    g.append(f'<polyline points="51.1,-74.1 51.1,-121.8 100.65,-121.8 100.65,-74.1" '
             f'fill="none" stroke="#000" stroke-width="{f(THIN)}" '
             'stroke-dasharray="1.3 1.1"/>')
    # front porch slab edge + pilaster
    g.append(line(171.5, 198, 400, 198))
    g.append(rect(171.5, 172.3, 11.1, 25.7))
    return g


# --------------------------------------------------------------- furniture
def bed(x0, y0):
    g = [rect(x0, y0, BED_LEN, BED_W),
         rect(x0, y0, 4, BED_W, fill="#d9d9d9"),
         rect(x0 + 5, y0 + 2, 80, 76, rx=2.5)]
    for py in (y0 + 4, y0 + 41.5):
        g.append(rect(x0 + 8, py, 16, 34.5, rx=4))
    tx = x0 + 31
    g.append(line(tx, y0 + 2, tx, y0 + 78))
    g.append(line(tx + 5, y0 + 2, tx + 5, y0 + 56, sw=THIN))
    g.append(f'<path d="M{f(tx + 5)},{f(y0 + 56)} L{f(tx + 27)},{f(y0 + 78)}" '
             f'fill="none" stroke="#000" stroke-width="{f(THIN)}"/>')
    g.append(text(x0 + 60, y0 + BED_W / 2 + 1.8, "KING BED", 5, "bold"))
    g.append(text(x0 + 60, y0 + BED_W / 2 + 8, "76\" x 80\"", 3.8))
    return g


def nightstand(x0, y0):
    cx, cy = x0 + NS_D / 2, y0 + NS_W / 2
    return [rect(x0, y0, NS_D, NS_W),
            f'<circle cx="{f(cx)}" cy="{f(cy)}" r="5.4" fill="#fff" stroke="#000" stroke-width="{f(THIN)}"/>',
            f'<circle cx="{f(cx)}" cy="{f(cy)}" r="1.2" fill="#000"/>']


def tv_console(y0):
    x0 = 160 - TV_D
    yc = y0 + TV_LEN / 2
    return [rect(x0, y0, TV_D, TV_LEN),
            rect(x0 + 11.5, yc - 33, 2.8, 66, fill="#222", sw=THIN),
            text(x0 + 7.2, yc, "84\" TV CONSOLE", 4.1, "bold", rotate=-90)]


def sofa(x0, y0, back):
    w, d, arm, bk = SOFA_W, SOFA_D, 7, 9
    g = [rect(x0, y0, w, d, rx=2.5)]
    by = y0 + d - bk if back == "south" else y0
    g.append(rect(x0 + arm, by, w - 2 * arm, bk, rx=1.5))
    g.append(rect(x0, y0, arm, d, rx=2.5))
    g.append(rect(x0 + w - arm, y0, arm, d, rx=2.5))
    cw = (w - 2 * arm) / 3
    cy0, cy1 = (y0 + 1, by) if back == "south" else (by + bk, y0 + d - 1)
    for i in range(3):
        g.append(rect(x0 + arm + i * cw + 0.4, cy0, cw - 0.8, cy1 - cy0, rx=2))
    mid = (cy0 + cy1) / 2
    g.append(text(x0 + w / 2, mid - 0.8, "86\"", 4.6, "bold"))
    g.append(text(x0 + w / 2, mid + 4.6, "SOFA", 4.6, "bold"))
    return g


# -------------------------------------------------------------- annotation
def dim(kind, at, a, b, label):
    g, t = [], 1.7
    style = dict(sw=THIN, stroke="#222")
    if kind == "v":
        g.append(line(at, a, at, b, **style))
        for y in (a, b):
            g.append(line(at - t, y + t, at + t, y - t, sw=0.6, stroke="#222"))
            g.append(line(at - 3, y, at + 3, y, **style))
        g.append(text(at - 1.6, (a + b) / 2, label, 4.4, rotate=-90, halo=True,
                      fill="#222"))
    else:
        g.append(line(a, at, b, at, **style))
        for x in (a, b):
            g.append(line(x - t, at + t, x + t, at - t, sw=0.6, stroke="#222"))
            g.append(line(x, at - 3, x, at + 3, **style))
        g.append(text((a + b) / 2, at - 1.6, label, 4.4, halo=True, fill="#222"))
    return g


def labels(opt):
    gray = "#7a7a7a"
    ly = opt["label_y"]
    return [
        text(114, ly, "BEDROOM 2", 6.6, "bold", underline=True),
        text(114, ly + 7.4, "13'-4\" x 16'-4\"", 4.6),
        text(80, 208.6, "NOOK", 4.8, "bold", underline=True),
        text(80, 215.6, "7'-0½\" x 2'-3\"", 4.3),
        text(62, -44.5, "BATH 2", 5.4, "bold", underline=True),
        text(76, -108.5, "WIC", 5.4, "bold", underline=True),
        text(138.8, -22, "ENTRY", 4.2, fill="#444", spacing=0.4),
        text(138.8, -122, "HALL", 4.4, fill=gray, spacing=0.4),
        text(190.5, 2, "STUDY", 4.4, fill=gray, spacing=0.4),
        text(193.5, 150, "COV. PORCH", 4.4, fill=gray, spacing=0.2),
        text(14, -104, "MST. BATH", 4.2, fill=gray, spacing=0.2),
        text(80, 246.5, "FRONT OF HOUSE  ↓  STREET", 4.2, fill=gray,
             spacing=0.5),
    ]


def plan(opt):
    """Plan-view group in room coordinates, clipped to CROP."""
    x0, y0, x1, y1 = CROP
    by = opt["bed_y"]
    sx, sy, back = opt["sofa"]
    g = walls() + fixtures() + doors()
    g += bed(0, by)
    g += nightstand(0, by - NS_W) + nightstand(0, by + BED_W)
    g += tv_console(by + BED_W / 2 - TV_LEN / 2)
    g += sofa(sx, sy, back)
    for d in opt["dims"]:
        g += dim(*d)
    g += labels(opt)
    clip = f"clip-{opt['file']}"
    return (f'<clipPath id="{clip}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" '
            f'height="{y1 - y0}"/></clipPath>'
            f'<g clip-path="url(#{clip})">' + "".join(g) + "</g>"
            + rect(x0, y0, x1 - x0, y1 - y0, fill="none", stroke="#b5b5b5", sw=0.5))


def scale_bar(x, y):
    g = []
    for i, (a, b) in enumerate([(0, 24), (24, 48), (48, 96)]):
        g.append(rect(x + a, y, b - a, 2.6, fill="#000" if i % 2 == 0 else "#fff",
                      sw=0.4))
    for v, lab in [(0, "0"), (24, "2'"), (48, "4'"), (96, "8'")]:
        g.append(text(x + v, y + 8, lab, 3.8))
    g.append(text(x - 4, y + 2.6, "SCALE", 3.8, "bold", anchor="end"))
    return g


def sheet(opt):
    x0, y0, x1, y1 = CROP
    page = (x0 - 10, y0 - 50, x1 + 10, y1 + 66)
    w, h = page[2] - page[0], page[3] - page[1]
    g = [rect(page[0], page[1], w, h, fill="#fff", stroke="none", sw=0)]
    g.append(text(x0, y0 - 25, f"Bedroom 2 — {opt['title']}", 13,
                  anchor="start"))
    g.append(text(x0, y0 - 11, opt["subtitle"], 5.6, "bold", anchor="start",
                  spacing=0.6))
    g.append(text(x1, y0 - 11, "KING BED · 84\" TV CONSOLE · 86\" SOFA",
                  4.4, anchor="end", fill="#555", spacing=0.3))
    g.append(plan(opt))
    ny = y1 + 13
    g.append(text(x0, ny, "NOTES", 4.6, "bold", anchor="start", spacing=0.6))
    for i, note in enumerate(opt["notes"] + [SIZES_NOTE]):
        g.append(text(x0, ny + 7.5 + i * 6.6, note, 4.1, anchor="start"))
    g += scale_bar(x1 - 100, y1 + 50)
    return svg_doc(page, "".join(g))


def side_by_side():
    x0, y0, x1, y1 = CROP
    cw = x1 - x0
    gap = 24
    page = (x0 - 10, y0 - 46, x0 + 2 * cw + gap + 10, y1 + 30)
    w, h = page[2] - page[0], page[3] - page[1]
    g = [rect(page[0], page[1], w, h, fill="#fff", stroke="none", sw=0)]
    g.append(text(x0, y0 - 26, "Bedroom 2 — Furniture Options", 13,
                  anchor="start"))
    for i, key in enumerate("ab"):
        opt = OPTIONS[key]
        dx = i * (cw + gap)
        g.append(f'<g transform="translate({dx} 0)">')
        g.append(text(x0, y0 - 8, f"{opt['title'].upper()} — {opt['subtitle']}",
                      5.2, "bold", anchor="start", spacing=0.4))
        g.append(plan(opt))
        g.append("</g>")
    ny = y1 + 13
    g.append(text(x0, ny, "NOOK ≈ 7'-0½\" W x 2'-3\" D. AN 86\" SOFA IS "
                  "~1½\" TOO WIDE TO SLIDE INTO IT (82\" OR LESS FITS).",
                  4.4, anchor="start"))
    g.append(text(x0, ny + 7, SIZES_NOTE, 4.1, anchor="start"))
    g += scale_bar(page[2] - 110, y1 + 9)
    return svg_doc(page, "".join(g))


def svg_doc(page, body):
    x, y, x1, y1 = page
    w, h = x1 - x, y1 - y
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(x)} {f(y)} {f(w)} {f(h)}" '
            f'width="{round(w * PX_PER_IN)}" height="{round(h * PX_PER_IN)}">'
            f'{body}</svg>\n')


def main():
    for opt in OPTIONS.values():
        (OUT / f"{opt['file']}.svg").write_text(sheet(opt))
    (OUT / "options-side-by-side.svg").write_text(side_by_side())


if __name__ == "__main__":
    main()
