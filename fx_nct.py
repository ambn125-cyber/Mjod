"""Editing ideas pass for the NCT clip (runs on the source, before captions):
  1. punch-in zooms when a piece is held up,
  2. split screen "on the thobe / on casual" for the jackets line,
  3. beat cuts in the shoes section (alternating punch-in on every word),
  4. hanging product tags that drop in on a string (text stays straight).
Usage: fx_nct.py SRC OUT FONTS [preview times]"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONTS = sys.argv[1:4]
PREVIEW = sys.argv[4] if len(sys.argv) > 4 else None
W, H, FPS = 1080, 1920, 30
ORANGE, WHITE = (242, 125, 38), (255, 255, 255)

ZOOMS = [6.20, 10.56, 11.86, 26.32, 32.32, 35.16, 44.92, 47.76]          # punch-ins (start times)
SPLIT = (49.02, 50.20, 5.30)            # split window, and where the casual shot starts in the source
SPLIT_LABELS = ("مع الثوب", "مع الكاجوال")
BEATS = [51.82, 52.58, 52.96, 53.58, 54.48, 55.02, 55.54, 56.18, 56.96, 57.66, 58.06, 58.60, 59.60,
         60.18, 60.90, 61.62, 62.10]    # word onsets in the shoes section
TAGS = [(10.56, 12.58, "الخامات", "جلد · قماش"), (32.32, 33.66, "طقم", "هودي + بنطلون"),
        (35.16, 37.56, "القصّة", "Oversize"), (44.92, 47.32, "سديريات رجالية", "أشكال وألوان"),
        (52.58, 56.16, "أحذية جديدة", "رياضية · طبية")]


def ease(p):
    p = min(max(p, 0.0), 1.0)
    return 1 - (1 - p) ** 3


def back(p, s=1.8):
    p = min(max(p, 0.0), 1.0) - 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


def zoom_at(t):
    z = 1.0
    for s in ZOOMS:
        d = t - s
        if 0 <= d < 0.22:
            z = max(z, 1 + 0.16 * ease(d / 0.22))
        elif 0.22 <= d < 0.75:
            z = max(z, 1.16)
        elif 0.75 <= d < 1.15:
            z = max(z, 1 + 0.16 * (1 - ease((d - 0.75) / 0.4)))
    for i, b in enumerate(BEATS):          # beat cuts: hard alternate framing on every word
        nxt = BEATS[i + 1] if i + 1 < len(BEATS) else 62.8
        if b <= t < nxt:
            z = max(z, 1.14 if i % 2 else 1.0)
    return z


def zoom(im, z):
    if z <= 1.001:
        return im
    cw, ch = int(W / z), int(H / z)
    return im.crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)).resize((W, H), Image.BILINEAR)


F_TAG_T = ImageFont.truetype(f"{FONTS}/Tajawal-Black.ttf", 62)
F_TAG_S = ImageFont.truetype(f"{FONTS}/Tajawal-ExtraBold.ttf", 48)
F_SPLIT = ImageFont.truetype(f"{FONTS}/Tajawal-Black.ttf", 64)
_tags = {}


def tag_sprite(title, sub):
    k = (title, sub)
    if k in _tags:
        return _tags[k]
    d = lambda s: "rtl" if any("؀" <= ch <= "ۿ" for ch in s) else "ltr"
    b1 = F_TAG_T.getbbox(title, direction=d(title)); b2 = F_TAG_S.getbbox(sub, direction=d(sub))
    tw = max(b1[2] - b1[0], b2[2] - b2[0]) + 70
    th = 220
    S = 30
    im = Image.new("RGBA", (tw + 2 * S, th + 2 * S + 40), (0, 0, 0, 0))
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((S, S + 50, S + tw, S + 40 + th), 26, fill=120)
    im.putalpha(sh.filter(ImageFilter.GaussianBlur(10)))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((S, S + 40, S + tw, S + 40 + th), 26, fill=ORANGE + (255,))
    cx = S + tw / 2
    dr.ellipse((cx - 13, S + 52, cx + 13, S + 78), fill=(255, 255, 255, 255))        # tag hole
    dr.ellipse((cx - 7, S + 58, cx + 7, S + 72), fill=(60, 30, 10, 255))
    dr.text((cx - (b1[2] - b1[0]) / 2 - b1[0], S + 92 - b1[1]), title, font=F_TAG_T, fill=WHITE, direction=d(title))
    dr.text((cx - (b2[2] - b2[0]) / 2 - b2[0], S + 185 - b2[1]), sub, font=F_TAG_S, fill=(255, 236, 214), direction=d(sub))
    _tags[k] = (im, cx, S + 65)
    return _tags[k]


def draw_tags(c, t):
    for t0, t1, title, sub in TAGS:
        if not (t0 <= t < t1 + 0.25):
            continue
        im, hx, hy = tag_sprite(title, sub)
        p = (t - t0) / 0.45
        drop = -420 * (1 - back(p))                      # falls in on its string and settles
        out = 1 - ease((t - t1) / 0.25) if t > t1 else 1.0
        x = W - 70 - im.width + hx                       # string anchor x (right side)
        y_hole = 300 + drop - (1 - out) * 300
        dr = ImageDraw.Draw(c)
        dr.line((x, 0, x, y_hole), fill=(255, 255, 255, 230), width=4)
        c.alpha_composite(im, (int(x - hx), int(y_hole - hy)))


def draw_split(c, t, casual):
    s0, s1, _ = SPLIT
    p = ease((t - s0) / 0.25)
    out = 1 - ease((t - (s1 - 0.2)) / 0.2) if t > s1 - 0.2 else 1.0
    if p * out <= 0:
        return c
    top = c.crop((0, 480, W, 1440)).resize((W, 960))                 # current shot, centre band
    bot = casual.crop((0, 380, W, 1340))
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    frame.paste(top, (0, 0)); frame.paste(bot, (0, 960))
    dr = ImageDraw.Draw(frame)
    dr.rectangle((0, 954, W, 966), fill=ORANGE + (255,))
    for i, lab in enumerate(SPLIT_LABELS):
        bb = F_SPLIT.getbbox(lab, direction="rtl")
        w, h = bb[2] - bb[0] + 60, 100
        x0, y0 = W - 60 - w, (60 if i == 0 else 1020)
        dr.rounded_rectangle((x0, y0, x0 + w, y0 + h), 22, fill=(0, 0, 0, 170))
        dr.text((x0 + 30 - bb[0], y0 + 18 - bb[1]), lab, font=F_SPLIT, fill=ORANGE if i else WHITE, direction="rtl")
    # slide the split in from the right
    a = p * out
    off = int(W * (1 - p))
    res = c.copy()
    res.alpha_composite(frame.crop((0, 0, W - off, H)) if off < W else frame, (off, 0)) if off < W else None
    if a < 1:
        res = Image.blend(c, res, a)
    return res


def frames(src, start=0.0):
    args = ["ffmpeg", "-v", "error"] + (["-ss", str(start)] if start else []) + ["-i", src, "-vf", f"scale={W}:{H}",
                                                                                 "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.stdout.close()


casual_iter = None


def composite(f, t):
    global casual_iter
    im = zoom(Image.fromarray(f), zoom_at(t)).convert("RGBA")
    s0, s1, cs = SPLIT
    if s0 <= t < s1:
        if casual_iter is None:
            casual_iter = frames(SRC, cs)
        casual = Image.fromarray(next(casual_iter)).convert("RGBA")
        im = draw_split(im, t, casual)
    draw_tags(im, t)
    return np.asarray(im.convert("RGB"))


if PREVIEW:
    want = sorted(float(x) for x in PREVIEW.split(","))
    for fi, f in enumerate(frames(SRC)):
        t = fi / FPS
        if any(abs(t - w) < 0.5 / FPS for w in want):
            Image.fromarray(composite(f, t)).save(f"{OUT}_{t:.2f}.png")
        elif SPLIT[0] <= t < SPLIT[1]:
            composite(f, t)                       # keep the casual stream in step
        if t > max(want):
            break
    sys.exit()

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-i", SRC, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", OUT], stdin=subprocess.PIPE)
for fi, f in enumerate(frames(SRC)):
    enc.stdin.write(composite(f, fi / FPS).tobytes())
enc.stdin.close(); enc.wait()
print("done", file=sys.stderr)
