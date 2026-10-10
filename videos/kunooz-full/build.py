"""Builds the talking-head-recut composition for the full Kunooz video.

Writes storyboard.json, public/cards/*.html and public/index.html.
Cards follow the talking-head-recut card contract (scoped <style>, no
<script>, motion declared with data-anim-*); every data-anim declaration
is compiled into the single master GSAP timeline here.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, "public")
FPS = 30
W, H = 1080, 1920

# Pause cuts (source seconds) removed with HyperFrames jump cuts.
KEEP = [(0.0, 1.58), (1.78, 7.82), (8.03, 45.12)]


def o(src):
    """Source time -> output time after the jump cuts."""
    t = 0.0
    for a, b in KEEP:
        if src <= b:
            return round(t + max(src, a) - a, 3)
        t += b - a
    return round(t, 3)


DUR = round(sum(b - a for a, b in KEEP), 2)

# ---------------------------------------------------------------- helpers
_anims = []  # (selector, kind, at, dur, params) for the card being built
_card = None


def A(eid, kind, at, dur, **p):
    _anims.append((eid, kind, at, dur, p))
    attrs = f'data-anim="{kind}" data-anim-at="{at}" data-anim-duration="{dur}"'
    for k, v in p.items():
        attrs += f' data-anim-{k.replace("_", "-")}="{v}"'
    return attrs


def el(tag, eid, cls, inner="", anim=None, style=""):
    eid = f"{_card}-{eid}"
    a = ""
    if anim:
        kind, at, dur, *rest = anim
        a = " " + A(eid, kind, at, dur, **(rest[0] if rest else {}))
    st = f' style="{style}"' if style else ""
    c = f' class="{cls}"' if cls else ""
    return f'<{tag} id="{eid}"{c}{a}{st}>{inner}</{tag}>'


def words(text):
    return " ".join(f'<span class="char">{w}</span>' for w in text.split())


def ltr(s):
    return f'<span style="direction:ltr;unicode-bidi:isolate;display:inline-block">{s}</span>'


CARDS = []


def card(cid, start, end, zone, layout, intent, hints, css, body, accent=0):
    global _card
    CARDS.append(dict(id=cid, start=start, end=end, zone=zone, layout=layout,
                      intent=intent, hints=hints, css=css, body=body,
                      anims=list(_anims), accent=accent))
    _anims.clear()


def begin(cid):
    global _card
    _card = cid
    _anims.clear()


def scope(cid, css):
    return re.sub(r"(^|})\s*([^{}@]+?)\s*{",
                  lambda m: f'{m.group(1)}\n.card[data-card-id="{cid}"] {m.group(2).strip()} {{',
                  css)


# ---------------------------------------------------------------- cards
# c01 · geom × overlay — the hook
begin("k01")
card("k01", 0.0, o(1.52), "video-overlay", "overlay",
     "hook: discount up to 70%", {"kicker": "خصم يوصل إلى", "title": "70%"},
     """
.root{position:absolute;inset:0;direction:rtl;font-family:'Lalezar','Tajawal',sans-serif}
.slab{position:absolute;right:0;top:150px;width:0;height:420px;background:#0a0a0a}
.lime{position:absolute;right:0;top:110px;width:440px;height:86px;background:#d4ff00}
.pink{position:absolute;left:70px;top:470px;width:150px;height:150px;background:#ff2e88}
.kick{position:absolute;right:56px;top:120px;font-size:64px;line-height:1;color:#0a0a0a;padding-top:10px}
.big{position:absolute;right:50px;top:200px;font:700 300px/1 'Inter';color:#d4ff00;letter-spacing:-.04em;direction:ltr}
.big .pc{-webkit-text-stroke:6px #d4ff00;color:transparent}
""",
     el("span", "slab", "slab", anim=("grow-x", 0.0, 0.35, {"target_w": 820}))
     + el("span", "lime", "lime", anim=("slide-in", 0.05, 0.3, {"from": "right", "distance": 440}))
     + el("span", "pink", "pink", anim=("scale-pop", 0.35, 0.35))
     + el("div", "kick", "kick", "خصم يوصل إلى", anim=("fade-in", 0.1, 0.25))
     + f'<div class="big">{el("span", "num", "", "0", anim=("count-up", 0.15, 0.6, {"from": 0, "to": 70, "format": ".0f"}))}<span class="pc">%</span></div>')

# c02 · xhs × overlay — free delivery
begin("k02")
card("k02", o(1.52), o(3.6), "video-overlay", "overlay",
     "free home delivery", {"title": "توصيل لباب بيتك", "chip": "مجاناً"},
     """
.root{position:absolute;inset:0;direction:rtl;font-family:'Marhey','Tajawal',sans-serif}
.box{position:absolute;left:60px;right:60px;top:150px;padding:40px 44px 34px;background:#fff8f0;border-radius:44px;box-shadow:0 30px 70px -20px rgba(0,0,0,.45)}
.tags{display:flex;gap:14px;margin-bottom:18px}
.tag{font-size:30px;color:#ff2e63;background:#ffe3ea;border-radius:999px;padding:8px 22px}
.t{font-size:96px;line-height:1.15;color:#1b1b1b;font-weight:700}
.free{display:inline-block;margin-top:16px;font-size:92px;color:#fff;background:#ff2e63;border-radius:28px;padding:4px 40px 14px}
.row{display:flex;gap:30px;margin-top:24px;font:700 30px 'Inter';color:#8a7d78;direction:ltr;justify-content:flex-end}
""",
     el("div", "box", "box",
        '<div class="tags">' + el("span", "tg1", "tag", "#توصيل", anim=("fade-in", 0.1, 0.25))
        + el("span", "tg2", "tag", "#كنوز_السعادة", anim=("fade-in", 0.2, 0.25)) + "</div>"
        + el("div", "t", "t", words("توصيل لباب بيتك"), anim=("kinetic-chars", 0.15, 0.3, {"stagger": 0.12, "pattern": "pop"}))
        + el("div", "free", "free", "مجاناً", anim=("scale-pop", o(3.06) - o(1.52), 0.3))
        + el("div", "row", "row", "♥ 2.4k &nbsp; 💬 312", anim=("fade-in", 0.9, 0.3)),
        anim=("slide-in", 0.0, 0.35, {"from": "top", "distance": 120})))

# c03 · minimal × overlay — instalments
begin("k03")
card("k03", o(3.6), o(5.08), "video-overlay", "overlay",
     "instalments available", {"title": "متوفر تقسيط"},
     """
.root{position:absolute;inset:0;direction:rtl;font-family:'Tajawal',sans-serif}
.band{position:absolute;left:0;right:0;top:1270px;height:300px;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center}
.s{font:800 40px/1 'Tajawal';color:#777;letter-spacing:.02em}
.t{font:900 150px/1.1 'Tajawal';color:#000;margin-top:10px}
.u{position:absolute;bottom:34px;height:10px;width:0;background:#000}
""",
     el("div", "band", "band",
        el("div", "s", "s", "وفوقها متوفر عندهم", anim=("fade-in", 0.15, 0.25))
        + el("div", "t", "t", "تقسيط", anim=("blur-in", o(4.72) - o(3.6), 0.3))
        + el("span", "u", "u", anim=("grow-x", o(4.72) - o(3.6) + 0.1, 0.35, {"target_w": 380})),
        anim=("mask-reveal", 0.0, 0.3, {"direction": "right"})))

# c04 · swiss × overlay — the website (site video pops in on "موقع")
begin("k04")
SITE1 = (o(6.42) - 0.12, o(9.5) - 0.05)
card("k04", o(5.8), o(9.5), "video-overlay", "overlay",
     "available on the new website + all branches", {"title": "موقع كنوز السعادة الجديد", "detail": "وفي جميع الفروع"},
     """
.root{position:absolute;inset:0;direction:rtl;font-family:'Cairo','Tajawal',sans-serif}
.panel{position:absolute;right:40px;top:120px;width:560px;background:#fff;padding:30px 34px 34px}
.r1{height:6px;background:#111;width:0}
.r2{height:2px;background:#111;margin-top:6px;width:0}
.k{font:700 26px/1 'Inter';letter-spacing:.24em;color:#e8190f;margin:22px 0 6px;direction:ltr;text-align:right}
.t{font:900 76px/1.15 'Cairo';color:#111}
.t b{color:#e8190f}
.d{display:flex;align-items:center;gap:16px;margin-top:22px;font:800 44px/1 'Cairo';color:#111}
.d i{display:inline-block;width:26px;height:26px;background:#e8190f}
""",
     el("div", "panel", "panel",
        el("div", "r1", "r1", anim=("grow-x", 0.0, 0.3, {"target_w": 492}))
        + el("div", "r2", "r2", anim=("grow-x", 0.08, 0.3, {"target_w": 492}))
        + el("div", "k", "k", "KUNOOZ · ONLINE", anim=("fade-in", 0.2, 0.25))
        + el("div", "t", "t", words("موقع كنوز <b>السعادة</b> الجديد").replace("<span class=\"char\"><b>السعادة</b></span>", "<span class=\"char\"><b>السعادة</b></span>"),
             anim=("kinetic-chars", o(6.42) - o(5.8), 0.25, {"stagger": 0.22, "pattern": "pop"}))
        + el("div", "d", "d", "<i></i>وفي جميع الفروع", anim=("slide-in", o(8.38) - o(5.8), 0.3, {"from": "right", "distance": 60})),
        anim=("fade-in", 0.0, 0.2)))

# c05 · editorial × stack — baby milk
begin("k05")
card("k05", o(9.5), o(12.52), "lower-third", "stack",
     "buy two baby milk, third 60% off", {"title": "حليب الأطفال", "detail": "الثالثة خصم 60%"},
     """
.root{position:absolute;inset:0;direction:rtl;background:#f6efe4;font-family:'El Messiri','Tajawal',serif;color:#1d1a17}
.block{position:absolute;left:0;top:0;width:0;height:100%;background:#ff3a2d}
.k{position:absolute;right:60px;top:70px;font:700 40px/1 'El Messiri';color:#ff3a2d}
.t{position:absolute;right:60px;top:130px;font:700 120px/1.15 'El Messiri'}
.d{position:absolute;right:60px;top:300px;font:600 56px/1.3 'El Messiri';color:#5a524b}
.big{position:absolute;right:60px;left:200px;top:400px;display:flex;flex-direction:column;align-items:flex-start;gap:0}
.big .w{font:700 84px/1 'El Messiri'}
.big .n{font:700 190px/1 'Inter';color:#ff3a2d;direction:ltr;margin-top:10px}
""",
     el("span", "block", "block", anim=("grow-x", 0.1, 0.5, {"target_w": 150}))
     + el("div", "k", "k", "— عرض الحليب", anim=("fade-in", 0.15, 0.3))
     + el("div", "t", "t", "حليب الأطفال", anim=("mask-reveal", o(10.54) - o(9.5) - 0.2, 0.4, {"direction": "right"}))
     + el("div", "d", "d", "خذ لك أي حبتين…", anim=("fade-in", 0.25, 0.3))
     + '<div class="big">' + el("span", "w", "w", "والثالثة خصم", anim=("fade-in", o(11.18) - o(9.5), 0.25))
     + f'<span class="n">{el("span", "n", "", "0", anim=("count-up", o(11.92) - o(9.5), 0.45, {"from": 0, "to": 60, "format": ".0f"}))}%</span></div>')

# c06 · audit × split — baby care prices (receipt)
begin("k06")
b = o(12.52)
card("k06", b, o(16.92), "side-panel", "split",
     "Baby Joy box 85, bag 75, Pampers carton 77", {"rows": ["بيبي جوي البوكس 85", "الكيس 75", "كرتون بامبرز 77"]},
     """
.root{position:absolute;inset:0;direction:rtl;background:#efe4c8;font-family:'Changa','Tajawal',sans-serif;color:#2a2118}
.paper{position:absolute;left:70px;right:70px;top:60px;bottom:40px;background:#fbf6e9;box-shadow:0 18px 40px -18px rgba(0,0,0,.35);padding:40px 50px}
.h{display:flex;justify-content:space-between;align-items:baseline;border-bottom:3px double #2a2118;padding-bottom:16px}
.h .t{font:700 64px/1 'Changa'}
.h .m{font:400 26px/1 'Inter';color:#8b1d1d;direction:ltr}
.row{display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px dashed #b9ab8a;padding:22px 0}
.row .n{font:600 52px/1.1 'Changa'}
.row .p{font:700 76px/1 'Inter';direction:ltr}
.row .p small{font:600 30px 'Changa';color:#8b1d1d;margin-left:8px}
.stamp{position:absolute;left:60px;bottom:50px;border:6px solid #8b1d1d;color:#8b1d1d;font:700 56px/1 'Changa';padding:10px 26px 18px;border-radius:10px}
""",
     el("div", "paper", "paper",
        '<div class="h"><span class="t">أسعار الأطفال</span><span class="m">BABY · SAR</span></div>'
        + el("div", "r1", "row", '<span class="n">بيبي جوي · البوكس</span><span class="p">85<small>ريال</small></span>', anim=("slide-in", o(12.52) - b, 0.3, {"from": "right", "distance": 80}))
        + el("div", "r2", "row", '<span class="n">بيبي جوي · الكيس</span><span class="p">75<small>ريال</small></span>', anim=("slide-in", o(14.26) - b, 0.3, {"from": "right", "distance": 80}))
        + el("div", "r3", "row", '<span class="n">كرتون بامبرز</span><span class="p">77<small>ريال</small></span>', anim=("slide-in", o(15.26) - b, 0.3, {"from": "right", "distance": 80}))
        + el("div", "st", "stamp", "عرض خاص", anim=("scale-pop", o(16.0) - b, 0.3)),
        anim=("slide-in", 0.0, 0.4, {"from": "top", "distance": 200})))

# c07 · spotlight × overlay — Johnson 25%
begin("k07")
b = o(16.92)
card("k07", b, o(19.24), "video-overlay", "overlay",
     "all Johnson's products 25% off", {"title": "جونسون", "stat": "25%"},
     """
.root{position:absolute;inset:0;direction:rtl;font-family:'Rakkas','Tajawal',serif}
.g{position:absolute;left:50px;right:50px;top:140px;height:470px;border-radius:36px;background:radial-gradient(120% 140% at 80% 0%,#3b2a7a 0%,#160f33 60%,#0b0820 100%);box-shadow:0 0 90px rgba(167,139,250,.55);overflow:hidden}
.k{position:absolute;right:50px;top:44px;font:400 46px/1 'Rakkas';color:#c4b5fd}
.t{position:absolute;right:50px;top:110px;font:400 130px/1.1 'Rakkas';color:#fff}
.n{position:absolute;left:50px;top:150px;font:700 190px/1 'Inter';color:#a78bfa;direction:ltr;text-shadow:0 0 40px rgba(167,139,250,.9)}
.s{position:absolute;right:50px;top:300px;font:400 54px/1 'Rakkas';color:#e9e3ff}
""",
     el("div", "g", "g",
        el("div", "k", "k", "جميع منتجات", anim=("fade-in", 0.1, 0.3))
        + el("div", "t", "t", "جونسون", anim=("blur-in", o(17.56) - b, 0.35))
        + el("div", "s", "s", "عليها خصم", anim=("fade-in", o(17.88) - b, 0.25))
        + f'<div class="n">{el("span", "n", "", "0", anim=("count-up", o(18.32) - b, 0.45, {"from": 0, "to": 25, "format": ".0f"}))}%</div>',
        anim=("scale-pop", 0.0, 0.35)))

# c08 · whiteboard × overlay — wipes buy one get one
begin("k08")
b = o(19.24)
card("k08", b, o(21.62), "video-overlay", "overlay",
     "baby wipes: buy one, get the second free", {"title": "مناديل أطفال", "stat": "1 + 1"},
     """
.root{position:absolute;inset:0;direction:rtl;font-family:'Marhey','Tajawal',sans-serif}
.p{position:absolute;left:60px;right:60px;top:140px;height:480px;background:#fffdf6;border:5px solid #1e1e1e;border-radius:26px 40px 30px 44px;box-shadow:10px 12px 0 #1e1e1e}
.t{position:absolute;right:50px;top:40px;font:700 92px/1.2 'Marhey';color:#1e1e1e}
.d{position:absolute;right:50px;top:170px;font:500 52px/1.3 'Marhey';color:#444}
.big{position:absolute;left:90px;top:250px;font:700 150px/1 'Inter';color:#ff6b35;direction:ltr}
.f{position:absolute;right:50px;top:330px;font:700 84px/1 'Marhey';color:#ff6b35}
svg{position:absolute;left:40px;top:215px}
""",
        el("div", "p", "p",
           el("div", "t", "t", words("مناديل أطفال"), anim=("kinetic-chars", 0.1, 0.3, {"stagger": 0.15, "pattern": "pop"}))
           + el("div", "d", "d", "خذ حبة والثانية", anim=("fade-in", o(20.2) - b, 0.25))
           + el("div", "f", "f", "مجاناً", anim=("scale-pop", o(21.14) - b, 0.3))
           + el("div", "big", "big", "1+1", anim=("scale-pop", o(20.82) - b, 0.3))
           + '<svg width="420" height="250" viewBox="0 0 420 250">'
           + el("path", "c", "", anim=("draw-path", o(20.9) - b, 0.5),
                style="fill:none;stroke:#1e1e1e;stroke-width:7;stroke-linecap:round").replace("></path>", ' d="M370 60 C 300 10, 80 20, 40 110 C 10 190, 160 240, 280 225 C 390 210, 410 120, 330 70"></path>')
           + "</svg>",
           anim=("slide-in", 0.0, 0.35, {"from": "left", "distance": 140})))

# c09 · academic × pip — skincare prices, speaker in a corner pill
begin("k09")
b = o(21.62)
card("k09", b, o(28.42), "fullscreen", "pip",
     "skincare prices: QV 55, Bioderma 59.95, Eucerin 59", {"rows": ["QV 55", "Bioderma 59.95", "Eucerin 59"]},
     """
.root{position:absolute;inset:0;direction:rtl;background:#f7f3ea;font-family:'Cairo','Tajawal',sans-serif;color:#1f2430;
 background-image:linear-gradient(#e6dfcf 1px,transparent 1px),linear-gradient(90deg,#e6dfcf 1px,transparent 1px);background-size:60px 60px}
.k{position:absolute;right:70px;top:120px;font:700 34px/1 'Inter';letter-spacing:.2em;color:#2557a7;direction:ltr}
.t{position:absolute;right:70px;left:380px;top:170px;font:900 100px/1.15 'Cairo'}
.hl{position:absolute;right:62px;top:420px;height:26px;width:0;background:rgba(37,87,167,.25)}
.list{position:absolute;left:70px;right:70px;top:660px}
.row{display:flex;justify-content:space-between;align-items:center;background:#fff;border-right:12px solid #2557a7;border-radius:18px;padding:34px 40px;margin-bottom:34px;box-shadow:0 14px 30px -18px rgba(0,0,0,.35)}
.row .n{font:800 60px/1.2 'Cairo'}
.row .n small{display:block;font:600 34px 'Cairo';color:#6b7280}
.row .p{font:700 96px/1 'Inter';color:#2557a7;direction:ltr}
.row .p small{font:700 34px 'Cairo';margin-left:10px;color:#1f2430}
""",
     el("div", "k", "k", "SKIN CARE · PRICES", anim=("fade-in", 0.3, 0.3))
     + el("div", "t", "t", "العناية بالبشرة", anim=("mask-reveal", 0.35, 0.45, {"direction": "right"}))
     + el("span", "hl", "hl", anim=("grow-x", 0.7, 0.4, {"target_w": 600}))
     + '<div class="list">'
     + el("div", "r1", "row", '<span class="n">كريم QV</span><span class="p">55<small>ريال</small></span>', anim=("slide-in", o(21.84) - b, 0.35, {"from": "right", "distance": 120}))
     + el("div", "r2", "row", '<span class="n">بيوديرما<small>Atoderm</small></span><span class="p">59.95<small>ريال</small></span>', anim=("slide-in", o(23.14) - b, 0.35, {"from": "right", "distance": 120}))
     + el("div", "r3", "row", '<span class="n">يوسيرين لوشن<small>كل الأنواع</small></span><span class="p">59<small>ريال</small></span>', anim=("slide-in", o(25.9) - b, 0.35, {"from": "right", "distance": 120}))
     + "</div>")

# c10 · terminal × overlay — shampoo prices
begin("k10")
b = o(28.42)
card("k10", b, o(35.06), "video-overlay", "overlay",
     "Lux 700ml 21, 500ml 15; Herbal all types 18", {"rows": ["Lux 700ml 21", "Lux 500ml 15", "Herbal 18"]},
     """
.root{position:absolute;inset:0;direction:rtl;font-family:'Changa','Tajawal',sans-serif}
.term{position:absolute;left:44px;right:44px;top:120px;background:rgba(10,14,12,.9);border:2px solid #4ade80;border-radius:20px;padding:26px 40px 30px;box-shadow:0 30px 70px -20px rgba(0,0,0,.6)}
.bar{display:flex;gap:12px;direction:ltr;margin-bottom:14px}
.bar i{width:20px;height:20px;border-radius:50%;background:#4ade80;opacity:.5}
.cmd{font:700 30px/1 'Inter';color:#4ade80;direction:ltr;text-align:left;margin-bottom:12px}
.row{display:flex;justify-content:space-between;align-items:baseline;padding:16px 0;border-bottom:1px dashed rgba(74,222,128,.35);color:#e7ffe9}
.row .n{font:600 54px/1.15 'Changa'}
.row .n small{font:500 36px 'Changa';color:#86efac}
.row .p{font:700 78px/1 'Inter';color:#4ade80;direction:ltr}
.row .p small{font:600 30px 'Changa';color:#e7ffe9;margin-left:8px}
""",
     el("div", "term", "term",
        '<div class="bar"><i></i><i></i><i></i></div>'
        + el("div", "cmd", "cmd", "$ kunooz --shampoo", anim=("fade-in", 0.15, 0.25))
        + el("div", "r1", "row", '<span class="n">شامبو لوكس <small>700 مل</small></span><span class="p">21<small>ريال</small></span>', anim=("fade-in", o(28.96) - b, 0.3))
        + el("div", "r2", "row", '<span class="n">شامبو لوكس <small>500 مل</small></span><span class="p">15<small>ريال</small></span>', anim=("fade-in", o(30.88) - b, 0.3))
        + el("div", "r3", "row", '<span class="n">شامبو هيربل <small>جميع الأنواع</small></span><span class="p">18<small>ريال</small></span>', anim=("fade-in", o(32.76) - b, 0.3)),
        anim=("mask-reveal", 0.0, 0.35, {"direction": "top"})))

# c11 · geom × overlay — Astera 30%
begin("k11")
b = o(35.06)
card("k11", b, o(37.36), "video-overlay", "overlay",
     "all Astera products 30% off", {"title": "استيرا", "stat": "30%"},
     """
.root{position:absolute;inset:0;direction:rtl;font-family:'Lalezar','Tajawal',sans-serif}
.pink{position:absolute;left:0;top:150px;width:0;height:400px;background:#ff2e88}
.blk{position:absolute;right:60px;top:110px;width:250px;height:90px;background:#0a0a0a}
.k{position:absolute;right:84px;top:122px;font-size:56px;line-height:1.2;color:#d4ff00}
.t{position:absolute;right:60px;top:220px;font-size:170px;line-height:1.1;color:#fff}
.n{position:absolute;left:60px;top:250px;font:700 200px/1 'Inter';color:#0a0a0a;direction:ltr}
""",
     el("span", "pink", "pink", anim=("grow-x", 0.0, 0.35, {"target_w": 1080}))
     + el("span", "blk", "blk", anim=("slide-in", 0.1, 0.3, {"from": "right", "distance": 260}))
     + el("div", "k", "k", "جميع منتجات", anim=("fade-in", 0.25, 0.2))
     + el("div", "t", "t", "استيرا", anim=("scale-pop", o(35.94) - b, 0.3))
     + f'<div class="n">{el("span", "n", "", "0", anim=("count-up", o(36.56) - b, 0.4, {"from": 0, "to": 30, "format": ".0f"}))}%</div>')

# c12 · xhs × overlay — vitamins for everyone
begin("k12")
b = o(37.36)
card("k12", b, o(41.06), "video-overlay", "overlay",
     "strong discounts on vitamins for women, men, kids", {"title": "خصومات الفيتامينات", "chips": ["للنساء", "للرجال", "للأطفال"]},
     """
.root{position:absolute;inset:0;direction:rtl;font-family:'Marhey','Tajawal',sans-serif}
.box{position:absolute;left:50px;right:50px;top:1180px;padding:34px 40px 40px;background:#fff8f0;border-radius:44px;box-shadow:0 30px 70px -20px rgba(0,0,0,.45)}
.k{font-size:36px;color:#ff2e63}
.t{font-size:92px;line-height:1.2;color:#1b1b1b;font-weight:700}
.chips{display:flex;gap:18px;margin-top:20px}
.c{font-size:52px;color:#fff;background:#ff2e63;border-radius:999px;padding:8px 36px 16px}
""",
     el("div", "box", "box",
        el("div", "k", "k", "#خصمات_قوية", anim=("fade-in", 0.15, 0.25))
        + el("div", "t", "t", words("على جميع الفيتامينات"), anim=("kinetic-chars", o(38.66) - b, 0.3, {"stagger": 0.18, "pattern": "pop"}))
        + '<div class="chips">'
        + el("span", "c1", "c", "للنساء", anim=("scale-pop", o(39.6) - b, 0.28))
        + el("span", "c2", "c", "للرجال", anim=("scale-pop", o(40.04) - b, 0.28))
        + el("span", "c3", "c", "للأطفال", anim=("scale-pop", o(40.58) - b, 0.28))
        + "</div>",
        anim=("slide-in", 0.0, 0.35, {"from": "bottom", "distance": 160})))

# c13 · minimal × overlay — all branches, with logo
begin("k13")
b = o(41.06)
card("k13", b, o(43.08), "video-overlay", "overlay",
     "these offers are in all branches", {"title": "متوفرة في جميع الفروع"},
     """
.root{position:absolute;inset:0;direction:rtl;font-family:'Tajawal',sans-serif}
.band{position:absolute;left:0;right:0;top:150px;height:330px;background:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 60px}
.txt .s{font:800 40px/1 'Tajawal';color:#777}
.txt .t{font:900 104px/1.15 'Tajawal';color:#000;margin-top:12px}
.logo{width:230px;height:auto}
""",
     el("div", "band", "band",
        '<div class="txt">' + el("div", "s", "s", "وعلى فكرة… العروض هذه", anim=("fade-in", 0.1, 0.25))
        + el("div", "t", "t", "في جميع الفروع", anim=("mask-reveal", o(42.42) - b, 0.35, {"direction": "right"})) + "</div>"
        + el("img", "logo", "logo", anim=("scale-pop", 0.3, 0.35)).replace("></img>", ' src="img/logo.png" alt="">'),
        anim=("mask-reveal", 0.0, 0.3, {"direction": "left"})))

# c14 · spotlight × pip — the website again, bigger, speaker in a corner
begin("k14")
b = o(43.08)
SITE2 = (o(43.58) - 0.1, DUR)
card("k14", b, DUR, "fullscreen", "pip",
     "go to the website for even stronger offers", {"title": "بالموقع عروض أقوى"},
     """
.root{position:absolute;inset:0;direction:rtl;background:radial-gradient(90% 70% at 50% 40%,#1a94d4 0%,#0b3d66 55%,#06182b 100%);font-family:'Tajawal',sans-serif}
.k{position:absolute;right:60px;left:380px;top:110px;font:800 44px/1 'Tajawal';color:#bfe6ff}
.t{position:absolute;right:60px;left:380px;top:170px;font:900 104px/1.15 'Tajawal';color:#fff;text-shadow:0 0 40px rgba(26,148,212,.9)}
.t b{color:#F26A21}
""",
     el("div", "k", "k", "ولو تدخل الموقع", anim=("fade-in", 0.1, 0.25))
     + el("div", "t", "t", words("بتحصل عروض <b>أقوى</b>").replace('<span class="char"><b>أقوى</b></span>', '<span class="char"><b>أقوى</b></span>'),
          anim=("kinetic-chars", o(43.96) - b, 0.25, {"stagger": 0.2, "pattern": "pop"})))

# ---------------------------------------------------------------- layouts
# #video-wrap stays 1080x1920; each layout is reached with transforms + clip-path
# (sub-pixel smooth under seek-by-frame capture).
LAYOUT = {
    "overlay": dict(x=0, y=0, scale=1, clipPath="inset(0px 0px 0px 0px round 0px)"),
    "stack": dict(x=0, y=-545, scale=1, clipPath="inset(545px 0px 545px 0px round 0px)"),   # product band on top 830px
    "split": dict(x=0, y=480, scale=1, clipPath="inset(480px 0px 480px 0px round 0px)"),    # centre band in bottom half
    "pip": dict(x=30, y=40, scale=0.2889, clipPath="inset(0px 0px 0px 0px round 96px)"),   # 312x555 corner pill
}
HOST = {
    "video-overlay": (0, 0, W, H),
    "fullscreen": (0, 0, W, H),
    "lower-third": (0, 844, W, H - 844),
    "side-panel": (0, 0, W, 946),
}


def q(t):
    return round(round(t * FPS) / FPS, 4)


def compile_anim(cid, start, eid, kind, at, dur, p):
    sel = f'.card[data-card-id="{cid}"] #{eid}'
    T = q(start + at)
    S = json.dumps(sel)
    if kind == "fade-in":
        return f"tl.fromTo({S},{{opacity:0}},{{opacity:1,duration:{dur},ease:'power2.out'}},{T});"
    if kind == "fade-out":
        return f"tl.to({S},{{opacity:0,duration:{dur},ease:'power2.in'}},{T});"
    if kind == "slide-in":
        d = p.get("distance", 80)
        axis, sign = {"left": ("x", -1), "right": ("x", 1), "top": ("y", -1), "bottom": ("y", 1)}[p.get("from", "left")]
        return f"tl.fromTo({S},{{opacity:0,{axis}:{sign * d}}},{{opacity:1,{axis}:0,duration:{dur},ease:'power3.out'}},{T});"
    if kind == "kinetic-chars":
        return (f"tl.from({json.dumps(sel + ' .char')},{{opacity:0,y:18,scale:0.8,duration:{dur},"
                f"ease:'back.out(1.7)',stagger:{p.get('stagger', 0.05)}}},{T});")
    if kind == "count-up":
        return (f"(function(){{const o={{v:{p['from']}}};tl.to(o,{{v:{p['to']},duration:{dur},ease:'power2.out',"
                f"onUpdate:function(){{const el=document.querySelector({S});if(el)el.textContent=__fmt(o.v,'{p.get('format', '.0f')}');}}}},{T});}})();")
    if kind == "draw-path":
        return (f"(function(){{const el=document.querySelector({S});if(el){{const L=el.getTotalLength();"
                f"tl.set({S},{{strokeDasharray:L,strokeDashoffset:L}},0);tl.to({S},{{strokeDashoffset:0,duration:{dur},ease:'power2.inOut'}},{T});}}}})();")
    if kind == "grow-x":
        return f"tl.fromTo({S},{{width:0}},{{width:{p['target_w']},duration:{dur},ease:'power3.out'}},{T});"
    if kind == "grow-y":
        return f"tl.fromTo({S},{{height:0}},{{height:{p['target_h']},duration:{dur},ease:'power3.out'}},{T});"
    if kind == "scale-pop":
        return f"tl.fromTo({S},{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:{dur},ease:'back.out(1.6)'}},{T});"
    if kind == "blur-in":
        return f"tl.fromTo({S},{{opacity:0,filter:'blur(18px)'}},{{opacity:1,filter:'blur(0px)',duration:{dur},ease:'power2.out'}},{T});"
    if kind == "mask-reveal":
        start_clip = {"left": "inset(0 100% 0 0)", "right": "inset(0 0 0 100%)",
                      "top": "inset(0 0 100% 0)", "bottom": "inset(100% 0 0 0)"}[p.get("direction", "left")]
        return f"tl.fromTo({S},{{clipPath:'{start_clip}'}},{{clipPath:'inset(0% 0% 0% 0%)',duration:{dur},ease:'power2.inOut'}},{T});"
    raise ValueError(kind)


def build():
    os.makedirs(os.path.join(PUB, "cards"), exist_ok=True)
    hosts, js = [], []
    prev_layout = "overlay"
    for c in CARDS:
        cid = c["id"]
        frag = (f'<div class="card" data-card-id="{cid}">\n<style>{scope(cid, c["css"])}\n</style>\n'
                f'<div class="root">{c["body"]}</div>\n</div>\n')
        open(os.path.join(PUB, "cards", f"{cid}.html"), "w").write(frag)
        x, y, w, h = HOST[c["zone"]]
        s, e = q(c["start"]), q(c["end"])
        hosts.append(f'<div id="host-{cid}" class="card-host clip" data-card-id="{cid}" data-start="{s}" data-duration="{q(e - s)}" '
                     f'data-track-index="3" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;visibility:hidden;opacity:0;">\n{frag}</div>')
        hs = json.dumps(f'.card-host[data-card-id="{cid}"]')
        js.append(f"// {cid} · {c['layout']} · {c['intent']}")
        if c["layout"] != prev_layout:
            L = LAYOUT[c["layout"]]
            cls = "video-wrapper pip-pill" if c["layout"] == "pip" else "video-wrapper"
            js.append(f"tl.set('#video-wrap',{{className:'{cls}',zIndex:{6 if c['layout'] == 'pip' else 1}}},{s});")
            js.append(f"tl.to('#video-wrap',{{x:{L['x']},y:{L['y']},scale:{L['scale']},clipPath:'{L['clipPath']}',duration:0.5,ease:'power3.inOut'}},{s});")
            prev_layout = c["layout"]
        js.append(f"tl.set({hs},{{visibility:'visible'}},{s});")
        js.append(f"tl.fromTo({hs},{{opacity:0}},{{opacity:1,duration:0.2,ease:'power2.out'}},{s});")
        for eid, kind, at, dur, p in c["anims"]:
            js.append(compile_anim(cid, c["start"], eid, kind, at, dur, p))
        if e < DUR - 0.01:
            js.append(f"tl.to({hs},{{opacity:0,duration:0.2,ease:'power2.in'}},{q(e - 0.2)});")
            js.append(f"tl.set({hs},{{visibility:'hidden'}},{e});")
    # leaving the last non-overlay layout is handled by the next card; nothing after k14.

    # jump-cut source clips (HyperFrames hard cuts: data-media-start per kept range)
    clips, t = [], 0.0
    for i, (a, b) in enumerate(KEEP):
        d = q(b - a) if i < len(KEEP) - 1 else q(DUR - t)
        clips.append(f'<video id="take{i + 1}" src="input-video.mp4" playsinline data-has-audio="true" '
                     f'data-start="{q(t)}" data-duration="{d}" data-media-start="{a}" data-track-index="1"></video>')
        t += b - a

    # the website pops onto the screen on each mention (host-root media, motion on the main timeline)
    site = []
    for n, (s, e), mstart, rate, box in [
        (1, SITE1, 0.3, 2, (70, 640, 420, 805)),
        (2, SITE2, 24.0, 3, (280, 660, 520, 996)),
    ]:
        s, e = q(s), q(e)
        x, y, w, h = box
        site.append(f'<div id="site{n}-wrap" class="site-phone" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;">'
                    f'<video id="site{n}" src="site.mp4" muted playsinline data-start="{s}" data-duration="{q(e - s)}" '
                    f'data-media-start="{mstart}" data-playback-rate="{rate}" data-track-index="{4 + n}"></video></div>')
        sel = f"'#site{n}-wrap'"
        js.append(f"// site video #{n} — quick pop on the mention")
        js.append(f"tl.fromTo({sel},{{opacity:0,scale:0.4,y:120}},{{opacity:1,scale:1,y:0,duration:0.32,ease:'back.out(1.8)'}},{s});")
        if e < DUR - 0.01:
            js.append(f"tl.to({sel},{{opacity:0,scale:0.85,y:60,duration:0.22,ease:'power2.in'}},{q(e - 0.22)});")

    fonts = "".join(
        f'@font-face{{font-family:"{fam}";src:url("fonts/{f}");font-weight:{wt};font-display:block}}\n'
        for fam, f, wt in [("Inter", "Inter-400-latin.woff2", 400), ("Inter", "Inter-700-latin.woff2", 700),
                           ("Tajawal", "Tajawal-ExtraBold.ttf", 800), ("Tajawal", "Tajawal-Black.ttf", 900),
                           ("Lalezar", "Lalezar-Regular.ttf", 400), ("Marhey", "Marhey.ttf", "300 700"),
                           ("El Messiri", "ElMessiri.ttf", "400 700"), ("Rakkas", "Rakkas-Regular.ttf", 400),
                           ("Changa", "Changa.ttf", "200 800"), ("Cairo", "Cairo.ttf", "200 1000")])
    html = f"""<!doctype html>
<html lang="ar">
<head>
<meta charset="utf-8" />
<style>
{fonts}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #0a0c12;
  font-family: "Tajawal", "Cairo", "Inter", sans-serif; }}
#stage {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #0a0c12; }}
.video-wrapper {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; overflow: hidden; z-index: 1; transform-origin: 0 0; clip-path: inset(0px 0px 0px 0px round 0px); }}
.video-wrapper video {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.video-wrapper.pip-pill {{ border-radius: 96px; }}
.card-host {{ position: absolute; pointer-events: none; overflow: hidden; z-index: 3; }}
.card-host .card {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
.card-host .char {{ display: inline-block; }}
.site-phone {{ position: absolute; z-index: 8; opacity: 0; border-radius: 44px; overflow: hidden; background: #fff;
  border: 10px solid #111; box-shadow: 0 40px 90px -20px rgba(0,0,0,.65), 0 0 0 4px rgba(255,255,255,.9); }}
.site-phone video {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
</style>
</head>
<body>
<div id="stage" data-composition-id="talking-head-recut" data-start="0" data-duration="{DUR}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
<div class="video-wrapper" id="video-wrap">
{chr(10).join(clips)}
</div>
{chr(10).join(hosts)}
{chr(10).join(site)}
<script src="vendor/gsap.min.js"></script>
<script>
(function () {{
  window.__fmt = function (v, fmt) {{
    if (typeof fmt === "string" && /^\\.[0-9]+f$/.test(fmt)) return Number(v).toFixed(Number(fmt.slice(1, -1)));
    if (fmt === ",d") return Math.round(v).toLocaleString();
    return String(Math.round(v));
  }};
  const tl = window.gsap.timeline({{ paused: true }});
  {(chr(10) + '  ').join(js)}
  window.__timelines = window.__timelines || {{}};
  window.__timelines["talking-head-recut"] = tl;
}})();
</script>
</div>
</body>
</html>
"""
    open(os.path.join(PUB, "index.html"), "w").write(html)

    sb = {"schemaVersion": 3,
          "composition": {"fps": FPS, "width": W, "height": H, "durationSeconds": DUR, "layout": "portrait",
                          "themeId": "kunooz", "seed": 7},
          "videoTrack": {"sourcePath": "public/input-video.mp4", "startSec": 0, "endSec": 45.12,
                         "cuts": [[1.58, 1.78], [7.82, 8.03]]},
          "subtitles": {"enabled": False},
          "cards": [{"id": c["id"], "intent": c["intent"], "startSec": q(c["start"]), "endSec": q(c["end"]),
                     "accentIndex": c["accent"], "zone": c["zone"], "contentHints": c["hints"]} for c in CARDS]}
    json.dump(sb, open(os.path.join(HERE, "storyboard.json"), "w"), ensure_ascii=False, indent=2)
    print("cards:", len(CARDS), "duration:", DUR)


if __name__ == "__main__":
    build()
