# عالم أرووش Aroosh (kids play centre) — pass 1: style 5 ستيكر in poster purple/orange; source times
CH = []
def S(text, t, end=None): CH.append(dict(kind="small", text=text, t0=t, end=end))
def B(*lines, end=None): CH.append(dict(kind="big", lines=list(lines), t0=lines[0][1], end=end))
def w(text, t, size="mid"): return (text, t, "w", None, size)
def g(text, t, num=None, size="big"): return (text, t, "g", num, size)
B(w("الإجازة المطوّلة", 0.00), g("قرّبت", 1.22), end=1.68)
S("لأطفالك مع عالم أرووش", 2.66, end=4.00)
B(w("المكان", 9.32), g("مليان فعاليات", 9.66), end=10.56)
B(g("القفز الحر", 11.38), end=12.18)
B(g("ملعب كرة قدم", 12.70), end=13.32)
B(w("منطقة", 14.24), g("ماريو", 14.82), end=15.44)
B(w("منطقة", 15.56), g("السفاري", 16.06), end=16.62)
S("ومناطق ألعاب كثيرة", 16.64, end=18.16)
B(w("المكان", 18.64), g("جداً رهيب", 18.96), end=19.78)
S("وللأكل والشرب", 19.80, end=21.56)
B(w("منطقة خاصة", 21.58), g("للمأكولات", 22.20), end=22.60)
B(w("منطقة خاصة", 23.48), g("للأطفال", 24.34), end=24.82)
S("من أفضل الأماكن للأطفال", 24.84, end=27.28)
B(w("الألعاب", 27.30), g("رهيبة وحركية", 27.78), end=28.74)
S("موقعهم في حي العليا", 31.70, end=33.96)
B(w("اكتب في قوقل ماب", 33.98), g("عالم أرووش", 34.88), end=37.10)
for i, c in enumerate(CH):
    nxt = CH[i + 1]["t0"] if i + 1 < len(CH) else 37.1
    c["t1"] = min(c["end"] or nxt, nxt) if c["end"] else nxt
CHUNKS = CH
BRAND = (255, 140, 20)
INK = (85, 45, 165)
LOGOS = []
Y_SMALL, Y_BIG, RIGHT = 1250, 1150, 90
