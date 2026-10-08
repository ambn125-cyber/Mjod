"""Reference style v2: one word at a time (white, keyword colour), serif SAR prices with
strike-through / hand-drawn circle, big numbered section cards, white flashes.
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
WHITE, GREEN, OLD = (255, 255, 255), (52, 235, 52), (226, 30, 30)


def font(name, size, var=None):
    f = ImageFont.truetype(f"{FONTS}/{name}", size)
    if var:
        f.set_variation_by_name(var)
    return f


F_WORD = font("Tajawal-ExtraBold.ttf", 100)
F_PRICE = font("NotoSerif.ttf", 128, "Black")
F_NUM = font("NotoSerif.ttf", 230, "Black")
F_LABEL = font("Tajawal-ExtraBold.ttf", 78)


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
    return f"{n} SAR"


def is_price(text):
    return bool(re.search(r"\d", text)) and "ريال" in text


# ---------------- build timeline ----------------
words, prices, events = [], [], []
for cap in CAPS:
    toks = [t for t in cap["toks"] if t[0] != "\n"]
    out = cap["out"]
    plain = [t for t in toks if not (t[2] in ("x",) or (t[2] == "p" and is_price(t[0])))]
    # one word at a time; very short words merge into the next one
    pending, pend_t = "", None
    for i, (text, t, c, s, join) in enumerate(plain):
        nxt = plain[i + 1][1] if i + 1 < len(plain) else out
        txt = (pending + " " + text).strip()
        t0 = pend_t if pend_t is not None else t
        if nxt - t < 0.16 and i + 1 < len(plain):
            pending, pend_t = txt, t0
            continue
        pending, pend_t = "", None
        words.append(dict(text=txt, t0=t0, t1=min(max(nxt, t + 0.35), t + 1.3, out + 0.05),
                          color=KEY if c in ("o", "p") else WHITE, big=c == "p"))
        if c == "p":
            events.append(("pop", t0))
    # prices
    old = None
    for text, t, c, s, join in toks:
        if c == "x":
            old = dict(kind="old", text=sar(text), t0=t, t1=out)
            prices.append(old); events.append(("pop", t))
        elif c == "p" and is_price(text):
            if old:
                old["strike"] = t - 0.22
                events.append(("swish", t - 0.22))
                prices.append(dict(kind="new", text=sar(text), t0=t, t1=out, y=Y_PRICE + 150))
                events.append(("ding", t))
                old = None
            else:
                prices.append(dict(kind="solo", text=sar(text), t0=t, t1=out))
                events.append(("ding", t)); events.append(("scribble", t + 0.12))
SECTIONS = [tuple(x) + (True,) * (4 - len(x)) for x in SECTIONS]  # (num, label, t, flash)
for num, label, t, fl in SECTIONS:
    if fl:
        events.append(("flash", t)); events.append(("boom", t + 0.05))
    else:
        events.append(("pop", t))
for t in SCENES:
    events.append(("whoosh", t))
first_price = sorted(p["t0"] for p in prices)
sections = []
starts = [x[2] for x in SECTIONS]
for num, label, t, fl in SECTIONS:
    nxt = [p for p in first_price if p > t] + [x for x in starts if x > t]
    sections.append(dict(num=str(num), label=label, t0=t, t1=min(t + 1.6, (min(nxt) - 0.02) if nxt else 1e9)))
json.dump(sorted(events, key=lambda e: e[1]), open(OUT + ".events.json", "w"))


# ---------------- per-frame drawing ----------------
def draw_words(c, t):
    for w in words:
        if w["t0"] <= t < w["t1"]:
            sp = sprite(w["text"], F_WORD, w["color"])
            p = (t - w["t0"]) / 0.13
            sc = (1.15 if w["big"] else 1.0) * (0.78 + 0.22 * back(p))
            place(c, sp, W / 2, Y_WORD, sc, min(1.0, p * 2.5))


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
            place(c, sprite(s["num"], F_NUM, WHITE), W / 2, 470, 0.6 + 0.4 * back(q), min(1, q * 3) * out)
            q2 = (t - s["t0"] - 0.12) / 0.18
            if q2 > 0:
                place(c, sprite(s["label"], F_LABEL, WHITE), W / 2, 640, 0.7 + 0.3 * back(q2), min(1, q2 * 3) * out)


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


def composite(frame, t):
    img = Image.fromarray(flash(frame, t)).convert("RGBA")
    draw_sections(img, t)
    draw_prices(img, t)
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
print("done", len(words), "words", len(prices), "prices", len(sections), "sections", file=sys.stderr)
