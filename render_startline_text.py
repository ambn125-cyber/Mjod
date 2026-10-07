"""Style 2 in Start Line colours: white + orange bold words with a dark halo, orange pill badges for the offers."""
import subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONT = sys.argv[1:4]
PREVIEW = sys.argv[4] if len(sys.argv) > 4 else None
W, H, FPS = 1080, 1920, 30
WHITE, ORANGE, NAVY = (255, 255, 255), (246, 104, 38), (8, 22, 34)

# token: (text, t_in, color, scale, join)   "\n" = new line, join=True -> no gap before it
def T(text, t, c="w", s=1.0, join=False):
    return (text, t, c, s, join)  # c: "w" white, "o" orange, "p" orange pill

NL = ("\n", 0, None, 1, False)
Y = 1460
CAPS = [
    dict(toks=[T("ستارت", 0.10, "o", 1.15), T("لاين", 0.66, "o", 1.15), T("يقول", 0.88), NL,
               T("غيّر", 1.10), T("زيت", 1.44), T("سيارتك", 1.70)], out=2.30, pos=(540, Y), size=100),
    dict(toks=[T("والغسيل", 2.24), T("علينا", 2.80, "p", 1.1)], out=3.48, pos=(540, Y), size=104),
    dict(toks=[T("غيّر", 3.54), T("الزيت", 3.86), T("+", 4.60, "o"), T("السيفون", 4.60), NL,
               T("+", 5.14, "o"), T("فلتر", 5.14), T("الهواء", 5.64)], out=5.92, pos=(540, Y), size=96),
    dict(toks=[T("وغسيل", 5.96), T("السيارة", 6.24), NL, T("مجاناً", 6.82, "p", 1.35)], out=7.20, pos=(540, Y), size=100),
    dict(toks=[T("لو", 7.26), T("غيّرت", 7.38), T("الزيت", 7.74), T("+", 8.02, "o"), T("السيفون", 8.02)], out=8.70,
         pos=(540, Y - 120), size=92),
    dict(toks=[T("خصم 50%", 8.76, "p", 1.3), NL, T("على", 9.68), T("الغسيل", 9.80, "o")],
         out=10.62, pos=(540, Y), size=104),
    dict(toks=[T("قسم", 11.44), T("غسيل", 11.68, "o"), T("السيارات", 12.02, "o")], out=12.78, pos=(540, 560), size=104),
    dict(toks=[T("استراحة", 13.54), T("خاصة", 13.98), NL, T("للنساء", 14.36, "o"), T("والرجال", 14.90, "o")], out=15.44,
         pos=(540, 560), size=104),
    dict(toks=[T("خدمات", 16.54), T("أخرى", 17.00, "o", 1.15)], out=17.48, pos=(540, 560), size=110),
    dict(toks=[T("تابع", 17.96), T("سيارتك", 18.28), NL, T("وأنت", 18.90), T("مرتاح", 19.10, "o", 1.2)], out=19.64,
         pos=(540, 600), size=104),
    dict(toks=[T("موقعهم", 20.14), T("ما", 20.60), T("يضيع", 20.68, "o"), NL,
               T("مقابل", 21.00), T("إدارة", 21.32), T("التعليم", 21.62, "o")], out=22.26, pos=(540, 560), size=96),
    dict(toks=[T("ابحث", 22.28), T("في", 22.50), T("قوقل", 22.62), T("ماب", 22.88), NL,
               T("ستارت لاين", 23.14, "p", 1.3)], out=99, pos=(540, 1450), size=92),
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
