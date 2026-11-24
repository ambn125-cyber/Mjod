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
import os
T0 = float(os.environ.get("T0", "0"))   # time offset when rendering a cut-out segment


def duo(t0, t1, ar, en, y=None): return dict(k="duo", t0=t0, t1=t1, ar=ar, en=en, y=y)
def neon(t0, t1, num, t, label=None, y=None, color=None): return dict(k="neon", t0=t0, t1=t1, num=num, t=t, label=label, y=y, color=color)
def plain(t0, t1, text, type=False, y=None): return dict(k="plain", t0=t0, t1=t1, text=text, type=type, y=y)
def serif(t0, t1, text, y=None): return dict(k="serif", t0=t0, t1=t1, text=text, y=y)
def word(t0, t1, text, col=None, size=None, x=540, y=None):
    """15 (كلمة كلمة): one spoken word at a time. col=None → small plain white Naskh word with a soft shadow;
    col=(r,g,b) → big glowing neon keyword (Amiri Bold). Place keywords in empty space with x/y."""
    return dict(k="word", t0=t0, t1=t1, text=text, col=col, size=size, x=x, y=y)
def iz(t0, t1, *rows, y=None, glass=False, line=False):
    """16 (iaz.199 reel): 1–2 centred rows, each word slides/blur-fades in on its time. rows = [("كلمة", t, "g"|"w"), ...];
    "g" = mustard gold (IZ_GOLD), "w" = white; soft shadow, Tajawal Black. glass=True puts the whole block on a frosted pill."""
    #   colour "p" = price: bigger white, rises from behind a hidden baseline, then a light glint sweeps across it once.
    #   line=True draws a thin IZ_GOLD rule under row 1 (right → left) once its words are in. Spec ZOOM=[(t0,t1),..] = gentle punch-in.
    return dict(k="iz", t0=t0, t1=t1, rows=rows, y=y, glass=glass, line=line)


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


def gw(t0, t1, big, tb, top=None, tt=None, y=None, x=540, size=None):
    """17 (Revibe ref): small white word on top + huge pink→purple gradient glowing word, bouncy pop. Straight."""
    return dict(k="gw", t0=t0, t1=t1, big=big, tb=tb, top=top, tt=tt if tt is not None else t0, y=y, x=x, size=size)


def ico(t0, t1, path, t=None, cx=540, cy=900, w=300, glow=None, rot=0):
    """17: cut-out product / logo / emoji with a soft colour glow, bounces in and floats gently."""
    return dict(k="ico", t0=t0, t1=t1, path=path, t=t0 if t is None else t, cx=cx, cy=cy, w=w, glow=glow, rot=rot)


def sc(t0, t1, frames, fps=10, start=0.0, cx=540, cy=470, w=620, tilt=1):
    """17: phone screen recording shown as a tilted 3D card (frames = folder of numbered PNGs at fps), slides down in."""
    return dict(k="sc", t0=t0, t1=t1, frames=frames, fps=fps, start=start, cx=cx, cy=cy, w=w, tilt=tilt)


spec = dict(gw=gw, ico=ico, sc=sc, iz=iz, duo=duo, neon=neon, plain=plain, serif=serif, kin=kin, card=card, pop=pop, word=word)
_src = open(SPEC, encoding="utf-8").read()
exec("\n".join(l for l in _src.splitlines() if re.match(r"^[A-Z_0-9]+ *=", l) and not l.startswith("EV")), spec)
COLOR = tuple(spec.get("COLOR", (245, 170, 20)))      # duo English word
NEON = tuple(spec.get("NEON", (90, 255, 60)))         # neon numbers
Y_PLAIN = spec.get("Y_PLAIN", 1150)
Y_DUO = spec.get("Y_DUO", 470)
Y_NEON = spec.get("Y_NEON", 1220)
Y_POP = spec.get("Y_POP", 520)
TAG = tuple(spec.get("TAG", (255, 222, 40)))           # marker-tag background (style 13)
TAG_STYLE = spec.get("TAG_STYLE", "box")                # tag look: box (default) | pill | ribbon | outline
TAG_FG = tuple(spec.get("TAG_FG", (15, 15, 15)))         # tag text colour for pill/ribbon/outline
IZ_GOLD = tuple(spec.get("IZ_GOLD", (245, 175, 45))); IZ_SIZE = spec.get("IZ_SIZE", 100); IZ_Y = spec.get("IZ_Y", 1000); IZ_SH = spec.get("IZ_SH", 200); IZ_GLINT = spec.get("IZ_GLINT", False); IZ_TINT = tuple(spec.get("IZ_TINT", (255, 255, 255, 60))); IZ_BLUR = spec.get("IZ_BLUR", 12); IZ_WHITE = tuple(spec.get("IZ_WHITE", (255, 255, 255)))   # IZ_TINT = glass wash; dark e.g. (20,12,0,150) for busy light walls
POP2 = spec.get("POP2", False)        # style-13 upgrades: dark rim under light outlines, count-up prices, exit anim, tag auto-fit
AUTO_FACE = spec.get("AUTO_FACE", False)
COUNT = spec.get("COUNT", True)   # POP2 count-up prices (False = numbers appear fixed)  # move pops off detected faces
STRIKE = tuple(spec.get("STRIKE", (235, 30, 40)))     # strike-through colour for an old price in pop(top=(..., strike_t))
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


PLAIN_SIZE = spec.get("PLAIN_SIZE", 66)
NEON_SHADOW = spec.get("NEON_SHADOW", False)   # dark shadow behind coloured word() neon too (bright stores)
WORD_SIZE = spec.get("WORD_SIZE", 74); WORD_Y = spec.get("WORD_Y", 380)          # style 15 plain word
WORD_BIG = spec.get("WORD_BIG", 170); WORD_BIG_Y = spec.get("WORD_BIG_Y", 600)   # style 15 neon keyword
GRADE = spec.get("GRADE", "")                         # optional ffmpeg colour filter on the footage, e.g. "eq=saturation=1.3"
DUO_BIG = spec.get("DUO_BIG", 210)                     # size of an Arabic big word in duo()
DUO_POP = spec.get("DUO_POP", False)
DUO_SCRIM = spec.get("DUO_SCRIM")   # e.g. (40,20,8,170): soft horizontal band behind duo() text
DUO_FONT = spec.get("DUO_FONT", "lalezar")               # "amiri" = calligraphic Naskh big word (luxury / weddings)                   # bouncy pop-in for the duo big word


def F_PLAIN_FOR(text, size=None, maxw=940):
    """one font size per caption so typed-in text keeps its size; shrinks long lines to stay inside the frame"""
    size = size or PLAIN_SIZE
    if text not in _pf:
        while size > 34 and mask(text, font("Tajawal-ExtraBold.ttf", size)).width - 80 > maxw:
            size -= 4
        _pf[text] = font("Tajawal-ExtraBold.ttf", size)
    return _pf[text]
F_SERIF = lambda s: font("Fraunces.ttf", s, [144, 900, 60, 1])
F_BIG_AR = lambda s: font("Lalezar-Regular.ttf", s)
F_NASKH = lambda s: font("NotoNaskh.ttf", s, [650])   # style 15 plain word
F_AMIRI = lambda s: font("Amiri-Bold.ttf", s)          # style 15 neon keyword   # duo big word when it is Arabic (user wants Arabic-only)
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


def neon_soft(m, color):
    """style 15: soft neon — wide colour bloom + light core, no dark outline"""
    pad = 70
    big = Image.new("L", (m.width + 2 * pad, m.height + 2 * pad), 0); big.paste(m, (pad, pad))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    if min(color) > 220 or NEON_SHADOW:   # dark soft shadow first so it reads on bright ceilings/walls
        sh = Image.new("RGBA", big.size, (0, 0, 0, 255)); sh.putalpha(big.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(16)).point(lambda v: min(255, int(v * 1.5))))
        out.alpha_composite(sh)
    for r, a in (((40, 0.7), (16, 0.9), (5, 1.0)) if min(color) <= 220 else ((22, 0.45), (6, 0.8))):
        g = Image.new("RGBA", big.size, color + (255,)); g.putalpha(big.filter(ImageFilter.GaussianBlur(r)).point(lambda v: min(255, int(v * a * 1.8))))
        out.alpha_composite(g)
    core = tuple(int(c + (255 - c) * 0.45) for c in color)
    c = Image.new("RGBA", big.size, core + (255,)); c.putalpha(big); out.alpha_composite(c)
    return out


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
    if NEON_SHADOW:   # dark backing so gold/yellow neon reads on gold or white shelves
        sh = Image.new("RGBA", big.size, (0, 0, 0, 255)); sh.putalpha(big.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(22)).point(lambda v: min(255, int(v * 1.6))))
        out.alpha_composite(sh)
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


_CARDS = {}
GW_SIZE = spec.get("GW_SIZE", 200); GW_Y = spec.get("GW_Y", 1350)
GW_A = tuple(spec.get("GW_A", (255, 120, 210))); GW_B = tuple(spec.get("GW_B", (170, 60, 240))); GW_GLOW = tuple(spec.get("GW_GLOW", (200, 70, 255)))
FLASH = spec.get("FLASH", [])
EDGE = spec.get("EDGE", [])   # [(t0, t1)] purple glowing frame around the screen


def glowtxt(txt, size, col, glow):
    m = mask(txt, F_AR(size), pad=60)
    out = Image.new("RGBA", m.size, (0, 0, 0, 0))
    g = Image.new("RGBA", m.size, glow + (255,)); g.putalpha(m.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(18)).point(lambda v: min(255, v * 2)))
    out.alpha_composite(g)
    sh = Image.new("RGBA", m.size, (40, 0, 60, 255)); sh.putalpha(m.filter(ImageFilter.GaussianBlur(4)).point(lambda v: v * 150 // 255)); out.alpha_composite(sh, (0, 0))
    f = Image.new("RGBA", m.size, col + (255,)); f.putalpha(m); out.alpha_composite(f)
    return out


def gradtxt(txt, size):
    """chunky Lalezar word: vertical pink→purple gradient, light inner highlight, thin light rim, wide magenta glow"""
    m = mask(txt, F_BIG_AR(size), pad=80)
    h = m.height; gy = np.linspace(0, 1, h)[:, None, None]
    a, b = np.array(GW_A), np.array(GW_B)
    rgb = (a * (1 - gy) + b * gy).repeat(m.width, 1)
    hi = np.clip(1 - np.abs(np.linspace(0, 1, h) - 0.33) / 0.18, 0, 1)[:, None, None] * 0.35
    rgb = (rgb * (1 - hi) + 255 * hi).astype(np.uint8)
    out = Image.new("RGBA", m.size, (0, 0, 0, 0))
    g = Image.new("RGBA", m.size, GW_GLOW + (255,)); g.putalpha(m.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(30)).point(lambda v: min(255, int(v * 1.6))))
    out.alpha_composite(g)
    sh = Image.new("RGBA", m.size, (60, 0, 80, 255)); sh.putalpha(m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(6)).point(lambda v: v * 170 // 255)); out.alpha_composite(sh, (0, 8))
    rim = Image.new("RGBA", m.size, (255, 235, 250, 255)); rim.putalpha(m.filter(ImageFilter.MaxFilter(7))); out.alpha_composite(rim)
    f = Image.fromarray(np.dstack([rgb, np.asarray(m)]), "RGBA"); out.alpha_composite(f)
    return out


def icon_img(path, w, glow, rot):
    im = Image.open(path).convert("RGBA"); im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    pad = 70; out = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0); a.paste(im.split()[3], (pad, pad))
    if glow:
        g = Image.new("RGBA", out.size, tuple(glow) + (255,)); g.putalpha(a.filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.GaussianBlur(26)).point(lambda v: min(255, int(v * 1.4)))); out.alpha_composite(g)
    sh = Image.new("RGBA", out.size, (0, 0, 0, 255)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(14)).point(lambda v: v * 110 // 255))
    out.alpha_composite(sh, (0, 0)); out.alpha_composite(im, (pad, pad))
    return out


def screen_card(path, w, tilt):
    im = Image.open(path).convert("RGBA"); hgt = int(im.height * w / im.width)
    im = im.resize((w, hgt), Image.LANCZOS)
    hgt = min(hgt, int(w * 0.62)); im = im.crop((0, int(im.height * 0.06), w, int(im.height * 0.06) + hgt))   # top strip of the page, like the ref
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, hgt - 1), 28, fill=255); im.putalpha(m)
    # perspective: far edge narrower (tilt=1 right side farther, -1 left)
    pad = 60; d = int(w * 0.10)
    W2, H2 = w + 2 * pad, hgt + 2 * pad
    if tilt >= 0: quad = (0, 0, 0, hgt, w, hgt + d, w, -d)
    else: quad = (0, -d, 0, hgt + d, w, hgt, w, 0)
    big = Image.new("RGBA", (w, hgt + 2 * d), (0, 0, 0, 0)); big.paste(im, (0, d))
    q = [quad[0], quad[1] + d, quad[2], quad[3] + d, quad[4], quad[5] + d, quad[6], quad[7] + d]
    # PIL QUAD maps output rect corners (UL, LL, LR, UR) to input quad: invert by warping the card into the quad
    tgt = Image.new("RGBA", big.size, (0, 0, 0, 0))
    src_pts = [(0, d), (0, d + hgt), (w, d + hgt), (w, d)]
    dst_pts = [(q[0], q[1]), (q[2], q[3]), (q[4], q[5]), (q[6], q[7])]
    A = []; B = []
    for (xs, ys), (xd, yd) in zip(src_pts, dst_pts):
        A.append([xd, yd, 1, 0, 0, 0, -xs * xd, -xs * yd]); B.append(xs)
        A.append([0, 0, 0, xd, yd, 1, -ys * xd, -ys * yd]); B.append(ys)
    coef = np.linalg.solve(np.array(A, float), np.array(B, float))
    tgt = big.transform(big.size, Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)
    out = Image.new("RGBA", (W2, tgt.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0); a.paste(tgt.split()[3], (pad, pad))
    g = Image.new("RGBA", out.size, (190, 90, 255, 255)); g.putalpha(a.filter(ImageFilter.GaussianBlur(30)).point(lambda v: v * 170 // 255)); out.alpha_composite(g)
    out.alpha_composite(tgt, (pad, pad))
    return out


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
    """fill colour with a thick dark outline + soft drop shadow (bold TikTok caption look).
    col may be ((fill), (outline)) for a coloured word with a light outline, e.g. brand blue on white."""
    oc = (25, 20, 20)
    if isinstance(col[0], (tuple, list)):
        col, oc = tuple(col[0]), tuple(col[1])
    pad = stroke + 20
    big = Image.new("L", (m.width + 2 * pad, m.height + 2 * pad), 0); big.paste(m, (pad, pad))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", big.size, (0, 0, 0, 255)); sh.putalpha(big.filter(ImageFilter.MaxFilter(stroke * 2 + 1)).filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * 150 // 255))
    out.alpha_composite(sh, (0, 8))
    if POP2 and sum(oc) > 500:   # light outline gets a thin dark rim so it reads on white/beige backgrounds too
        rim = Image.new("RGBA", big.size, (20, 18, 18, 255)); rim.putalpha(big.filter(ImageFilter.MaxFilter(stroke * 2 + 7)))
        out.alpha_composite(rim)
    ol = Image.new("RGBA", big.size, oc + (255,)); ol.putalpha(big.filter(ImageFilter.MaxFilter(stroke * 2 + 1)))
    out.alpha_composite(ol)
    f = Image.new("RGBA", big.size, col + (255,)); f.putalpha(big); out.alpha_composite(f)
    return out


def marker_tag(txt, size=58):
    if TAG_STYLE == "outline":   # no box: white text with dark outline, like the big words but smaller
        return outlined(mask(txt, font("Tajawal-Black.ttf", 66), pad=18), TAG_FG, stroke=7)
    if TAG_STYLE in ("pill", "ribbon"):   # rounded brand-colour pill (ribbon = pill + light inner line)
        m = mask(txt, font("Tajawal-Black.ttf", size), pad=18)
        w, h = m.width + 50, m.height + 4
        out = Image.new("RGBA", (w + 24, h + 28), (0, 0, 0, 0))
        sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((14, 18, w + 8, h + 20), h // 2, fill=(0, 0, 0, 120))
        out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
        d = ImageDraw.Draw(out); d.rounded_rectangle((10, 8, w, h + 8), h // 2, fill=TAG + (255,))
        if TAG_STYLE == "ribbon":
            d.rounded_rectangle((18, 16, w - 8, h), (h - 16) // 2, outline=(255, 255, 255, 200), width=3)
        ink = Image.new("RGBA", m.size, TAG_FG + (255,)); ink.putalpha(m)
        out.alpha_composite(ink, (10 + (w - 10 - m.width) // 2, 8 + (h - m.height) // 2))
        return out
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
if AUTO_FACE:   # move style-13 pops that would sit on a face
    import cv2
    _cas = [cv2.CascadeClassifier(cv2.data.haarcascades + n) for n in ("haarcascade_frontalface_default.xml", "haarcascade_profileface.xml")]
    _cap = cv2.VideoCapture(SRC)
    def _faces(tt):
        _cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, tt - T0) * 1000); ok, fr = _cap.read()
        if not ok: return []
        fr = cv2.resize(fr, (W, H)); g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY); out = []
        for cc in _cas:
            for (x, y_, w, h) in cc.detectMultiScale(g, 1.1, 7, minSize=(90, 90)): out.append((y_ - 40, y_ + h + 60))
        return out
    def _band(e, y):
        big = e["big"][4] if e["big"] and len(e["big"]) > 4 else 200
        return (y - (205 + big * 0.45 + 60 if e["top"] else big * 0.5 + 10), y + (big * 0.85 + 60 if e["tag"] else big * 0.5 + 10))
    for e in EV:
        if e["k"] != "pop" or e.get("fix"): continue
        fs = [f for tt in (e["t0"] + 0.15, (e["t0"] + e["t1"]) / 2, e["t1"] - 0.15) for f in _faces(tt)]
        if not fs: continue
        y0 = e["y"] or Y_POP
        hit = lambda y: any(a < _band(e, y)[1] and _band(e, y)[0] < b for a, b in fs)
        if not hit(y0): continue
        for y in sorted((380, 560, 800, 1050, 1300, 1450), key=lambda v: abs(v - y0)):
            b0, b1 = _band(e, y)
            if b0 >= 230 and b1 <= 1700 and not hit(y):
                print(f"face: pop {e['t0']:.2f} y {y0} -> {y}", file=sys.stderr); e["y"] = y; break


def sprite(key, make):
    if key not in _cache:
        _cache[key] = make()
    return _cache[key]


def ease(p):
    p = min(max(p, 0.0), 1.0); return 1 - (1 - p) ** 3


def _glint(sp, dt, dur=0.8):
    """one diagonal light sweep across a text sprite (dt = seconds since the sweep started); bright core + soft glow"""
    if not (0 <= dt <= dur): return sp
    q = dt / dur
    a = np.asarray(sp.split()[3]).astype(np.float32)
    xx = np.arange(sp.width)[None, :] + np.arange(sp.height)[:, None] * 0.45
    cx_ = -sp.width * 0.25 + sp.width * 1.5 * q
    band = np.clip(1 - np.abs(xx - cx_) / (sp.width * 0.07), 0, 1)
    out = sp.copy()
    glow = Image.new("RGBA", sp.size, (255, 255, 255, 0)); glow.putalpha(Image.fromarray((a * band).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)))
    core = Image.new("RGBA", sp.size, (255, 255, 255, 0)); core.putalpha(Image.fromarray((a * np.clip(band * 1.6, 0, 1)).astype(np.uint8)))
    out.alpha_composite(glow); out.alpha_composite(glow); out.alpha_composite(core)
    return out


_PS = [1.0]   # extra scale for the current pop (exit animation)


def put(c, sp, cx, cy, a=1.0, s=1.0):
    s *= _PS[0]
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
        if DUO_SCRIM:   # soft chocolate band behind the block (white/gold stores ate gold text)
            sk = _CARDS.get("_scrim")
            if sk is None:
                hh = 520; g = np.exp(-((np.arange(hh) - hh / 2) / (hh * 0.28)) ** 2)
                sk = Image.fromarray((np.repeat(g[:, None], W, 1) * DUO_SCRIM[3]).astype(np.uint8)); _CARDS["_scrim"] = sk
            ov = Image.new("RGBA", sk.size, tuple(DUO_SCRIM[:3]) + (255,)); ov.putalpha(sk.point(lambda v: int(v * fa)))
            c.alpha_composite(ov, (0, int(y - 60 - sk.height / 2)))
        sa = sprite(("ar", ar), lambda: shadowed(fitted(ar, F_AR, 104), (255, 255, 255)))
        se = sprite(("en", en), lambda: shadowed(fitted(en, (F_AMIRI if DUO_FONT == "amiri" else F_BIG_AR) if re.search(r"[\u0600-\u06ff]", en) else F_SERIF,
                                                           DUO_BIG if re.search(r"[\u0600-\u06ff]", en) else 250), COLOR, sh=235 if NEON_SHADOW else 120, blur=16 if NEON_SHADOW else 10))
        pa, pe = ease((t - ta) / 0.3), ease((t - te) / 0.35)
        put(c, sa, W / 2, y - se.height * 0.32 - sa.height / 2 + 30 + 20 * (1 - pa), pa * fa)
        if t >= te:
            if DUO_POP:   # fast scale-in with a damped bounce
                q = (t - te) / 0.16
                sc = 1.45 - 0.45 * ease(min(1, q)) + (0.08 * np.sin((t - te - 0.16) * 22) * np.exp(-(t - te - 0.16) * 6) if q > 1 else 0)
                put(c, se, W / 2, y + 10, min(1, q * 2) * fa, sc)
            else:
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
        if POP2:   # exit: shrink a little and lift while fading
            ex = ease(min(1.0, max(0.0, (e["t1"] - t) / 0.2)))
            y -= 30 * (1 - ex)
            _PS[0] = 0.88 + 0.12 * ex
        def bigspr(txt, col):
            return sprite(("popb", txt, col), lambda: outlined(fitted(txt, F_BIG_AR, 200, 940), col))
        if e["top"] and t >= e["top"][1]:
            txt, tt, col = e["top"][:3]
            sp = bigspr(txt, tuple(col)); p = (t - tt) / 0.14
            st = e["top"][3] if len(e["top"]) > 3 else None   # old price: red strike line swiped right→left from time st
            if st is not None and t >= st:
                q = ease((t - st) / 0.22)
                sp = sp.copy(); d = ImageDraw.Draw(sp)
                x1 = sp.width - 26; x0 = x1 - (sp.width - 52) * q; yy = sp.height * 0.52
                d.line((x0, yy + 4, x1, yy + 4), fill=(25, 20, 20, 255), width=24)
                d.line((x0, yy, x1, yy), fill=STRIKE + (255,), width=14)
            put(c, sp, W / 2, y - (205 if not e["big"] or len(e["big"]) < 5 else 205 + (e["big"][4] - 200) * 0.75), min(1, p * 2) * fa, 1.3 - 0.3 * ease(p))
        if e["big"] and t >= e["big"][1]:
            txt, tt, col = e["big"][:3]
            times = e["big"][3] if len(e["big"]) > 3 and e["big"][3] else None
            size = e["big"][4] if len(e["big"]) > 4 else 200
            col = tuple(tuple(c_) for c_ in col) if isinstance(col[0], (tuple, list)) else tuple(col)
            if times:   # word-by-word: final RTL layout fixed, each word pops at its own time
                words = txt.split()
                times = list(times) + [times[-1]] * (len(words) - len(times))   # never drop a word when the list is short
                sps = [sprite(("popw", w_, col, size), lambda w_=w_: outlined(mask(w_, F_BIG_AR(size)), col)) for w_ in words]
                gap = -40
                total = sum(sp.width for sp in sps) + gap * (len(sps) - 1)
                k = min(1.0, 980 / total)
                x = W / 2 + total * k / 2
                for sp, tw in zip(sps, times):
                    cx = x - sp.width * k / 2; x -= (sp.width + gap) * k
                    if t >= tw:
                        p = (t - tw) / 0.14
                        w_ = words[sps.index(sp)] if sp in sps else ""
                        if POP2 and COUNT and re.fullmatch(r"[0-9]+([.,][0-9]+)?%?", w_) and t - tw < 0.4:   # price counts up
                            num = float(w_.rstrip("%").replace(",", "")); v = num * ease((t - tw) / 0.4)
                            dig = (f"{v:.2f}" if "." in w_ else str(int(round(v)))) + ("%" if w_.endswith("%") else "")
                            sp = sprite(("popw", dig, col, size), lambda d_=dig: outlined(mask(d_, F_BIG_AR(size)), col))
                        put(c, sp, cx, y, min(1, p * 2) * fa, k * (1.3 - 0.3 * ease(p)))
            else:
                sp = sprite(("popb", txt, col, size), lambda: outlined(fitted(txt, F_BIG_AR, size, 940), col))
                p = (t - tt) / 0.14
                beat = 0.07 * np.exp(-(t - tt - 0.14) * 5) * np.sin((t - tt) * 18) if p > 1 and size > 200 else 0
                put(c, sp, W / 2, y, min(1, p * 2) * fa, 1.3 - 0.3 * ease(p) + beat)
        if e["tag"] and t >= e["tag"][1]:
            txt, tt = e["tag"][:2]
            sp = sprite(("popt", txt), lambda: marker_tag(txt))
            if sp.width > 980:   # long tag: shrink to fit the frame
                sp = sprite(("poptf", txt), lambda: sp.resize((980, int(sp.height * 980 / sp.width)), Image.LANCZOS))
            p = ease((t - tt) / 0.2)
            ty = e["tag"][2] if len(e["tag"]) > 2 else y + ((e["big"][4] if len(e["big"]) > 4 else 200) * 0.85 if e["big"] else 0)
            put(c, sp, W / 2, ty + 12 * (1 - p), p * fa)
    elif k == "iz":
        P = 40; gap = int(IZ_SIZE * 0.26)
        def wid(sz):
            f = F_AR(sz); return max(sum(mask(w[0], f).width - 2 * P for w in row) + gap * (len(row) - 1) for row in e["rows"])
        sz = IZ_SIZE; w0 = wid(sz)
        if w0 > 900: sz = int(sz * 900 / w0)
        fnt = F_AR(sz); gap = int(sz * 0.26)
        rows = []
        for row in e["rows"]:
            ws = []
            for txt, tw, cc in row:
                if cc == "p":
                    psz = int(sz * 1.3)
                    def _metal(txt=txt, psz=psz):
                        m_ = mask(txt, F_AR(psz)); fill = Image.new("RGBA", m_.size)
                        gy = np.linspace(0, 1, m_.height)[:, None]
                        top, bot = np.array([255, 255, 255]), np.array([150, 185, 230])
                        rgb = (top * (1 - gy[..., None]) + bot * gy[..., None]).repeat(m_.width, 1).astype(np.uint8)
                        fill = Image.fromarray(np.dstack([rgb, np.asarray(m_)]), "RGBA")
                        out = shadowed(m_, (255, 255, 255), sh=IZ_SH, blur=IZ_BLUR, dy=5)
                        out.alpha_composite(fill, (0, 0)); return out
                    sp = sprite(("izp2", txt, psz), _metal)
                else:
                    col = IZ_GOLD if cc == "g" else IZ_WHITE
                    sp = sprite(("iz", txt, col, sz), lambda txt=txt, col=col: shadowed(mask(txt, fnt), col, sh=IZ_SH, blur=IZ_BLUR, dy=5))
                ws.append((sp, tw, cc))
            rows.append(ws)
        lh = int(sz * 1.25)
        hs = [max(sp.height for sp, _, _ in r) - 2 * P for r in rows]
        y0 = (e["y"] or IZ_Y) - lh * (len(rows) - 1) / 2
        ys = [y0]
        for ri in range(1, len(rows)):
            ys.append(ys[-1] + max(lh, (hs[ri - 1] + hs[ri]) / 2 + sz * 0.15))
        widths = [sum(sp.width - 2 * P for sp, _, _ in r) + gap * (len(r) - 1) for r in rows]
        if e["glass"]:
            tot = max(widths) + 70; gx0 = W / 2 - tot / 2; gy0 = ys[0] - hs[0] / 2 - 26; gh = ys[-1] + hs[-1] / 2 + 26 - gy0
            box = c.crop((int(gx0), int(gy0), int(gx0 + tot), int(gy0 + gh))).filter(ImageFilter.GaussianBlur(22)).convert("RGBA")
            box.alpha_composite(Image.new("RGBA", box.size, IZ_TINT))
            m = Image.new("L", box.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, box.width - 1, box.height - 1), 30, fill=int(255 * fa))
            c.paste(box, (int(gx0), int(gy0)), m)
        for ri, ws in enumerate(rows):
            x = W / 2 + widths[ri] / 2; cy = ys[ri]
            for sp, tw, cc in ws:
                cw = sp.width - 2 * P; cx = x - cw / 2; x -= cw + gap
                if t < tw: continue
                if cc == "p":   # rise from a hidden baseline, then one glint
                    p = ease((t - tw) / 0.35)
                    hv = max(1, int(sp.height * p))
                    part = sp.crop((0, 0, sp.width, hv))
                    top = cy - sp.height / 2 + (sp.height - hv)
                    if p >= 1: part = _glint(sp, t - tw - 0.35)
                    put(c, part, cx, top + part.height / 2, fa)
                    continue
                if cc == "g" and IZ_GLINT and t - tw >= 0.35:
                    put(c, _glint(sp, t - tw - 0.35), cx, cy, fa); continue
                p = ease((t - tw) / 0.3)
                s_ = sp if p >= 1 else sp.filter(ImageFilter.GaussianBlur(9 * (1 - p)))
                put(c, s_, cx - 26 * (1 - p), cy, p * fa)
        if e.get("line") and rows:
            tl = max(tw for _, tw, _ in rows[0]) + 0.25
            if t >= tl:
                q = ease((t - tl) / 0.5); lw = widths[0] + 40
                x1 = W / 2 + lw / 2; x0 = x1 - lw * q; ly = ys[0] + hs[0] / 2 + 14
                ov = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
                d.rounded_rectangle((x0, ly + 3, x1, ly + 11), 4, fill=(0, 0, 0, int(90 * fa)))
                d.rounded_rectangle((x0, ly, x1, ly + 7), 4, fill=IZ_GOLD + (int(255 * fa),))
                c.alpha_composite(ov)
    elif k == "gw":
        y = e["y"] or GW_Y; sz = e["size"] or GW_SIZE
        if e["top"] and t >= e["tt"]:
            sp = sprite(("gwt", e["top"]), lambda: glowtxt(e["top"], int(sz * 0.42), (255, 255, 255), GW_GLOW))
            p = ease((t - e["tt"]) / 0.25)
            put(c, sp, e["x"] + 0, y - sz * 0.62 + 30 * (1 - p), p * fa)
        if t >= e["tb"]:
            sp = sprite(("gwb", e["big"], sz), lambda: gradtxt(e["big"], sz))
            q = (t - e["tb"]) / 0.32
            sc_ = 0.4 + 0.6 * ease(q) + (0.12 * np.sin(min(q, 1) * np.pi) if q < 1 else 0) + 0.04 * np.exp(-(t - e["tb"] - 0.32) * 6) * np.sin((t - e["tb"]) * 20) * (q >= 1)
            put(c, sp, e["x"], y, min(1, q * 2.5) * fa, sc_)
    elif k == "ico":
        if t >= e["t"]:
            sp = sprite(("ico", e["path"], e["w"], e["glow"], e["rot"]), lambda: icon_img(e["path"], e["w"], e["glow"], e["rot"]))
            q = (t - e["t"]) / 0.35
            sc_ = 0.3 + 0.7 * ease(q) + (0.15 * np.sin(min(q, 1) * np.pi) if q < 1 else 0)
            fy = 10 * np.sin((t - e["t"]) * 2.6)
            put(c, sp, e["cx"], e["cy"] + fy, min(1, q * 2) * fa, sc_)
    elif k == "sc":
        import glob as _g
        fl = _CARDS.setdefault(e["frames"], sorted(_g.glob(e["frames"] + "/*.png")))
        i = min(len(fl) - 1, max(0, int((t - e["t0"] + e["start"]) * e["fps"])))
        sp = sprite(("sc", fl[i], e["w"], e["tilt"]), lambda: screen_card(fl[i], e["w"], e["tilt"]))
        if len(_cache) > 900: _cache.clear()
        p = ease((t - e["t0"]) / 0.4)
        put(c, sp, e["cx"], e["cy"] - 160 * (1 - p), p * fa, 0.85 + 0.15 * p)
    elif k == "card":
        sp = sprite(("card", e["path"], e["w"]), lambda: card_img(e["path"], e["w"], e["r"]))
        p = ease((t - e["t"]) / 0.3)
        if t >= e["t"]:
            put(c, sp, e["cx"], e["cy"] + 140 * (1 - p), p * fa, 0.9 + 0.1 * p)
    elif k == "word":
        if e["col"]:
            sz = e["size"] or WORD_BIG
            sp = sprite(("wd", e["text"], tuple(e["col"]), sz), lambda: neon_soft(fitted(e["text"], F_AMIRI, sz, 900), tuple(e["col"])))
            y = e["y"] or WORD_BIG_Y
        else:
            sz = e["size"] or WORD_SIZE
            sp = sprite(("wd", e["text"], None, sz), lambda: shadowed(fitted(e["text"], F_NASKH, sz, 900), (255, 255, 255), sh=170, blur=9, dy=4))
            y = e["y"] or WORD_Y
        p = ease((t - e["t0"]) / 0.12)
        put(c, sp, e["x"], y + 10 * (1 - p), p * fa, 1.06 - 0.06 * p)
    elif k == "serif":
        y = e["y"] or 1480
        sp = sprite(("sf", e["text"]), lambda: shadowed(fitted(e["text"], F_SERIF, 120), (255, 255, 255), sh=140))
        put(c, sp, W / 2, y, ease((t - e["t0"]) / 0.5) * fa)


ZOOM = spec.get("ZOOM", [])   # [(t0, t1), ...] gentle punch-in windows


def composite(raw, t):
    c = Image.frombytes("RGB", (W, H), raw)
    for z0, z1 in ZOOM:
        if z0 <= t < z1:
            k_ = min(ease((t - z0) / 0.45), ease((z1 - t) / 0.45)); s_ = 1 + 0.07 * k_
            if s_ > 1.001:
                nw, nh = int(W * s_), int(H * s_); c = c.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    c = c.convert("RGBA")
    for e0, e1 in EDGE:
        if e0 <= t < e1:
            k_ = min(ease((t - e0) / 0.3), ease((e1 - t) / 0.5)) * (0.75 + 0.25 * np.sin(t * 9))
            fr = _CARDS.get("_edge")
            if fr is None:
                m_ = Image.new("L", (W, H), 0); d_ = ImageDraw.Draw(m_); d_.rectangle((0, 0, W - 1, H - 1), outline=255, width=14)
                fr = m_.filter(ImageFilter.GaussianBlur(18)).point(lambda v: min(255, int(v * 2.2))); _CARDS["_edge"] = fr
            ov = Image.new("RGBA", (W, H), (150, 70, 255, 255)); ov.putalpha(fr.point(lambda v: int(v * k_))); c.alpha_composite(ov)
    for f0 in FLASH:   # quick white flash on a beat
        if f0 <= t < f0 + 0.16:
            k_ = 1 - (t - f0) / 0.16
            c.alpha_composite(Image.new("RGBA", (W, H), (255, 245, 255, int(150 * k_))))
    for e in EV:
        if e["t0"] <= t < e["t1"]:
            _PS[0] = 1.0
            draw(c, t, e)
    _PS[0] = 1.0
    return c.convert("RGB")


dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", (GRADE + "," if GRADE else "") + f"scale={W}:{H},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
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
    enc.stdin.write(composite(b, i / FPS + T0).tobytes()); i += 1
enc.stdin.close(); enc.wait()
print("done", i, "frames", file=sys.stderr)
