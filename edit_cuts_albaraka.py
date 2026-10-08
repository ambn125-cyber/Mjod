"""Remove pauses and add transitions at scene changes: white flash first, then zoom-in pulls (no sound)."""
import subprocess, sys, wave
import numpy as np
from PIL import Image, ImageFilter

SRC, OUT = sys.argv[1], sys.argv[2]
PREVIEW = sys.argv[3] if len(sys.argv) > 3 else None
W, H, FPS, SR = 1080, 1920, 30, 48000

DUR = 58.9
CUTS = [(6.95, 7.16), (10.88, 11.30), (12.21, 12.47), (15.47, 15.80), (17.23, 17.45), (18.48, 18.61), (19.51, 19.65), (21.04, 21.38), (23.00, 23.21), (30.07, 30.21), (37.15, 37.48), (48.54, 48.73), (49.43, 49.71), (53.57, 53.76), (58.55, DUR)]
SCENES = []  # every cut already carries a blur transition
HALF = 6  # frames each side of a transition


def keep(t):
    return not any(a <= t < b for a, b in CUTS)


def src_to_out(t):
    return t - sum(min(max(t - a, 0), b - a) for a, b in CUTS)


# ---------- output frame list ----------
src_frames = [i for i in range(int(DUR * FPS)) if keep(i / FPS)]
trans = []
for k, s in enumerate(SCENES):
    # a scene change inside a removed pause lands on the junction
    t = s
    for a, b in CUTS:
        if a <= s < b:
            t = b
    trans.append((src_to_out(t), "zoom"))
print("output", len(src_frames) / FPS, "s; transitions at", [round(t, 2) for t, _ in trans], file=sys.stderr)


def ease(p):
    return p * p * (3 - 2 * p)


def hblur(arr, r):
    r = int(r)
    if r < 1:
        return arr
    c = np.cumsum(np.pad(arr.astype(np.float32), ((0, 0), (r + 1, r), (0, 0)), mode="edge"), axis=1)
    return ((c[:, 2 * r + 1:] - c[:, :-2 * r - 1]) / (2 * r + 1)).astype(np.uint8)


def effect(frame, oi):
    for tt, kind in trans:
        d = oi - tt * FPS  # frames from the cut (negative = outgoing clip)
        if -HALF <= d < HALF:
            p = 1 - (abs(d + 0.5) / HALF)  # 0 far .. 1 at the cut
            p = ease(min(max(p, 0), 1))
            if kind == "flash":
                arr = frame.astype(np.float32)
                return (arr + (255 - arr) * p).clip(0, 255).astype(np.uint8)
            if kind == "zoom":
                sc = 1 + 0.35 * p
                im = Image.fromarray(frame)
                cw, ch = int(W / sc), int(H / sc)
                im = im.crop(((W - cw) // 2, (H - ch) // 2, (W + cw) // 2, (H + ch) // 2)).resize((W, H), Image.BILINEAR)
                im = im.filter(ImageFilter.GaussianBlur(10 * p))
                return np.asarray(im)
            else:  # whip pan: outgoing slides left, incoming arrives from the right
                shift = int(W * 0.45 * p) * (1 if d < 0 else -1)
                arr = np.roll(frame, -shift, axis=1)
                return hblur(arr, 90 * p)
    return frame


# ---------- video ----------
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       stdout=subprocess.PIPE)
if PREVIEW:
    want = {int(float(x) * FPS) for x in PREVIEW.split(",")}
else:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                            "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-colorspace", "bt709", OUT + ".video.mp4"], stdin=subprocess.PIPE)
keepset = set(src_frames)
oi = 0
n = W * H * 3
for si in range(int(DUR * FPS)):
    b = dec.stdout.read(n)
    if len(b) < n:
        break
    if si not in keepset:
        continue
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    if PREVIEW:
        if oi in want:
            Image.fromarray(effect(f, oi)).save(f"{OUT}_{oi / FPS:.2f}.png")
    else:
        enc.stdin.write(effect(f, oi).tobytes())
    oi += 1
if PREVIEW:
    sys.exit()
enc.stdin.close(); enc.wait()

# ---------- audio: cut pauses with short fades, add whooshes ----------
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                     capture_output=True).stdout
a = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768
segs, t = [], 0.0
for c0, c1 in CUTS + [(DUR, DUR)]:
    if c0 > t:
        segs.append(a[int(t * SR):int(c0 * SR)].copy())
    t = c1
fade = int(0.012 * SR)
ramp = np.linspace(0, 1, fade)[:, None]
for s in segs:
    s[:fade] *= ramp; s[-fade:] *= ramp[::-1]
audio = np.concatenate(segs)
audio = audio[:int(len(src_frames) / FPS * SR)]

audio = np.clip(audio, -1, 1)
with wave.open(OUT + ".audio.wav", "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
    wv.writeframes((audio * 32767).astype(np.int16).tobytes())

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", OUT + ".audio.wav", "-map", "0:v",
                "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT],
               check=True)
print("done", file=sys.stderr)
