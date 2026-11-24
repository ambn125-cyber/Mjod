"""Replace the room behind a seated presenter with a brand studio backdrop.
keep = person (rembg u2net_human_seg) ∪ dark furniture (table/chair: low luma), cleaned + feathered.
usage: python3 -I bgswap.py src.mp4 out.mp4 [preview_times]   env BG=path.png (1080x1920) or BG_A/BG_B colours"""
import os, sys, subprocess
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from rembg import remove, new_session
SRC, OUT = sys.argv[1:3]; PREV = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
W, H = 1080, 1920; FPS = 30
LUMA = int(os.environ.get("LUMA", "135")); SAT = float(os.environ.get("SAT", "0.28")); MINAREA = int(os.environ.get("MINAREA", "25000"))
ses = new_session("u2net_human_seg")


def backdrop():
    if os.environ.get("BG"): return Image.open(os.environ["BG"]).convert("RGB").resize((W, H))
    a = np.array([60, 20, 110], float); b = np.array([215, 70, 170], float)
    y = np.linspace(0, 1, H)[:, None]; x = np.linspace(-1, 1, W)[None, :]
    r = np.sqrt((x * 0.9) ** 2 + ((y - 0.42) * 1.6) ** 2)
    glow = np.clip(1 - r, 0, 1) ** 1.6
    base = a[None, None] * (1 - glow[..., None]) + b[None, None] * glow[..., None]
    floor = np.clip((y - 0.62) / 0.38, 0, 1)[..., None]            # darker seamless floor
    base = base * (1 - 0.45 * floor)
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    # soft logo-ish light streaks
    ov = Image.new("L", (W, H), 0); d = ImageDraw.Draw(ov)
    for i, xx in enumerate((120, 960)): d.rectangle((xx - 18, 120, xx + 18, 1150), fill=120)
    img = Image.composite(Image.new("RGB", (W, H), (255, 170, 240)), img, ov.filter(ImageFilter.GaussianBlur(40)))
    return img


BGI = backdrop()


def frame(im):
    import cv2
    m = np.asarray(remove(im, session=ses, only_mask=True)).astype(np.float32) / 255
    a = np.asarray(im).astype(np.float32)
    mx, mn = a.max(2), a.min(2); luma = a @ [0.3, 0.59, 0.11]
    sat = (mx - mn) / (mx + 1)
    wall = ((luma > LUMA) & (sat < SAT)).astype(np.uint8)          # light, low-saturation = wall / ceiling / floor / door
    wall = cv2.morphologyEx(wall, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    keep = (1 - wall).astype(np.uint8)
    # drop small keep-blobs (switches, grout, cabinet edges) not touching the person
    n, lab, st, _ = cv2.connectedComponentsWithStats(keep, 8)
    big = np.zeros_like(keep)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] > MINAREA: big[lab == i] = 1
    keep = np.maximum(big.astype(np.float32), m)
    k = Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(2.2))
    return Image.composite(im, BGI, k)


if PREV:
    for t in PREV:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", SRC, "-frames:v", "1", "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        frame(Image.frombytes("RGB", (W, H), raw)).save(f"{OUT}_{t:.2f}.png")
    sys.exit()
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"scale={W}:{H},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", SRC, "-map", "0:v", "-map", "1:a?",
                        "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", OUT], stdin=subprocess.PIPE)
n = 0
while True:
    raw = dec.stdout.read(W * H * 3)
    if len(raw) < W * H * 3: break
    enc.stdin.write(frame(Image.frombytes("RGB", (W, H), raw)).tobytes()); n += 1
    if n % 100 == 0: print(n, file=sys.stderr)
enc.stdin.close(); enc.wait(); print("done", n)
