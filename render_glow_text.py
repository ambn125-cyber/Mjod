import subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

SRC = sys.argv[1]
OUT = sys.argv[2]
FONT = sys.argv[3]
W, H, FPS = 1080, 1920, 30
PREVIEW = len(sys.argv) > 4  # render only a few stills

# ---------- captions: words (text, t_in), "\n" = new line ----------
CAPS = [
    dict(words=[("يا", 0.05), ("هل", 0.40), ("تبوك", 0.72)], out=2.85,
         pos=(290, 620), size=124, angle=7, tilt=0.86),
    dict(words=[("موعدنا", 0.98), ("\n", 0), ("29/10", 1.98)], out=2.85,
         pos=(360, 1420), size=118, angle=-9, tilt=0.86),
    dict(words=[("قاعة", 3.30), ("تركواز", 3.62)], out=4.45,
         pos=(330, 1180), size=118, angle=-6, tilt=0.88),
    dict(words=[("أكبر", 4.58), ("معرض", 5.14), ("\n", 0), ("للعطور", 5.48), ("والبخور", 6.02)], out=6.38,
         pos=(540, 1520), size=110, angle=-7, tilt=0.86),
    dict(words=[("دلّع", 7.06), ("\n", 0), ("نفسك", 7.52)], out=9.75,
         pos=(215, 1180), size=124, angle=-8, tilt=0.88),
    dict(words=[("بالعطور", 7.80), ("والعروض", 8.38), ("\n", 0), ("والفخامة", 8.90)], out=9.75,
         pos=(560, 1670), size=104, angle=-6, tilt=0.84),
    dict(words=[("قاعة", 10.94), ("\n", 0), ("تركواز", 11.10)], out=99,
         pos=(215, 1180), size=118, angle=-8, tilt=0.88),
    dict(words=[("لمدة", 11.72), ("10", 12.10), ("أيام", 12.36), ("\n", 0), ("من", 12.60), ("29/10", 12.90)], out=99,
         pos=(560, 1670), size=104, angle=-6, tilt=0.84),
]
IN_DUR, OUT_DUR = 0.22, 0.30
WORD_GAP, LINE_GAP = 0.28, 1.12


def run_frames(vf, w, h):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", vf, "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)


# ---------- simple camera tracking (phase correlation, translation only) ----------
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
            if np.hypot(*d) > 120:  # scene cut -> ignore
                d[:] = 0
            cum = cum + d
        prev = g
        out.append(cum.copy())
    return np.array(out)


font = ImageFont.truetype(FONT, 10)


def word_img(text, size):
    f = font.font_variant(size=size)
    direction = "ltr" if text[0].isdigit() else "rtl"
    bb = f.getbbox(text, direction=direction)
    im = Image.new("L", (bb[2] - bb[0] + 4, size + size // 2), 0)
    ImageDraw.Draw(im).text((2 - bb[0], size // 6), text, font=f, fill=255, direction=direction)
    return im


def prepare(cap):
    s = cap["size"]
    lines, cur = [], []
    for t, tin in cap["words"]:
        if t == "\n":
            lines.append(cur); cur = []
        else:
            cur.append((t, tin, word_img(t, s)))
    lines.append(cur)
    gap = int(s * WORD_GAP)
    lh = int(s * LINE_GAP)
    widths = [sum(w[2].width for w in ln) + gap * (len(ln) - 1) for ln in lines]
    pad = 90
    cw = max(widths) + 2 * pad
    ch = lh * (len(lines) - 1) + lines[0][0][2].height + 2 * pad
    placed = []
    for i, ln in enumerate(lines):
        x = pad + (max(widths) + widths[i]) // 2  # right edge, centered line, RTL
        for t, tin, im in ln:
            x -= im.width
            placed.append((tin, im, x, pad + i * lh))
            x -= gap
    cap["placed"], cap["cw"], cap["ch"] = placed, cw, ch
    cap["start"] = min(p[0] for p in placed)
    cap["coeffs"] = persp(cw, ch, cap["angle"], cap["tilt"])


def persp(w, h, angle, tilt):
    # destination quad: top edge narrower (text lies back into the scene), then rotated
    cx, cy = w / 2, h / 2
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    dst = [(-w / 2 * tilt, -h / 2), (w / 2 * tilt, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    a = math.radians(-angle)
    dst = [(cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)) for x, y in dst]
    A, B = [], []
    for (X, Y), (x, y) in zip(dst, src):  # map output (dst) -> input (src)
        A.append([X, Y, 1, 0, 0, 0, -x * X, -x * Y]); B.append(x)
        A.append([0, 0, 0, X, Y, 1, -y * X, -y * Y]); B.append(y)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def ease(p):
    p = min(max(p, 0), 1)
    return 1 - (1 - p) ** 3


def render_cap(cap, t):
    if t < cap["start"] or t > cap["out"] + OUT_DUR:
        return None
    mask = Image.new("L", (cap["cw"], cap["ch"]), 0)
    for tin, im, x, y in cap["placed"]:
        if t < tin:
            continue
        p = ease((t - tin) / IN_DUR)
        sc = 1.25 - 0.25 * p
        wi = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
        if p < 1:
            wi = wi.filter(ImageFilter.GaussianBlur(6 * (1 - p)))
            wi = wi.point(lambda v, p=p: int(v * p))
        ox = x + (im.width - wi.width) // 2
        oy = y + (im.height - wi.height) // 2
        mask.paste(ImageChops.lighter(mask.crop((ox, oy, ox + wi.width, oy + wi.height)), wi), (ox, oy))
    fade = 1.0
    if t > cap["out"]:
        q = ease((t - cap["out"]) / OUT_DUR)
        mask = mask.filter(ImageFilter.GaussianBlur(10 * q))
        fade = 1 - q
    m = np.asarray(mask, np.float32) / 255
    g1 = np.asarray(mask.filter(ImageFilter.GaussianBlur(9)), np.float32) / 255
    g2 = np.asarray(mask.filter(ImageFilter.GaussianBlur(26)), np.float32) / 255
    sh = np.asarray(mask.filter(ImageFilter.GaussianBlur(14)), np.float32) / 255
    # premultiplied: white text + white glow, over a soft dark shadow for bright scenes
    glow = np.clip(m + 0.9 * g1 + 0.65 * g2, 0, 1)
    shadow = np.clip(sh * 0.45, 0, 1)
    alpha = np.clip(glow + shadow * (1 - glow), 0, 1) * fade
    color = np.clip(glow, 0, 1) * fade  # premultiplied white amount
    layer = np.dstack([color, alpha])
    rgba = Image.fromarray((layer * 255).astype(np.uint8)[:, :, [0, 0, 0, 1]], "RGBA")
    return rgba.transform(rgba.size, Image.PERSPECTIVE, cap["coeffs"], Image.BICUBIC)


def composite(frame, t, fi, cam):
    out = frame.astype(np.float32) / 255
    for cap in CAPS:
        lay = render_cap(cap, t)
        if lay is None:
            continue
        s0 = int(round(cap["start"] * FPS))
        off = cam[min(fi, len(cam) - 1)] - cam[min(s0, len(cam) - 1)]
        x0 = int(cap["pos"][0] - cap["cw"] / 2 + off[0])
        y0 = int(cap["pos"][1] - cap["ch"] / 2 + off[1])
        L = np.asarray(lay, np.float32) / 255
        xs, ys = max(x0, 0), max(y0, 0)
        xe, ye = min(x0 + lay.width, W), min(y0 + lay.height, H)
        if xe <= xs or ye <= ys:
            continue
        l = L[ys - y0:ye - y0, xs - x0:xe - x0]
        a = l[:, :, 3:4]
        out[ys:ye, xs:xe] = l[:, :, :3] + out[ys:ye, xs:xe] * (1 - a)
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


for c in CAPS:
    prepare(c)
cam = track()
print("tracked", len(cam), "frames; drift range", cam.min(0), cam.max(0), file=sys.stderr)

if PREVIEW:
    times = [float(x) for x in sys.argv[4].split(",")]
    frames = list(run_frames(f"scale={W}:{H}", W, H))
    for t in times:
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
