"""Mix synthesized sound effects from render_v2 events into an edited (pause-cut) clip."""
import json, re, subprocess, sys, wave
import numpy as np

VIDEO, EVENTS, CUTS_SRC, OUT = sys.argv[1:5]
SR = 48000
src = open(CUTS_SRC, encoding="utf-8").read()
DUR = float(re.search(r"^DUR = ([0-9.]+)", src, re.M).group(1))
CUTS = eval(re.search(r"^CUTS = (.*)$", src, re.M).group(1), {"DUR": DUR})


def src_to_out(t):
    for a, b in CUTS:
        if a <= t < b:
            t = b
    return t - sum(min(max(t - a, 0), b - a) for a, b in CUTS)


rng = np.random.default_rng(7)
tt = lambda d: np.arange(int(d * SR)) / SR


def band_sweep(n, f0, f1, width=0.45, k=10):
    spec = np.fft.rfft(rng.standard_normal(n)); freqs = np.fft.rfftfreq(n, 1 / SR); out = np.zeros(n)
    for i in range(k):
        fc = f0 * (f1 / f0) ** (i / (k - 1))
        part = np.fft.irfft(spec * np.exp(-0.5 * ((np.log(freqs + 1) - np.log(fc)) / width) ** 2), n)
        lo, hi = i * n // k, (i + 1) * n // k
        out[lo:hi] = part[lo:hi]
    return out


def norm(x):
    return x / (np.abs(x).max() + 1e-9)


def whoosh(d=0.42):
    n = int(d * SR); return norm(band_sweep(n, 300, 2600) * np.sin(np.linspace(0, np.pi, n)) ** 1.5)


def swish(d=0.2):
    n = int(d * SR); return norm(band_sweep(n, 1500, 6000, 0.35) * np.sin(np.linspace(0, np.pi, n)) ** 2)


def pop(d=0.09):
    t = tt(d); f = 900 * np.exp(-t * 28) + 180
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45))


def ding(d=1.0):
    t = tt(d)
    s = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in ((1568, 1, 4.5), (2350, .5, 6), (3136, .35, 8), (4700, .2, 11)))
    s[:200] *= np.linspace(0, 1, 200); return norm(s)


def scribble(d=0.32):
    n = int(d * SR); t = tt(d)
    am = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 22 * t)) * np.abs(np.sin(2 * np.pi * 11 * t))
    return norm(band_sweep(n, 2500, 4500, 0.5) * am * np.sin(np.linspace(0, np.pi, n)))


def flash(d=0.35):
    t = tt(d); click = np.zeros(len(t)); click[:240] = np.hanning(480)[240:] * rng.standard_normal(240)
    return norm(click * 1.5 + band_sweep(len(t), 3000, 8000, 0.6) * np.exp(-t * 14))


def boom(d=0.6):
    t = tt(d); f = 110 * np.exp(-t * 5) + 45
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7))


SOUNDS = {"whoosh": (whoosh(), 0.45, -0.25), "swish": (swish(), 0.5, 0), "pop": (pop(), 0.8, 0),
          "ding": (ding(), 0.55, 0), "scribble": (scribble(), 0.35, 0), "flash": (flash(), 0.5, -0.02),
          "boom": (boom(), 0.7, 0)}

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", VIDEO, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768 * 0.85
for kind, t in json.load(open(EVENTS)):
    if any(a <= t < b for a, b in CUTS) and kind != "whoosh":
        continue
    sig, gain, off = SOUNDS[kind]
    s0 = int((src_to_out(t) + off) * SR)
    if 0 <= s0 < len(audio):
        e0 = min(s0 + len(sig), len(audio)); audio[s0:e0] += (sig[:e0 - s0] * gain)[:, None]
audio = np.tanh(audio * 1.1) / np.tanh(1.1)
with wave.open(OUT + ".wav", "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
    wv.writeframes((audio * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-i", OUT + ".wav", "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "slow", "-b:v", "1650k", "-maxrate", "2200k", "-bufsize", "4000k",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], check=True)
print("done", file=sys.stderr)
