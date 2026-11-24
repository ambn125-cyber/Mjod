# رولز شوكولاتة ROLS — v4: user «ليش الخط مو مرتب، خليه مرتب» on v3 → every caption: same place (y 1450), same size, centred,
# whole line fades in at once (no word-by-word, no «·» tokens), max 2 lines; logo card start + end; earlier: spec_rols16 / spec_rols9
IZ_GOLD = (255, 255, 255); IZ_SH = 230; IZ_BLUR = 10; IZ_SIZE = 92; IZ_Y = 1450
LOGO = "kit/brands/rols/logo_card.png"
def L(t0, t1, *lines):
    return iz(t0, t1, *[[(w, t0 + 0.05, "w") for w in ln.split()] for ln in lines])
EV = [
    L(0.20, 3.08, "شوكولاتة تعلق لذّتها", "بدماغك؟"),
    card(3.10, 5.68, LOGO, 3.10, cx=540, cy=560, w=300, r=28),
    L(3.80, 5.68, "57 فرع بالمملكة"),
    L(5.70, 7.88, "بكج الزواج"),
    L(25.28, 29.88, "حشوات جديدة"),
    L(33.34, 37.92, "بالفروع", "والمتجر الإلكتروني"),
    card(44.88, 49.34, LOGO, 44.88, cx=540, cy=420, w=260, r=28),
    L(44.88, 49.34, "تبوك", "حي المروج - طريق ولي العهد"),
]
