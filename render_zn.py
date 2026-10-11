"""Caption style "Zinco": small white phrases for running speech; key lines stack big on the right
in Lalezar, white or gold, gold words stretched with kashida (the stretch grows in) and a gold serif
number dropped into the kashida gap. Optional logo sticker. Spec CHUNKS are in source time.
Usage: render_zn.py SRC OUT FONTS SPEC [preview times]"""
import re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONTS, SPEC = sys.argv[1:5]
PREVIEW = sys.argv[5] if len(sys.argv) > 5 else None
W, H, FPS = 1080, 1920, 30
spec = {}
exec(open(SPEC, encoding="utf-8").read(), spec)
CHUNKS, LOGOS = spec["CHUNKS"], spec.get("LOGOS", [])
GOLD = spec.get("GOLD", [(255, 228, 130), (247, 183, 51), (214, 128, 26)])
Y_SMALL, Y_BIG, RIGHT = spec.get("Y_SMALL", 1180), spec.get("Y_BIG", 560), spec.get("RIGHT", 90)
K = "ـ"

F_SMALL = ImageFont.truetype(f"{FONTS}/Tajawal-ExtraBold.ttf", 62)
F_BIG = ImageFont.truetype(f"{FONTS}/Lalezar-Regular.ttf", 150)
F_MID = ImageFont.truetype(f"{FONTS}/Lalezar-Regular.ttf", 112)
F_NUM = ImageFont.truetype(f"{FONTS}/NotoSerif.ttf", 150)
F_NUM.set_variation_by_name("Bold")


def ease(p):
    p = min(max(p, 0.0), 1.0)
    return 1 - (1 - p) ** 3


def back(p, s=1.7):
    p = min(max(p, 0.0), 1.0) - 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


def is_ar(s):
    return bool(re.search(r"[؀-ۿ]", s))


_c = {}


def text_sprite(text, f, kind, pad=40):
    """kind: 'w' white or 'g' gold gradient. Soft shadow. Returns (img, bbox offset)."""
    k = (text, id(f), kind)
    if k in _c:
        return _c[k]
    d = "rtl" if is_ar(text) else "ltr"
    bb = f.getbbox(text, direction=d)
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((pad - bb[0], pad - bb[1]), text, font=f, fill=255, direction=d)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("L", (w, h), 0); sh.paste(m, (3, 8))
    out.putalpha(sh.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.6)))
    if kind == "g":
        y = np.linspace(0, 1, h)[:, None]
        c0, c1, c2 = (np.array(c, np.float32) for c in GOLD)
        col = np.where(y < 0.55, c0 + (c1 - c0) * (y / 0.55), c1 + (c2 - c1) * ((y - 0.55) / 0.45))
        fill = Image.fromarray(np.repeat(col[:, None, :], w, 1).reshape(h, w, 3).astype(np.uint8)).convert("RGBA")
    else:
        fill = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    fill.putalpha(m)
    out.alpha_composite(fill)
    _c[k] = (out, pad - bb[0], pad - bb[1])
    return _c[k]


def place(c, im, x, y, sc=1.0, a=1.0, anchor="c"):
    if sc != 1.0:
        im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
    if a < 1.0:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    if anchor == "r":
        x0 = int(x - im.width)
    else:
        x0 = int(x - im.width / 2)
    y0 = int(y - im.height / 2)
    cx, cy = max(0, -x0), max(0, -y0)
    c.alpha_composite(im.crop((cx, cy, im.width, im.height)), (x0 + cx, y0 + cy))


def stretched(text, frac):
    """Shrink the kashida run in text to a fraction of its length (min 1)."""
    m = re.search(K + "+", text)
    if not m:
        return text
    n = max(1, round(len(m.group()) * frac))
    return text[:m.start()] + K * n + text[m.end():]


def gap_center(text, f):
    """x offset (from the right edge of the rendered word) of the kashida run's centre."""
    m = re.search(K + "+", text)
    if not m:
        return None
    pre = text[:m.start()]
    full = f.getlength(text, direction="rtl")
    lp = f.getlength(pre + K, direction="rtl") - f.getlength(K, direction="rtl") * 0.5
    run = f.getlength(K * len(m.group()), direction="rtl")
    return lp + run / 2, full


def draw_chunk(c, ch, t):
    t0, t1 = ch["t0"], ch["t1"]
    out = 1 - ease((t - (t1 - 0.15)) / 0.15) if t > t1 - 0.15 else 1.0
    if ch["kind"] == "small":
        sp, _, _ = text_sprite(ch["text"], F_SMALL, "w")
        p = ease((t - t0) / 0.18)
        place(c, sp, W / 2, Y_SMALL + 18 * (1 - p), 1.0, p * out)
        return
    y = ch.get("y", Y_BIG)
    for text, tt, kind, num, size in ch["lines"]:
        f = {"big": F_BIG, "mid": F_MID}[size]
        lh = f.size * 0.98
        if t >= tt:
            p = (t - tt) / 0.16
            sgrow = ease((t - tt - 0.05) / 0.3)          # kashida grows in
            txt = stretched(text, 0.25 + 0.75 * sgrow) if K in text else text
            sp, ox, oy = text_sprite(txt, f, kind)
            sc = 0.82 + 0.18 * back(p)
            place(c, sp, W - RIGHT + 40, y + lh / 2, sc, min(1.0, p * 3) * out, anchor="r")
            if num and sgrow > 0.6:
                g = gap_center(text, f)
                if g:
                    off, full = g
                    q = (t - tt - 0.2) / 0.16
                    ns, _, _ = text_sprite(num, F_NUM, "g")
                    nx = W - RIGHT - off
                    place(c, ns, nx, y + lh * 0.30, 0.7 + 0.3 * back(q), min(1.0, max(q, 0) * 3) * out)
        y += lh


_logo = {}


def draw_logos(c, t):
    for path, a, b, cy, w in LOGOS:
        if not (a <= t < b + 0.3):
            continue
        if path not in _logo:
            lg = Image.open(path).convert("RGBA")
            _logo[path] = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
        p = (t - a) / 0.3
        out = 1 - ease((t - b) / 0.3) if t > b else 1.0
        place(c, _logo[path], W / 2, cy, 0.6 + 0.4 * back(p), min(1, p * 3) * out)


def composite(frame, t):
    img = Image.fromarray(frame).convert("RGBA")
    for ch in CHUNKS:
        if ch["t0"] <= t < ch["t1"]:
            draw_chunk(img, ch, t)
    draw_logos(img, t)
    return np.asarray(img.convert("RGB"))


def frames():
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
    want = {int(round(float(x) * FPS)): float(x) for x in PREVIEW.split(",")}
    for fi, f in enumerate(frames()):
        if fi in want:
            Image.fromarray(composite(f, want[fi])).save(f"{OUT}_{want[fi]:.2f}.png")
        if fi >= max(want):
            break
    sys.exit()
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-i", SRC, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                        "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", OUT],
                       stdin=subprocess.PIPE)
for fi, f in enumerate(frames()):
    enc.stdin.write(composite(f, fi / FPS).tobytes())
enc.stdin.close(); enc.wait()
print("done", len(CHUNKS), "chunks", file=sys.stderr)
