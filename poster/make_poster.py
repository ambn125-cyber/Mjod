"""Ad-rate poster for عبدالمجيد (1080x1920 story size). usage: python3 -I make_poster.py photo.png out.png fonts_dir"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
PH, OUT, FD = sys.argv[1:4]
W, H = 1080, 1920
NAVY, NAVY2, GOLD, WHITE = (12, 22, 48), (24, 40, 82), (245, 190, 40), (255, 255, 255)
F = lambda n, s: ImageFont.truetype(f"{FD}/{n}", s)
c = Image.new("RGB", (W, H), NAVY)
# vertical gradient + soft gold glow
g = Image.new("RGB", (1, H)); [g.putpixel((0, y), tuple(int(NAVY[i] + (NAVY2[i] - NAVY[i]) * (1 - abs(y - 700) / 1300)) for i in range(3))) for y in range(H)]
c = g.resize((W, H))
glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((140, 150, 940, 900), fill=120); glow = glow.filter(ImageFilter.GaussianBlur(120))
c.paste(Image.new("RGB", (W, H), GOLD), (0, 0), glow)
d = ImageDraw.Draw(c)
def text(xy, s, f, fill=WHITE, anchor="mm", stroke=0, sfill=None):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, direction="rtl" if any("؀" <= ch <= "ۿ" for ch in s) else "ltr",
           stroke_width=stroke, stroke_fill=sfill)
# photo: brighten a touch, circle with gold ring
p = Image.open(PH).convert("RGB")
p = ImageEnhance.Contrast(ImageEnhance.Brightness(p).enhance(1.04)).enhance(1.06)
p = ImageEnhance.Sharpness(p).enhance(1.3)
D = 600; p = p.resize((D, D), Image.LANCZOS)
m = Image.new("L", (D, D), 0); ImageDraw.Draw(m).ellipse((0, 0, D - 1, D - 1), fill=255)
cx, cy = W // 2, 520
sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).ellipse((cx - D // 2 - 10, cy - D // 2 + 20, cx + D // 2 + 10, cy + D // 2 + 40), fill=160)
c.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(25)))
d = ImageDraw.Draw(c)
d.ellipse((cx - D // 2 - 16, cy - D // 2 - 16, cx + D // 2 + 16, cy + D // 2 + 16), fill=GOLD)
d.ellipse((cx - D // 2 - 6, cy - D // 2 - 6, cx + D // 2 + 6, cy + D // 2 + 6), fill=NAVY)
c.paste(p, (cx - D // 2, cy - D // 2), m)
# badge
d.rounded_rectangle((cx - 210, cy + D // 2 - 20, cx + 210, cy + D // 2 + 52), 36, fill=GOLD)
text((cx, cy + D // 2 + 16), "معلن معتمد · موثوق", F("Tajawal-Black.ttf", 44), NAVY)
# name + title
text((cx, 1010), "عبدالمجيد تبوك", F("Lalezar-Regular.ttf", 130), WHITE)
text((cx, 1115), "صانع محتوى", F("Tajawal-ExtraBold.ttf", 54), GOLD)
text((cx, 1180), "رقم توثيق موثوق 341448", F("Tajawal-ExtraBold.ttf", 38), (200, 210, 230))
# services
d.line((140, 1240, 940, 1240), fill=(255, 255, 255, 60), width=2)
text((cx, 1310), "متاح لاستقبال طلبات الإعلانات", F("Tajawal-Black.ttf", 56), WHITE)
text((cx, 1380), "والتغطيات الميدانية", F("Tajawal-Black.ttf", 56), WHITE)
chips = ["المطاعم", "الكافيهات", "البراندات التجارية"]
fc = F("Tajawal-Black.ttf", 42); x = W - 90
ws = [d.textlength(s, font=fc, direction="rtl") + 60 for s in chips]; gap = 24
x = cx + (sum(ws) + gap * (len(ws) - 1)) / 2
for s, w in zip(chips, ws):
    d.rounded_rectangle((x - w, 1450, x, 1526), 38, outline=GOLD, width=4)
    text((x - w / 2, 1488), s, fc, GOLD); x -= w + gap
# phone bar
d.rounded_rectangle((90, 1660, 990, 1770), 55, fill=GOLD)
text((cx + 170, 1715), "للتنسيق والحجز", F("Tajawal-Black.ttf", 44), NAVY)
text((cx - 170, 1717), "0510972773", F("Tajawal-Black.ttf", 60), NAVY)
c.save(OUT)
