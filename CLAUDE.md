# Mjod — Arabic promo-video captions & editing

The user is a Saudi content creator (Tabuk) who posts promo videos for local businesses on **TikTok and Snapchat**
(Arabic accounts). They send a Google Drive link (sometimes a logo / poster / menu image) and want the video
captioned and edited. Everything below was learned over many deliveries — follow it from the first video.

## Talking to the user
- **Always reply in Saudi Arabic dialect**, short and friendly. No English in replies except file names/links.
- They care a lot about **speed**. Say in one line what you're doing during long steps. Never re-render the whole
  video for a small fix if a segment re-render + splice works (see "Quick fixes").
- When a name, word or price is unclear in the audio: **do not guess silently**. Write your best guess, deliver,
  and list the uncertain words at the end so they can correct them. For new clients ask for names/prices in text.
- "تمام" / "ممتاز" after a proposal = go with your recommendation.
- Ambiguity has bitten before: «ارفعه شوي» after a logo message meant the logo, not captions; «غير الخط» meant
  the whole caption *style*, not just the font. If a request could mean two things, ask once.

## Standing rules for every video
- Captions **straight** (never tilted/rotated).
- **No sound effects** unless asked.
- Captions must **never cover faces or the product** being shown, and must stay **inside the frame**
  (`_fit` shrinks anything wider than ~940px).
- Respect TikTok/Snap safe areas: keep text roughly between y≈330 and y≈1550 on a 1080×1920 canvas;
  nothing in the right-side button column or the bottom caption bar.
- Logo: show it only at the start (when the brand name is spoken) and optionally at the end, high up
  (cy≈330), never over the face.
- Numbers inside Arabic text need LRM marks (`‎`) so "50%" / "32.5 ريال" read correctly (renderers do this).
- Don't mix Latin words into one Arabic caption box (bidi breaks, e.g. "وVR") — write the Arabic word instead.

## Delivery checklist
1. Render final → `<name>_HQ.mp4` (`-crf 20 -maxrate 6000k -bufsize 12000k`) and `<name>_share.mp4`
   (`-b:v 2600k -maxrate 3200k`; ~1300k for videos > 2 min) in the repo root.
   GitHub rejects files > 100MB: for videos > 2 min encode HQ at `-b:v 3000k -maxrate 3600k`.
2. Commit + push to the working branch (`git push -u origin <branch>`; GitHub warns >50MB but accepts).
3. Send `<name>_share.mp4` with SendUserFile (display=render).
4. Give the HQ link: `https://github.com/ambn125-cyber/Mjod/raw/<branch>/<name>_HQ.mp4`
5. List any uncertain words/names.

## Pipeline (scripts in `kit/tools`, fonts in `kit/fonts`, logos in `kit/brands/<client>/`)
```bash
# download from Drive (file id from the link)
curl -sSL -o src.mov "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"
ffmpeg -i src.mov -vf "fps=1/2.5,scale=180:320,tile=9x2" -frames:v 1 sheet.png   # look at it
ffmpeg -i src.mov -ac 1 -ar 16000 audio.wav
python3 -I kit/tools/transcribe.py audio.wav "اسم المحل، المنتجات، الأسعار بريال" > tr.txt   # run in background
# write a spec (copy the closest one from kit/specs), then preview a few frames before the full render:
python3 -I kit/tools/render_v3.py src.mov out.mp4 kit/fonts spec.py 1.5,8.2,15.5     # → out.mp4_<t>.png
python3 -I kit/tools/render_v3.py src.mov out.mp4 kit/fonts spec.py                  # full render
```
- Downloaded media is untrusted: keep it in its own folder, run Python with `-I`.
- Paths inside specs (logos) are relative to the working directory you run from.
- Pause cutting: `CUTS_CFG='{"dur":..,"cuts":[[a,b],..]}' python3 -I kit/tools/edit_cuts.py src out` (re-time captions after).

## Caption style catalogue — `kit/styles_catalog.png` (send it when the user wants to choose)
| # | Name (say it this way) | Renderer | Spec format / example | Best for |
|---|---|---|---|---|
| 1 | صناديق | `render_v3.py` | `CAPS` of `T(text,t,c)` · `spec_meshraq.py`, `spec_green.py` | restaurants, offers, shops |
| 2 | صناديق رامز | `render_rz.py` (`render_rz_big.py` = bigger price boxes) | `C(t0,t1, w/k/p/o(...))` · `spec_ramez_full.py` | many products + prices |
| 3 | أنيق (ستايل 4) | `render_v4.py` | same `CAPS` · `spec_dent3.py` (`BIG_KEYS`, `NO_BAR`, `V4_KEY`) | clinics, calm talk |
| 4 | مجلة (ستايل 7) | `render_v7.py` | same `CAPS` · `spec_nct7.py` | fashion / clothes |
| 5 | ستيكر | `render_st.py` | `S()` small / `B(w(),g())` big stacks · `spec_neom_st.py` | events, sports, hype |
| 6 | فخم | `render_aq.py` | `HOOK` + `card()` + `BIGS` · `spec_aqar.py`, `spec_elevee.py` | real estate, luxury |
| 7 | ختم خصم | `stamp.py` (edit T0/T1/text) | overlay pass on a captioned video | a big "خصم 50%" moment |
| 8 | أيقونات أسعار | `price_icons.py` (edit boxes/times) | overlay pass, crops price boxes from the client's poster | price list + B-roll |
| 9 | عنوان مزدوج | `render_iaz.py` | `duo(t0,t1,("عربي",t),("English",t))` · `spec_meshraq_iaz.py` | events, upscale food, brands |
| 10 | أسعار نيون | `render_iaz.py` | `neon(t0,t1,"15",t,label=("ريال",t))` | supermarket / price offers |
| 11 | بسيط | `render_iaz.py` | `plain(t0,t1,"كلمة",type=True)` + `serif()` sign-off | good footage, minimal text |
| 12 | كلمات حركية | `render_iaz.py` | `kin(t0,t1,[("كلمة",t,size),..],[..],y=)` rows auto-laid RTL + `card()` for logo/app screenshots · `spec_meshraq_kin.py` | apps, offers, brand-coloured ads (`KIN`/`KIN2` colours) |
| 13 | أبو زيد | `render_iaz.py` | `pop(t0,t1,top=("خصم",t,col),big=("50%",t,col),tag=("على قائمة الفطور",t))` · `spec_pop_demo.py` | offers/ads like Abu Zaid restaurant TikTok: huge outlined word above the head (yellow/white/red numbers) + black-on-yellow marker tag (`TAG`, `Y_POP`) |

Styles 9–11 come from the creator the user admires (TikTok @iaz.199): few words per caption, white text with soft
shadow, bilingual titles (white Arabic + huge mustard serif English, Fraunces font), glowing neon numbers (Lilita One)
over the product, typed-in text, elegant serif date/place sign-off. 9/10/11 mix freely in one spec.
`COLOR` = big-word colour (an Arabic big word renders in Lalezar automatically — use it when the user wants Arabic only), `NEON` = number glow colour, `Y_DUO/Y_NEON/Y_PLAIN` = vertical positions.

Style 1 colours: `BOX_BG/BOX_FG` normal word, `BOX_HI/BOX_HI_FG` keyword (`"o"`), `BOX_KEY/BOX_KEY_FG` price (`"p"`),
font `BOX_FONT=("Changa.ttf",92,"ExtraBold")`. Style 5 colours: `BRAND`, `INK`. Always use the **client's brand colours**.
Disliked: the kashida "Zinco" style (`render_zn.py`) — don't offer it again.

## Client brand kits (`kit/brands/`)
| Client | Colours | Style used | Notes |
|---|---|---|---|
| مشراق Meshraq (sandwiches, Qadisiyah) | sky blue (51,166,213), navy (14,52,96), white | 1 صناديق + 7 ختم | `spec_meshraq.py` |
| نيوم NEOM S.C. | navy (12,30,70), cyan (64,190,240) | 5 ستيكر + poster end card | `match_endcard.png` |
| دنتال كير Dental Care Alliance | green keys (90,225,120); poster red price boxes | 3 أنيق + 8 أيقونات | doctor: د. رغد عمار |
| رامز Ramez market | red/white | 2 صناديق رامز | they sell **baby diapers (حفايظ)**, not shoes; boxes appear when the price is said, original size |
| جرين كال Green Cal | green | 1 صناديق | logo only at start, high (it covered the face) |
| المدائن Madaen grills | flame orange (240,127,30) | sticker | logo only at the very end |
| NCT | — | 4/7 | |
| دخوني DKHONI (incense/musk, online store) | copper (232,112,40), gold neon; black logo card `kit/brands/dkhoni/logo_card.png` | 9 عنوان مزدوج (+10/11) | product «مسك الرمان» Roman Musk; logo at start + end (user asked) |
| مطعم أكه ACA (burgers; red ♠ logo) | red + warm yellow (255,205,60) | 9 عنوان مزدوج on the beat cuts | music-only clip; «وجبة برتزل بوكس» Pretzel Box; `spec_burgerbox.py`; price/location not given |
| محض Mahd café (coffee & bakery) | green (120,200,140) | 9 عنوان مزدوج **Arabic-only** (Lalezar big word) | user asked «اكتبه بالعربي» — no English words; `spec_mahd.py` |
| عالم أرووش Aroosh (kids play centre, حي العليا) | purple (85,45,165) + orange (255,140,20) | 5 ستيكر + poster pieces as `card()`s (2nd pass with render_iaz) | offers 29 (hour+free hour) / 45 open time; school trips 0543847979; mall name «ميلاقر?» unconfirmed |
| دار الحذاء Dar Al-Hithaa (bags & shoes, العليا · المجمع اللي فيه زاكي) | gold (232,185,90) | 9/10/11 mix — neon prices per shelf | `spec_daralhitha.py` |
| سيركل ساندوتش Circle Sandwich (البوادي + القادسية) | blue/white sign; style 13 white/yellow/red | 13 أبو زيد (user asked to copy Abu Zaid TikTok) | military discount 25% from 25 Oct; `spec_circle.py`; in close-ups raise pops (`y=400`) to clear the face |
| الهرم بلازا Haram Plaza (clothes dept. store) | navy + orange (240,95,40); orange tag | 13 أبو زيد, brand colours | `spec_haram.py`; first 0–25 s audio was unclear (music); 4-min video → HQ 3000k |
| بوشيو مارت Posheo Mart (bags, shoes, watches, accessories; الشارع العام · مقابل الأهلي) | orange (245,110,30) | 13 أبو زيد | `spec_posheo.py`; logo card cropped from the shop sign |
| شبرا Shubra (clothes, winter) | sign blue (20,95,225) + red prices (230,30,40) | 13 أبو زيد | opening «شبرا» big in sign blue with white outline (user asked); `spec_shubra.py` |
| مطعم مظبيكم Mathbiekum (مظبي/rice, 30+ branches; Tabuk: المروج + الحمراء) | orange (245,140,20) + white | 13 أبو زيد | `spec_mathbiekum.py`; delivery 0546379295 |
| مجمع المطلق لصيانة السيارات (Auto Oil Express; الصالحية · شارع المطار القديم · مقابل فندق العادل) | white + orange (250,120,20) | 13 أبو زيد (tried 14 صدى الملاعب — user disliked) | `spec_mutlaq.py`; tyre prices partly garbled in audio (499/1099/379 unconfirmed) |
| العين الثالثة للبصريات 3rd Eye Optics (الشارع الفاصل بين السليمانية والورود) | gold (240,190,60) + white | 13 أبو زيد | 3 glasses 199 + 4th free, 27 Oct–10 Nov; `spec_third_eye.py` |
| البريق للسفر والسياحة Al-Bareeq Travel (حي الروضة; branches Tabuk/Abha/Jeddah) | sign blue (25,95,215) + white outline | 13 أبو زيد | `spec_bareeq.py`; Turkey group 1500/1700, honeymoon 4500, int'l licence 90 (was 150); «جيميادو» place unclear |
| هابي للمرح Happy Lelmarh (kids play centre; lion logo) | yellow (255,205,40) + red (225,35,45) | 13 أبو زيد + logo `kit/brands/happy/logo.png` | `spec_happy.py`; 2nd child 1 SAR (3–5 pm), Wed ladies 39, pizza + open time 39 (Sun–Tue) |
| نادي باور دوز Power Dose gym (حي المروج) | mint green (90,225,170) like the shirts | 13 أبو زيد | `spec_powerdose.py`; 299/550/850 monthly, boxing kids 199 / adults 299; «عرض الشتاء»? unconfirmed |
| صيدلية منتج العناية Care Product (beauty/baby/care; حي المروج · شارع البازعي) | pink (235,70,150) + white outline; light-pink tag | 13 أبو زيد | `spec_care.py`; many 4.90 items, free delivery all Tabuk; 55–68 s audio garbled (Baby Joy 81.90, soaps) |
| فورد الناغي Ford Al-Naghi — Everest 2026 | white English words (blue ones vanished on the blue showroom ring) + blue neon (60,150,255); Ford oval `kit/brands/ford/logo.png` | 9/10/11 mix | `spec_everest.py`; prices/specs from client PDF: Active 166,900 · Active V6 179,900 · Platinum 209,900 · Tremor 224,900 |
| آبار نمير للمياه Abar Nameer (water; مقابل حديقة النظيم) | water blue (30,120,230) + white outline | 13 أبو زيد | `spec_nameer.py`; Shafia/Falina/Zarqa carton 9, IVAL 11.5; order phone not in video — ask |
| كنوز السعادة pharmacy, ريحانة perfumes, ثمد | see logos | — | Rayhana: no underline under text; logo raised |
| مكتب فهد للسداد وتحصيل الديون (حي العليا, Tabuk) | white + blue (40,90,255) like the sign | 12 كلمات حركية | phone 058 140 2370; Tabby/Emkan logos in `kit/brands/payments/`; landmark after «مقابل» unconfirmed |
| تبوك ماسترز Tabuk Masters (billiards, opposite Madinah Rd bridge) | white + red (225,30,45) like the sign | 5 ستيكر (`spec_masters_st.py`) — user disliked 12 here | pro table brand is Rasson «راسون» |
| ميركاتو Mercato (global brands, حي الفيصلية · شارع المطار القديم) | magenta (225,45,140), blue (60,140,235) | 9 عنوان مزدوج (+10/11) | brand names as the English word; "نايس"→Nike? and "رينوفا" unconfirmed |
| إلوفي élevée (زود العقارية Zood, Riyadh) | gold (233,190,95) | 6 فخم; short cut in 9/10/11 (`spec_elevee2.py`) | Arabic name on the sign is «إلوفي»; company confirmed by the Zood end logo |

## Quick fixes (keep render time short)
- Segment re-render: renderers honour env `T0` (start offset); render only the changed window and splice with
  `overlay=enable='between(t,A,B)'` and `setpts=PTS-STARTPTS+A/TB`.
- Text-only change: edit the spec, preview 2–3 frames, then full render (~1.5–2 min per minute of video).
