# الجمّار v2 — user's own re-cut (64 s) that already has my v1 captions burned in; this pass only adds the pops missing from that burned version: opening 0–5.8 s + the two dish words added later (نكهة وقرمشة / مقرمش وطري); source times
B_ = ((30, 110, 230), (255, 255, 255)); R_ = ((230, 40, 55), (255, 255, 255)); W_ = (255, 255, 255)
Y_POP = 400
TAG = (255, 255, 255)
def dish(t0, t1, txt, col=W_):
    return pop(t0, t1, big=(txt, t0, col, [t0] * len(txt.split()), 150), y=360)
EV = [
    pop(0.00, 3.28, top=("أهلاً بكم في", 0.00, W_), big=("الجمّار", 0.72, B_), tag=("من أقوى وألذ المطاعم", 1.82), y=1350),
    pop(3.30, 5.80, top=("متخصصين في", 3.30, W_), big=("دجاج عالجمر", 4.60, R_, [4.60, 5.38]), y=1300),
    dish(10.14, 13.42, "نكهة وقرمشة"),
    dish(18.08, 24.64, "مقرمش وطري"),
]
