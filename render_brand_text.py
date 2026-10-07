"""Style 2 in THMD brand colours: navy + gold bold words with a white halo, sliding in one by one, plus the logo."""
import subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONT, EMOJI = sys.argv[1:5]
LOGO = sys.argv[5]
PREVIEW = sys.argv[6] if len(sys.argv) > 6 else None
W, H, FPS = 1080, 1920, 30
NAVY, GOLD = (30, 50, 84), (178, 132, 58)

# token: (text, t_in, color, scale, join)   "\n" = new line, join=True -> no gap before it
def T(text, t, c="w", s=1.0, join=False):
    return (text, t, GOLD if c == "g" else NAVY, s, join)

NL = ("\n", 0, None, 1, False)
CAPS = [
    dict(toks=[T("الكحل", 0.84), T("أو", 1.20), T("الأثمد", 1.36, "g", 1.15)], out=2.62,
         pos=(540, 1330), size=104, angle=-4),
    dict(toks=[T("أمر", 2.76), T("محرج؟", 2.96, "g", 1.2)], out=3.38,
         pos=(540, 1330), size=110, angle=-4),
    dict(toks=[T("عيوننا", 3.62), T("يومياً", 4.22), NL, T("ترهق", 4.80, "g", 1.25)], out=5.30,
         pos=(540, 1350), size=104, angle=4),
    dict(toks=[T("من", 5.22), T("الشاشات", 5.40), NL, T("والجوالات", 6.04, "g", 1.15)], out=6.58,
         pos=(540, 1350), size=104, angle=-4),
    dict(toks=[T("قال", 6.82), T("النبي", 6.95), NL, T("صلى", 7.08, s=0.7), T("الله", 7.28, s=0.7),
               T("عليه", 7.46, s=0.7), T("وسلم", 7.60, s=0.7)], out=8.55,
         pos=(540, 1350), size=110, angle=-3),
    dict(toks=[T("اكتحلوا", 8.68), T("بالإثمد", 8.85, "g", 1.15), NL, T("فإنه", 9.10), T("يجلو", 9.76),
               T("البصر", 10.00, "g", 1.15)], out=10.55,
         pos=(540, 1560), size=100, angle=-3),
    dict(toks=[T("وينبت", 10.64), T("الشعر", 11.02, "g", 1.15)], out=11.40,
         pos=(540, 1350), size=104, angle=-3),
    dict(toks=[T("مو", 11.48), T("لازم", 11.72), NL, T("تطلع", 11.88), T("فيه", 12.16), T("برا", 12.28, "g")], out=12.72,
         pos=(540, 1350), size=100, angle=4),
    dict(toks=[T("استخدمه", 12.76), NL, T("قبل", 13.20, "g", 1.15), T("النوم", 13.34, "g", 1.15)], out=14.34,
         pos=(540, 1350), size=104, angle=-4),
    dict(toks=[T("فعل", 14.78), T("النبي", 14.96, "g", 1.15), NL, T("صلى", 15.26, s=0.7), T("الله", 15.44, s=0.7),
               T("عليه", 15.74, s=0.7), T("وسلم", 15.94, s=0.7)], out=16.24,
         pos=(540, 1350), size=108, angle=3),
    dict(toks=[T("والأهم", 16.28, "g", 1.1)], out=17.25,
         pos=(540, 1350), size=108, angle=-3),
    dict(toks=[T("مفحوص", 17.34), T("ومضمون", 17.86), NL, T("وخالي", 18.30), T("من", 18.66),
               T("الرصاص", 18.78, "g", 1.15)], out=19.62,
         pos=(540, 1400), size=100, angle=-4),
    dict(toks=[T("جرّب", 19.66), T("وشوف", 20.42), NL, T("الفرق", 20.76, "g", 1.3)], out=21.18,
         pos=(540, 1400), size=104, angle=4),
    dict(toks=[T("كحل", 21.54), T("الأثمد", 21.84), T("الأصلي", 22.20), NL, T("وين", 22.68), T("تحصله؟", 22.94, "g", 1.2)],
         out=23.38, pos=(540, 1400), size=96, angle=-3),
    dict(toks=[T("متجر", 24.26), T("ثمد", 24.64, "g", 1.25)], out=25.0,
         pos=(540, 400), size=120, angle=-3),
    dict(toks=[T("وما", 30.36), T("راح", 31.06), T("يقصرون", 31.26), T("معكم", 31.64, "g", 1.1)], out=99,
         pos=(540, 1760), size=88, angle=-3),
]
LOGO_IN, LOGO_POS, LOGO_W = 24.95, (540, 360), 330
IN_DUR, OUT_DUR, SLIDE = 0.18, 0.25, 70
PAD = 40

font = ImageFont.truetype(FONT, 10)
font.set_variation_by_name("Black")
efont = ImageFont.truetype(EMOJI, 109)


def sprite(text, color, size):
    """Styled RGBA sprite: white halo + solid fill."""
    if ord(text[0]) >= 0x1F000:  # emoji
        im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), text, font=efont, embedded_color=True)
        im = im.crop(im.getbbox())
        k = size / im.height
        fill = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    else:
        f = font.font_variant(size=size)
        f.set_variation_by_name("Black")
        d = "ltr" if text[0].isdigit() else "rtl"
        bb = f.getbbox(text, direction=d)
        m = Image.new("L", (bb[2] - bb[0], bb[3] - bb[1]), 0)
        ImageDraw.Draw(m).text((-bb[0], -bb[1]), text, font=f, fill=255, direction=d)
        fill = Image.new("RGBA", m.size, color + (0,))
        fill.putalpha(m)
    w, h = fill.width + 2 * PAD, fill.height + 2 * PAD
    a = Image.new("L", (w, h), 0)
    a.paste(fill.getchannel("A"), (PAD, PAD))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for r, k in ((16, 0.65), (5, 1.0)):  # white halo so navy/gold read on any background
        g = a.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(r)).point(lambda v, k=k: min(255, int(v * k * 1.6)))
        halo = Image.new("RGBA", (w, h), (255, 255, 255, 0)); halo.putalpha(g)
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
    a = math.radians(cap["angle"])
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
    if t >= LOGO_IN:
        p = ease((t - LOGO_IN) / 0.35)
        lw = int(LOGO_W * (0.8 + 0.2 * p))
        lg = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
        if p < 1:
            lg = lg.filter(ImageFilter.GaussianBlur(8 * (1 - p)))
            lg.putalpha(lg.getchannel("A").point(lambda v: int(v * p)))
        paste_clipped(img, lg, LOGO_POS[0] - lg.width // 2, LOGO_POS[1] - lg.height // 2)
    return np.asarray(img.convert("RGB"))


def make_logo(path):
    lg = Image.open(path).convert("RGBA")
    m = 60
    w, h = lg.width + 2 * m, lg.height + 2 * m
    a = Image.new("L", (w, h), 0); a.paste(lg.getchannel("A"), (m, m))
    out = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    for r, k in ((40, 0.8), (12, 1.0)):
        g = a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(r)).point(lambda v, k=k: min(255, int(v * k * 1.8)))
        halo = Image.new("RGBA", (w, h), (255, 255, 255, 0)); halo.putalpha(g)
        out.alpha_composite(halo)
    out.alpha_composite(lg, (m, m))
    return out


def paste_clipped(img, lay, x, y):
    cx, cy = max(0, -x), max(0, -y)
    img.alpha_composite(lay.crop((cx, cy, lay.width, lay.height)), (x + cx, y + cy))


for c in CAPS:
    prepare(c)
cam = np.zeros((int(40 * FPS), 2))  # static tripod shot: no tracking needed
logo = make_logo(LOGO)

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
