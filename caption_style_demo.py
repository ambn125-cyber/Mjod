"""2x2 demo of four caption styles on the same clip segment."""
import subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONTS = sys.argv[1:4]
T0, T1 = 20.85, 25.15
W, H, FPS = 540, 960, 30
WORDS = [("كان", 20.96), ("سعره", 21.14), ("السابق", 21.54), ("99 ريال", 21.92),
         ("والآن", 22.86), ("تاخذه", 23.62), ("بـ", 24.06), ("29 ريال", 24.34)]
GROUPS = [(0, 4, 22.80), (4, 8, 99)]  # word index range, group end time
NUM = lambda w: w[0].isdigit()
RED, WHITE, YEL, GOLD = (232, 28, 40), (255, 255, 255), (255, 214, 0), (228, 180, 90)


def font(name, size, var=None):
    f = ImageFont.truetype(f"{FONTS}/{name}", size)
    if var:
        f.set_variation_by_name(var)
    return f


def text_img(text, f, fill, stroke=0, stroke_fill=(0, 0, 0)):
    d = "ltr" if text[0].isdigit() else "rtl"
    bb = f.getbbox(text, direction=d, stroke_width=stroke)
    im = Image.new("RGBA", (bb[2] - bb[0] + 2, bb[3] - bb[1] + 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((-bb[0] + 1, -bb[1] + 1), text, font=f, fill=fill, direction=d,
                            stroke_width=stroke, stroke_fill=stroke_fill)
    return im


def shadow(im, r=8, a=0.7, off=(0, 6)):
    s = Image.new("RGBA", im.size, (0, 0, 0, 0))
    s.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    s = s.filter(ImageFilter.GaussianBlur(r))
    out = Image.new("RGBA", (im.width + 40, im.height + 40), (0, 0, 0, 0))
    out.alpha_composite(s, (20 + off[0], 20 + off[1]))
    out.alpha_composite(im, (20, 20))
    return out


def layout_rtl(imgs, gap, cx):
    total = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    x = cx + total // 2
    xs = []
    for i in imgs:
        x -= i.width
        xs.append(x)
        x -= gap
    return xs


def ease_out_back(p, s=1.9):
    p = min(max(p, 0), 1) - 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


def ease(p):
    p = min(max(p, 0), 1)
    return 1 - (1 - p) ** 3


def group_at(t):
    for a, b, end in GROUPS:
        if WORDS[a][1] <= t < end:
            return a, b
    return None


def paste(canvas, im, x, y, alpha=1.0):
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    canvas.alpha_composite(im, (int(x), int(y)))


# A: karaoke highlight — whole line shown, spoken word gets a red box
fA = font("Cairo.ttf", 44, "Black")
def style_a(c, t):
    g = group_at(t)
    if not g:
        return
    a, b = g
    imgs = [text_img(w, fA, WHITE) for w, _ in WORDS[a:b]]
    xs = layout_rtl(imgs, 14, W // 2)
    y = 700
    gp = ease((t - WORDS[a][1]) / 0.2)
    cur = max(i for i in range(a, b) if WORDS[i][1] <= t) if t >= WORDS[a][1] else a
    for k, (im, x) in enumerate(zip(imgs, xs)):
        i = a + k
        if i == cur:
            pad = 10
            box = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
            ImageDraw.Draw(box).rounded_rectangle((0, 0, box.width - 1, box.height - 1), 16, fill=RED)
            sc = 1 + 0.12 * (1 - ease((t - WORDS[i][1]) / 0.15))
            box = box.resize((int(box.width * sc), int(box.height * sc)))
            paste(c, box, x - pad - (box.width - im.width - 2 * pad) / 2, y - pad - (box.height - im.height - 2 * pad) / 2)
        paste(c, shadow(im, 6, 0.8, (0, 4)), x - 20, y - 20 + 30 * (1 - gp), gp)


# B: Lalezar bounce — words drop in one by one with overshoot, yellow numbers, thick outline
fB = font("Lalezar-Regular.ttf", 54)
def style_b(c, t):
    g = group_at(t)
    if not g:
        return
    a, b = g
    imgs = [text_img(w, fB, YEL if NUM((w, 0)) else WHITE, stroke=5) for w, _ in WORDS[a:b]]
    xs = layout_rtl(imgs, 12, W // 2)
    for k, (im, x) in enumerate(zip(imgs, xs)):
        ti = WORDS[a + k][1]
        if t < ti:
            continue
        p = (t - ti) / 0.35
        yoff = -90 * (1 - ease_out_back(p))
        rot = 12 * (1 - ease_out_back(p)) * (1 if k % 2 else -1)
        r = im.rotate(rot, expand=True, resample=Image.BICUBIC)
        paste(c, r, x, 680 + yoff, min(1, p * 3))


# C: elegant lower-third card — dark glass box, El Messiri, line slides up, gold numbers
fC = font("ElMessiri.ttf", 42, "Bold")
def style_c(c, t):
    g = group_at(t)
    if not g:
        return
    a, b = g
    shown = [(w, ti) for w, ti in WORDS[a:b] if ti <= t]
    full = [text_img(w, fC, GOLD if w[0].isdigit() else WHITE) for w, _ in WORDS[a:b]]
    xs = layout_rtl(full, 14, W // 2)
    p = ease((t - WORDS[a][1]) / 0.3)
    bw = sum(i.width for i in full) + 14 * (len(full) - 1) + 60
    bh = max(i.height for i in full) + 44
    card = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, bw - 1, bh - 1), 22, fill=(12, 14, 20, 170))
    ImageDraw.Draw(card).rectangle((bw - 8, 14, bw - 3, bh - 14), fill=RED)
    y = 720 + 40 * (1 - p)
    paste(c, card, W // 2 - bw // 2, y - 22, p)
    for k, (im, x) in enumerate(zip(full, xs)):
        ti = WORDS[a + k][1]
        if t < ti:
            continue
        q = ease((t - ti) / 0.25)
        paste(c, im, x, y + 12 * (1 - q), q)


# D: big punch word — one word at a time, huge, zooms in hard, numbers in red
fD = font("Changa.ttf", 120, "ExtraBold")
def style_d(c, t):
    cur = [i for i, (_, ti) in enumerate(WORDS) if ti <= t]
    if not cur or t > 25.1:
        return
    i = cur[-1]
    w, ti = WORDS[i]
    im = text_img(w, fD, RED if w[0].isdigit() else WHITE, stroke=4, stroke_fill=(0, 0, 0))
    p = ease((t - ti) / 0.12)
    sc = 1.6 - 0.6 * p
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.BILINEAR)
    if p < 1:
        im = im.filter(ImageFilter.GaussianBlur(4 * (1 - p)))
    im = shadow(im, 10, 0.8, (0, 8))
    paste(c, im, W // 2 - im.width // 2, 560 - im.height // 2, min(1, p * 2 + 0.2))


STYLES = [("A  كاريوكي", style_a), ("B  نطّة", style_b), ("C  بطاقة أنيقة", style_c), ("D  كلمة كبيرة", style_d)]
fL = font("Cairo.ttf", 34, "Black")

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(T0), "-t", str(T1 - T0), "-i", SRC, "-vf", f"scale={W}:{H}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W * 2}x{H * 2}",
                        "-r", str(FPS), "-i", "-", "-ss", str(T0), "-t", str(T1 - T0), "-i", SRC, "-map", "0:v", "-map", "1:a",
                        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                        "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
n, fi = W * H * 3, 0
while True:
    b = dec.stdout.read(n)
    if len(b) < n:
        break
    t = T0 + fi / FPS
    base = Image.fromarray(np.frombuffer(b, np.uint8).reshape(H, W, 3)).convert("RGBA")
    grid = Image.new("RGB", (W * 2, H * 2))
    for k, (label, fn) in enumerate(STYLES):
        tile = base.copy()
        fn(tile, t)
        lab = text_img(label, fL, WHITE)
        tag = Image.new("RGBA", (lab.width + 30, lab.height + 20), (0, 0, 0, 170))
        tag.alpha_composite(lab, (15, 10))
        tile.alpha_composite(tag, (W - tag.width - 16, 16))
        grid.paste(tile.convert("RGB"), ((1 - k % 2) * W, (k // 2) * H))  # A top-right (RTL reading order)
    d = ImageDraw.Draw(grid)
    d.line((W, 0, W, H * 2), fill=(0, 0, 0), width=4); d.line((0, H, W * 2, H), fill=(0, 0, 0), width=4)
    enc.stdin.write(np.asarray(grid).tobytes())
    fi += 1
enc.stdin.close(); enc.wait()
print("done", fi, file=sys.stderr)
