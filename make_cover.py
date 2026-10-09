import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
BG, OUT, FONTS = sys.argv[1:4]
W, H = 1080, 1920
RED, GREEN, WHITE = (226, 28, 40), (52, 235, 52), (255, 255, 255)
img = Image.open(BG).convert("RGB").resize((W, H))
img = ImageEnhance.Contrast(ImageEnhance.Color(img).enhance(1.15)).enhance(1.05).convert("RGBA")
# dark gradients top and bottom so text reads
g = np.zeros((H, 1), np.float32)
y = np.arange(H)[:, None]
g = np.clip(1 - y / 760, 0, 1) ** 1.4 * 0.82 + np.clip((y - 1180) / 740, 0, 1) ** 1.3 * 0.88
shade = Image.fromarray((np.repeat(g, W, 1) * 255).astype(np.uint8))
dark = Image.new("RGBA", (W, H), (8, 8, 12, 0)); dark.putalpha(shade)
img.alpha_composite(dark)

def font(n, s, v=None):
    f = ImageFont.truetype(f"{FONTS}/{n}", s)
    if v: f.set_variation_by_name(v)
    return f

def text(canvas, s, f, color, cx, cy, stroke=0):
    d = "rtl" if any("؀" <= ch <= "ۿ" for ch in s) else "ltr"
    bb = f.getbbox(s, direction=d, stroke_width=stroke)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    P = 50
    m = Image.new("L", (w + 2 * P, h + 2 * P), 0)
    ImageDraw.Draw(m).text((P - bb[0], P - bb[1]), s, font=f, fill=255, direction=d, stroke_width=stroke)
    sh = m.filter(ImageFilter.GaussianBlur(12)).point(lambda v: int(v * .85))
    x, yy = int(cx - m.width / 2), int(cy - m.height / 2)
    canvas.alpha_composite(Image.merge("RGBA", (Image.new("L", m.size, 0),) * 3 + (sh,)), (x + 3, yy + 9))
    layer = Image.new("L", m.size, 0)
    ImageDraw.Draw(layer).text((P - bb[0], P - bb[1]), s, font=f, fill=255, direction=d)
    if stroke:
        ol = Image.merge("RGBA", (Image.new("L", m.size, 10),) * 3 + (m,)); canvas.alpha_composite(ol, (x, yy))
    fill = Image.new("RGBA", m.size, color + (0,)); fill.putalpha(layer); canvas.alpha_composite(fill, (x, yy))
    return w, h

def pill(canvas, s, f, cx, cy, bg, fg=WHITE, padx=50, pady=26):
    bb = f.getbbox(s, direction="rtl"); w, h = bb[2] - bb[0], bb[3] - bb[1]
    box = Image.new("RGBA", (w + 2 * padx, h + 2 * pady), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((0, 0, box.width - 1, box.height - 1), radius=box.height // 2, fill=bg)
    sh = Image.new("RGBA", (box.width + 80, box.height + 80), (0, 0, 0, 0))
    sm = Image.new("L", sh.size, 0); sm.paste(box.getchannel("A"), (40, 40))
    sh.putalpha(sm.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .6)))
    canvas.alpha_composite(sh, (int(cx - sh.width / 2) + 2, int(cy - sh.height / 2) + 10))
    ImageDraw.Draw(box).text((padx - bb[0], pady - bb[1]), s, font=f, fill=fg, direction="rtl")
    canvas.alpha_composite(box, (int(cx - box.width / 2), int(cy - box.height / 2)))

AR = lambda s: font("Tajawal-Black.ttf", s)
SER = lambda s: font("NotoSerif.ttf", s, "Black")

# top: hook + price
text(img, "تيشيرتات بـ", AR(118), WHITE, W / 2, 250)
pw, ph = text(img, "9 SAR", SER(250), GREEN, W / 2, 470, stroke=6)
# hand-drawn circle around price
d = ImageDraw.Draw(img)
rw, rh, cx, cy = pw / 2 + 70, ph / 2 + 70, W / 2, 485
pts = []
for i in range(161):
    a = math.radians(205) - math.radians(395) * i / 160
    wob = 1 + 0.035 * math.sin(a * 3) + 0.05 * i / 160
    pts.append((cx + rw * wob * math.cos(a), cy + rh * wob * math.sin(a)))
d.line(pts, fill=(0, 0, 0, 120), width=16, joint="curve")
d.line(pts, fill=WHITE + (255,), width=10, joint="curve")

# bottom: store + offers line
text(img, "حرق أسعار!", AR(150), WHITE, W / 2, 1450)
pill(img, "صدى الملاعب", AR(104), W / 2, 1640, RED)
text(img, "تيشيرتات · بناطيل · أحذية", AR(56), WHITE, W / 2, 1790)
img.convert("RGB").save(OUT, quality=95)
