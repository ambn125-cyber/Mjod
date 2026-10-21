# تبوك ماسترز — style 5 ستيكر in red/white (user disliked style 12 on this video); source times
CH = []
def S(text, t, end=None): CH.append(dict(kind="small", text=text, t0=t, end=end))
def B(*lines, end=None): CH.append(dict(kind="big", lines=list(lines), t0=lines[0][1], end=end))
def w(text, t, size="mid"): return (text, t, "w", None, size)
def g(text, t, num=None, size="big"): return (text, t, "g", num, size)
B(w("أقوى وأقدم", 0.32), g("صالة بلياردو", 1.00), w("في تبوك", 1.82), end=2.20)
B(w("أسعارهم", 2.94), g("طول السنة عروض", 3.32), end=4.16)
B(w("عدد كبير من", 4.94), g("طاولات البلياردو", 5.58), end=6.30)
S("طالع أنت وخوياك؟", 6.72); B(g("المكان المناسب", 7.64), end=8.54)
B(w("ومتوفر", 8.56), g("طاولة سنوكر", 9.46), end=10.14)
B(g("شاشة عملاقة", 11.20), w("للمباريات مجاناً", 12.14), end=13.50)
S("ما تعرف تلعب؟", 13.92); B(g("متوفر تدريب", 15.52), end=16.46)
B(g("طاولة فرفيرة", 17.52), w("لعشاق الفرفيرة", 18.16), end=19.08)
B(w("متوفر", 19.10), g("بلايستيشن", 19.94), end=20.82)
B(g("تنس", 22.42), g("شطرنج", 23.20), g("جاكارو", 24.24), g("بلوت", 25.22), end=25.52)
S("الأقمشة تتغير كل 4 شهور", 26.82, end=28.38)
B(w("بطولات البلياردو", 29.08), g("بث مباشر", 30.16), end=30.86)
B(w("للمحترفين", 31.32), g("طاولة راسون", 32.62), w("الوحيدة في تبوك", 33.14), end=33.92)
B(w("جوعان؟", 34.72), g("سناكات وكوفي", 35.68), end=37.10)
S("موقعهم مقابل كبري طريق المدينة", 37.78, end=40.96)
B(w("اكتب في قوقل ماب", 40.98), g("تبوك ماسترز", 41.86), end=43.86)
for i, c in enumerate(CH):
    nxt = CH[i + 1]["t0"] if i + 1 < len(CH) else 43.9
    c["t1"] = min(c["end"] or nxt, nxt) if c["end"] else nxt
CHUNKS = CH
BRAND = (225, 30, 45)
INK = (20, 20, 30)
LOGOS = []
Y_SMALL, Y_BIG, RIGHT = 1250, 1150, 90
