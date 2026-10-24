"""Styles 9/10/11 (inspired by @iaz.199): duo titles, neon numbers, minimal white captions.

usage: python3 -I render_iaz.py SRC OUT FONTS SPEC [t1,t2,...]   (times → preview PNGs OUT_<t>.png)
SPEC defines EV (list of events built with the helpers below) and optional COLOR / NEON / Y_PLAIN.
  duo(t0, t1, ("عربي", t), ("English", t))   9  white Arabic line + huge coloured serif word under it
  neon(t0, t1, "15", t, label=("ريال", t))   10 huge glowing number (+ small glowing label above it)
  plain(t0, t1, "كلمة أو ثلاث", type=True)   11 small white caption with soft shadow; type=True → typed in
  serif(t0, t1, "Meshraq · Tabuk")            elegant serif sign-off line (date, place, website)
"""
import re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC, OUT, FONTS, SPEC = sys.argv[1:5]
PREVIEW = [float(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 else None
W, H, FPS = 1080, 1920, 30


def duo(t0, t1, ar, en, y=None): return dict(k="duo", t0=t0, t1=t1, ar=ar, en=en, y=y)
def neon(t0, t1, num, t, label=None, y=None, color=None): return dict(k="neon", t0=t0, t1=t1, num=num, t=t, label=label, y=y, color=color)
def plain(t0, t1, text, type=False, y=None): return dict(k="plain", t0=t0, t1=t1, text=text, type=type, y=y)
def serif(t0, t1, text, y=None): return dict(k="serif", t0=t0, t1=t1, text=text, y=y)
def kin(t0, t1, *rows, y=1200, gap=26, nudge=0):
    """12: kinetic brand words. rows = [("word", t, size), ...] per row; each row is laid out right-to-left and
    re-centred on the words already shown, so a half-spoken row stays balanced. nudge=40 staggers rows sideways."""
    out, cy = [], y
    for ri, row in enumerate(rows):
        ws = [(txt, tt, sz, mask(txt, F_AR(sz)).width - 80) for txt, tt, sz in row]
        total = sum(w for *_, w in ws) + gap * (len(ws) - 1)
        if total > 900:   # keep the row inside the frame
            k = 900 / total
            ws = [(txt, tt, int(sz * k), mask(txt, F_AR(int(sz * k))).width - 80) for txt, tt, sz, _ in ws]
        out.append(dict(ws=ws, cy=cy, dx=(nudge if ri % 2 else -nudge) * (len(rows) > 1), gap=gap))
        cy += max(sz for _, _, sz, _ in ws) * 1.15
    return dict(k="kin", t0=t0, t1=t1, rows=out)
def card(t0, t1, path, t, cx=540, cy=560, w=760, r=36): return dict(k="card", t0=t0, t1=t1, path=path, t=t, cx=cx, cy=cy, w=w, r=r)


def pop(t0, t1, big=None, tag=None, y=None, top=None):
    """13 (Abu Zaid style): one huge outlined word (big=("كلمة", t, colour)) + a small black-on-yellow marker tag
    under it (tag=("نص", t)); optional top=("خصم", t, colour) stacked above the big word. Sits above the head."""
    return dict(k="pop", t0=t0, t1=t1, big=big, tag=tag, top=top, y=y)


spec = dict(duo=duo, neon=neon, plain=plain, serif=serif, kin=kin, card=card, pop=pop)
_src = open(SPEC, encoding="utf-8").read()
exec("\n".join(l for l in _src.splitlines() if re.match(r"^[A-Z_0-9]+ *=", l) and not l.startswith("EV")), spec)
COLOR = tuple(spec.get("COLOR", (245, 170, 20)))      # duo English word
NEON = tuple(spec.get("NEON", (90, 255, 60)))         # neon numbers
Y_PLAIN = spec.get("Y_PLAIN", 1150)
Y_DUO = spec.get("Y_DUO", 470)
Y_NEON = spec.get("Y_NEON", 1220)
Y_POP = spec.get("Y_POP", 520)
TAG = tuple(spec.get("TAG", (255, 222, 40)))           # marker-tag background (style 13)
KIN = tuple(spec.get("KIN", (64, 225, 235)))           # kinetic word colour (brand)
KIN2 = tuple(spec.get("KIN2", (140, 70, 255)))         # its offset shadow colour
LRM = "‎"
NONJOIN = set("اأإآدذرزوؤةىء ")


def font(name, size, axes=None):
    f = ImageFont.truetype(f"{FONTS}/{name}", size)
    if axes:
        f.set_variation_by_axes(axes)
    return f


F_AR = lambda s: font("Tajawal-Black.ttf", s)
_pf = {}


def F_PLAIN_FOR(text, size=66, maxw=940):
    """one font size per caption so typed-in text keeps its size; shrinks long lines to stay inside the frame"""
    if text not in _pf:
        while size > 34 and mask(text, font("Tajawal-ExtraBold.ttf", size)).width - 80 > maxw:
            size -= 4
        _pf[text] = font("Tajawal-ExtraBold.ttf", size)
    return _pf[text]
F_SERIF = lambda s: font("Fraunces.ttf", s, [144, 900, 60, 1])
F_BIG_AR = lambda s: font("Lalezar-Regular.ttf", s)   # duo big word when it is Arabic (user wants Arabic-only)
F_NUM = lambda s: font("LilitaOne.ttf", s)


EV = None  # filled after the drawing helpers exist (see bottom of setup)


def fix(t):
    return re.sub(r"(\d[\d.,%:/\-–]*)", LRM + r"\1" + LRM, t)


def mask(text, f, pad=40):
    s = fix(text)
    d = "rtl" if re.search(r"[؀-ۿ]", s) else "ltr"
    bb = f.getbbox(s, direction=d)
    m = Image.new("L", (bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad), 0)
    ImageDraw.Draw(m).text((pad - bb[0], pad - bb[1]), s, font=f, fill=255, direction=d)
    return m


def fitted(text, ff, size, maxw=980):
    m = mask(text, ff(size))
    while m.width - 80 > maxw and size > 30:
        size = int(size * 0.92); m = mask(text, ff(size))
    return m


def shadowed(m, color, sh=150, blur=10, dy=6):
    out = Image.new("RGBA", (m.width, m.height + dy), (0, 0, 0, 0))
    s = Image.new("RGBA", m.size, (0, 0, 0, 255)); s.putalpha(m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v * sh // 255))
    out.alpha_composite(s, (0, dy))
    c = Image.new("RGBA", m.size, color + (255,)); c.putalpha(m); out.alpha_composite(c)
    return out


def glow(m, color, core_mix=0.35):
    pad = 60
    big = Image.new("L", (m.width + 2 * pad, m.height + 2 * pad), 0); big.paste(m, (pad, pad))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    edge = big.filter(ImageFilter.MaxFilter(13))
    dark = Image.new("RGBA", big.size, tuple(int(c * 0.18) for c in color) + (255,)); dark.putalpha(edge.filter(ImageFilter.GaussianBlur(2)))
    for r, a in ((34, 0.9), (14, 1.0)):
        g = Image.new("RGBA", big.size, color + (255,)); g.putalpha(big.filter(ImageFilter.GaussianBlur(r)).point(lambda v: min(255, int(v * a * 1.6))))
        out.alpha_composite(g)
    out.alpha_composite(dark)
    core = tuple(int(c + (255 - c) * core_mix) for c in color)
    c = Image.new("RGBA", big.size, core + (255,)); c.putalpha(big); out.alpha_composite(c)
    return out


def duotone(m, a, b, off=9):
    out = Image.new("RGBA", (m.width + off, m.height + off), (0, 0, 0, 0))
    sh = Image.new("RGBA", m.size, (0, 0, 0, 255)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(12)).point(lambda v: v * 120 // 255))
    out.alpha_composite(sh, (off, off + 6))
    s2 = Image.new("RGBA", m.size, b + (255,)); s2.putalpha(m); out.alpha_composite(s2, (off, off))
    s1 = Image.new("RGBA", m.size, a + (255,)); s1.putalpha(m); out.alpha_composite(s1, (0, 0))
    return out


def smear(sp, n):
    if n <= 1:
        return sp
    acc = np.zeros((sp.height, sp.width + n, 4), np.float32); a = np.asarray(sp, np.float32)
    for i in range(0, n, max(1, n // 8)):
        acc[:, i:i + sp.width] += a
    acc /= len(range(0, n, max(1, n // 8)))
    return Image.fromarray(acc.clip(0, 255).astype(np.uint8))


def card_img(path, w, r):
    im = Image.open(path).convert("RGBA"); im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    im.putalpha(Image.fromarray(np.minimum(np.asarray(m), np.asarray(im.split()[3]))))
    pad = 40; out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 255)); sh.putalpha(im.split()[3].point(lambda v: v * 140 // 255))
    tmp = Image.new("RGBA", out.size, (0, 0, 0, 0)); tmp.alpha_composite(sh, (pad, pad + 14))
    out.alpha_composite(tmp.filter(ImageFilter.GaussianBlur(16))); out.alpha_composite(im, (pad, pad))
    return out


def outlined(m, col, stroke=10):
    """fill colour with a thick dark outline + soft drop shadow (bold TikTok caption look)"""
    pad = stroke + 20
    big = Image.new("L", (m.width + 2 * pad, m.height + 2 * pad), 0); big.paste(m, (pad, pad))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", big.size, (0, 0, 0, 255)); sh.putalpha(big.filter(ImageFilter.MaxFilter(stroke * 2 + 1)).filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * 150 // 255))
    out.alpha_composite(sh, (0, 8))
    ol = Image.new("RGBA", big.size, (25, 20, 20, 255)); ol.putalpha(big.filter(ImageFilter.MaxFilter(stroke * 2 + 1)))
    out.alpha_composite(ol)
    f = Image.new("RGBA", big.size, col + (255,)); f.putalpha(big); out.alpha_composite(f)
    return out


def marker_tag(txt, size=58):
    m = mask(txt, font("Tajawal-Black.ttf", size), pad=18)
    w, h = m.width + 30, m.height - 6
    out = Image.new("RGBA", (w + 20, h + 26), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((14, 16, w + 6, h + 18), fill=(0, 0, 0, 110))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(out).rectangle((10, 8, w, h + 8), fill=TAG + (255,))
    ink = Image.new("RGBA", m.size, (15, 15, 15, 255)); ink.putalpha(m)
    out.alpha_composite(ink, (10 + (w - 10 - m.width) // 2, 8 + (h - m.height) // 2))
    return out


_cache = {}
exec(_src, spec)
EV = spec["EV"]


def sprite(key, make):
    if key not in _cache:
        _cache[key] = make()
    return _cache[key]


def ease(p):
    p = min(max(p, 0.0), 1.0); return 1 - (1 - p) ** 3


def put(c, sp, cx, cy, a=1.0, s=1.0):
    if a <= 0:
        return
    if s != 1.0:
        sp = sp.resize((max(1, int(sp.width * s)), max(1, int(sp.height * s))), Image.BILINEAR)
    if a < 1:
        sp = sp.copy(); sp.putalpha(sp.split()[3].point(lambda v: int(v * a)))
    c.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)))


def out_a(t, e):
    return min(1.0, (e["t1"] - t) / 0.15)


def typed(text, p):
    n = max(1, int(round(len(text) * min(p, 1.0))))
    s = text[:n]
    if n < len(text) and s[-1] not in NONJOIN and re.match(r"[؀-ۿ]", s[-1]):
        s += "ـ"
    return s


def draw(c, t, e):
    k, fa = e["k"], out_a(t, e)
    if k == "duo":
        (ar, ta), (en, te) = e["ar"], e["en"]
        y = e["y"] or Y_DUO
        sa = sprite(("ar", ar), lambda: shadowed(fitted(ar, F_AR, 104), (255, 255, 255)))
        se = sprite(("en", en), lambda: shadowed(fitted(en, F_BIG_AR if re.search(r"[\u0600-\u06ff]", en) else F_SERIF,
                                                           210 if re.search(r"[\u0600-\u06ff]", en) else 250), COLOR, sh=120))
        pa, pe = ease((t - ta) / 0.3), ease((t - te) / 0.35)
        put(c, sa, W / 2, y - se.height * 0.32 - sa.height / 2 + 30 + 20 * (1 - pa), pa * fa)
        if t >= te:
            put(c, se, W / 2, y + 10, pe * fa, 1.12 - 0.12 * pe)
    elif k == "neon":
        col = tuple(e["color"] or NEON); y = e["y"] or Y_NEON
        sn = sprite(("num", e["num"], col), lambda: glow(fitted(e["num"], F_NUM, 380, 900), col))
        p = (t - e["t"]) / 0.2
        if p >= 0:
            s = 1.4 - 0.4 * ease(p) + (0.04 * np.sin((t - e["t"]) * 9) * np.exp(-(t - e["t"]) * 3) if p > 1 else 0)
            put(c, sn, W / 2, y, min(1, p * 2) * fa, s)
        if e["label"]:
            lab, tl = e["label"]
            sl = sprite(("lab", lab, col), lambda: glow(fitted(lab, F_AR, 92), col, 0.55))
            pl = ease((t - tl) / 0.3)
            if t >= tl:
                put(c, sl, W / 2, y - sn.height * 0.42 - sl.height * 0.25 + 15 * (1 - pl), pl * fa)
    elif k == "plain":
        y = e["y"] or Y_PLAIN
        if e["type"]:
            s = typed(e["text"], (t - e["t0"]) / max(0.25, 0.045 * len(e["text"])))
            fp = F_PLAIN_FOR(e["text"])
            sp = sprite(("pl", s, id(fp)), lambda: shadowed(mask(s, fp), (255, 255, 255), sh=170, blur=8, dy=4))
            put(c, sp, W / 2, y, fa)
        else:
            sp = sprite(("pl", e["text"]), lambda: shadowed(mask(e["text"], F_PLAIN_FOR(e["text"])), (255, 255, 255), sh=170, blur=8, dy=4))
            put(c, sp, W / 2, y + 12 * (1 - ease((t - e["t0"]) / 0.25)), ease((t - e["t0"]) / 0.2) * fa)
    elif k == "kin":
        for row in e["rows"]:
            vis = [w for w in row["ws"] if t >= w[1]]
            if not vis:
                continue
            total = sum(w[3] for w in vis) + row["gap"] * (len(vis) - 1)
            x = W / 2 + total / 2 + row["dx"]
            for text, tw, size, wd in vis:
                cx, cy = x - wd / 2, row["cy"]; x -= wd + row["gap"]
                sp = sprite(("kin", text, size), lambda: duotone(mask(text, F_AR(size)), KIN, KIN2))
                p = (t - tw) / 0.16
                if p < 1:   # fast pop-in with horizontal smear
                    put(c, smear(sp, int(40 * (1 - p))), cx, cy, min(1, p * 1.6) * fa, 1.25 - 0.25 * ease(p))
                else:
                    put(c, sp, cx, cy, fa, 1 + 0.06 * np.exp(-(t - tw - 0.16) * 8) * np.sin((t - tw) * 20))
    elif k == "pop":
        y = e["y"] or Y_POP
        def bigspr(txt, col):
            return sprite(("popb", txt, col), lambda: outlined(fitted(txt, F_BIG_AR, 200, 940), col))
        if e["top"] and t >= e["top"][1]:
            txt, tt, col = e["top"]
            sp = bigspr(txt, tuple(col)); p = (t - tt) / 0.14
            put(c, sp, W / 2, y - (205 if not e["big"] or len(e["big"]) < 5 else 205 + (e["big"][4] - 200) * 0.75), min(1, p * 2) * fa, 1.3 - 0.3 * ease(p))
        if e["big"] and t >= e["big"][1]:
            txt, tt, col = e["big"][:3]
            times = e["big"][3] if len(e["big"]) > 3 and e["big"][3] else None
            size = e["big"][4] if len(e["big"]) > 4 else 200
            col = tuple(col)
            if times:   # word-by-word: final RTL layout fixed, each word pops at its own time
                words = txt.split()
                sps = [sprite(("popw", w_, col, size), lambda w_=w_: outlined(mask(w_, F_BIG_AR(size)), col)) for w_ in words]
                gap = -40
                total = sum(sp.width for sp in sps) + gap * (len(sps) - 1)
                k = min(1.0, 980 / total)
                x = W / 2 + total * k / 2
                for sp, tw in zip(sps, times):
                    cx = x - sp.width * k / 2; x -= (sp.width + gap) * k
                    if t >= tw:
                        p = (t - tw) / 0.14
                        put(c, sp, cx, y, min(1, p * 2) * fa, k * (1.3 - 0.3 * ease(p)))
            else:
                sp = sprite(("popb", txt, col, size), lambda: outlined(fitted(txt, F_BIG_AR, size, 940), col))
                p = (t - tt) / 0.14
                beat = 0.07 * np.exp(-(t - tt - 0.14) * 5) * np.sin((t - tt) * 18) if p > 1 and size > 200 else 0
                put(c, sp, W / 2, y, min(1, p * 2) * fa, 1.3 - 0.3 * ease(p) + beat)
        if e["tag"] and t >= e["tag"][1]:
            txt, tt = e["tag"][:2]
            sp = sprite(("popt", txt), lambda: marker_tag(txt))
            p = ease((t - tt) / 0.2)
            ty = e["tag"][2] if len(e["tag"]) > 2 else y + ((e["big"][4] if len(e["big"]) > 4 else 200) * 0.85 if e["big"] else 0)
            put(c, sp, W / 2, ty + 12 * (1 - p), p * fa)
    elif k == "card":
        sp = sprite(("card", e["path"], e["w"]), lambda: card_img(e["path"], e["w"], e["r"]))
        p = ease((t - e["t"]) / 0.3)
        if t >= e["t"]:
            put(c, sp, e["cx"], e["cy"] + 140 * (1 - p), p * fa, 0.9 + 0.1 * p)
    elif k == "serif":
        y = e["y"] or 1480
        sp = sprite(("sf", e["text"]), lambda: shadowed(fitted(e["text"], F_SERIF, 120), (255, 255, 255), sh=140))
        put(c, sp, W / 2, y, ease((t - e["t0"]) / 0.5) * fa)


def composite(raw, t):
    c = Image.frombytes("RGB", (W, H), raw).convert("RGBA")
    for e in EV:
        if e["t0"] <= t < e["t1"]:
            draw(c, t, e)
    return c.convert("RGB")


dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"scale={W}:{H},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
N = W * H * 3
if PREVIEW:
    want = {int(round(x * FPS)): x for x in PREVIEW}
    i = 0
    while want and i <= max(want):
        b = dec.stdout.read(N)
        if len(b) < N:
            break
        if i in want:
            composite(b, want[i]).save(f"{OUT}_{want[i]:.2f}.png")
        i += 1
    dec.kill(); sys.exit()
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", SRC, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", OUT], stdin=subprocess.PIPE)
i = 0
while True:
    b = dec.stdout.read(N)
    if len(b) < N:
        break
    enc.stdin.write(composite(b, i / FPS).tobytes()); i += 1
enc.stdin.close(); enc.wait()
print("done", i, "frames", file=sys.stderr)
