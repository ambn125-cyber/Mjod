import subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
SRC, OUT, FONTS = sys.argv[1:4]; PREV = [float(x) for x in sys.argv[4:]]
T0, T1, FPS, W, H = 4.36, 6.80, 30, 1080, 1920
NAVY, BLUE, WHITE = (14, 52, 96), (51, 166, 213), (255, 255, 255)
CY = 1240
def stamp():
    fb = ImageFont.truetype(FONTS + "/Lalezar-Regular.ttf", 300)
    fs = ImageFont.truetype(FONTS + "/Tajawal-Black.ttf", 96)
    num = "‎50%‎"
    nb = fb.getbbox(num); sb = fs.getbbox("خصم", direction="rtl")
    bw = max(nb[2] - nb[0], sb[2] - sb[0]) + 140; bh = 640
    S = 40; im = Image.new("RGBA", (bw + 2 * S, bh + 2 * S), (0, 0, 0, 0))
    sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).rounded_rectangle((S, S + 14, S + bw, S + bh + 14), 60, fill=150)
    im.putalpha(sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((S, S, S + bw, S + bh), 60, fill=NAVY + (255,), outline=BLUE + (255,), width=14)
    d.rounded_rectangle((S + 26, S + 26, S + bw - 26, S + bh - 26), 42, outline=WHITE + (255,), width=4)
    cx = S + bw / 2
    d.text((cx, S + 120), "خصم", font=fs, fill=BLUE + (255,), anchor="mm", direction="rtl")
    d.text((cx, S + 330), num, font=fb, fill=WHITE + (255,), anchor="mm")
    return im
def stamp2():
    im = stamp(); d = ImageDraw.Draw(im)
    f2 = ImageFont.truetype(FONTS + "/Tajawal-Black.ttf", 64)
    d.text((im.width / 2, 40 + 545), "على جميع المنتجات", font=f2, fill=WHITE + (255,), anchor="mm", direction="rtl")
    return im
ST, ST2 = stamp(), stamp2()
def comp(fr, t):
    p = (t - T0) / 0.22
    if p < 0: return fr
    if p < 1: s, a = 1.7 - 0.75 * p, p          # slam in
    elif p < 1.6: s, a = 0.95 + 0.05 * (p - 1) / 0.6, 1
    else: s, a = 1.0, 1
    if t > T1 - 0.18: a = max(0, (T1 - t) / 0.18)
    src = ST2 if t >= 5.36 else ST
    sp = src.resize((int(src.width * s), int(src.height * s)), Image.BILINEAR)
    if a < 1: sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
    fr.alpha_composite(sp, (int(W / 2 - sp.width / 2), int(CY - sp.height / 2)))
    return fr
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(T0), "-t", str(T1 - T0), "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
N = int(round((T1 - T0) * FPS))
if PREV:
    want = {int(round((t - T0) * FPS)): t for t in PREV}
    for i in range(N):
        b = dec.stdout.read(W * H * 3)
        if i in want: comp(Image.frombytes("RGB", (W, H), b).convert("RGBA"), want[i]).convert("RGB").save(f"{OUT}_{want[i]}.png")
    dec.kill(); sys.exit()
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30", "-i", "-",
    "-filter_complex", f"[1:v]setpts=PTS-STARTPTS+{T0}/TB[o];[0:v][o]overlay=eof_action=pass:enable='between(t,{T0},{T1 - 0.001})'[v]",
    "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", OUT], stdin=subprocess.PIPE)
last = None
for i in range(N):
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: b = last
    last = b
    enc.stdin.write(comp(Image.frombytes("RGB", (W, H), b).convert("RGBA"), T0 + i / FPS).convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); dec.kill()
