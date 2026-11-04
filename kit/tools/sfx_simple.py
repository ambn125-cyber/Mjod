"""Mix simple sound effects under an existing video's audio, at given times (output time).
SFX_CFG='{"whoosh":[1.2, 4.3], "kaching":[197.8]}' python3 -I kit/tools/sfx_simple.py in.mp4 out.mp4
Effects come from sfx_rz.py's synths (ka-ching) plus a soft whoosh; kept well under the voice."""
import json, os, subprocess, sys, wave
import numpy as np

VIDEO, OUT = sys.argv[1:3]
CFG = json.loads(os.environ["SFX_CFG"])
SR = 48000
rng = np.random.default_rng(7)
tt = lambda d: np.arange(int(d * SR)) / SR


def norm(x):
    return x / (np.abs(x).max() + 1e-9)


def hp_noise(n, cut, top=None):
    sp = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR)
    m = (f > cut) & ((f < top) if top else True)
    return np.fft.irfft(sp * m, n)


def kaching():
    d = 0.9; t = tt(d); n = len(t)
    ka = np.zeros(n); m = int(0.05 * SR)
    ka[:m] = hp_noise(m, 1800) * np.exp(-np.arange(m) / SR * 90)
    bell = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in
               ((2637, 1.0, 5.5), (3520, .6, 7), (5274, .35, 9), (7040, .2, 12)))
    bell = np.concatenate([np.zeros(int(0.07 * SR)), bell])[:n]
    coins = hp_noise(n, 4500) * np.exp(-np.maximum(t - 0.07, 0) * 9) * (t > 0.07) * 0.25
    return norm(0.7 * ka + bell + coins)


def whoosh():
    d = 0.45; n = int(d * SR); x = np.linspace(0, 1, n)
    env = np.sin(np.pi * x ** 0.7) ** 2
    # band-passed noise whose centre sweeps up: crude filter by mixing two bands over time
    lo, hi = hp_noise(n, 300, 1500), hp_noise(n, 1500, 6000)
    return norm((lo * (1 - x) + hi * x) * env)


FX = {"whoosh": (whoosh, 0.22, -0.12), "kaching": (kaching, 0.30, 0.0)}   # (synth, gain, lead-in seconds)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", VIDEO, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                     capture_output=True).stdout
a = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768
fx = np.zeros(len(a), np.float32); n_ev = 0
for name, times in CFG.items():
    fn, g, lead = FX[name]; s = fn() * g
    for t in times:
        i = int((t + lead) * SR)
        if 0 <= i < len(fx):
            e = min(len(fx), i + len(s)); fx[i:e] += s[:e - i]; n_ev += 1
mix = np.clip(a + fx[:, None], -1, 1)
tmp = OUT + ".wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-i", tmp, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], check=True)
os.remove(tmp)
print("events", n_ev, file=sys.stderr)
