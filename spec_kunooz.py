# Kunooz Alsaada Pharmacy — spec for render_v2.py (source times)
def T(text, t, c="w", s=1.0, join=False):
    return (text, t, c, s, join)
NL = ("\n", 0, None, 1, False)
CAPS = [
    dict(toks=[T("وعلى", 0.00), T("فكرة", 0.70), T("العروض", 0.98, "o"), T("متوفرة", 1.28), T("في", 1.74), T("جميع", 1.82),
               T("الفروع", 2.08, "p")], out=2.42),
    dict(toks=[T("ولو", 2.44), T("تدخل", 2.74), T("الموقع", 3.00, "p"), T("بتحصل", 3.38), T("العروض", 3.66),
               T("أقوى!", 3.94, "o", 1.2), T("منها", 4.20)], out=5.2),
]
KEY_COLOR = (243, 112, 33)   # Kunooz orange
LOGOS = [("kunooz_logo_card.png", 2.44, 99, 520, 470)]
Y_WORD = 1250
