"""Luxury real-estate captions: gold-gradient Lalezar headlines, white El Messiri lines, frosted
glass info cards with a gold hairline, big gold serif numbers. Soft fades/slides only.
Usage: render_aq.py SRC OUT FONTS SPEC  (encodes OUT directly; ENC env 'share' or 'hq')"""
import os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONTS, SPEC = sys.argv[1:5]
PREVIEW = sys.argv[5] if len(sys.argv) > 5 else None
W, H, FPS = 1080, 1920, 30
spec = {}
exec(open(SPEC, encoding="utf-8").read(), spec)
GOLD = [(255, 241, 193), (233, 196, 106), (184, 134, 43)]
EDGE = (233, 196, 106)
FL = lambda s: ImageFont.truetype(f"{FONTS}/Lalezar-Regular.ttf", s)
def FE(s):
    f = ImageFont.truetype(f"{FONTS}/ElMessiri.ttf", s); f.set_variation_by_name("Bold"); return f
def FN(s):
    f = ImageFont.truetype(f"{FONTS}/NotoSerif.ttf", s); f.set_variation_by_name("Bold"); return f
LRM = "‎"


def ease(p):
    p = min(max(p, 0.0), 1.0)
    return 1 - (1 - p) ** 3


def fix(t):
    return re.sub(r"(\d[\d.,%]*)", LRM + r"\1" + LRM, t)


_c = {}


def text(t, f, kind):
    k = (t, id(f), kind)
    if k in _c:
        return _c[k]
    s = fix(t)
    d = "rtl" if re.search(r"[؀-ۿ]", s) else "ltr"
    bb = f.getbbox(s, direction=d)
    pad = 30
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).text((pad - bb[0], pad - bb[1]), s, font=f, fill=255, direction=d)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("L", (w, h), 0); sh.paste(m, (0, 5)); im.putalpha(sh.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * .75)))
    if kind == "g":
        y = np.linspace(0, 1, h)[:, None]
        c0, c1, c2 = (np.array(c, np.float32) for c in GOLD)
        col = np.where(y < .45, c0 + (c1 - c0) * (y / .45), c1 + (c2 - c1) * ((y - .45) / .55))
        fill = Image.fromarray(np.repeat(col[:, None, :], w, 1).astype(np.uint8)).convert("RGBA")
    else:
        fill = Image.new("RGBA", (w, h), {"w": (255, 255, 255), "e": EDGE, "s": (225, 225, 225)}[kind] + (255,))
    fill.putalpha(m); im.alpha_composite(fill)
    _c[k] = im
    return im


def put(c, im, x, y, a, anchor="r"):
    if a <= 0:
        return
    if a < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x0 = int(x - im.width) if anchor == "r" else int(x - im.width / 2)
    y0 = int(y - im.height / 2)
    c.alpha_composite(im, (max(0, x0), max(0, y0)))


def fade(t, t0, t1, din=0.45, dout=0.35):
    if t < t0 or t >= t1:
        return 0.0
    return min(ease((t - t0) / din), 1 - ease((t - (t1 - dout)) / dout) if t > t1 - dout else 1.0)


def draw_hook(c, t, hk):
    t1 = hk["t1"]
    R = W - 70
    a = fade(t, hk["l1"][1], t1); put(c, text(hk["l1"][0], FE(60), "w"), R, 1130 + 20 * (1 - a), a)
    a = fade(t, hk["big"][1], t1, 0.6); put(c, text(hk["big"][0], FL(190), "g"), R + 20, 1290 + 30 * (1 - a), a)
    a = fade(t, hk["sub"][1], t1); put(c, text(hk["sub"][0], FE(66), "w"), R, 1440, a)
    if t >= hk["sub"][1]:
        q = ease((t - hk["sub"][1]) / 0.6) * (fade(t, hk["l1"][1], t1) > 0)
        lw = int(340 * q)
        if lw > 2:
            bar = Image.new("RGBA", (lw, 6), (0, 0, 0, 0))
            g = np.linspace(0, 1, lw)[None, :, None] * np.array(EDGE + (255,), np.float32)[None, None, :]
            bar = Image.fromarray(np.repeat(g, 6, 0).astype(np.uint8), "RGBA")
            c.alpha_composite(bar, (R - lw, 1510))


def draw_card(c, t, cd, frame_img):
    t0, t1 = cd["t0"], cd["t1"]
    a = fade(t, t0, t1, 0.5)
    if a <= 0:
        return
    lines = []
    if cd.get("k"): lines.append(("k", cd["k"], t0))
    lines.append(("t", cd["t"][0], cd["t"][1]))
    if cd.get("s"): lines.append(("s", cd["s"][0], cd["s"][1]))
    sprites = [(kind, text(s, {"k": FE(40), "t": FL(92), "s": FE(46)}[kind], {"k": "e", "t": "w", "s": "s"}[kind]), ts) for kind, s, ts in lines]
    cw = max(620, max(sp.width for _, sp, _ in sprites) + 40)
    ch = sum(sp.height - 40 for _, sp, _ in sprites) + 60
    x1 = W - 56; x0 = x1 - cw; y0 = 1160 - ch // 2 + int(30 * (1 - a)); y1 = y0 + ch
    region = frame_img.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(18))
    tint = Image.new("RGBA", region.size, (15, 12, 8, 120)); region = region.convert("RGBA"); region.alpha_composite(tint)
    mask = Image.new("L", region.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch - 1), 34, fill=int(255 * a))
    c.paste(region, (x0, y0), mask)
    ImageDraw.Draw(c).rounded_rectangle((x0, y0, x1, y1), 34, outline=EDGE + (int(200 * a),), width=3)
    y = y0 + 30
    for kind, sp, ts in sprites:
        h = sp.height - 40
        la = a * ease((t - ts) / 0.4) if t >= ts else 0
        put(c, sp, x1 - 14, y + h / 2, la)
        y += h


def draw_big(c, t, bg):
    a = fade(t, bg["t0"], bg["t1"], 0.5)
    if a <= 0:
        return
    y = 1080
    for item in bg["rows"]:
        kind, s, ts = item[:3]
        if kind == "nums":
            xs = [W / 2 + 200, W / 2 - 200]
            for (num, lab, tn), x in zip(s, xs):
                la = a * ease((t - tn) / 0.45) if t >= tn else 0
                put(c, text(num, FN(170), "g"), x, y + 80 + 20 * (1 - la), la, "c")
                put(c, text(lab, FE(54), "w"), x, y + 220, la, "c")
            y += 300
        else:
            f = FL(130) if kind == "g" else FE(64)
            sp = text(s, f, kind)
            la = a * ease((t - ts) / 0.45) if t >= ts else 0
            put(c, sp, W / 2, y + 20 * (1 - la), la, "c")
            y += sp.height - 20


def composite(frame, t):
    base = Image.fromarray(frame)
    img = base.convert("RGBA")
    hk = spec["HOOK"]
    if t < hk["t1"]:
        draw_hook(img, t, hk)
    for cd in spec["CARDS"]:
        if cd["t0"] <= t < cd["t1"]:
            draw_card(img, t, cd, base)
    for bg in spec["BIGS"]:
        if bg["t0"] <= t < bg["t1"]:
            draw_big(img, t, bg)
    return np.asarray(img.convert("RGB"))


def frames():
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
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
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", SRC, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for fi, f in enumerate(frames()):
    enc.stdin.write(composite(f, fi / FPS).tobytes())
enc.stdin.close(); enc.wait()
print("done", file=sys.stderr)
