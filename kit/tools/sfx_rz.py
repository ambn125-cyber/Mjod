"""Add offer sound effects to the Ramez edit: cash-register 'ka-ching' on every new price, a quick
swish when an old price is struck, a soft impact under each giant '50%'. Events come from the
render_rz spec (source time) and are mapped through the pause cuts. Kept well under the voice."""
import json, os, subprocess, sys, wave
import numpy as np

VIDEO, SPEC, OUT = sys.argv[1:4]
CUTS = [tuple(c) for c in json.loads(os.environ["CUTS_CFG"])["cuts"]]
SR = 48000
spec = {}
exec(open(SPEC, encoding="utf-8").read(), spec)
rng = np.random.default_rng(11)
tt = lambda d: np.arange(int(d * SR)) / SR


def s2o(t):
    for a, b in CUTS:
        if a <= t < b:
            t = b
    return t - sum(min(max(t - a, 0), b - a) for a, b in CUTS)


def norm(x):
    return x / (np.abs(x).max() + 1e-9)


def hp_noise(n, cut):
    sp = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR)
    return np.fft.irfft(sp * (f > cut), n)


def kaching():
    d = 0.9; t = tt(d); n = len(t)
    ka = np.zeros(n); m = int(0.05 * SR)                       # drawer click
    ka[:m] = hp_noise(m, 1800) * np.exp(-np.arange(m) / SR * 90)
    bell = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in
               ((2637, 1.0, 5.5), (3520, .6, 7), (5274, .35, 9), (7040, .2, 12)))
    bell = np.concatenate([np.zeros(int(0.07 * SR)), bell])[:n]
    coins = hp_noise(n, 4500) * np.exp(-np.maximum(t - 0.07, 0) * 9) * (t > 0.07) * 0.25
    return norm(0.7 * ka + bell + coins)


def swish():
    d = 0.22; n = int(d * SR)
    return norm(hp_noise(n, 2500) * np.sin(np.linspace(0, np.pi, n)) ** 2)


def impact():
    d = 0.7; t = tt(d); f = 110 * np.exp(-t * 6) + 45
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) + 0.2 * hp_noise(len(t), 200) * np.exp(-t * 25))


events = []
for ch in spec["CHUNKS"]:
    ps = [t for k, _, t in ch["items"] if k == "p"]
    for t in ps:
        events.append((kaching, s2o(t), 0.30))
    if ps and any(k == "o" for k, _, _ in ch["items"]):
        events.append((swish, s2o(ps[0]) - 0.02, 0.22))
    if ch.get("big"):
        events.append((impact, s2o(ch["big"][1]), 0.40))

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", VIDEO, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                     capture_output=True).stdout
a = np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float32) / 32768
fx = np.zeros(len(a), np.float32)
for fn, t, g in events:
    s = fn() * g; i = int(t * SR)
    if 0 <= i < len(fx):
        e = min(len(fx), i + len(s)); fx[i:e] += s[:e - i]
mix = np.clip(a + fx[:, None], -1, 1)
tmp = OUT + ".wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VIDEO, "-i", tmp, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], check=True)
os.remove(tmp)
print("events", len(events), file=sys.stderr)
