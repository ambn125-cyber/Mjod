"""Caption style "sticker": every line looks like a die-cut sticker (thick white outline + drop shadow).
Running speech in dark ink; key lines big in the brand colour, stacked and centred, popping in with a
small overshoot. Reads the same CHUNKS spec as render_zn.py (kashida marks are ignored, a number is
joined to its word). Usage: render_st.py SRC OUT FONTS SPEC [preview times]"""
import re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONTS, SPEC = sys.argv[1:5]
PREVIEW = sys.argv[5] if len(sys.argv) > 5 else None
W, H, FPS = 1080, 1920, 30
spec = {}
exec(open(SPEC, encoding="utf-8").read(), spec)
CHUNKS, LOGOS = spec["CHUNKS"], spec.get("LOGOS", [])
BRAND = tuple(spec.get("BRAND", (240, 127, 30)))
INK = tuple(spec.get("INK", (43, 43, 43)))
Y_SMALL, Y_BIG, RIGHT = spec.get("Y_SMALL", 1180), spec.get("Y_BIG", 560), spec.get("RIGHT", 90)
K = "ـ"

F_SMALL = ImageFont.truetype(f"{FONTS}/Lalezar-Regular.ttf", 76)
F_BIG = ImageFont.truetype(f"{FONTS}/Lalezar-Regular.ttf", 128)
F_MID = ImageFont.truetype(f"{FONTS}/Lalezar-Regular.ttf", 80)
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


def text_sprite(text, f, kind, pad=50):
    """Die-cut sticker text: kind 'w' dark ink, 'g' brand colour; thick white outline + shadow."""
    k = (text, id(f), kind)
    if k in _c:
        return _c[k]
    d = "rtl" if is_ar(text) else "ltr"
    sw = max(10, f.size // 7)
    bb = f.getbbox(text, direction=d, stroke_width=sw)
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    org = (pad - bb[0], pad - bb[1])
    edge = Image.new("L", (w, h), 0)
    ImageDraw.Draw(edge).text(org, text, font=f, fill=255, direction=d, stroke_width=sw, stroke_fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = Image.new("L", (w, h), 0); sh.paste(edge, (0, 9))
    out.putalpha(sh.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.55)))
    white = Image.new("RGBA", (w, h), (255, 255, 255, 255)); white.putalpha(edge)
    out.alpha_composite(white)
    ink = Image.new("L", (w, h), 0)
    ImageDraw.Draw(ink).text(org, text, font=f, fill=255, direction=d)
    col = Image.new("RGBA", (w, h), (INK if kind == "w" else BRAND) + (255,)); col.putalpha(ink)
    out.alpha_composite(col)
    _c[k] = (out, 0, 0)
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


_hd = {}


def plain_white(text):
    if ("pw", text) not in _hd:
        f = ImageFont.truetype(f"{FONTS}/Tajawal-ExtraBold.ttf", 60)
        bb = f.getbbox(text, direction="rtl"); pad = 30
        w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).text((pad - bb[0], pad - bb[1]), text, font=f, fill=255, direction="rtl")
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sh = Image.new("L", (w, h), 0); sh.paste(m, (0, 4)); im.putalpha(sh.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * .8)))
        wf = Image.new("RGBA", (w, h), (255, 255, 255, 255)); wf.putalpha(m); im.alpha_composite(wf)
        _hd[("pw", text)] = im
    return _hd[("pw", text)]


def hgrad(w, h, stops=((255, 209, 102), (240, 127, 30), (255, 77, 26))):
    x = np.linspace(0, 1, max(w, 1))[None, :, None]
    c0, c1, c2 = (np.array(c, np.float32) for c in stops)
    col = np.where(x < .6, c0 + (c1 - c0) * (x / .6), c1 + (c2 - c1) * ((x - .6) / .4))
    return Image.fromarray(np.repeat(col, h, 0).astype(np.uint8)).convert("RGBA")


def gradient_word(text):
    if ("gw", text) not in _hd:
        f = ImageFont.truetype(f"{FONTS}/Lalezar-Regular.ttf", 132)
        bb = f.getbbox(text, direction="rtl"); pad = 40
        w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).text((pad - bb[0], pad - bb[1]), text, font=f, fill=255, direction="rtl")
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sh = Image.new("L", (w, h), 0); sh.paste(m, (0, 7)); im.putalpha(sh.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * .65)))
        g = hgrad(w, h); g.putalpha(m); im.alpha_composite(g)
        _hd[("gw", text)] = im
    return _hd[("gw", text)]


def gradient_bar(w, h):
    w = max(w, 2)
    im = hgrad(w, h, ((255, 77, 26), (240, 127, 30), (255, 209, 102)))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=255)
    im.putalpha(m)
    return im


_rb = {}


def ribbon(text, dt):
    """Orange offer ribbon with notched ends, white text, and a light sheen that sweeps once."""
    if text not in _rb:
        f = ImageFont.truetype(f"{FONTS}/Lalezar-Regular.ttf", 74)
        bb = f.getbbox(text, direction="rtl")
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        bw, bh, notch, S = tw + 120, th + 56, 34, 26
        w, h = bw + 2 * S, bh + 2 * S
        base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        poly = [(S, S), (S + bw, S), (S + bw - notch, S + bh / 2), (S + bw, S + bh), (S, S + bh), (S + notch, S + bh / 2)]
        sh = Image.new("L", (w, h), 0); ImageDraw.Draw(sh).polygon([(x, y + 8) for x, y in poly], fill=130)
        base.putalpha(sh.filter(ImageFilter.GaussianBlur(9)))
        body = Image.new("L", (w, h), 0); ImageDraw.Draw(body).polygon(poly, fill=255)
        col = Image.new("RGBA", (w, h), BRAND + (255,)); col.putalpha(body); base.alpha_composite(col)
        dr = ImageDraw.Draw(base)
        dr.line([(S + 30, S + 10), (S + bw - 30, S + 10)], fill=(255, 255, 255, 110), width=3)       # stitch lines
        dr.line([(S + 30, S + bh - 10), (S + bw - 30, S + bh - 10)], fill=(255, 255, 255, 110), width=3)
        dr.text((S + 60 - bb[0], S + 28 - bb[1]), text, font=f, fill=(255, 255, 255, 255), direction="rtl")
        _rb[text] = (base, body)
    base, body = _rb[text]
    q = (dt - 0.25) / 0.6                                          # sheen sweeps right to left once
    if not (0 <= q <= 1):
        return base
    im = base.copy()
    w, h = im.size
    x0 = int(w * (1 - q)) - 120
    band = Image.new("L", (w, h), 0)
    ImageDraw.Draw(band).polygon([(x0, 0), (x0 + 90, 0), (x0 + 40, h), (x0 - 50, h)], fill=150)
    band = Image.fromarray(np.minimum(np.asarray(band), np.asarray(body)))
    glow = Image.new("RGBA", (w, h), (255, 255, 255, 255)); glow.putalpha(band.filter(ImageFilter.GaussianBlur(6)))
    im.alpha_composite(glow)
    return im


_gp = {}


def ghost_price(text):
    """Very large sticker price with a see-through fill (brand colour at ~55%, white edge ~80%)."""
    if text in _gp:
        return _gp[text]
    f = ImageFont.truetype(f"{FONTS}/Lalezar-Regular.ttf", 300)
    d = "rtl"
    sw = 26
    bb = f.getbbox(text, direction=d, stroke_width=sw)
    pad = 40
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    org = (pad - bb[0], pad - bb[1])
    edge = Image.new("L", (w, h), 0); ImageDraw.Draw(edge).text(org, text, font=f, fill=255, direction=d, stroke_width=sw, stroke_fill=255)
    ink = Image.new("L", (w, h), 0); ImageDraw.Draw(ink).text(org, text, font=f, fill=255, direction=d)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ring = Image.fromarray(np.clip(np.asarray(edge, np.int16) - np.asarray(ink, np.int16), 0, 255).astype(np.uint8))
    wl = Image.new("RGBA", (w, h), (255, 255, 255, 255)); wl.putalpha(ring.point(lambda v: int(v * 0.85))); out.alpha_composite(wl)
    cl = Image.new("RGBA", (w, h), BRAND + (255,)); cl.putalpha(ink.point(lambda v: int(v * 0.55))); out.alpha_composite(cl)
    if out.width > W - 40:
        out = out.resize((W - 40, int(out.height * (W - 40) / out.width)), Image.LANCZOS)
    _gp[text] = out
    return out


def line_text(text, num):
    text = text.replace(K, "")
    if not num:
        return text
    num = "\u200e" + num + "\u200e"                      # keep "20%" in reading order inside RTL
    return f"{text} {num}" if text.startswith("خص") else f"{num} {text}"


def draw_chunk(c, ch, t):
    t0, t1 = ch["t0"], ch["t1"]
    out = 1 - ease((t - (t1 - 0.15)) / 0.15) if t > t1 - 0.15 else 1.0
    if ch["kind"] == "grid":
        pt, num, tp = ch["price"]
        fade = 1 - ease((t - tp) / 0.12) if t > tp else 1.0     # items step aside for the price
        y = ch.get("top", 1080)
        ht, th = ch["header"]
        if t >= th:
            small, big = ht.split(" ", 2)[:2], ht.split(" ", 2)[2:]
            small, big = " ".join(small), " ".join(big)
            p = (t - th) / 0.2
            a = min(1.0, p * 3) * out * fade
            place(c, plain_white(small), W / 2, y - 70, 1.0, a)
            q = (t - th - 0.15) / 0.22
            if q > 0:
                gs = gradient_word(big)
                place(c, gs, W / 2, y + 20, 0.7 + 0.3 * back(q, 2.2), min(1.0, q * 3) * out * fade)
                u = ease((t - th - 0.35) / 0.35)                 # underline draws in from the right
                if u > 0:
                    uw = int(min(gs.width - 120, 520) * u)
                    bar = gradient_bar(uw, 14)
                    bx = W / 2 + min(gs.width - 120, 520) / 2 - uw
                    c.alpha_composite(bar.copy() if a >= 1 else Image.blend(Image.new("RGBA", bar.size, (0, 0, 0, 0)), bar, a),
                                      (int(bx), int(y + 85)))
        y += 200
        for i, (txt, tt) in enumerate(ch["items"]):
            row, col = divmod(i, 2)
            x = W / 2 + (230 if col == 0 else -230)      # first item of a pair on the right (RTL)
            if t >= tt:
                p = (t - tt) / 0.2
                sp = text_sprite(txt, F_MID, "w")[0]
                place(c, sp, x, y + row * 125, 0.6 + 0.4 * back(p, 2.2), min(1.0, p * 3) * out * fade)
        if t >= tp:                                       # flash, then a huge translucent price
            p = (t - tp) / 0.25
            sp = ghost_price(line_text(pt, num))
            place(c, sp, W / 2, 1300, 1.35 - 0.35 * ease(p), min(1.0, p * 4) * out)
        return
    if ch["kind"] == "small":
        sp, _, _ = text_sprite(ch["text"], F_SMALL, "w")
        p = (t - t0) / 0.2
        place(c, sp, W / 2, Y_SMALL, 0.75 + 0.25 * back(p), min(1.0, p * 3) * out)
        return
    sprites = []
    for text, tt, kind, num, size in ch["lines"]:
        f = F_BIG if kind == "g" else F_MID
        sprites.append((text_sprite(line_text(text, num), f, kind)[0], tt, f.size))
    total = sum(fs * 1.28 for _, _, fs in sprites)
    y = ch.get("yc", Y_SMALL) - total / 2 + 40
    for sp, tt, fs in sprites:
        lh = fs * 1.28
        if t >= tt:
            p = (t - tt) / 0.2
            place(c, sp, W / 2, y + lh / 2, 0.6 + 0.4 * back(p, 2.2), min(1.0, p * 3) * out)
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


def flash_amount(t):
    for ch in CHUNKS:
        if ch["kind"] == "grid":
            d = t - ch["price"][2]
            if -0.03 <= d < 0.22:
                return 0.85 * (1 - max(d, 0) / 0.22)
    return 0.0


def composite(frame, t):
    a = flash_amount(t)
    if a > 0:
        frame = (frame.astype(np.float32) + (255 - frame.astype(np.float32)) * a).astype(np.uint8)
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
