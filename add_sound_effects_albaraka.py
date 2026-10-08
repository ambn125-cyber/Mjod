"""Mix synthesized sound effects into an edited clip: whoosh on transitions, pop on badges, ding on key moments."""
import re, subprocess, sys, wave
import numpy as np

VIDEO, CAPS_SRC, OUT = sys.argv[1:4]
SR = 48000
DUR = 58.9
CUTS = [(6.95, 7.16), (10.88, 11.30), (12.21, 12.47), (15.47, 15.80), (17.23, 17.45), (18.48, 18.61), (19.51, 19.65), (21.04, 21.38), (23.00, 23.21), (30.07, 30.21), (37.15, 37.48), (48.54, 48.73), (49.43, 49.71), (53.57, 53.76), (58.55, DUR)]
# scene changes in the source (all carry a blur transition; the blur peaks just before the cut)
SCENES = [1.63, 4.27, 8.27, 24.67, 28.03, 32.60, 35.17, 40.07, 43.97, 46.27, 55.50]
DING_WORDS = ("ضمان ذهبي", "ملحمة البركة")


def src_to_out(t):
    for a, b in CUTS:
        if a <= t < b:
            t = b
    return t - sum(min(max(t - a, 0), b - a) for a, b in CUTS)


rng = np.random.default_rng(7)


def whoosh(dur=0.42, f0=300, f1=2600):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    spec = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    k = 10
    for i in range(k):  # band-pass sweeping upward
        fc = f0 * (f1 / f0) ** (i / (k - 1))
        part = np.fft.irfft(spec * np.exp(-0.5 * ((np.log(freqs + 1) - np.log(fc)) / 0.45) ** 2), n)
        lo, hi = i * n // k, (i + 1) * n // k
        out[lo:hi] = part[lo:hi]
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return out * env / np.abs(out * env).max()


def pop(dur=0.09):
    t = np.arange(int(dur * SR)) / SR
    f = 900 * np.exp(-t * 28) + 180  # fast pitch drop
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)
    return s / np.abs(s).max()


def ding(dur=1.1):
    t = np.arange(int(dur * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * d)
            for f, a, d in ((1568, 1.0, 4.5), (2350, 0.5, 6), (3136, 0.35, 8), (4700, 0.2, 11)))
    s[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return s / np.abs(s).max()


raw = subprocess.run(["ffmpeg", "-v", "error", "-i", VIDEO, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768 * 0.85  # headroom for effects


def add(sig, t, gain):
    s0 = int(t * SR)
    if s0 < 0 or s0 >= len(audio):
        return
    e0 = min(s0 + len(sig), len(audio))
    audio[s0:e0] += (sig[: e0 - s0] * gain)[:, None]


# whooshes centred on each transition
w = whoosh()
for s in SCENES:
    add(w, src_to_out(s) - len(w) / SR * 0.6, 0.55)

# pops / dings when a badge (pill) appears
caps = open(CAPS_SRC, encoding="utf-8").read()
for text, t in re.findall(r'T\("([^"]+)", ([0-9.]+), "p"', caps):
    t = src_to_out(float(t))
    if text in DING_WORDS:
        add(ding(), t, 0.65)
    else:
        add(pop(), t, 0.85)

audio = np.tanh(audio * 1.1) / np.tanh(1.1)  # soft limiter instead of hard clipping
with wave.open(OUT + ".wav", "wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
    wv.writeframes((audio * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-i", OUT + ".wav", "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], check=True)
print("done", file=sys.stderr)
