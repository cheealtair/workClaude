# Ebook Publishing from Markdown

## Can You Publish a .md File as an Ebook?

Yes. Markdown must first be converted to a distribution format, then uploaded to a platform.

## Converting MD to Ebook Format

Use **Pandoc** for conversion:

- **EPUB** (universal — Kindle, Apple Books, Kobo): `pandoc book.md -o book.epub`
- **PDF**: `pandoc book.md -o book.pdf`
- **MOBI**: Use Calibre, or submit EPUB directly to Amazon

## Publishing Platforms

| Platform | Format | You Keep |
|---|---|---|
| Amazon KDP | EPUB or DOCX | 70% (price $2.99–$9.99, select regions) or 35% |
| Gumroad | PDF/EPUB | ~90% minus Stripe fees |
| Leanpub | Markdown natively | 80% |
| Payhip | PDF/EPUB | 95% |
| Draft2Digital | EPUB | Distributes to many retailers |

## Royalty Clarification

- **Leanpub 80%** — you keep 80%, they take 20%
- **Amazon KDP 70%** — you keep 70%, they take 30% (must price $2.99–$9.99 in select countries; otherwise 35% tier applies)

## Monetization Options

- One-time purchase
- Pay-what-you-want (Gumroad/Leanpub)
- Early access / iterative publishing (Leanpub model)
- Bundle with a course (Teachable/Podia)
- Newsletter upsell — free sample, paid full version

## Recommendation

- **Technical/niche book**: Leanpub (Markdown-native, 80% royalty) or Gumroad (simple, low friction)
- **Broad retail reach**: Amazon KDP via Pandoc-generated EPUB

## Leanpub Publishing Steps (Manuscript Already Written)

1. Create a Leanpub account and start a new book project
2. Connect your manuscript — Dropbox folder, GitHub repo, or direct upload of `.md` files
3. Configure metadata — title, description, cover image, pricing (minimum and suggested price)
4. Preview the book — Leanpub generates PDF/EPUB for formatting review
5. Publish — click "Publish New Version"; book goes live immediately
6. Set up payments — connect PayPal or Stripe for monthly royalty payouts
7. Promote — share your Leanpub URL; use reader notifications to alert past buyers on updates

Full process from account creation to live book: under an hour.

## Copy Protection on Leanpub (Markdown Source)

### Source Markdown
Readers never see your `.md` source files. The Leanpub build pipeline reads from your private
Dropbox folder or private GitHub repo — keep it private and only Leanpub's system can access it.

### Output Files (PDF/EPUB)
Leanpub does not offer hard DRM. Copy protection on the distributed files works as follows:

- **Buyer watermarking (default)** — Leanpub embeds the buyer's name and email into every
  PDF and EPUB at download time. If a copy leaks, you can identify the source.
- **No hard DRM** — Leanpub intentionally omits DRM. It is user-hostile, easily stripped by
  determined pirates, and frustrates legitimate buyers more than bad actors.
- **Honor system + watermark** — The standard model for technical books on Leanpub. Most
  buyers are professionals who will not pirate a low-priced technical book.

### Practical Advice
- Leave watermarking enabled (it is on by default).
- Price reasonably — low friction pricing reduces the motivation to pirate.
- Accept residual risk; no distribution platform eliminates it entirely.

## Amazon KDP Publishing Steps (Manuscript Already Written)

### Step 1 — Convert Your Manuscript
- Use Pandoc to generate EPUB: `pandoc book.md -o book.epub`
- Or convert to DOCX: `pandoc book.md -o book.docx`
- EPUB is preferred; KDP accepts both but renders EPUB more reliably.
- For PDF (print-on-demand only), format to 6x9 inches with 0.5in margins.

### Step 2 — Prepare Your Cover Image
- Minimum 1000px on shortest side; recommended 2560 x 1600px (1.6:1 ratio)
- JPEG or TIFF, RGB color space
- KDP provides a free Cover Creator tool if you don't have a design

### Step 3 — Create a KDP Account
- Go to kdp.amazon.com and sign in with your Amazon account
- Complete tax interview (W-9 for US; W-8BEN for non-US) — required before any royalties paid
- Add a bank account for direct deposit

### Step 4 — Create a New Kindle eBook Title
1. Click **Create** > **Kindle eBook**
2. Fill in **Book Details**:
   - Language, title, subtitle, series (if any)
   - Author name (pen name allowed)
   - Description — this is your sales copy; invest time here
   - Publishing rights — confirm you hold rights
   - Keywords (up to 7) — choose searchable phrases, not single words
   - Categories (up to 2 BISAC categories) — browse carefully, affects discoverability
   - Age/grade range (if applicable)
3. Fill in **Kindle eBook Content**:
   - Upload manuscript (EPUB or DOCX)
   - Use KDP's online previewer to check formatting on simulated devices
   - Upload cover image
   - Enable DRM — recommended unless you explicitly want DRM-free
4. Fill in **Kindle eBook Pricing**:
   - Enroll in **KDP Select** (optional) — exclusive to Amazon for 90 days, unlocks Kindle
     Unlimited income and promotional tools (free days, Countdown Deals)
   - Set territories — worldwide or specific countries
   - Choose royalty plan:
     - **70% royalty** — requires $2.99–$9.99 price in supported territories
     - **35% royalty** — any price; applies automatically outside supported territories
   - Set price; Amazon shows equivalent prices in other currencies automatically
   - Matchbook / lending — optional features

### Step 5 — Publish
- Click **Publish Your Kindle eBook**
- Review takes 24–72 hours; you receive an email when live
- Your book appears on Amazon.com (and other Amazon stores) once approved

### Step 6 — Print-on-Demand (Optional — KDP Paperback)
- After publishing the eBook, click **Create Paperback**
- Upload a print-ready PDF (6x9 recommended for technical books)
- Upload a cover via KDP's cover calculator (spine width depends on page count)
- Set paperback price — royalty is 60% minus printing cost (varies by page count and market)
- Paperback and eBook listings auto-link on Amazon's product page

### Step 7 — Ongoing Management
- Monitor sales and royalties in **KDP Reports** (updated daily)
- Update manuscript anytime — upload new file, click publish; buyers do not get auto-updates
  (unlike Leanpub), but can request the update via Amazon customer service
- Run price promotions via **KDP Select** if enrolled
- Request Amazon Marketing Services (AMS) ads via the KDP dashboard for paid promotion

### Royalty Reference
| Price Range | Territory | Royalty Rate |
|---|---|---|
| $2.99 - $9.99 | US, UK, CA, AU + others | 70% |
| $0.99 - $2.98 or $10.00+ | Same territories | 35% |
| Any price | All other territories | 35% |

Delivery fee of $0.15/MB is deducted from 70% royalties — keep file size small.

## Payment Methods for Non-US / Non-Local Bank Authors

### Amazon KDP

Amazon's preferred payout method is direct bank transfer (EFT). Supported countries are listed
in KDP account settings — many are covered, but not all.

| Method | Works? | Notes |
|---|---|---|
| Direct bank transfer (EFT) | Yes, where supported | Check KDP's supported country list |
| Wire transfer | Yes (fallback) | ~$15 fee per payment; $100 minimum threshold |
| PayPal | No | Not supported by KDP for royalty payments |
| Wise (virtual bank account) | Yes (workaround) | Get a Wise US/UK/EU virtual account; register it in KDP as a local bank account |
| Payoneer (virtual bank account) | Yes (workaround) | Same approach as Wise; KDP treats it as domestic |

**Recommended for unsupported countries:** Wise first (lower fees, better exchange rates),
Payoneer second. Both provide virtual US/UK/EU bank details that KDP accepts as local accounts.

### Leanpub

Leanpub pays via Stripe or PayPal. Minimum payout threshold is $50.

| Method | Works? | Notes |
|---|---|---|
| PayPal | Yes | Supported in most PayPal-enabled countries; 0-2% receipt fee |
| Stripe | Yes | Connect a local bank account to Stripe; broader country support than PayPal in some regions |
| Wise (via Stripe) | Yes (workaround) | Link a Wise virtual bank account to your Stripe account if your country is not natively supported |
| Wire transfer | No | Not offered by Leanpub |

**Recommended for non-US authors on Leanpub:** PayPal if available in your country; Stripe +
Wise virtual account as fallback.

## Amazon KDP — Copy Protection

Amazon's approach differs significantly from Leanpub's watermarking model.

### DRM (Digital Rights Management)
- Enabled via a checkbox during Step 4 (Kindle eBook Content) at publish time
- Locks the file to the buyer's registered Kindle devices and apps
- Prevents opening on non-Amazon readers without stripping the DRM
- **Cannot be reversed after publishing** — enabling then disabling DRM requires unpublishing
  and republishing as a new title; existing buyers keep the DRM version

### DRM Limitations
- Determined pirates can strip Kindle DRM using freely available tools (e.g. Calibre + DeDRM plugin)
- DRM deters casual copying but not motivated bad actors
- Amazon does not embed buyer identity into the file — leaked copies cannot be traced to a
  specific buyer (unlike Leanpub's watermarking)

### Third-Party Watermarking Options
If you want Leanpub-style buyer traceability on files sold via KDP or directly:

| Tool | Type | Notes |
|---|---|---|
| Booxtream | Commercial service | Embeds invisible forensic watermarks per buyer; aimed at publishers |
| Digimarc | Commercial service | Enterprise-level invisible watermarking; expensive |
| Pressbooks | Platform | Generates watermarked EPUBs per buyer — requires selling outside KDP |
| Calibre + plugin | DIY | Manual watermarking before upload; not per-buyer without scripting |

### Practical Recommendation for Indie Authors on KDP
1. Enable DRM at publish time — deters casual sharing
2. Keep file size small (reduces delivery fee and piracy appeal of large bundles)
3. Price reasonably — low prices reduce motivation to pirate
4. Accept that per-buyer traceability is not available natively on KDP
5. Commercial watermarking services are cost-effective only at publisher scale

## Multi-Platform Strategy — Publishing on Amazon and Leanpub Simultaneously

### Are They Mutually Exclusive?
No — you can publish on both Amazon KDP and Leanpub at the same time, with one condition:
**do not enroll in KDP Select**. KDP Select requires 90-day exclusivity to Amazon; enrolling
while selling on Leanpub violates the terms and risks account action.

Without KDP Select, Amazon has no exclusivity claim over your content.

### What You Give Up by Skipping KDP Select
| Feature | KDP Select | Without KDP Select |
|---|---|---|
| Kindle Unlimited (KU) income | Yes | No |
| Free promotion days | Yes | No |
| Countdown Deals | Yes | No |
| Multi-platform selling | No | Yes |

For technical and niche books, KU income is typically modest — most KU readers target
fiction. Skipping Select to stay multi-platform is usually the right trade-off.

### Recommended Split for Technical Authors
- **Leanpub** — primary channel for your core audience; early access, iterative updates,
  pay-what-you-want pricing, and direct author-reader relationship
- **Amazon KDP** (without Select) — retail discoverability; reaches Kindle readers who
  would never find Leanpub

### Pricing Strategy Across Platforms
- Price Leanpub slightly lower or offer a bundle (book + files/code) — gives buyers a
  reason to buy direct rather than via Amazon
- Amazon price should reflect the "final" version; Leanpub can sell in-progress drafts
- Amazon does not allow prices below $0.99 for the 35% tier; Leanpub allows free minimum price

### Updating Your Book
- **Leanpub** — publish a new version anytime; existing buyers are notified and can
  download the update immediately
- **Amazon KDP** — upload a new file and republish; existing buyers do NOT automatically
  receive updates and must request them via Amazon customer service
- Maintain your master manuscript in one place (e.g. private GitHub repo) and export
  to each platform's required format from there
