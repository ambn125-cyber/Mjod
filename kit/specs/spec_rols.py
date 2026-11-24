# رولز شوكولاتة ROLS — v3 «minimal»: user disliked v2 (calligraphic duo) and 3 previews, then «مدري محتار» → I chose: the footage sells itself,
# text only on the hook, key points and ending; clean white Tajawal with soft shadow (style 16, white rows only), logo card start + end; earlier specs spec_rols16 / spec_rols9
IZ_GOLD = (255, 255, 255); IZ_SH = 230; IZ_BLUR = 10; IZ_SIZE = 96; IZ_Y = 400
LOGO = "kit/brands/rols/logo_card.png"
def r(*ws, c="w"): return [(w[0], w[1], w[2] if len(w) > 2 else c) for w in ws]
EV = [
    iz(0.20, 3.08, r(("شوكولاتة", 0.20), ("تعلق", 0.80), ("لذّتها", 1.20), ("بدماغك؟", 1.60)), y=1450),
    card(3.10, 5.68, LOGO, 3.10, cx=540, cy=560, w=300, r=28),
    iz(3.80, 5.68, r(("57", 3.90), ("فرع", 4.10), ("بالمملكة", 4.80)), y=1200),
    iz(5.70, 7.88, r(("بكج", 6.80), ("الزواج", 7.00)), y=1450),
    iz(25.28, 29.88, r(("حشوات", 25.80), ("جديدة", 26.20))),
    iz(33.34, 37.92, r(("بالفروع", 35.00), ("·", 35.40), ("والمتجر", 36.40), ("الإلكتروني", 36.80)), y=1450),
    card(44.88, 49.34, LOGO, 44.88, cx=540, cy=420, w=260, r=28),
    iz(44.88, 49.34, r(("تبوك", 44.88)), r(("حي", 46.00), ("المروج", 46.20), ("·", 46.60), ("طريق", 46.80), ("ولي", 47.00), ("العهد", 47.20)), y=1450),
]
