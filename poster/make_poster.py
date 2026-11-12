"""Ad-rate poster for عبدالمجيد تبوك (1080x1920 story size), several themes.
usage: python3 -I make_poster.py THEME out.png fonts_dir     (THEME: navy | black | white)"""
import sys, qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
THEME, OUT, FD = sys.argv[1:4]
W, H = 1080, 1920
T = {
    # bg top/bottom, accent, text, soft text, name font, body font, photo
    "navy":  dict(bg=((14, 26, 58), (8, 14, 34)), acc=(245, 190, 40), txt=(255, 255, 255), soft=(190, 202, 228),
                  name=("ElMessiri.ttf", "Bold", 132), body=("Cairo.ttf", "Black"), sub=("Cairo.ttf", "Bold"), photo="poster/photo_yellow.png"),
    "black": dict(bg=((22, 20, 18), (6, 6, 6)), acc=(212, 172, 92), txt=(250, 244, 230), soft=(190, 178, 150),
                  name=("Amiri-Bold.ttf", None, 140), body=("Changa.ttf", "ExtraBold"), sub=("Changa.ttf", "SemiBold"), photo="poster/photo_yellow.png"),
    "white": dict(bg=((250, 250, 252), (228, 234, 242)), acc=(20, 60, 140), txt=(16, 28, 60), soft=(80, 95, 125),
                  name=("Lalezar-Regular.ttf", None, 140), body=("Tajawal-Black.ttf", None), sub=("Tajawal-ExtraBold.ttf", None), photo="poster/photo_light.png",
                  acc2=(245, 180, 30)),
}[THEME]
ACC, TXT, SOFT = T["acc"], T["txt"], T["soft"]
ACC2 = T.get("acc2", ACC)
ON_ACC = (255, 255, 255) if THEME == "white" else (14, 16, 24)


def F(spec, size):
    name, var = spec[0], spec[1]
    f = ImageFont.truetype(f"{FD}/{name}", size)
    if var:
        f.set_variation_by_name(var)
    return f


# background: vertical gradient + soft glow behind the photo
top, bot = T["bg"]
g = Image.new("RGB", (1, H))
for y in range(H):
    k = y / H
    g.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * k) for i in range(3)))
c = g.resize((W, H))
glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).ellipse((140, 120, 940, 920), fill=110 if THEME != "white" else 70)
c.paste(Image.new("RGB", (W, H), ACC2), (0, 0), glow.filter(ImageFilter.GaussianBlur(130)))
d = ImageDraw.Draw(c)


def text(xy, s, f, fill, anchor="mm"):
    rtl = any("؀" <= ch <= "ۿ" for ch in s)
    d.text(xy, s, font=f, fill=fill, anchor=anchor, direction="rtl" if rtl else "ltr")


# thin frame
d.rounded_rectangle((36, 36, W - 36, H - 36), 40, outline=ACC + (0,), width=3)

# photo in a ringed circle
p = Image.open(T["photo"]).convert("RGB")
p = ImageEnhance.Sharpness(ImageEnhance.Contrast(ImageEnhance.Brightness(p).enhance(1.04)).enhance(1.06)).enhance(1.3)
D = 560; p = p.resize((D, D), Image.LANCZOS)
m = Image.new("L", (D, D), 0); ImageDraw.Draw(m).ellipse((0, 0, D - 1, D - 1), fill=255)
cx, cy = W // 2, 470
sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).ellipse((cx - D // 2, cy - D // 2 + 30, cx + D // 2, cy + D // 2 + 50), fill=150 if THEME != "white" else 70)
c.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(28)))
d = ImageDraw.Draw(c)
d.ellipse((cx - D // 2 - 16, cy - D // 2 - 16, cx + D // 2 + 16, cy + D // 2 + 16), fill=ACC)
d.ellipse((cx - D // 2 - 6, cy - D // 2 - 6, cx + D // 2 + 6, cy + D // 2 + 6), fill=top)
c.paste(p, (cx - D // 2, cy - D // 2), m)

# badge, sitting just below the circle (not over the face/chin)
by = cy + D // 2 + 40
fb = F(T["body"], 40)
bw = d.textlength("معلن معتمد · موثوق", font=fb, direction="rtl") + 80
d.rounded_rectangle((cx - bw / 2, by - 36, cx + bw / 2, by + 36), 36, fill=ACC)
text((cx, by + 2), "معلن معتمد · موثوق", fb, ON_ACC)

# name + title
text((cx, 975), "عبدالمجيد تبوك", F(T["name"], T["name"][2]), TXT)
text((cx, 1085), "صانع محتوى", F(T["sub"], 56), ACC2 if THEME == "white" else ACC)
d.line((300, 1150, 780, 1150), fill=ACC, width=3)

# services
text((cx, 1215), "متاح لاستقبال طلبات الإعلانات", F(T["body"], 54), TXT)
text((cx, 1285), "والتغطيات الميدانية", F(T["body"], 54), TXT)
chips = ["المطاعم", "الكافيهات", "البراندات التجارية"]
fc = F(T["body"], 40)
ws = [d.textlength(s, font=fc, direction="rtl") + 60 for s in chips]; gap = 22
x = cx + (sum(ws) + gap * (len(ws) - 1)) / 2
for s, w in zip(chips, ws):
    d.rounded_rectangle((x - w, 1350, x, 1424), 37, outline=ACC, width=4)
    text((x - w / 2, 1387), s, fc, ACC); x -= w + gap

# QR codes (TikTok / Snapchat)
def qr(url, size=170):
    q = qrcode.QRCode(border=1, box_size=10); q.add_data(url); q.make(fit=True)
    return q.make_image(fill_color="black", back_color="white").convert("RGB").resize((size, size), Image.NEAREST)
for url, lbl, qx in (("https://snapchat.com/t/CDMKZQ8l", "سناب شات", 640), ("https://www.tiktok.com/@zzs_1", "تيك توك", 270)):
    d.rounded_rectangle((qx - 10, 1455, qx + 180, 1645), 20, fill=(255, 255, 255), outline=ACC, width=3)
    c.paste(qr(url), (qx, 1465))
    text((qx + 85, 1675), lbl, F(T["sub"], 34), TXT)
text((cx, 1530), "امسح", F(T["body"], 38), ACC)
text((cx, 1578), "وتابعني", F(T["body"], 38), ACC)

# phone bar
d.rounded_rectangle((90, 1720, 990, 1830), 55, fill=ACC)
text((cx + 175, 1775), "للتنسيق والحجز", F(T["body"], 44), ON_ACC)
text((cx - 165, 1777), "0510972773", F(T["body"], 62), ON_ACC)
text((cx, 1862), "رقم توثيق موثوق: 341448", F(T["sub"], 28), SOFT)
c.save(OUT)
