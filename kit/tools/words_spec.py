"""Build a style-15 spec (word-by-word + neon keywords) from a transcribe.py output.
usage: python3 -I words_spec.py tr.txt out_spec.py   (edit FIX / KEY / colours below per video)"""
import re, sys, json
FIX = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
words = []
for line in open(sys.argv[1], encoding="utf-8"):
    m = re.match(r"\s+([\d.]+)-([\d.]+)\s+(.*)", line)
    if m:
        w = m.group(3).strip().strip("،.؟?!,")
        if w:
            words.append([float(m.group(1)), float(m.group(2)), w])
# merge "ب179" → "179", fix words
out = []
for t0, t1, w in words:
    w = FIX.get(w, w)
    w = re.sub(r"^(ب|بـ)(\d)", r"\2", w)
    if w in ("بـ", "ب", "%"):
        if w == "%" and out: out[-1][2] += "%"
        continue
    if out and w.startswith(".") and re.match(r"\.\d", w):
        out[-1][2] += w; continue
    out.append([t0, t1, w])
NEON_WORDS = set(json.loads(open(sys.argv[4], encoding="utf-8").read())) if len(sys.argv) > 4 else set()
COLS = ["R_", "C_"]
ev, ci = [], 0
i = 0
while i < len(out):
    t0, t1, w = out[i]
    nxt = out[i + 1][0] if i + 1 < len(out) else t1 + 0.6
    # two-word neon phrases
    if i + 1 < len(out) and f"{w} {out[i+1][2]}" in NEON_WORDS:
        w2 = f"{w} {out[i+1][2]}"; nxt = out[i + 2][0] if i + 2 < len(out) else out[i+1][1] + 0.6
        end = min(nxt, t0 + 1.6); ev.append(f'    word({t0:.2f}, {end:.2f}, "{w2}", col={COLS[ci%2]}),'); ci += 1; i += 2; continue
    neon = w in NEON_WORDS or bool(re.fullmatch(r"\d[\d.,%]*", w))
    end = min(nxt, t0 + (1.4 if neon else 0.9))
    if end - t0 < 0.12: end = t0 + 0.12
    if neon:
        ev.append(f'    word({t0:.2f}, {end:.2f}, "{w}", col={COLS[ci%2]}),'); ci += 1
    else:
        ev.append(f'    word({t0:.2f}, {end:.2f}, "{w}"),')
    i += 1
# neon keywords linger (up to 1.3 s) over the following plain words, until the next neon one
pat = re.compile(r'    word\(([\d.]+), ([\d.]+), "(.*?)"(, col=\w+)?\),')
P = [pat.match(e).groups() for e in ev]
nstarts = [float(a) for a, b, w, c in P if c]
ev = []
for a, b, w, c in P:
    a, b = float(a), float(b)
    if c:
        later = [x for x in nstarts if x > a]
        b = max(b, min(a + 1.3, later[0] if later else a + 1.3))
    ev.append(f'    word({a:.2f}, {b:.2f}, "{w}"{c or ""}),')
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(ev) + "\n")
print(len(ev), "events")
