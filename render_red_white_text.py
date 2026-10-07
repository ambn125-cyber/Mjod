"""Style 2: white + red bold words that slide in one by one, stuck to the scene."""
import subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONT, EMOJI = sys.argv[1:5]
PREVIEW = sys.argv[5] if len(sys.argv) > 5 else None
W, H, FPS = 1080, 1920, 30
WHITE, RED = (255, 255, 255), (232, 20, 28)

# token: (text, t_in, color, scale, join)   "\n" = new line, join=True -> no gap before it
def T(text, t, c="w", s=1.0, join=False):
    return (text, t, RED if c == "r" else WHITE, s, join)

NL = ("\n", 0, None, 1, False)
CAPS = [
    dict(toks=[T("يا", 0.05), T("هل", 0.40), T("تبوك", 0.72, "r", 1.15)], out=2.85,
         pos=(370, 640), size=104, angle=6),
    dict(toks=[T("موعدنا", 0.98), NL, T("29/10", 1.98, "r", 1.45)], out=2.85,
         pos=(330, 1400), size=110, angle=-8),
    dict(toks=[T("قاعة", 3.30), T("تركواز", 3.62, "r", 1.1)], out=4.45,
         pos=(390, 1180), size=104, angle=-5),
    dict(toks=[T("أكبر", 4.58), T("معرض", 5.14), NL, T("للعطور", 5.48, "r"), T("والبخور", 6.02, "r")], out=6.38,
         pos=(540, 1520), size=104, angle=-6),
    dict(toks=[T("دلّع", 7.06), NL, T("نفسك", 7.52, "r", 1.1)], out=9.75,
         pos=(235, 1180), size=112, angle=-7),
    dict(toks=[T("بالعطور", 7.80), T("والعروض", 8.38), NL,
               T("والفخـ", 8.90, "r"), T("👑", 8.90, s=0.85, join=True), T("ـامة", 8.90, "r", join=True)],
         out=9.75, pos=(560, 1670), size=100, angle=-5),
    dict(toks=[T("قاعة", 10.94), NL, T("تركواز", 11.10, "r", 1.1)], out=99,
         pos=(235, 1180), size=108, angle=-7),
    dict(toks=[T("لمدة", 11.72), T("10", 12.10, "r", 1.5), T("أيام", 12.36), NL,
               T("من", 12.60), T("29/10", 12.90, "r", 1.3)], out=99,
         pos=(560, 1670), size=100, angle=-5),
]
IN_DUR, OUT_DUR, SLIDE = 0.18, 0.25, 70
PAD = 40

font = ImageFont.truetype(FONT, 10)
font.set_variation_by_name("Black")
efont = ImageFont.truetype(EMOJI, 109)


def sprite(text, color, size):
    """Styled RGBA sprite: soft dark shadow + colour halo + solid fill."""
    if not text[0].isalpha() and not text[0].isdigit() and text[0] not in "ـ":
        im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), text, font=efont, embedded_color=True)
        im = im.crop(im.getbbox())
        k = size / im.height
        fill = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
        glow_col = None
    else:
        f = font.font_variant(size=size)
        f.set_variation_by_name("Black")
        d = "ltr" if text[0].isdigit() else "rtl"
        bb = f.getbbox(text, direction=d)
        m = Image.new("L", (bb[2] - bb[0], bb[3] - bb[1]), 0)
        ImageDraw.Draw(m).text((-bb[0], -bb[1]), text, font=f, fill=255, direction=d)
        fill = Image.new("RGBA", m.size, color + (0,))
        fill.putalpha(m)
        glow_col = color
    w, h = fill.width + 2 * PAD, fill.height + 2 * PAD
    a = Image.new("L", (w, h), 0)
    a.paste(fill.getchannel("A"), (PAD, PAD))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = a.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.6))
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0)); shadow.putalpha(sh)
    out.alpha_composite(shadow.transform((w, h), Image.AFFINE, (1, 0, -4, 0, 1, -6)))  # offset down-right
    if glow_col:
        g = a.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * (0.55 if glow_col == RED else 0.25)))
        gl = Image.new("RGBA", (w, h), glow_col + (0,)); gl.putalpha(g)
        out.alpha_composite(gl)
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
    return np.asarray(img.convert("RGB"))


def paste_clipped(img, lay, x, y):
    cx, cy = max(0, -x), max(0, -y)
    img.alpha_composite(lay.crop((cx, cy, lay.width, lay.height)), (x + cx, y + cy))


for c in CAPS:
    prepare(c)
cam = track()

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
