# رولز شوكولاتة ROLS — v5: user «تذكر حق الماجد للعود» → «ايه ولا تكثر كتابة بس الأشياء المهمة»
# = Al-Majed v2 look (style 9 Arabic-only: bold Lalezar gold big word + small white line, NEON_SHADOW), fixed high position y 420, only key points; logo start + end
GRADE = "eq=contrast=1.10:saturation=1.22:gamma=0.96,colorbalance=rm=0.05:gm=0.01:bm=-0.05:rh=0.03:bh=-0.03"   # warmer, glossier chocolate (user approved preview)
COLOR = (225, 170, 70); DUO_BIG = 190; NEON_SHADOW = True; DUO_POP = True; Y_DUO = 420
LOGO = "kit/brands/rols/logo_card.png"
EV = [
    duo(0.20, 3.08, ("شوكولاتة تعلق لذّتها بدماغك؟", 0.20), ("رولز", 2.30)),
    card(3.10, 5.68, LOGO, 3.10, cx=540, cy=1350, w=300, r=28),
    duo(3.80, 5.68, ("في كل مدن المملكة", 3.80), ("57 فرع", 3.90)),
    duo(5.70, 7.88, ("عندك زواج؟", 5.70), ("بكج الزواج", 6.80)),
    duo(25.28, 29.88, ("جرّبوا", 25.28), ("الحشوات الجديدة", 25.80)),
    duo(33.34, 37.92, ("بالفروع والمتجر الإلكتروني", 33.34), ("البوكسات", 34.00)),
        duo(44.88, 46.70, ("حي المروج - طريق ولي العهد", 44.88), ("تبوك", 44.88)),
]
# 46.7–end: end card kit/brands/rols/endcard.png (night storefront, darkened, logo + location) faded in with ffmpeg after the render
EV += [
]
