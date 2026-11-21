# طاووق Tawouk v2 — two offers: بوكس طاووق 16 (4 crispy pcs + fries + bun + 2 garlic) and وجبة التوفير 19 (4 chicken pcs + same); all branches, limited time.
# style 13 brand orange + blue; poster cards cropped from the user's screenshots; seated shots: pops high (y≈340), posters low over the tray; source times
O_ = ((245, 125, 20), (255, 255, 255)); B_ = ((25, 100, 195), (255, 255, 255)); W_ = (255, 255, 255); Y_ = (255, 210, 40)
LOGO = "kit/brands/tawouk/logo_card.png"; BOX = "kit/brands/tawouk/poster_box.png"; TAWFEER = "kit/brands/tawouk/poster_tawfeer.png"
Y_POP = 340
def b(t0, t1, txt, t, col, size=None, y=None, **k):
    return pop(t0, t1, big=(txt, t, col, [t] * len(txt.split())) + ((size,) if size else ()), y=y or Y_POP, **k)
EV = [
    pop(0.00, 2.24, big=("وقف!", 0.00, Y_, [0.00]), tag=("شوف هذا العرض قبل لا تطلب", 0.76), y=420),
    pop(2.26, 4.72, top=("معك بس", 2.26, W_), big=("16 ريال؟", 2.62, Y_, [2.62, 2.76]), tag=("تعال أعلمك وش تاخذ من طاووق", 3.18), y=560),
    b(4.74, 6.40, "4 قطع كرسبي", 5.14, O_),
    pop(6.42, 8.40, top=("زائد", 6.42, W_), big=("بطاطس وخبز", 6.62, Y_, [6.62, 7.38]), tag=("و 2 ثوم", 7.94), y=500),
    pop(8.42, 10.44, top=("بوكس طاووق", 8.90, W_), big=("16 ريال", 9.66, Y_, [9.66, 9.80]), y=500),
    b(10.46, 11.20, "ولا دلّع نفسك", 10.46, W_, y=1230),
    pop(12.14, 13.46, big=("19 ريال", 12.36, Y_, [12.36, 12.68])),
    b(13.48, 14.70, "4 قطع دجاج", 13.48, O_),
    pop(14.72, 16.48, top=("زائد", 14.42, W_), big=("بطاطس وخبز", 14.72, Y_, [14.72, 15.54]), tag=("و 2 ثوم", 16.04), y=500),
    b(16.50, 17.32, "مقرمش من برا", 16.50, Y_),
    b(17.34, 19.04, "وطري من جوا", 17.34, O_),
    pop(19.06, 21.93, top=("العرض في", 19.88, W_), big=("جميع الفروع", 20.22, B_, [20.22, 20.48]), tag=("والفترة محدودة", 20.86), y=520),
    card(8.42, 10.44, BOX, 8.90, cx=540, cy=1690, w=440, r=18),
    card(10.46, 13.46, TAWFEER, 11.22, cx=215, cy=1730, w=390, r=18),
    card(19.88, 21.93, LOGO, 19.88, cx=540, cy=1300, w=400, r=24),
]
TAG = (255, 255, 255)
