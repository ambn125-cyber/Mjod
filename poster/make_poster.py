"""Ad-rate poster for عبدالمجيد (1080x1920 story size). usage: python3 -I make_poster.py photo.png out.png fonts_dir"""
import sys, qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
PH, OUT, FD = sys.argv[1:4]
W, H = 1080, 1920
NAVY, NAVY2, GOLD, WHITE = (12, 22, 48), (24, 40, 82), (245, 190, 40), (255, 255, 255)
F = lambda n, s: ImageFont.truetype(f"{FD}/{n}", s)
c = Image.new("RGB", (W, H), NAVY)
# vertical gradient + soft gold glow
g = Image.new("RGB", (1, H)); [g.putpixel((0, y), tuple(int(NAVY[i] + (NAVY2[i] - NAVY[i]) * (1 - abs(y - 700) / 1300)) for i in range(3))) for y in range(H)]
c = g.resize((W, H))
glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((190, 150, 890, 850), fill=120); glow = glow.filter(ImageFilter.GaussianBlur(120))
c.paste(Image.new("RGB", (W, H), GOLD), (0, 0), glow)
d = ImageDraw.Draw(c)
def text(xy, s, f, fill=WHITE, anchor="mm", stroke=0, sfill=None):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, direction="rtl" if any("؀" <= ch <= "ۿ" for ch in s) else "ltr",
           stroke_width=stroke, stroke_fill=sfill)
# photo: brighten a touch, circle with gold ring
p = Image.open(PH).convert("RGB")
p = ImageEnhance.Contrast(ImageEnhance.Brightness(p).enhance(1.04)).enhance(1.06)
p = ImageEnhance.Sharpness(p).enhance(1.3)
D = 520; p = p.resize((D, D), Image.LANCZOS)
m = Image.new("L", (D, D), 0); ImageDraw.Draw(m).ellipse((0, 0, D - 1, D - 1), fill=255)
cx, cy = W // 2, 470
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
text((cx, 900), "عبدالمجيد", F("Lalezar-Regular.ttf", 150), WHITE)
text((cx, 1010), "صانع محتوى · تبوك", F("Tajawal-ExtraBold.ttf", 54), GOLD)
text((cx, 1075), "رقم توثيق موثوق 341448", F("Tajawal-ExtraBold.ttf", 38), (200, 210, 230))
# services
d.line((140, 1130, 940, 1130), fill=(255, 255, 255, 60), width=2)
text((cx, 1190), "متاح لاستقبال طلبات الإعلانات", F("Tajawal-Black.ttf", 56), WHITE)
text((cx, 1258), "والتغطيات الميدانية", F("Tajawal-Black.ttf", 56), WHITE)
chips = ["المطاعم", "الكافيهات", "البراندات التجارية"]
fc = F("Tajawal-Black.ttf", 42); x = W - 90
ws = [d.textlength(s, font=fc, direction="rtl") + 60 for s in chips]; gap = 24
x = cx + (sum(ws) + gap * (len(ws) - 1)) / 2
for s, w in zip(chips, ws):
    d.rounded_rectangle((x - w, 1312, x, 1388), 38, outline=GOLD, width=4)
    text((x - w / 2, 1350), s, fc, GOLD); x -= w + gap
# QR codes
def qr(url):
    q = qrcode.QRCode(border=1, box_size=10); q.add_data(url); q.make(fit=True)
    return q.make_image(fill_color="black", back_color="white").convert("RGB").resize((220, 220), Image.NEAREST)
for url, lbl, x0 in (("https://www.tiktok.com/@zzs_1", "تيك توك", 210), ("https://snapchat.com/t/CDMKZQ8l", "سناب شات", 650)):
    d.rounded_rectangle((x0 - 12, 1430, x0 + 232, 1674), 24, fill=WHITE)
    c.paste(qr(url), (x0, 1442))
    text((x0 + 110, 1712), lbl, F("Tajawal-Black.ttf", 40), WHITE)
text((cx, 1555), "تابعني", F("Tajawal-Black.ttf", 40), GOLD)
text((cx, 1610), "@zzs_1", F("Tajawal-ExtraBold.ttf", 40), (200, 210, 230))
# phone bar
d.rounded_rectangle((90, 1770, 990, 1880), 55, fill=GOLD)
text((cx + 170, 1825), "للتنسيق والحجز", F("Tajawal-Black.ttf", 44), NAVY)
text((cx - 170, 1827), "0510972773", F("Tajawal-Black.ttf", 60), NAVY)
c.save(OUT)
