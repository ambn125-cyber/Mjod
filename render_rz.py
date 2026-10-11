"""Supermarket-offer box captions (Ramez): words pop in on white boxes (brand red text), brand names on
red boxes, prices on big green boxes; an old price shows on a dark box and gets struck in red when the
new price lands; big discounts appear as a giant translucent number behind. Spec chunks in source time.
Usage: render_rz.py SRC OUT FONTS SPEC [preview times]"""
import re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONTS, SPEC = sys.argv[1:5]
PREVIEW = sys.argv[5] if len(sys.argv) > 5 else None
W, H, FPS = 1080, 1920, 30
spec = {}
exec(open(SPEC, encoding="utf-8").read(), spec)
CH = spec["CHUNKS"]
RED, GREEN, WHITE, DARK = tuple(spec["RED"]), tuple(spec["GREEN"]), (255, 255, 255), (20, 20, 20)
YC = spec.get("Y", 1230)
F_W = ImageFont.truetype(f"{FONTS}/Tajawal-Black.ttf", 76)
F_P = ImageFont.truetype(f"{FONTS}/Tajawal-Black.ttf", 104)
F_BIG = ImageFont.truetype(f"{FONTS}/Lalezar-Regular.ttf", 400)
LRM = "‎"


def ease(p):
    p = min(max(p, 0.0), 1.0)
    return 1 - (1 - p) ** 3


def back(p, s=2.0):
    p = min(max(p, 0.0), 1.0) - 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


def fix(t):  # keep numbers (with % . ) in reading order inside RTL text
    return re.sub(r"(\d[\d.,%]*)", LRM + r"\1" + LRM, t)


_c = {}


def box(text, kind):
    k = (text, kind)
    if k in _c:
        return _c[k]
    f = F_P if kind in ("p", "o") else F_W
    if kind == "o":
        f = F_W
    bg, fg, a = {"w": (WHITE, RED, 255), "k": (RED, WHITE, 255), "p": (GREEN, WHITE, 255), "o": (DARK, WHITE, 165)}[kind]
    t = fix(text)
    bb = f.getbbox(t, direction="rtl")
    px, py = (30, 14) if kind != "p" else (38, 18)
    asc, desc = f.getmetrics()
    bw, bh = bb[2] - bb[0] + 2 * px, int((asc + desc) * 0.86) + 2 * py - 14
    S = 26
    im = Image.new("RGBA", (bw + 2 * S, bh + 2 * S), (0, 0, 0, 0))
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((S, S + 9, S + bw, S + bh + 9), 22, fill=100)
    im.putalpha(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((S, S, S + bw, S + bh), 22, fill=bg + (a,))
    d.text((S + px - bb[0], S + py - 6), t, font=f, fill=fg, direction="rtl")
    _c[k] = im
    return im


_g = {}


def ghost(text):
    if text not in _g:
        t = fix(text)
        sw = 10
        bb = F_BIG.getbbox(t, direction="ltr", stroke_width=sw)
        pad = 30
        w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
        org = (pad - bb[0], pad - bb[1])
        edge = Image.new("L", (w, h), 0); ImageDraw.Draw(edge).text(org, t, font=F_BIG, fill=255, stroke_width=sw, stroke_fill=255)
        ink = Image.new("L", (w, h), 0); ImageDraw.Draw(ink).text(org, t, font=F_BIG, fill=255)
        ring = Image.fromarray(np.clip(np.asarray(edge, np.int16) - np.asarray(ink, np.int16), 0, 255).astype(np.uint8))
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        r = Image.new("RGBA", (w, h), WHITE + (255,)); r.putalpha(ring.point(lambda v: int(v * .85))); im.alpha_composite(r)
        c = Image.new("RGBA", (w, h), RED + (255,)); c.putalpha(ink.point(lambda v: int(v * .58))); im.alpha_composite(c)
        if im.width > W - 60:
            im = im.resize((W - 60, int(im.height * (W - 60) / im.width)), Image.LANCZOS)
        _g[text] = im
    return _g[text]


def place(c, im, x, y, sc=1.0, a=1.0):
    if sc != 1.0:
        im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
    if a < 1.0:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x0, y0 = int(x - im.width / 2), int(y - im.height / 2)
    cx, cy = max(0, -x0), max(0, -y0)
    c.alpha_composite(im.crop((cx, cy, im.width, im.height)), (x0 + cx, y0 + cy))


# layout: wrap items into rows (max width), prices/old prices share their own row
for ch in CH:
    rows, row, wsum = [], [], 0
    for kind, text, t in ch["items"]:
        sp = box(text, kind)
        wd = sp.width - 52 + 14
        if kind in ("p", "o"):
            if row and row[-1][0] not in ("p", "o"):
                rows.append(row); row, wsum = [], 0
        elif row and (row[-1][0] in ("p", "o") or wsum + wd > 940):
            rows.append(row); row, wsum = [], 0
        row.append((kind, text, t, sp)); wsum += wd
    if row:
        rows.append(row)
    ch["rows"] = rows
    newp = [t for k, _, t in ch["items"] if k == "p"]
    ch["strike"] = newp[0] if newp and any(k == "o" for k, _, _ in ch["items"]) else None


def draw(c, ch, t):
    out = 1 - ease((t - (ch["t1"] - 0.15)) / 0.15) if t > ch["t1"] - 0.15 else 1.0
    if ch.get("big") and t >= ch["big"][1]:
        p = (t - ch["big"][1]) / 0.25
        place(c, ghost(ch["big"][0]), W / 2, YC - 330, 1.3 - 0.3 * ease(p), min(1.0, p * 4) * out)
    rh = [max(sp.height for *_, sp in r) - 40 for r in ch["rows"]]
    y = YC - sum(rh) / 2
    for r, h in zip(ch["rows"], rh):
        total = sum(sp.width - 52 for *_, sp in r) + 14 * (len(r) - 1)
        x = W / 2 + total / 2
        for kind, text, tt, sp in r:
            wd = sp.width - 52
            if t >= tt:
                p = (t - tt) / 0.16
                place(c, sp, x - wd / 2, y + h / 2, 0.7 + 0.3 * back(p), min(1.0, p * 3) * out)
                if kind == "o" and ch["strike"] and t >= ch["strike"]:
                    s = ease((t - ch["strike"]) / 0.18)
                    x1 = x - 8
                    x0 = x - wd + 8
                    xe = x0 + (x1 - x0) * s
                    yy = y + h / 2
                    d = ImageDraw.Draw(c)
                    d.line((x0, yy + 14, xe, yy + 14 - 28 * s), fill=RED + (int(255 * out),), width=10)
            x -= wd + 14
        y += h


def composite(frame, t):
    img = Image.fromarray(frame).convert("RGBA")
    for ch in CH:
        if ch["t0"] <= t < ch["t1"]:
            draw(img, ch, t)
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
print("done", len(CH), "chunks", file=sys.stderr)
