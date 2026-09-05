# Presentation_Siemens_plan.md

Reference document covering the Siemens PowerPoint template layout inventory,
colour scheme analysis, and how to apply Siemens branding to the HTML Slide Reel.

Template file: `Presentation/Template_Apr2026.pptx`

---

## Background: Can we use PPTX layouts as HTML reel backgrounds?

Yes. Two practical approaches:

1. **Export a slide as an image** -- export one PPTX slide as a PNG (1920x1080 or similar),
   then use it as a CSS `background-image` on `.slide`. Clean and simple, but adds a file
   dependency (the reel is no longer fully self-contained).

2. **Embed the image as base64** -- same as above but encode the PNG to base64 and inline it
   directly into the CSS. Keeps the reel as a single self-contained HTML file, but inflates
   the file size noticeably (a full-slide image is typically 100-400 KB encoded).

After full analysis of the template (see sections below), it turned out that **no image export
is needed at all**. Every background in the template is either a solid colour or a two-stop
gradient -- both fully expressible in pure CSS. See the "Practical Summary" section.

---

## Siemens Brand Theme Colours

Extracted from `ppt/theme/theme1.xml` inside the template PPTX:

| Token | Hex | Description |
|---|---|---|
| `dk1` | `#000000` | Black |
| `dk2` / `bg2` | `#000028` | Siemens Deep Blue (primary background) |
| `lt1` / `bg1` | `#FFFFFF` | White |
| `lt2` | `#F3F3F0` | Light Sand / cream |
| `accent1` | `#009999` | Petrol teal (primary accent) |
| `accent2` | `#00D7A0` | Light green |
| `accent3` | `#00BEDC` | Cyan / light blue |
| `accent4` | `#0087BE` | Blue |
| `accent5` | `#00557C` | Dark teal |
| `accent6` | `#000028` | Deep Blue (same as dk2) |
| `hlink` | `#00C1B6` | Hyperlink colour (light petrol) |
| `folHlink` | `#00C1B6` | Followed hyperlink |

Scheme colour name mapping for background references in layout XML:
- `bg2` resolves to `dk2` = `#000028` Deep Blue
- `bg1` resolves to `lt1` = `#FFFFFF` white

---

## Template Layout Inventory -- All 57 Layouts

### Method of analysis

Each layout's `<p:bg>` element was read directly from the PPTX XML. Background type was
classified as: solid-ref (references a theme colour), gradient (two-stop gradient fill),
inherits (no explicit background -- falls back to slide master which is solid `#000028`).

Note: layouts named "picture", "image", or "spotlight" contain image *placeholder shapes*
overlaid on a solid background -- the photos are not embedded in the background itself.
The background XML is solid colour only.

### Full layout table

| # | Layout Name | Background Type | Colour Scheme | Min Size for HTML Reel |
|---|---|---|---|---|
| 0 | Chapter title dark 80pt | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 1 | Chapter title dark 60pt | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 2 | Chapter title dark 40pt | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 3 | Chapter title color 80pt | solid-ref | `#FFFFFF` White | 0 KB -- CSS only |
| 4 | 1_Chapter title color 80pt | solid-ref | `#FFFFFF` White | 0 KB -- CSS only |
| 5 | 1_Chapter title color 60pt | solid-ref | `#FFFFFF` White | 0 KB -- CSS only |
| 6 | 1_Chapter title color 40pt | solid-ref | `#FFFFFF` White | 0 KB -- CSS only |
| 7 | 1_Chapter title dark 40pt | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 8 | Title picture dark 48pt | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 9 | Title picture dark 40pt | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 10 | Title picture dark 36pt | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 11 | Title picture Gradient 48pt | gradient | `#000028` -> `#009999` (Deep Blue -> Petrol) | ~5 KB PNG |
| 12 | Title picture Gradient 40pt | gradient | `#000028` -> `#009999` (Deep Blue -> Petrol) | ~5 KB PNG |
| 13 | Title picture Gradient 36pt | gradient | `#000028` -> `#009999` (Deep Blue -> Petrol) | ~5 KB PNG |
| 14 | 1_Title picture dark 48pt | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 15 | 1_Title picture dark 40pt | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 16 | 1_Title picture dark 36pt | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 17 | Single large image | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 18 | Single large image Deep Blue | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 19 | Single image (Text spotlight) | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 20 | 1_Single image (Text spotlight) | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 21 | 2_Single image (Text spotlight) | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 22 | 3_Single image (Text spotlight) | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 23 | Free Content | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 24 | Full bleed color Deep Blue | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 25 | 3_Full bleed color Deep Blue | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 26 | 1_Full bleed color Deep Blue | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 27 | Full bleed color Gradient | gradient | `#000028` -> `#009999` (Deep Blue -> Petrol) | ~5 KB PNG |
| 28 | 1_Full bleed color Gradient | gradient | `#000028` -> `#009999` (Deep Blue -> Petrol) | ~5 KB PNG |
| 29 | 2_Full bleed color Gradient | gradient | `#000028` -> `#009999` (Deep Blue -> Petrol) | ~5 KB PNG |
| 30 | 5_Full bleed color Deep Blue | solid | `#00D7A0` accent2 light green (accent overlay) | 0 KB -- CSS only |
| 31 | Statement dark | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 32 | Contact | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 33 | 6_Full bleed color Deep Blue | solid | `#00D7A0` accent2 light green (accent overlay) | 0 KB -- CSS only |
| 34 | Single image_ Full length with text - Dark | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 35 | Quote dark | solid | `#000028` Deep Blue (direct) | 0 KB -- CSS only |
| 36 | 1_Statement dark | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 37 | Agenda | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 38 | 1_Contact | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 39 | Chapter title light 80pt | solid-ref | `#000028` Deep Blue bg, shapes create light feel | 0 KB -- CSS only |
| 40 | Chapter title light 60pt | solid-ref | `#000028` Deep Blue bg, shapes create light feel | 0 KB -- CSS only |
| 41 | Chapter title light 40pt | solid-ref | `#000028` Deep Blue bg, shapes create light feel | 0 KB -- CSS only |
| 42 | Title picture light 48pt | solid-ref | `#000028` Deep Blue bg, image area lightens it | 0 KB -- CSS only |
| 43 | Title picture light 40pt | solid-ref | `#000028` Deep Blue bg, image area lightens it | 0 KB -- CSS only |
| 44 | Title picture light 36pt | solid-ref | `#000028` Deep Blue bg, image area lightens it | 0 KB -- CSS only |
| 45 | Index / Agenda light | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 46 | 1_Free Content | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 47 | Full bleed color Light Sand | solid-ref | `#F3F3F0` Light Sand / cream, dark text | 0 KB -- CSS only |
| 48 | 1_Single large image | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 49 | 4_Single image (Text spotlight) | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 50 | 1_Two columns (Spotlight) | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 51 | 3_One object (small) | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 52 | 1_Single image_ Full length with text - Dark | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |
| 53 | Title and Content | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 54 | 1_Blank | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 55 | 1_Two Content | inherits master | `#000028` Deep Blue | 0 KB -- CSS only |
| 56 | 2_Single image_ Full length with text - Dark | solid-ref | `#000028` Deep Blue | 0 KB -- CSS only |

---

## Practical Summary -- Distinct Background Styles

Only 3 distinct background types exist across all 57 layouts:

| Background Style | Colours | How to Apply in HTML Reel | Compressed Size |
|---|---|---|---|
| Deep Blue solid | `#000028` | CSS `background-color` | **0 KB** -- already what the reel uses |
| White / Light Sand solid | `#FFFFFF` or `#F3F3F0` | CSS `background-color` | **0 KB** |
| Deep Blue to Petrol gradient | `#000028` to `#009999` | CSS `linear-gradient()` -- no image needed | **0 KB** |

The gradient that appears in layouts 11-13 and 27-29 is a two-stop linear gradient:
Deep Blue (#000028) flowing into Petrol (#009999). This is expressible in one CSS line:

```css
background: linear-gradient(135deg, #000028 0%, #009999 100%);
```

No PNG export or base64 encoding is needed for any Siemens brand background.
The "gradient" and "picture" layout names refer to decorative shapes and image
placeholder boxes overlaid on a solid background -- not embedded photos.

---

## How to Apply a Siemens Background to the HTML Reel

### Option A -- Solid Deep Blue (current default, no change needed)

The HTML reel already uses `--deepblue: #000028` as `background: var(--deepblue)` on `.slide`.
This matches the majority of Siemens template layouts exactly.

### Option B -- Deep Blue to Petrol gradient (matches layouts 11-13, 27-29)

In the CSS block (Section 6 of HTML_SlideReel.md), change `.slide`:

```css
.slide {
  /* replace: background: var(--deepblue); */
  background: linear-gradient(135deg, #000028 0%, #009999 100%);
}
```

Or apply per slide type for variety (e.g. cover slides use gradient, content slides use solid):

```css
.slide.cover {
  background: linear-gradient(135deg, #000028 0%, #009999 100%);
}
```

### Option C -- Light Sand (matches layout 47, Full bleed color Light Sand)

```css
.slide {
  background: #F3F3F0;
  color: #000028;  /* invert text to dark */
}
```

Note: using a light background requires inverting all text colours (they are currently
set for dark backgrounds). Not recommended for mixed-content reels unless all slides
share the light scheme.

### Option D -- Per-slide background (mixed schemes)

Add a `bg` field to individual SLIDES array objects and apply it in the JS renderer:

```js
function buildSlide(data) {
  var div = document.createElement('div');
  div.className = 'slide' + (data.type === 'cover' ? ' cover' : '');
  if (data.bg) div.style.background = data.bg;
  ...
}
```

Then in the SLIDES array:

```js
{ type: 'cover', bg: 'linear-gradient(135deg, #000028 0%, #009999 100%)', ... }
{ type: 'bullets', bg: '#000028', ... }
```

---

## Notes on Layout Naming Conventions

- Prefix `1_`, `2_`, `3_` etc. = variant of the same layout (different placeholder positions)
- `dark` in name = white text on deep blue background
- `light` in name = visual impression created by overlaid shapes; background XML is still deep blue
- `color` in name = white background with coloured accents
- `picture` in name = contains an image placeholder shape; user must supply the photo
- `Gradient` in name = two-stop gradient fill on background
- `Free Content` (index 23) = the default workhorse layout used in build_deck.py
- Font size in name (80pt, 60pt, 40pt, 48pt etc.) = size of the title placeholder text
