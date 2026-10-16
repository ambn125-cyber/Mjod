# NEOM S.C. Fan Zone — sticker style (render_st.py) in NEOM navy/cyan; source times
CH = []
def S(text, t, end=None): CH.append(dict(kind="small", text=text, t0=t, end=end))
def B(*lines, end=None):
    CH.append(dict(kind="big", lines=list(lines), t0=lines[0][1], end=end))
def w(text, t, size="mid"): return (text, t, "w", None, size)
def g(text, t, num=None, size="big"): return (text, t, "g", num, size)
B(w("بكرة مباراة", 0.00), g("نيوم", 0.68), w("ضد", 0.94), g("الاتفاق", 1.30), end=1.82)
B(w("وهذي منطقة", 1.84), g("الفان زون", 2.42), end=2.90)
S("منطقة مشجعين نادي نيوم", 2.92, end=4.26)
B(w("المنطقة مليانة", 4.28), g("فعاليات", 5.38), end=5.84)
S("ومناسبة لمختلف الأعمار", 5.86, end=7.00)
B(g("ألعاب أطفال", 7.06), end=7.82)
B(w("وألعاب حركية", 7.84), g("بلايستيشن", 8.70), g("واقع افتراضي", 9.26), end=9.82)
B(g("طاولة", 10.24), g("وسلة", 10.64), w("وغيرها كثير", 11.06), end=11.72)
S("كل مباراة لنيوم على أرضه", 11.74, end=13.44)
B(w("فيه", 13.46), g("مسابقات", 13.82), w("في الفان زون", 14.36), end=15.02)
B(w("وسحب على", 15.04), g("آيفون", 15.52), g("وآيباد", 16.04), g("وسماعات أبل", 16.46), end=17.26)
S("وكمان عندهم منطقة", 17.28)
B(g("مأكولات", 18.38), w("ومشروبات", 18.88), end=19.40)
B(w("وهذا", 19.42), g("متجر النادي", 19.74), end=20.34)
B(w("وسعر التذاكر", 20.36), g("مناسب جداً", 21.04), end=21.74)
B(w("ورابط التذاكر", 21.76), g("في الستوري", 22.60), end=23.08)
B(w("كل التوفيق", 23.10), g("لنادي نيوم", 23.76), end=25.20)
for i, c in enumerate(CH):
    nxt = CH[i + 1]["t0"] if i + 1 < len(CH) else 25.2
    c["t1"] = min(c["end"] or nxt, nxt) if c["end"] else nxt
CHUNKS = CH
BRAND = (64, 190, 240)
INK = (12, 30, 70)
LOGOS = [("neom/logo_card.png", 0.68, 2.40, 330, 260)]
Y_SMALL, Y_BIG, RIGHT = 1250, 1150, 90
