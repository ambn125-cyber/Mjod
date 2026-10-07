"""Style 2 for Saat Istirkha (green/white brand): white + orange bold words with a dark halo, orange pill badges for the offers."""
import subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONT = sys.argv[1:4]
PREVIEW = sys.argv[4] if len(sys.argv) > 4 else None
W, H, FPS = 1080, 1920, 30
WHITE, ORANGE, NAVY = (255, 255, 255), (34, 196, 92), (8, 22, 14)  # ORANGE slot = brand green

# token: (text, t_in, color, scale, join)   "\n" = new line, join=True -> no gap before it
def T(text, t, c="w", s=1.0, join=False):
    return (text, t, c, s, join)  # c: "w" white, "o" orange, "p" orange pill

NL = ("\n", 0, None, 1, False)
TOP, MID, LOW = 400, 1300, 1450
CAPS = [
    dict(toks=[T("بمناسبة", 0.02), T("فوز", 0.46), NL, T("منتخبنا", 0.70, "o"), T("السعودي", 1.26, "o")], out=1.64,
         pos=(540, LOW), size=100),
    dict(toks=[T("بكأس", 1.68), T("الخليج", 1.94, "o", 1.2)], out=2.45, pos=(540, LOW), size=104),
    dict(toks=[T("ساعة استرخاء", 2.80, "p", 1.2), NL, T("إيش", 3.44), T("قدّم", 3.62), T("لكم؟", 3.88, "o")], out=4.12,
         pos=(540, LOW), size=96),
    dict(toks=[T("خصم 30%", 4.86, "p", 1.45), NL, T("على", 5.72), T("جميع", 5.92), T("خدمات", 6.20), T("السبا", 6.62, "o")],
         out=6.90, pos=(540, LOW), size=92),
    dict(toks=[T("وحرق", 6.94), T("الأسعار", 7.48, "o", 1.2)], out=8.15, pos=(540, LOW), size=104),
    dict(toks=[T("عروض", 9.40), T("السبا", 9.66, "o"), NL, T("المميزة", 10.02, "o")], out=10.62, pos=(540, LOW), size=104),
    dict(toks=[T("جلسة", 10.84), T("المساج", 11.14, "o"), NL, T("75 ريال", 11.80, "p", 1.2)], out=12.58, pos=(540, LOW), size=100),
    dict(toks=[T("الحمام", 12.60), T("المغربي", 13.04, "o"), NL, T("75 ريال", 13.76, "p", 1.2)], out=14.60, pos=(540, LOW), size=100),
    dict(toks=[T("المنكير", 14.64), T("والبدكير", 15.06, "o"), NL, T("75 ريال", 15.76, "p", 1.2)], out=16.46,
         pos=(540, LOW), size=100),
    dict(toks=[T("باقة", 17.86), T("راحة", 18.02, "o"), T("الملوك", 18.30, "o"), NL,
               T("بدكير", 18.84), T("+", 19.68, "o"), T("مساج", 19.68), T("+", 20.40, "o"), T("حمام", 20.40), NL,
               T("220 ريال", 20.94, "p", 1.3)], out=22.00, pos=(540, MID + 80), size=92),
    dict(toks=[T("وبالنسبة", 22.04), T("للحلاقة", 22.84, "o"), NL, T("ركّزوا", 23.36), T("معي", 23.96)], out=24.12,
         pos=(540, LOW), size=100),
    dict(toks=[T("باقة أبطال الأخضر", 24.42, "p", 1.1), NL, T("حلاقة", 25.84), T("شعر", 26.18), T("ودقن", 26.56), NL,
               T("بخار", 27.06), T("+", 27.56, "o"), T("قناع", 27.56), T("+", 27.98, "o"), T("لصقات", 27.98), T("أنف", 28.32), NL,
               T("60 ريال", 28.64, "p", 1.2)], out=29.02, pos=(540, MID), size=84),
    dict(toks=[T("أو", 29.04, "o"), T("حلاقة", 29.10), T("شعر", 29.48), T("ودقن", 29.88), NL,
               T("3", 30.32, "o"), T("أنواع", 30.62), T("صنفرة", 30.82), T("بالبخار", 31.14), NL,
               T("حمام", 31.68), T("زيت", 31.98), T("+", 32.26, "o"), T("لصقات", 32.26), T("أنف", 32.70), NL,
               T("60 ريال", 33.64, "p", 1.2)], out=34.26, pos=(540, MID), size=84),
    dict(toks=[T("باقة الملوك", 35.06, "p", 1.2), NL, T("تنظيف", 35.74), T("بشرة", 35.94), T("بالهيدرافيشل", 36.28, "o"), NL,
               T("+", 36.98, "o"), T("تنظيف", 36.98), T("فروة", 37.32), T("الرأس", 37.62)], out=37.88, pos=(540, MID), size=88),
    dict(toks=[T("حلاقة", 37.92), T("شعر", 38.24), T("ودقن", 38.58), NL, T("+", 38.90, "o"), T("جهاز", 38.90), T("ليزر", 39.24, "o"), NL,
               T("99 ريال", 39.66, "p", 1.25)], out=40.80, pos=(540, MID), size=92),
    dict(toks=[T("دلّع", 41.36), T("نفسك", 41.62, "o"), NL, T("باقة الأخضر", 42.38, "p", 1.2)], out=43.00, pos=(540, LOW), size=100),
    dict(toks=[T("حلاقة", 43.02), T("شعر", 43.28), T("ودقن", 43.70), NL, T("3", 44.12, "o"), T("أنواع", 44.40), T("صنفرة", 44.62),
               T("بالبخار", 44.90), NL, T("حمام", 45.46), T("زيت", 45.82), T("+", 46.12, "o"), T("لصقات", 46.12), T("أنف", 46.56)],
         out=46.86, pos=(540, MID), size=86),
    dict(toks=[T("تنظيف", 46.88), T("فروة", 47.22), T("الرأس", 47.46), NL, T("+", 47.78, "o"), T("حلاقة", 47.78), T("شعر", 48.22),
               T("ودقن", 48.52), NL, T("85 ريال", 48.86, "p", 1.25)], out=50.04, pos=(540, MID), size=88),
    dict(toks=[T("غرفة", 51.14), T("VIP", 51.42, "o", 1.15)], out=51.98, pos=(540, LOW), size=108),
    dict(toks=[T("وسويت", 52.78), T("خاص", 53.14, "o"), NL, T("فيه", 54.02), T("جميع", 54.16), T("الخدمات", 54.38, "o")], out=55.58,
         pos=(540, LOW), size=98),
    dict(toks=[T("العرض", 56.86), T("مستمر", 57.22), NL, T("لمدة أسبوعين", 57.58, "p", 1.2)], out=58.48, pos=(540, LOW), size=100),
    dict(toks=[T("اكتب", 58.73), T("في", 58.86), T("قوقل", 58.90), T("ماب", 59.16), NL, T("ساعة استرخاء", 59.40, "p", 1.3), NL,
               T("موقعهم", 61.32), T("في", 61.70), T("العليا", 61.84, "o")], out=99, pos=(540, MID), size=90),
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
    frames = list(run_frames(f"scale={W}:{H}", W, H))
    for t in map(float, PREVIEW.split(",")):
        fi = int(t * FPS)
        Image.fromarray(composite(frames[fi], t, fi, cam)).save(f"{OUT}_{t:.2f}.png")
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
