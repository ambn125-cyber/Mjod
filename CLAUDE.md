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
| كنوز السعادة pharmacy, ريحانة perfumes, ثمد | see logos | — | Rayhana: no underline under text; logo raised |
| مكتب فهد للسداد وتحصيل الديون (حي العليا, Tabuk) | white + blue (40,90,255) like the sign | 12 كلمات حركية | phone 058 140 2370; Tabby/Emkan logos in `kit/brands/payments/`; landmark after «مقابل» unconfirmed |
| تبوك ماسترز Tabuk Masters (billiards, opposite Madinah Rd bridge) | white + red (225,30,45) like the sign | 5 ستيكر (`spec_masters_st.py`) — user disliked 12 here | pro table brand is Rasson «راسون» |
| ميركاتو Mercato (global brands, حي الفيصلية · شارع المطار القديم) | magenta (225,45,140), blue (60,140,235) | 9 عنوان مزدوج (+10/11) | brand names as the English word; "نايس"→Nike? and "رينوفا" unconfirmed |
| إلوفي élevée (زود العقارية Zood, Riyadh) | gold (233,190,95) | 6 فخم; short cut in 9/10/11 (`spec_elevee2.py`) | Arabic name on the sign is «إلوفي»; company confirmed by the Zood end logo |

## Quick fixes (keep render time short)
- Segment re-render: renderers honour env `T0` (start offset); render only the changed window and splice with
  `overlay=enable='between(t,A,B)'` and `setpts=PTS-STARTPTS+A/TB`.
- Text-only change: edit the spec, preview 2–3 frames, then full render (~1.5–2 min per minute of video).
