# هيونداي الناغي Hyundai Naghi — EOY campaign 2026; v2 = style 16 «سطرين أنيق» (user rejected style 13 for a car showroom; v1 kept in spec_hyundai13.py)
# blue row = Hyundai blue, white row; "p" prices rise + glint; line=True rule under model names; glass for big offers; ZOOM punch-ins on prices; prices from the KVs
IZ_GOLD = (0, 95, 190); TAG_STYLE = "pill"; TAG = (0, 44, 95); TAG_FG = (255, 255, 255); IZ_SH = 255; IZ_BLUR = 8; IZ_SIZE = 128; IZ_GLINT = True; IZ_Y = 470   # user: no glass box, add the glint (prices metallic + glint, blue words glint)
LOGO = "kit/brands/hyundai/naghi_logo_card.png"
ZOOM = [(8.3, 10.0), (18.3, 19.7), (21.5, 22.9), (31.9, 33.9)]
def r(*ws, c="w"): return [(w[0], w[1], w[2] if len(w) > 2 else c) for w in ws]
EV = [   # v3: user «الكلام كثير» → model + price only, one line per idea
    iz(0.00, 3.14, r(("اشترِ", 0.00), ("الآن", 1.16)), r(("وادفع", 1.84), ("في", 2.24), ("2027", 2.38), c="g")),
    card(3.16, 6.58, LOGO, 3.16, cx=540, cy=330, w=330, r=26),
    iz(6.60, 10.04, r(("أكسنت", 6.60), c="g"), r(("929", 8.48, "p"), ("ريال", 9.46, "p")), line=True),
    iz(10.06, 15.68, r(("استرداد", 10.18), ("نقدي", 10.62), c="g"), r(("1,000", 11.32, "p"), ("ريال", 11.66, "p"))),
    iz(15.70, 19.74, r(("إلنترا", 16.20), c="g"), r(("1,099", 18.46, "p"), ("ريال", 19.22, "p")), line=True),
    iz(19.76, 22.98, r(("كونا", 19.76), c="g"), r(("1,129", 21.64, "p"), ("ريال", 22.32, "p")), line=True),
    iz(23.00, 29.64, r(("استرداد", 23.26), ("نقدي", 23.58), c="g"), r(("5,000", 24.36, "p"), ("ريال", 24.66, "p"))),
    iz(29.66, 33.96, r(("توسان", 29.66), c="g"), r(("1,399", 32.10, "p"), ("ريال", 33.44, "p")), line=True),
    iz(33.98, 35.90, r(("0%", 34.76, "p")), r(("دفعة", 35.26), ("أولى", 35.56), c="g")),
    iz(35.92, 38.94, r(("اربح", 36.78), c="w"), r(("هيونداي", 37.56), ("فينيو", 38.08), c="g"), line=True),
    iz(38.96, 46.56, r(("جرّب", 42.42), ("واربح!", 42.80), c="g")),
    iz(56.56, 59.18, r(("تجربة", 57.94), ("هيونداي", 58.34), c="g"), r(("المميزة", 58.76))),
    # closing while he talks (user: «خلي الكتابة اللي آخر المقطع مع الشعار وأنا أتكلم») — no freeze / end card
    card(59.20, 63.51, LOGO, 59.20, cx=540, cy=330, w=300, r=26),
    iz(59.20, 63.51, r(("اشترِ", 59.30), ("الآن", 59.40), ("وادفع", 59.50), ("في", 59.60), ("2027", 59.70), c="g"), r(("جرّب", 60.20), ("القيادة", 60.30), ("وادخل", 60.40), ("السحب", 60.50), ("على", 60.60), ("فينيو", 60.70)), y=600),
    plain(61.00, 63.51, "تُطبّق الشروط والأحكام", y=1520),
]
