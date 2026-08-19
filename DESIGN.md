---
version: alpha
name: ONEIGHTY
description: Monochrome, high-contrast youth-ministry identity — near-black surfaces, white Space Grotesk display type, and a single white-to-gray gradient as the only accent.
colors:
  primary: "#FFFFFF"
  void: "#000000"
  ink: "#0A0A0A"
  surface: "#111111"
  elevated: "#1A1A1A"
  muted: "#B3B3B3"
  subtle: "#666666"
  accent-soft: "#E6E6E6"
  brand: "#3B82F6"
  brand-cyan: "#22D3EE"
typography:
  h1:
    fontFamily: "Space Grotesk"
    fontSize: 6.5rem
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "-0.03em"
  h2:
    fontFamily: "Space Grotesk"
    fontSize: 3.5rem
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.03em"
  h3:
    fontFamily: "Space Grotesk"
    fontSize: 1.35rem
    fontWeight: 600
  body:
    fontFamily: "Inter"
    fontSize: 1.05rem
    lineHeight: 1.7
  body-md:
    fontFamily: "Inter"
    fontSize: 1rem
    lineHeight: 1.6
  eyebrow:
    fontFamily: "Inter"
    fontSize: 0.85rem
    fontWeight: 600
  label-caps:
    fontFamily: "Inter"
    fontSize: 0.72rem
    fontWeight: 700
    letterSpacing: "0.08em"
rounded:
  sm: 12px
  md: 14px
  lg: 18px
  xl: 32px
  pill: 999px
spacing:
  xs: 8px
  sm: 16px
  md: 24px
  lg: 32px
  xl: 48px
  section: 120px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.void}"
    rounded: "{rounded.pill}"
    padding: 14px 28px
  button-primary-hover:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.void}"
    rounded: "{rounded.pill}"
    padding: 14px 28px
  button-ghost:
    backgroundColor: "rgba(255, 255, 255, 0.06)"
    textColor: "{colors.primary}"
    rounded: "{rounded.pill}"
    padding: 14px 28px
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    rounded: "{rounded.lg}"
    padding: 32px
  card-hover:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    rounded: "{rounded.lg}"
    padding: 32px
  badge:
    backgroundColor: "rgba(255, 255, 255, 0.05)"
    textColor: "{colors.muted}"
    rounded: "{rounded.pill}"
    padding: 8px 18px
  eyebrow:
    backgroundColor: "rgba(255, 255, 255, 0.04)"
    textColor: "{colors.accent-soft}"
    rounded: "{rounded.pill}"
    padding: 8px 16px
  slider-button-hover:
    backgroundColor: "{colors.elevated}"
    textColor: "{colors.primary}"
    rounded: "{rounded.pill}"
---

## Overview

ONEIGHTY is the youth community of World Transformation Church. The visual
identity is deliberately monochrome — a near-black canvas with layered dark
surfaces, white display type, and a single white-to-gray gradient as the only
"color." The result reads premium, cinematic, and quiet: photography and
typography carry the emotion, not color. Interaction is signaled by a reserved
blue (`#3B82F6`) that appears only on hover borders and one faint radial glow.

Everything resolves to two typefaces and one accent. Nothing else is allowed.

## Colors

The palette is near-black neutrals with one light accent. Color is used for
*hierarchy and state*, never for decoration.

- **Primary (`#FFFFFF`):** White — the identity accent and all headings. On this
  site "brand color" means white-on-black.
- **Void (`#000000`):** Page background.
- **Ink (`#0A0A0A`):** Alternating section background (schedule, social, testimonies).
- **Surface (`#111111`):** Cards, nav, and any raised container.
- **Elevated (`#1A1A1A`):** Hover/active raised surfaces (slider buttons).
- **Muted (`#B3B3B3`):** Body and secondary text — the default `<p>` color.
- **Subtle (`#666666`):** Tertiary text, rarely used.
- **Accent-soft (`#E6E6E6`):** Eyebrows and all-caps labels.
- **Brand (`#3B82F6`):** The reserved interaction accent. Used ONLY as a hover
  border (`rgba(59,130,246,0.4)`) on cards and as a faint radial glow
  (`rgba(59,130,246,0.15)`) behind the CTA.
- **Brand-cyan (`#22D3EE`):** A secondary hover border for schedule rows only.
- **Gradient:** `linear-gradient(135deg, #ffffff 0%, #b3b3b3 100%)` — the single
  "color moment." Applied to primary buttons, play buttons, and as a text-fill
  gradient on date/number displays (via `background-clip: text`).

**Rule:** text on the gradient must be black (`#000000`). White text on the
light end of the gradient fails contrast. Translucent white fills
(`rgba(255,255,255,0.04–0.06)`) are used for ghost buttons, badges, and
eyebrows — they composite over near-black, so their *rendered* contrast is high
even though the raw alpha looks low against a white backdrop.

## Typography

Two faces, nothing else:

- **Space Grotesk** (400–800) — display and headings. Tight: `line-height 1.05`,
  `letter-spacing -0.03em`. `h1` is fluid `clamp(3rem, 8vw, 6.5rem)` at 800.
- **Inter** (300–800) — UI and body. Body is `1.05rem / 1.7` in muted; card body
  runs `0.95–1rem`. Links inherit color with no underline.

All-caps micro-labels (eyebrows, card tags, event day labels) use Inter 600–700
with `0.08–0.14em` letter-spacing. They are the only place uppercase is used.

## Layout

- Single centered column, `max-width 1200px`, `24px` side gutters.
- Sections breathe with `120px` vertical padding.
- The hero is a `1fr / 1fr` split — text left, floating visual right — collapsing
  to a single centered column below 968px.
- Card grids: 4-up on desktop, 2-up on tablet, 1-up on mobile (24px gaps).
- The nav is fixed and transparent, gaining a blurred dark background on scroll.

## Elevation & Depth

Depth comes from *layered near-blacks*, not heavy drop shadows. Cards sit at
`#111` on `#000`. Hover raises a card with `translateY(-4px)`, the brand-blue
border, and a soft `0 16px 48px rgba(0,0,0,0.4)` shadow. The scrolled nav blurs
the page with `backdrop-filter: blur(12px)`. The mobile menu casts a wide left
shadow (`-20px 0 60px`).

## Shapes

Generous, consistent radii. Nothing is sharp:

- `18px` — cards and media tiles
- `999px` (pill) — buttons, badges, meta pills
- `14px` — icon tiles and image placeholders
- `32px` — the CTA panel
- `12px` — social list rows

## Components

- **`button-primary`** — the single high-emphasis action. White gradient fill
  (the token records its dominant solid `#FFFFFF`), black text, pill radius,
  `14px 28px` padding, soft white glow. Hover lifts it 2px and brightens the
  glow. Use at most one per view.
- **`button-ghost`** — secondary action. Translucent white fill (`0.06`), white
  text, `1px` white border. For "Follow @oneightywtc" style secondary CTAs.
- **`card`** — the workhorse surface: `#111` fill, `1px rgba(255,255,255,0.07)`
  border, `18px` radius, `32px` padding. Hover: blue border + lift.
- **`badge` / pill** — inline metadata (times, dates, tags): pill radius,
  `rgba(255,255,255,0.05)` fill, muted text, `8px 18px` padding.
- **`eyebrow`** — section kicker: pill outline, `✦` glyph, accent-soft text,
  `8px 16px` padding.
- **Icon tile** — `52px` square, `14px` radius, `rgba(255,255,255,0.06)` fill,
  centered glyph. Used in cards and contact.

## Do's and Don'ts

**Do**

- Keep the canvas near-black (`#000` / `#0a0a0a`) with `#111` surfaces.
- Use white as the brand color and the gradient as the only accent.
- Pair Space Grotesk headings with Inter body.
- Signal interactivity with the reserved brand blue hover border.
- Round everything; prefer 18px and pill radii.

**Don't**

- Don't introduce any bright color beyond the reserved brand blue and cyan hover
  accents — no full-saturation fills.
- Don't put white text on the gradient; use black text on it.
- Don't add a third typeface.
- Don't use sharp corners or square buttons.
- Don't stack multiple `button-primary` CTAs in the same viewport.
