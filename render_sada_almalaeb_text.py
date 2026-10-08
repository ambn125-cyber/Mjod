"""Style 2 for Sada Al-Malaeb (red/white brand), with struck-through old prices: white + orange bold words with a dark halo, orange pill badges for the offers."""
import subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONT = sys.argv[1:4]
PREVIEW = sys.argv[4] if len(sys.argv) > 4 else None
W, H, FPS = 1080, 1920, 30
WHITE, ORANGE, NAVY = (255, 255, 255), (222, 30, 44), (20, 8, 8)  # ORANGE slot = brand red

# token: (text, t_in, color, scale, join)   "\n" = new line, join=True -> no gap before it
def T(text, t, c="w", s=1.0, join=False):
    return (text, t, c, s, join)  # c: "w" white, "o" orange, "p" orange pill

NL = ("\n", 0, None, 1, False)
TOP, LOW = 360, 1500
CAPS = [
    dict(toks=[T("أي", 0.40), T("تيشيرت", 0.48), NL, T("4 ريال", 1.86, "p", 1.3)], out=2.25, pos=(540, LOW), size=100),
    dict(toks=[T("ومن", 2.28), T("هنا", 2.62), T("أي", 2.76), T("تيشيرت", 2.88), NL, T("9 ريال", 3.90, "p", 1.3)], out=4.98, pos=(540, LOW), size=100),
    dict(toks=[T("تخيّل!", 5.00, "o", 1.1), NL, T("كلها", 5.42), T("بـ 9 ريال", 5.62, "p", 1.2)], out=8.3, pos=(540, TOP), size=100),
    dict(toks=[T("لو", 8.72), T("أخذت", 8.86), T("10", 9.16, "o", 1.2), NL, T("تطلع", 9.62), T("بـ 90 ريال", 10.20, "p", 1.15)], out=10.88, pos=(540, TOP), size=100),
    dict(toks=[T("كل", 10.90), T("هذا", 11.10), T("وين؟", 11.28, "o"), NL, T("صدى الملاعب", 11.66, "p", 1.25)], out=12.52, pos=(540, LOW), size=100),
    dict(toks=[T("عروض", 13.24), T("قوية", 13.56, "o"), NL, T("وحرق", 13.98), T("الأسعار", 14.50, "o", 1.15)], out=15.2, pos=(540, TOP), size=100),
    dict(toks=[T("أي", 16.10), T("تيشيرت", 16.42), T("رجالي", 16.92, "o"), NL, T("29 ريال", 17.52, "p", 1.3)], out=19.08, pos=(540, TOP), size=100),
    dict(toks=[T("كان", 20.96), T("سعره", 21.14), T("99 ريال", 21.92, "x", 1.1), NL, T("الآن", 22.86), T("29 ريال", 24.06, "p", 1.3)], out=25.08, pos=(540, TOP), size=100),
    dict(toks=[T("كان", 26.22), T("سعره", 26.78), T("69 ريال", 27.08, "x", 1.1), NL, T("الآن", 27.46), T("29 ريال", 28.34, "p", 1.3)], out=29.24, pos=(540, TOP), size=100),
    dict(toks=[T("لحّقوا", 29.26), T("على", 30.20), T("التصفيات", 30.34, "o"), NL, T("فرصة", 30.82), T("ما", 31.30), T("تتفوّت", 31.44, "o")], out=31.88, pos=(540, TOP), size=100),
    dict(toks=[T("الأطقم", 32.34, "o", 1.15), NL, T("كان", 34.70), T("99 ريال", 34.86, "x", 1.1), NL, T("الآن", 35.76), T("49 ريال", 36.86, "p", 1.3)], out=37.84, pos=(540, TOP), size=100),
    dict(toks=[T("طقم", 38.82), T("شورت", 39.38, "o"), NL, T("خامة", 39.72), T("طيبة", 40.30, "o")], out=40.66, pos=(540, TOP), size=100),
    dict(toks=[T("عرض", 43.44), T("خاص", 43.68, "o"), NL, T("على", 44.06), T("البناطيل", 44.16, "o")], out=44.48, pos=(540, TOP), size=100),
    dict(toks=[T("أي", 45.06), T("بنطلون", 45.32), NL, T("39 ريال", 46.18, "p", 1.3)], out=47.36, pos=(540, TOP), size=100),
    dict(toks=[T("بنطلون", 47.72), T("جينز", 48.12, "o"), NL, T("كان", 48.56), T("89 ريال", 49.80, "x", 1.1), NL, T("الآن", 50.76), T("39 ريال", 51.44, "p", 1.3)], out=52.44, pos=(540, TOP), size=100),
    dict(toks=[T("بناطيل", 52.94), T("أوفر", 53.52, "o"), T("سايز", 53.94, "o"), NL, T("39 ريال", 54.86, "p", 1.3)], out=55.8, pos=(540, TOP), size=100),
    dict(toks=[T("البناطيل", 56.48), T("الرياضية", 56.90, "o"), NL, T("كان", 57.56), T("89 ريال", 58.20, "x", 1.1), NL, T("الآن", 59.00), T("39 ريال", 60.18, "p", 1.3)], out=61.1, pos=(540, TOP), size=100),
    dict(toks=[T("مقاسات", 61.46), T("الجامبو", 61.94, "o"), NL, T("39 ريال", 62.44, "p", 1.3)], out=63.6, pos=(540, TOP), size=100),
    dict(toks=[T("الشورت", 63.88), T("الرياضي", 64.16, "o"), NL, T("39 ريال", 64.68, "p", 1.3)], out=66.1, pos=(540, TOP), size=100),
    dict(toks=[T("شورت", 66.44), T("مع", 66.80), T("مشد", 66.92, "o"), NL, T("39 ريال", 69.50, "p", 1.3)], out=70.4, pos=(540, TOP), size=100),
    dict(toks=[T("التيشيرتات", 71.28), T("الرياضية", 71.74, "o"), NL, T("أي", 72.70), T("تيشيرت", 72.74), NL, T("29 ريال", 73.68, "p", 1.3)], out=74.94, pos=(540, TOP), size=100),
    dict(toks=[T("صدى الملاعب", 75.46, "p", 1.2), NL, T("حرق", 76.66, "o", 1.2), T("الأسعار", 77.10, "o", 1.2)], out=77.7, pos=(540, TOP), size=100),
    dict(toks=[T("أي", 78.30), T("شورت", 78.44), T("رياضي", 78.82, "o"), NL, T("19 ريال", 79.34, "p", 1.3)], out=80.54, pos=(540, TOP), size=100),
    dict(toks=[T("الشورتات", 81.52), T("الرجالي", 82.08), NL, T("والجامبو", 82.82, "o"), NL, T("39 ريال", 83.38, "p", 1.3)], out=84.58, pos=(540, TOP), size=100),
    dict(toks=[T("تيشيرتات", 85.42), T("ولادي", 86.32, "o"), NL, T("أي", 87.78), T("تيشيرت", 87.98), NL, T("9 ريال", 89.48, "p", 1.3)], out=90.22, pos=(540, TOP), size=100),
    dict(toks=[T("تخيّلوا", 91.16, "o"), NL, T("9 ريال", 91.62, "p", 1.3)], out=92.18, pos=(540, TOP), size=100),
    dict(toks=[T("5", 92.88, "o", 1.2), T("تيشيرتات", 93.04), NL, T("ولادي", 93.72), T("وشبابي", 94.26, "o"), NL, T("69 ريال", 94.68, "p", 1.3)], out=95.92, pos=(540, TOP), size=100),
    dict(toks=[T("ولادي", 97.88), T("وشبابي", 98.44, "o"), NL, T("أي", 98.88), T("تيشيرت", 99.08), NL, T("15 ريال", 99.72, "p", 1.3)], out=100.48, pos=(540, TOP), size=100),
    dict(toks=[T("أو", 100.94), T("5", 101.36, "o", 1.2), T("بـ", 101.52), NL, T("69 ريال", 101.82, "p", 1.3)], out=102.8, pos=(540, TOP), size=100),
    dict(toks=[T("أطقم", 103.56), T("شبابي", 103.88), T("وولادي", 104.40, "o"), NL, T("أي", 105.22), T("طقم", 105.46), NL, T("29 ريال", 106.14, "p", 1.3)], out=106.92, pos=(540, TOP), size=100),
    dict(toks=[T("عروض", 107.56), T("على", 108.20), T("الأحذية", 108.32, "o", 1.15)], out=108.72, pos=(540, TOP), size=100),
    dict(toks=[T("أي", 109.48), T("حذاء", 109.62), NL, T("39 ريال", 111.12, "p", 1.3)], out=112.4, pos=(540, TOP), size=100),
    dict(toks=[T("أي", 114.18), T("حذاء", 114.48), NL, T("رجالي", 114.92), T("أو", 115.50), T("نسائي", 115.64, "o"), NL, T("59 ريال", 116.22, "p", 1.3)], out=117.68, pos=(540, TOP), size=100),
    dict(toks=[T("الأحذية", 118.32), T("الفخمة", 118.70, "o"), NL, T("أي", 120.58), T("حذاء", 120.80), NL, T("79 ريال", 121.48, "p", 1.3)], out=122.6, pos=(540, TOP), size=100),
    dict(toks=[T("عروض", 123.06), T("على", 123.78), T("الشرابات", 124.00, "o", 1.15)], out=124.54, pos=(540, TOP), size=100),
    dict(toks=[T("درزن", 124.56), T("12", 125.40, "o", 1.2), T("حبة", 125.60), NL, T("10 ريال", 126.12, "p", 1.3)], out=127.0, pos=(540, TOP), size=100),
    dict(toks=[T("ملوّن", 127.26, "o"), T("أسود", 127.70), T("أبيض", 128.46)], out=129.14, pos=(540, TOP), size=100),
    dict(toks=[T("موقعهم", 129.16), T("ما", 129.86), T("يضيع", 129.98, "o"), NL, T("المروج", 130.52, "o"), T("شارع", 130.84), T("البازعي", 131.10, "o")], out=131.58, pos=(540, TOP), size=100),
    dict(toks=[T("لحّقوا", 131.60), T("على", 132.20), T("العروض", 132.28, "o"), NL, T("قبل", 132.70), T("نفاد", 133.10), T("الكمية", 133.36, "o")], out=99, pos=(540, TOP), size=100),
]
IN_DUR, OUT_DUR, SLIDE = 0.18, 0.25, 70
PAD = 40

font = ImageFont.truetype(FONT, 10)
font.set_variation_by_name("Black")


def text_mask(text, size):
    f = font.font_variant(size=size)
    f.set_variation_by_name("Black")
    d = "ltr" if text[0].isdigit() or text == "+" else "rtl"
    bb = f.getbbox(text, direction=d)
    m = Image.new("L", (bb[2] - bb[0], bb[3] - bb[1]), 0)
    ImageDraw.Draw(m).text((-bb[0], -bb[1]), text, font=f, fill=255, direction=d)
    return m


def sprite(text, style, size):
    """Styled RGBA sprite: dark navy halo + white/orange fill, or an orange pill badge."""
    m = text_mask(text, size)
    if style == "p":
        px, py = int(size * 0.32), int(size * 0.2)
        fill = Image.new("RGBA", (m.width + 2 * px, m.height + 2 * py), (0, 0, 0, 0))
        ImageDraw.Draw(fill).rounded_rectangle((0, 0, fill.width - 1, fill.height - 1), radius=fill.height // 2, fill=ORANGE)
        fill.alpha_composite(Image.merge("RGBA", (*[Image.new("L", m.size, 255)] * 3, m)), (px, py))
    else:
        fill = Image.new("RGBA", m.size, (ORANGE if style == "o" else WHITE) + (0,))
        fill.putalpha(m)
        if style == "x":  # old price: white with a red strike-through
            th = max(4, size // 9)
            ImageDraw.Draw(fill).line((0, fill.height * 0.55, fill.width, fill.height * 0.45), fill=ORANGE + (255,), width=th)
    w, h = fill.width + 2 * PAD, fill.height + 2 * PAD
    a = Image.new("L", (w, h), 0)
    a.paste(fill.getchannel("A"), (PAD, PAD))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for r, k in ((16, 0.55), (4, 0.9)):  # dark halo so white/orange read on bright floors and walls
        g = a.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(r)).point(lambda v, k=k: min(255, int(v * k * 1.4)))
        halo = Image.new("RGBA", (w, h), NAVY + (0,)); halo.putalpha(g)
        out.alpha_composite(halo)
    if style != "p":  # solid dark outline: the restaurant walls are orange too
        o = a.filter(ImageFilter.MaxFilter(max(5, size // 12 * 2 + 1))).filter(ImageFilter.GaussianBlur(1.2))
        outline = Image.new("RGBA", (w, h), (12, 12, 14, 0)); outline.putalpha(o)
        out.alpha_composite(outline)
    out.alpha_composite(fill, (PAD, PAD))
    return out


def prepare(cap):
    s = cap["size"]
    lines, cur = [], []
    for text, t, col, sc, join in cap["toks"]:
        if text == "\n":
            lines.append(cur); cur = []
        else:
            cur.append(dict(t=t, join=join, im=sprite(text, col, int(s * sc))))
    lines.append(cur)
    gap = int(s * 0.22)
    def lw(ln):
        return sum(tk["im"].width - 2 * PAD for tk in ln) + sum(0 if tk["join"] else gap for tk in ln[1:])
    widths = [lw(ln) for ln in lines]
    heights = [max(tk["im"].height - 2 * PAD for tk in ln) for ln in lines]
    margin = 140
    cw = max(widths) + 2 * margin
    ch = sum(heights) + int(s * 0.05) * (len(lines) - 1) + 2 * margin
    y = margin
    placed = []
    for ln, wdt, hh in zip(lines, widths, heights):
        x = margin + (max(widths) + wdt) // 2
        for i, tk in enumerate(ln):
            if i and not tk["join"]:
                x -= gap
            iw, ih = tk["im"].width - 2 * PAD, tk["im"].height - 2 * PAD
            x -= iw
            placed.append((tk["t"], tk["im"], x - PAD, y + (hh - ih) // 2 - PAD))
        y += hh + int(s * 0.05)
    cap.update(placed=placed, cw=cw, ch=ch, start=min(p[0] for p in placed))
    a = math.radians(cap.get("angle", 0))
    c, sn = math.cos(a), math.sin(a)
    cx, cy = cw / 2, ch / 2  # inverse rotation about centre
    cap["aff"] = (c, -sn, cx - c * cx + sn * cy, sn, c, cy - sn * cx - c * cy)


def ease(p):
    p = min(max(p, 0), 1)
    return 1 - (1 - p) ** 3


def hblur(im, r):
    if r < 1:
        return im
    arr = np.asarray(im, np.float32)
    acc = np.zeros_like(arr)
    n = int(r) * 2 + 1
    for d in range(-int(r), int(r) + 1):
        acc += np.roll(arr, d, axis=1)
    return Image.fromarray((acc / n).astype(np.uint8), "RGBA")


def render_cap(cap, t):
    if t < cap["start"] or t > cap["out"] + OUT_DUR:
        return None
    canvas = Image.new("RGBA", (cap["cw"], cap["ch"]), (0, 0, 0, 0))
    for tin, im, x, y in cap["placed"]:
        if t < tin:
            continue
        p = ease((t - tin) / IN_DUR)
        spr = im
        if p < 1:
            sc = 1.12 - 0.12 * p
            spr = im.resize((int(im.width * sc), int(im.height * sc)), Image.BILINEAR)
            spr = hblur(spr, 14 * (1 - p))
            a = spr.getchannel("A").point(lambda v, p=p: int(v * p))
            spr.putalpha(a)
        dx = int(SLIDE * (1 - p))  # slides in from the right (reading direction)
        canvas.alpha_composite(spr, (x + dx - (spr.width - im.width) // 2, y - (spr.height - im.height) // 2))
    if t > cap["out"]:
        q = ease((t - cap["out"]) / OUT_DUR)
        canvas = canvas.filter(ImageFilter.GaussianBlur(8 * q))
        canvas.putalpha(canvas.getchannel("A").point(lambda v: int(v * (1 - q))))
    return canvas.transform(canvas.size, Image.AFFINE, cap["aff"], Image.BICUBIC)


def run_frames(vf, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", vf, "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)


def track():
    sw, sh = 270, 480
    win = np.outer(np.hanning(sh), np.hanning(sw))
    prev, cum, out = None, np.zeros(2), []
    for f in run_frames(f"scale={sw}:{sh}", sw, sh):
        g = f.mean(2) * win
        if prev is not None:
            R = np.fft.fft2(g) * np.conj(np.fft.fft2(prev))
            r = np.fft.ifft2(R / (np.abs(R) + 1e-9)).real
            y, x = np.unravel_index(r.argmax(), r.shape)
            if y > sh // 2: y -= sh
            if x > sw // 2: x -= sw
            d = np.array([x, y], float) * (W / sw)
            if np.hypot(*d) > 120:
                d[:] = 0
            cum = cum + d
        prev = g
        out.append(cum.copy())
    return np.array(out)


def composite(frame, t, fi, cam):
    img = Image.fromarray(frame).convert("RGBA")
    for cap in CAPS:
        lay = render_cap(cap, t)
        if lay is None:
            continue
        s0 = int(round(cap["start"] * FPS))
        off = cam[min(fi, len(cam) - 1)] - cam[min(s0, len(cam) - 1)]
        paste_clipped(img, lay, int(cap["pos"][0] - cap["cw"] / 2 + off[0]),
                      int(cap["pos"][1] - cap["ch"] / 2 + off[1]))
    return np.asarray(img.convert("RGB"))


def paste_clipped(img, lay, x, y):
    cx, cy = max(0, -x), max(0, -y)
    img.alpha_composite(lay.crop((cx, cy, lay.width, lay.height)), (x + cx, y + cy))


for c in CAPS:
    prepare(c)
cam = np.zeros((int(40 * FPS), 2))  # static tripod shot: no tracking needed

if PREVIEW:
    want = {int(t * FPS): t for t in map(float, PREVIEW.split(","))}
    for fi, f in enumerate(run_frames(f"scale={W}:{H}", W, H)):  # stream: long clips don't fit in memory
        if fi in want:
            Image.fromarray(composite(f, want[fi], fi, cam)).save(f"{OUT}_{want[fi]:.2f}.png")
        if fi >= max(want):
            break
    sys.exit()

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", SRC,
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                        "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                        "-color_trc", "bt709", "-c:a", "copy", "-movflags", "+faststart", "-shortest", OUT],
                       stdin=subprocess.PIPE)
for fi, f in enumerate(run_frames(f"scale={W}:{H}", W, H)):
    enc.stdin.write(composite(f, fi / FPS, fi, cam).tobytes())
enc.stdin.close()
enc.wait()
print("done", file=sys.stderr)
