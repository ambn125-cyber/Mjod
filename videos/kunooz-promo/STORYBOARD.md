---
format: 1080x1920
duration: 45s
message: "ليش تروح الصيدلية؟ كنوز السعادة توصلك لين باب بيتك"
arc: Hook (question) → Product_Intro → Benefit 1 → Benefit 2 → Benefit 3 → Recap → CTA
audience: أهالي الأطفال في السعودية
mode: autonomous
music: none
captions: skipped (no narration)
---

## Video direction

- **palette system** — `frame.md` (capsule, remixed on Kunooz): canvas cream `#F5F9FD`, ink `#231F1E`, brand blue (`coral` slot `#087FBD` + sky tints) for pills and fills, brand orange (`peach` `#F26A21`) is the one hot accent — used only on the answer words and the numbers. Every container is a pill with a 2px ink outline and a soft hard-offset shadow.
- **motion grammar + reveal model** — long-tail `power3.out` entrances, springy `back.out(1.6)` only on pills landing; pieces reveal on the beat (silent film — beats every ~0.5–0.8 s), never front-loaded; holds are still.
- **rhythm** — Frame 1 is fast staccato (question), Frames 3–5 share one shape (number pill → proof screenshot → hero claim) so the three answers rhyme, Frame 6 is the held breather that lists all three, Frame 7 is the lockup.
- **type** — Tajawal (shipped in `assets/fonts/`), Arabic right-to-left, sentence-length lines never; hero words only.
- **negative list** — no slideshow (front-load then freeze), no screensaver float; no bokeh, no purple AI gradients, no browser chrome; no audio of any kind.

## Frame 1 — The question

- scene: «ليش تروح الصيدلية؟» lands word by word, then a hard-cut answer «…وهي تجيك؟»
- duration: 5s
- poster: 3.8s
- transition_in: cut
- status: animated
- src: compositions/frames/01-question.html
- type: hook
- blueprint: kinetic-type-beats (Adapt)
- focal: type

Adapt: keep the in-place token swap; Arabic, two beats.
Scene 1 (0.0–2.2s): cream canvas; «ليش» «تروح» «الصيدلية؟» rise in one by one, centered at ~0.35 H, ink, display size; a blue pill outline draws under «الصيدلية؟».
Scene 2 (2.2–3.4s): hard swap — the line is replaced in place by «وهي» «تجيك» «لين بابك؟» with «تجيك» in orange.
Scene 3 (3.4–5.0s): a text pill «توصيل لين البيت» pops below and the frame holds still.

## Frame 2 — Kunooz is online

- scene: the Kunooz logo blooms, then the real home page rises in a phone pill under it
- duration: 6s
- poster: 4s
- transition_in: crossfade
- status: animated
- src: compositions/frames/02-intro.html
- type: product_intro
- blueprint: device-surface-showcase (Adapt)
- focal: assets/home.jpg
- roles: logo.png = supporting · home.jpg = cutout
- asset_candidates: assets/logo.png, assets/home.jpg

Scene 1 (0.0–1.4s): logo springs in at top-center (~0.12 H), wordmark under it.
Scene 2 (1.4–3.6s): a rounded phone pill rises from below carrying home.jpg; a slow scroll inside it.
Scene 3 (3.6–6.0s): pill label «الحين أونلاين» pops at the phone's top-right corner; hold.

## Frame 3 — Answer 1: free delivery

- scene: number pill «1», the site's own delivery banner, hero claim «توصيل مجاني»
- duration: 7s
- poster: 5s
- transition_in: crossfade
- status: animated
- src: compositions/frames/03-delivery.html
- type: benefit
- blueprint: compose
- focal: assets/banner-delivery.jpg
- asset_candidates: assets/banner-delivery.jpg

Scene 1 (0.0–1.0s): big orange circle «1» pops top-left of center.
Scene 2 (1.0–3.2s): hero «توصيل مجاني» rises line by line, ink, display.
Scene 3 (3.2–5.0s): the real banner strip slides in as a pill card, then «فوق 100 ريال» chip pops beside it.
Scene 4 (5.0–7.0s): hold still.

## Frame 4 — Answer 2: up to 60% off

- scene: number pill «2», old price 87 strikes to 51.99, hero «خصم حتى 60%»
- duration: 7s
- poster: 5.5s
- transition_in: crossfade
- status: animated
- src: compositions/frames/04-discount.html
- type: benefit
- blueprint: compose
- focal: assets/card-pampers.jpg
- asset_candidates: assets/card-pampers.jpg

Scene 1 (0.0–1.0s): orange circle «2» pops.
Scene 2 (1.0–2.8s): hero «خصم حتى 60%» — «60%» counts up 0→60 in orange.
Scene 3 (2.8–5.2s): the real Pampers card from the site slides in; a price pill shows «87.00» that strikes through, then «51.99 ريال» pops in orange.
Scene 4 (5.2–7.0s): hold.

## Frame 5 — Answer 3: Tamara

- scene: number pill «3», the Tamara page in a phone pill, four payment pills cascade «12.99»
- duration: 7s
- poster: 5.5s
- transition_in: crossfade
- status: animated
- src: compositions/frames/05-tamara.html
- type: benefit
- blueprint: grid-card-assemble (Adapt)
- focal: assets/tamara.jpg
- asset_candidates: assets/tamara.jpg

Adapt: keep the staggered cascade; four payment pills instead of a feature grid.
Scene 1 (0.0–1.0s): orange circle «3» pops.
Scene 2 (1.0–2.6s): hero «قسّطها مع تمارا».
Scene 3 (2.6–4.4s): the real Tamara page rises inside a phone pill (left 55%).
Scene 4 (4.4–6.0s): four «12.99» pills cascade down the right side, «دفعة ١…٤».
Scene 5 (6.0–7.0s): hold.

## Frame 6 — Recap

- scene: the three answers stack as pills under «ليش تروح؟»
- duration: 6s
- poster: 4.5s
- transition_in: crossfade
- status: animated
- src: compositions/frames/06-recap.html
- type: benefits
- blueprint: grid-card-assemble (Reproduce)

Scene 1 (0.0–1.0s): small heading «ليش تروح الصيدلية؟» at top.
Scene 2 (1.0–3.4s): three pills cascade: «توصيل مجاني», «خصم حتى 60%», «تقسيط مع تمارا», each with its orange number.
Scene 3 (3.4–6.0s): held breather.

## Frame 7 — CTA

- scene: logo lockup, URL pill types on, «اطلب الحين»
- duration: 7s
- poster: 5.5s
- transition_in: crossfade
- status: animated
- src: compositions/frames/07-cta.html
- type: cta
- blueprint: logo-assemble-lockup (Adapt)
- focal: assets/logo.png
- asset_candidates: assets/logo.png

Adapt: spring-bloom from zero on a cleared stage, extended to URL + CTA.
Scene 1 (0.0–1.4s): logo blooms from zero at center (~0.33 H).
Scene 2 (1.4–3.6s): URL pill «kunooz-alsaada.com» types on under it.
Scene 3 (3.6–5.0s): orange CTA pill «اطلب الحين» springs in.
Scene 4 (5.0–7.0s): hold; final frame settles (no exit needed).
