"""Style v4 ("elegant"): El Messiri captions with a soft shadow, no boxes. Words fade up into a
small line; the price lands big underneath (number in yellow, "ريال" in white) with an orange
bar drawn under it. Section names in the same type with a short orange bar.
Cuts, flashes and logo cards are the same as v2.
Also writes <OUT>.events.json (source-time sound-effect cues) for sfx_v2.py."""
import json, math, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONTS, SPEC = sys.argv[1:5]
PREVIEW = sys.argv[5] if len(sys.argv) > 5 else None
W, H, FPS = 1080, 1920, 30

spec = {}
exec(open(SPEC, encoding="utf-8").read(), spec)
CAPS, SECTIONS = spec["CAPS"], spec.get("SECTIONS", [])
KEY = spec.get("KEY_COLOR", (232, 28, 40))
Y_WORD, Y_PRICE = spec.get("Y_WORD", 1180), spec.get("Y_PRICE", 330)
SCENES = spec.get("SCENES", [])
WHITE, OLD = (255, 255, 255), (226, 30, 30)
GREEN = tuple(spec.get("PRICE_COLOR", (52, 235, 52)))
LOGOS = spec.get("LOGOS", [])  # (png path, t0, t1, center y, width)


def font(name, size, var=None):
    f = ImageFont.truetype(f"{FONTS}/{name}", size)
    if var:
        f.set_variation_by_name(var)
    return f


F_WORD = font("Tajawal-ExtraBold.ttf", 100)
F_PRICE = font("NotoSerif.ttf", 128, "Black")
F_NUM = font("NotoSerif.ttf", 230, "Black")
F_LABEL = font("Tajawal-ExtraBold.ttf", 78)


F_SMALL = font("ElMessiri.ttf", 88, "SemiBold")
F_BIG = font("ElMessiri.ttf", 150, "Bold")
F_SEC = font("ElMessiri.ttf", 92, "Bold")
YELLOW, ORANGE, INK = (255, 210, 63), tuple(spec.get("BOX_KEY", (242, 106, 33))), (17, 17, 17)


def box(text, f, bg, fg, pad=(30, 14, 30, 30), r=22):
    """Word on a rounded colour box with a soft drop shadow."""
    k = ("box", text, id(f), bg, fg)
    if k in _cache:
        return _cache[k]
    d = "rtl" if re.search(r"[\u0600-\u06ff]", text) else "ltr"
    bb = f.getbbox(text, direction=d)
    asc, desc = f.getmetrics()
    tw, th = bb[2] - bb[0], asc + desc
    bw, bh = tw + pad[0] + pad[2], int(th * 0.92) + pad[1] + pad[3] - 18
    S = 24
    out = Image.new("RGBA", (bw + 2 * S, bh + 2 * S), (0, 0, 0, 0))
    sh = Image.new("L", out.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((S, S + 8, S + bw, S + bh + 8), r, fill=110)
    out.putalpha(sh.filter(ImageFilter.GaussianBlur(10)))
    d2 = ImageDraw.Draw(out)
    d2.rounded_rectangle((S, S, S + bw, S + bh), r, fill=bg + (255,))
    d2.text((S + pad[0] - bb[0], S + pad[1] - 4), text, font=f, fill=fg, direction=d)
    _cache[k] = out
    return out


def ease(p):
    p = min(max(p, 0.0), 1.0)
    return 1 - (1 - p) ** 3


def back(p, s=2.2):
    p = min(max(p, 0.0), 1.0) - 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


_cache = {}


def sprite(text, f, color, key=None):
    """Text with thin dark outline and soft drop shadow, padded RGBA."""
    k = (text, id(f), color)
    if k in _cache:
        return _cache[k]
    d = "rtl" if re.search(r"[؀-ۿ]", text) else "ltr"
    bb = f.getbbox(text, direction=d, stroke_width=3)
    m = Image.new("L", (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4), 0)
    ImageDraw.Draw(m).text((2 - bb[0], 2 - bb[1]), text, font=f, fill=255, direction=d)
    edge = Image.new("L", m.size, 0)
    ImageDraw.Draw(edge).text((2 - bb[0], 2 - bb[1]), text, font=f, fill=255, direction=d, stroke_width=3)
    P = 40
    w, h = m.width + 2 * P, m.height + 2 * P
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("L", (w, h), 0); sh.paste(edge, (P + 2, P + 7))
    sh = sh.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.8))
    out.alpha_composite(Image.merge("RGBA", (Image.new("L", (w, h), 0),) * 3 + (sh,)))
    ol = Image.new("L", (w, h), 0); ol.paste(edge, (P, P))
    out.alpha_composite(Image.merge("RGBA", (Image.new("L", (w, h), 15),) * 3 + (ol.point(lambda v: int(v * 0.7)),)))
    fill = Image.new("RGBA", (w, h), color + (0,)); a = Image.new("L", (w, h), 0); a.paste(m, (P, P)); fill.putalpha(a)
    out.alpha_composite(fill)
    _cache[k] = out
    return out


def place(canvas, im, cx, cy, scale=1.0, alpha=1.0):
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    cx0, cy0 = max(0, -x), max(0, -y)
    canvas.alpha_composite(im.crop((cx0, cy0, im.width, im.height)), (x + cx0, y + cy0))


def sar(text):
    n = re.search(r"\d+(?:\.\d+)?", text).group()
    return f"{n}%" if "%" in text else f"{n} SAR"


def is_price(text):
    return bool(re.search(r"\d", text)) and ("ريال" in text or "%" in text)


# ---------------- build timeline ----------------
words, prices, events, chunks = [], [], [], []
MAXW = 900
for cap in CAPS:
    toks = [t for t in cap["toks"] if t[0] != "\n"]
    out = cap["out"]
    items = [dict(text=text, t=t, key=(c == "p" and is_price(text))) for text, t, c, s_, j in toks if c != "x"]
    KEYS = {text for text, t, c, s_, j in toks if c in ("o", "p")}
    for it in items:
        if it["key"]:
            num = re.search(r"\d+(?:\.\d+)?%?", it["text"]).group()
            rest = it["text"].replace(num, "").strip()
            it["num"] = sprite(num, F_BIG, YELLOW)
            it["unit"] = sprite(rest, F_SMALL if False else F_BIG, WHITE) if rest else None
            it["sp"] = it["num"]
        else:
            it["sp"] = sprite(it["text"], F_SMALL, YELLOW if it["text"] in KEYS else WHITE)
    # a chunk is one or two rows: up to three words per row; a price joins the current row
    # when it fits, otherwise sits on a second row under it, and always closes the chunk
    W_ = lambda row: sum(x["sp"].width - 40 for x in row)
    groups, rows = [], [[]]
    for it in items:
        row = rows[-1]
        if it["key"]:
            if row:
                rows.append([it])
            else:
                row.append(it)
            groups.append(rows); rows = [[]]
            continue
        if row and (len(row) == 3 or W_(row) + it["sp"].width - 40 > MAXW):
            groups.append(rows); rows = [[]]
        rows[-1].append(it)
    if rows[-1]:
        groups.append(rows)
    for gi, g in enumerate(groups):
        t1 = groups[gi + 1][0][0]["t"] if gi + 1 < len(groups) else out
        chunks.append(dict(rows=g, items=[i for r in g for i in r], t0=g[0][0]["t"], t1=t1))
SECTIONS = [tuple(x) + (True,) * (4 - len(x)) for x in SECTIONS]  # (num, label, t, flash)
for num, label, t, fl in SECTIONS:
    if fl:
        events.append(("flash", t)); events.append(("boom", t + 0.05))
    else:
        events.append(("pop", t))
for t in SCENES:
    events.append(("whoosh", t))
first_price = sorted(c["t0"] for c in chunks if any(i["key"] for i in c["items"]))
sections = []
starts = [x[2] for x in SECTIONS]
for num, label, t, fl in SECTIONS:
    nxt = [p for p in first_price if p > t] + [x for x in starts if x > t]
    sections.append(dict(num=str(num), label=label, t0=t, t1=min(t + 1.6, (min(nxt) - 0.02) if nxt else 1e9)))
json.dump(sorted(events, key=lambda e: e[1]), open(OUT + ".events.json", "w"))


# ---------------- per-frame drawing ----------------
def draw_words(c, t):
    for ch in chunks:
        if not (ch["t0"] <= t < ch["t1"]):
            continue
        rows = ch["rows"]
        hs = [(230 if r[0]["key"] else 135) for r in rows]
        y = Y_WORD - sum(hs) / 2
        for row, h in zip(rows, hs):
            cy = y + h / 2
            if row[0]["key"]:
                it = row[0]
                if it["t"] <= t:
                    p = (t - it["t"]) / 0.16
                    sc, al = 0.75 + 0.25 * back(p), min(1.0, p * 3)
                    gap = -50
                    parts = [it["num"]] + ([it["unit"]] if it["unit"] else [])
                    total = sum(x.width for x in parts) + gap * (len(parts) - 1)
                    x = W / 2 + total / 2      # number on the right, "ريال" to its left
                    for sp in parts:
                        place(c, sp, x - sp.width / 2, cy, sc, al)
                        x -= sp.width + gap
                    q = ease((t - it["t"] - 0.1) / 0.3)
                    if q > 0:
                        bw = (total - 60) * q
                        ImageDraw.Draw(c).rounded_rectangle((W / 2 - bw / 2, cy + 78, W / 2 + bw / 2, cy + 90), 6,
                                                            fill=ORANGE + (255,))
            else:
                gap = -80 + 26
                total = sum(i["sp"].width for i in row) + gap * (len(row) - 1)
                x = W / 2 + total / 2
                for i in row:
                    wd = i["sp"].width
                    if i["t"] <= t:
                        p = ease((t - i["t"]) / 0.2)
                        place(c, i["sp"], x - wd / 2, cy + 22 * (1 - p), 1.0, p)
                    x -= wd + gap
            y += h


def draw_circle(c, cx, cy, rw, rh, prog):
    if prog <= 0:
        return
    layer = Image.new("RGBA", (W, 600), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    oy = cy - 300
    start, span = math.radians(200), math.radians(400) * min(prog, 1.0)
    n = max(2, int(80 * min(prog, 1.0)))
    pts = []
    for i in range(n + 1):
        a = start - span * i / n
        wob = 1 + 0.04 * math.sin(a * 3) + 0.06 * (i / 80)
        pts.append((cx + rw * wob * math.cos(a), 300 + rh * wob * math.sin(a)))
    d.line(pts, fill=(0, 0, 0, 110), width=13, joint="curve")
    d.line(pts, fill=(255, 255, 255, 255), width=8, joint="curve")
    c.alpha_composite(layer, (0, oy))


def draw_prices(c, t):
    for p in prices:
        if not (p["t0"] <= t < p["t1"] + 0.18):
            continue
        fade = 1 - ease((t - p["t1"]) / 0.18) if t > p["t1"] else 1.0
        col = OLD if p["kind"] == "old" else GREEN
        sp = sprite(p["text"], F_PRICE, col)
        q = (t - p["t0"]) / 0.16
        sc = 1.35 - 0.35 * ease(q)
        y = p.get("y", Y_PRICE)
        place(c, sp, W / 2, y, sc, min(1.0, q * 3) * fade)
        if p["kind"] == "old" and "strike" in p and t >= p["strike"]:
            s = ease((t - p["strike"]) / 0.16)
            half = (sp.width - 80) / 2
            x0, x1 = W / 2 - half - 10, W / 2 - half - 10 + (2 * half + 20) * s
            d = ImageDraw.Draw(c)
            d.line((x0, y + 8, x1, y - 4 + 12 * (1 - s)), fill=(0, 0, 0, int(140 * fade)), width=14)
            d.line((x0, y + 6, x1, y - 6 + 12 * (1 - s)), fill=(255, 255, 255, int(255 * fade)), width=9)
        if p["kind"] == "solo" and fade > 0.5:
            draw_circle(c, W / 2, y + 6, sp.width / 2 - 10, sp.height / 2 - 4, (t - p["t0"] - 0.12) / 0.32)


def draw_sections(c, t):
    for s in sections:
        if s["t0"] <= t < s["t1"]:
            q = (t - s["t0"]) / 0.18
            out = 1 - ease((t - (s["t1"] - 0.15)) / 0.15) if t > s["t1"] - 0.15 else 1.0
            if s["num"]:
                place(c, sprite(s["num"], F_NUM, WHITE), W / 2, 470, 0.6 + 0.4 * back(q), min(1, q * 3) * out)
            q2 = (t - s["t0"] - 0.12) / 0.18
            if q2 > 0:
                sp = sprite(s["label"], F_SEC, WHITE)
                place(c, sp, W / 2, 640, 1.0, min(1, q2 * 3) * out)
                bw = 160 * ease(q2 / 1.6)
                ImageDraw.Draw(c).rounded_rectangle((W / 2 - bw / 2, 728, W / 2 + bw / 2, 738), 5,
                                                    fill=ORANGE + (int(255 * out),))


def flash(frame, t):
    for s in SECTIONS:
        if not s[3]:
            continue
        dt = t - s[2]
        if -0.04 <= dt < 0.28:
            a = 0.92 * (1 - max(dt, 0) / 0.28) if dt >= 0 else 0.5
            f = frame.astype(np.float32)
            return (f + (255 - f) * a).astype(np.uint8)
    return frame


_logos = {}


def draw_logos(c, t):
    for path, t0, t1, y, w in LOGOS:
        if not (t0 <= t < t1 + 0.25):
            continue
        if path not in _logos:
            lg = Image.open(path).convert("RGBA")
            _logos[path] = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
        q = ease((t - t0) / 0.35)
        out = 1 - ease((t - t1) / 0.25) if t > t1 else 1.0
        place(c, _logos[path], W / 2, y, 0.85 + 0.15 * q, q * out)


def composite(frame, t):
    img = Image.fromarray(flash(frame, t)).convert("RGBA")
    draw_logos(img, t)
    draw_sections(img, t)
    draw_words(img, t)
    return np.asarray(img.convert("RGB"))


def run_frames():
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"scale={W}:{H}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.stdout.close()


if PREVIEW:
    want = {int(float(x) * FPS): float(x) for x in PREVIEW.split(",")}
    for fi, f in enumerate(run_frames()):
        if fi in want:
            Image.fromarray(composite(f, want[fi])).save(f"{OUT}_{want[fi]:.2f}.png")
        if fi >= max(want):
            break
    sys.exit()

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-i", SRC, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                        "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", OUT],
                       stdin=subprocess.PIPE)
for fi, f in enumerate(run_frames()):
    enc.stdin.write(composite(f, fi / FPS).tobytes())
enc.stdin.close(); enc.wait()
print("done", len(chunks), "lines", len(sections), "sections", file=sys.stderr)
