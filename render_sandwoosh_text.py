"""Style 2 for Sandwoosh (orange/black brand): white + orange bold words with a dark halo, orange pill badges for the offers."""
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
TOP, LOW = 380, 1450
CAPS = [
    dict(toks=[T("اليوم", 0.05), T("الافتتاح", 0.48), T("الرسمي", 0.84), NL, T("مطعم سندووش", 1.16, "p", 1.25)],
         out=2.20, pos=(540, LOW), size=96),
    dict(toks=[T("سندويشات", 3.14), T("فطور", 3.56, "o"), NL, T("ووجبات", 3.96, "o")], out=4.90, pos=(540, LOW), size=104),
    dict(toks=[T("المنيو", 4.94), T("مليان", 5.70), NL, T("أصناف", 6.00, "o", 1.25)], out=6.44, pos=(540, TOP), size=104),
    dict(toks=[T("لا", 6.60), T("يفوتك", 6.66), NL, T("كلوب", 7.02, "o"), T("ساندوتش", 7.28, "o")], out=8.02,
         pos=(540, 300), size=100),
    dict(toks=[T("والتورتيلا", 8.06), NL, T("العربية", 8.70, "o", 1.15)], out=9.14, pos=(540, 300), size=100),
    dict(toks=[T("برجر", 9.92), T("دجاج", 10.24, "o", 1.15)], out=11.25, pos=(540, TOP), size=112),
    dict(toks=[T("مشروبات", 12.60), NL, T("طبيعية", 13.18, "o", 1.2)], out=13.95, pos=(540, TOP), size=108),
    dict(toks=[T("لا", 13.80), T("يفوتكم", 14.16), NL, T("برجر دجاج كريسبي", 15.26, "p", 1.1)], out=16.40,
         pos=(540, TOP), size=96),
    dict(toks=[T("والطعم", 20.12), T("رهيب", 20.26, "o", 1.3)], out=21.15, pos=(540, TOP), size=108),
    dict(toks=[T("تبي", 21.54), T("قهوة؟", 22.22, "o", 1.2), NL, T("متوفرة", 22.72), T("عندهم", 23.10)], out=23.90,
         pos=(540, TOP), size=100),
    dict(toks=[T("موقعهم", 24.32), T("ما", 24.70), T("يضيع", 24.84, "o"), NL, T("شارع", 25.48), T("البازعي", 25.78, "o")],
         out=26.28, pos=(540, TOP), size=98),
    dict(toks=[T("اكتب", 26.30), T("في", 26.74), T("قوقل", 26.84), T("ماب", 27.02), NL,
               T("مطعم سندووش", 27.28, "p", 1.3)], out=99, pos=(540, 360), size=92),
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
