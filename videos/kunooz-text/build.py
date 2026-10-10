"""Text-only re-edit of the full Kunooz video (TikTok / Snapchat).

Only captions with light motion over the full-bleed footage; every card
sits inside the TikTok/Snap safe area (centred vertically, 140px side margins on both sides because the Arabic
TikTok/Snap UI puts its buttons on the left).

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
# One caption style for the whole video: white Tajawal with a soft shadow,
# numbers in Kunooz yellow, no boxes or panels so the footage stays clear.
BASE_CSS = """
.root{position:absolute;inset:0;direction:rtl;font-family:'Tajawal',sans-serif}
.cap{position:absolute;left:140px;right:140px;top:420px;bottom:500px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:14px}
.s{font:800 52px/1.4 'Tajawal';color:#fff;text-shadow:0 0 3px rgba(0,0,0,.85),0 2px 5px rgba(0,0,0,.7),0 0 12px rgba(0,0,0,.55),0 0 12px rgba(0,0,0,.55),0 6px 24px rgba(0,0,0,.55)}
.t{font:900 88px/1.3 'Tajawal';color:#fff;text-shadow:0 0 3px rgba(0,0,0,.85),0 2px 5px rgba(0,0,0,.7),0 0 12px rgba(0,0,0,.55),0 0 12px rgba(0,0,0,.55),0 6px 24px rgba(0,0,0,.55)}
.y{color:#FFD23F}
.n{font:700 140px/1.1 'Inter';color:#FFD23F;direction:ltr;text-shadow:0 0 3px rgba(0,0,0,.85),0 2px 5px rgba(0,0,0,.7),0 0 12px rgba(0,0,0,.55),0 0 12px rgba(0,0,0,.55),0 6px 24px rgba(0,0,0,.55)}
.p{font:900 60px/1.35 'Tajawal';color:#fff;text-shadow:0 0 3px rgba(0,0,0,.85),0 2px 5px rgba(0,0,0,.7),0 0 12px rgba(0,0,0,.55),0 0 12px rgba(0,0,0,.55),0 6px 24px rgba(0,0,0,.55)}
.p b{font:700 68px 'Inter';color:#FFD23F;margin:0 10px;direction:ltr;display:inline-block}
.u{height:8px;width:0;border-radius:4px;background:#FFD23F;box-shadow:0 2px 10px rgba(0,0,0,.35);margin-top:6px}
"""


def cap(cid, s_src, e_src, intent, parts, underline=None):
    """parts: list of (cls, html, src_time_of_word, kind)."""
    begin(cid)
    s, e = o(s_src), o(e_src) if e_src else DUR
    body = ""
    for i, (cls, html, t_src, kind) in enumerate(parts):
        at = max(0.0, round(o(t_src) - s, 3)) if t_src is not None else 0.05
        if kind == "count":
            frm, to, suffix = html
            inner = el("span", f"c{i}", "", "0", anim=("count-up", at, 0.5, {"from": 0, "to": to, "format": ".0f"}))
            body += el("div", f"w{i}", cls, inner + suffix, anim=("fade-in", at, 0.2))
        else:
            body += el("div", f"w{i}", cls, html, anim=("slide-in", at, 0.3, {"from": "bottom", "distance": 24}))
    if underline:
        body += el("span", "u", "u", anim=("grow-x", round(o(underline[0]) - s, 3), 0.35, {"target_w": underline[1]}))
    card(cid, s, e, "video-overlay", "overlay", intent,
         {"lines": [p[1] if isinstance(p[1], str) else str(p[1][1]) for p in parts]},
         BASE_CSS, f'<div class="cap">{body}</div>')


R = lambda price, word="ريال": f"<b>{price}</b>{word}"

cap("k01", 0.0, 1.52, "discount up to 70%",
    [("s", "خصم يوصل إلى", 0.0, "slide"), ("n", (0, 70, "%"), 0.74, "count")])
cap("k02", 1.52, 3.6, "free delivery",
    [("t", "توصيل لباب بيتك", 2.14, "slide"), ("t y", "مجاناً", 3.06, "slide")])
cap("k03", 3.6, 5.08, "instalments",
    [("s", "وفوقها متوفر عندهم", 3.6, "slide"), ("t y", "تقسيط", 4.72, "slide")])
cap("k04", 5.8, 9.5, "website + branches",
    [("s", "متوفرة في", 5.8, "slide"), ("t", "موقع كنوز السعادة الجديد", 6.42, "slide"),
     ("s y", "وفي جميع الفروع", 8.38, "slide")], underline=(7.34, 420))
cap("k05", 9.5, 12.52, "baby milk",
    [("s", "خذ أي حبتين من", 9.5, "slide"), ("t", "حليب الأطفال", 10.54, "slide"),
     ("s", "والثالثة خصم", 11.18, "slide"), ("n", (0, 60, "%"), 11.92, "count")])
cap("k06", 12.52, 16.92, "baby care prices",
    [("p", "بيبي جوي البوكس" + R(85), 12.52, "slide"), ("p", "الكيس" + R(75), 14.26, "slide"),
     ("p", "كرتون بامبرز" + R(77), 15.26, "slide")])
cap("k07", 16.92, 19.24, "Johnson's 25% off",
    [("t", "جميع منتجات جونسون", 17.22, "slide"), ("s", "عليها خصم", 17.88, "slide"),
     ("n", (0, 25, "%"), 18.32, "count")])
cap("k08", 19.24, 21.62, "wipes 1+1",
    [("t", "مناديل أطفال", 19.24, "slide"), ("s", "خذ حبة والثانية", 20.2, "slide"),
     ("t y", "مجاناً", 21.14, "slide")])
cap("k09", 21.62, 23.14, "QV cream",
    [("t", "كريم QV", 21.62, "slide"), ("p", R(55), 22.14, "slide")])
cap("k10", 23.14, 25.9, "Bioderma",
    [("t", "كريم بيوديرما", 23.14, "slide"), ("p", R("59.95"), 24.42, "slide")])
cap("k11", 25.9, 28.42, "Eucerin lotion",
    [("t", "يوسيرين لوشن", 25.9, "slide"), ("s", "كل الأنواع", 26.74, "slide"), ("p", R(59), 27.48, "slide")])
cap("k12", 28.42, 32.76, "Lux shampoo",
    [("t", "شامبو لوكس", 28.42, "slide"), ("p", "700 مل" + R(21), 28.96, "slide"),
     ("p", "500 مل" + R(15), 30.88, "slide")])
cap("k13", 32.76, 35.06, "Herbal shampoo",
    [("t", "شامبو هيربل", 32.76, "slide"), ("s", "جميع الأنواع", 33.56, "slide"), ("p", R(18), 34.32, "slide")])
cap("k14", 35.06, 37.36, "Astera 30% off",
    [("t", "جميع منتجات استيرا", 35.3, "slide"), ("s", "عليها خصم", 36.3, "slide"),
     ("n", (0, 30, "%"), 36.78, "count")])
cap("k15", 37.36, 41.06, "vitamins",
    [("s", "خصومات قوية على", 37.36, "slide"), ("t", "جميع الفيتامينات", 38.78, "slide"),
     ("s y", "للنساء · للرجال · للأطفال", 39.6, "slide")])
cap("k16", 41.06, 43.08, "all branches",
    [("s", "وعلى فكرة العروض هذه", 41.06, "slide"), ("t", "متوفرة في جميع الفروع", 41.88, "slide")],
    underline=(42.66, 380))
cap("k17", 43.08, None, "website: stronger offers",
    [("s", "ولو تدخل الموقع", 43.08, "slide"), ("t", "بتحصل عروض", 43.96, "slide"), ("t y", "أقوى", 44.52, "slide")])

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

    site = []

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
