# Ebook Publishing from Markdown

## Table of Contents

- [General](#general)
  - [Can You Publish a .md File as an Ebook?](#can-you-publish-a-md-file-as-an-ebook)
  - [Converting MD to Ebook Format](#converting-md-to-ebook-format)
  - [Publishing Platforms](#publishing-platforms)
  - [Royalty Clarification](#royalty-clarification)
  - [Monetization Options](#monetization-options)
  - [Recommendation](#recommendation)
- [Leanpub (Manuscript Already Written)](#leanpub-manuscript-already-written)
  - [Publishing Steps](#publishing-steps)
  - [Copy Protection on Leanpub](#copy-protection-on-leanpub-markdown-source)
  - [Payment Methods for Non-US / Non-Local Bank Authors](#payment-methods-for-non-us--non-local-bank-authors)
- [Amazon KDP Publishing (Manuscript Already Written)](#amazon-kdp-publishing-manuscript-already-written)
  - [Steps to Publish](#steps-to-publish)
  - [Royalty Reference](#royalty-reference)
  - [Payment Methods for Non-US / Non-Local Bank Authors](#payment-methods-for-non-us--non-local-bank-authors-1)
  - [Copy Protection](#copy-protection)
  - [Practical Recommendation for Indie Authors on KDP](#practical-recommendation-for-indie-authors-on-kdp)
- [GitHub Self-Publishing — Automated PDF + GitHub Pages](#github-self-publishing--automated-pdf--github-pages)
  - [Publishing Architecture](#publishing-architecture)
  - [Markdown as the Book Source](#markdown-as-the-book-source)
  - [Automated PDF Generation](#automated-pdf-generation)
  - [Book Cover](#book-cover)
  - [Publishing Through GitHub Pages](#publishing-through-github-pages)
  - [Optional Reader Contributions](#optional-reader-contributions)
  - [Zero-Upfront-Cost Publishing](#zero-upfront-cost-publishing)
  - [Copy Protection](#copy-protection-1)
  - [Advantages and Limitations](#advantages-and-limitations)
  - [Security Considerations](#security-considerations)
  - [Position Alongside Leanpub and Amazon KDP](#position-alongside-leanpub-and-amazon-kdp)
- [Multi-Platform Strategy — Publishing on Amazon and Leanpub Simultaneously](#multi-platform-strategy--publishing-on-amazon-and-leanpub-simultaneously)
  - [Are They Mutually Exclusive?](#are-they-mutually-exclusive)
  - [What You Give Up by Skipping KDP Select](#what-you-give-up-by-skipping-kdp-select)
  - [Recommended Split for Technical Authors](#recommended-split-for-technical-authors)
  - [Pricing Strategy Across Platforms](#pricing-strategy-across-platforms)
  - [Updating Your Book](#updating-your-book)

\newpage

## General

### Can You Publish a .md File as an Ebook?

Yes. Markdown must first be converted to a distribution format, then uploaded to a platform.


### Converting MD to Ebook Format

Use **Pandoc** for conversion:

- **EPUB** (universal — Kindle, Apple Books, Kobo): `pandoc book.md -o book.epub`
- **PDF**: `pandoc book.md -o book.pdf`
- **MOBI**: Deprecated by Amazon (2022) — submit EPUB directly to KDP instead


### Publishing Platforms

| Platform | Format | You Keep |
|---|---|---|
| Amazon KDP | EPUB or DOCX | 70% (price $2.99–$9.99, select regions) or 35% |
| Gumroad | PDF/EPUB | ~90% minus Stripe fees |
| Leanpub | Markdown natively | 80% |
| Payhip | PDF/EPUB | 95% |
| Draft2Digital | EPUB | Distributes to many retailers |
| GitHub Pages | PDF | 100% — free distribution; optional Ko-fi contributions |


### Royalty Clarification

- **Leanpub 80%** — you keep 80%, they take 20%
- **Amazon KDP 70%** — you keep 70%, they take 30% (must price $2.99–$9.99 in select countries; otherwise 35% tier applies)
- **GitHub Pages 100%** — free distribution; no royalty split; reader contributions optional via Ko-fi


### Monetization Options

- One-time purchase
- Pay-what-you-want (Gumroad/Leanpub)
- Early access / iterative publishing (Leanpub model)
- Bundle with a course (Teachable/Podia)
- Newsletter upsell — free sample, paid full version


### Recommendation

- **Technical/niche book**: Leanpub (Markdown-native, 80% royalty) or Gumroad (simple, low friction)
- **Broad retail reach**: Amazon KDP via Pandoc-generated EPUB
- **Continuously updated / free distribution**: GitHub Pages — zero cost, fully automated, ideal for books that evolve frequently





\newpage

## Leanpub (Manuscript Already Written)

### Publishing Steps 

1. Create a Leanpub account and start a new book project
2. Connect your manuscript — Dropbox folder, GitHub repo, or direct upload of `.md` files
3. Configure metadata — title, description, cover image, pricing (minimum and suggested price)
4. Preview the book — Leanpub generates PDF/EPUB for formatting review
5. Publish — click "Publish New Version"; book goes live immediately
6. Set up payments — connect PayPal or Stripe for monthly royalty payouts
7. Promote — share your Leanpub URL; use reader notifications to alert past buyers on updates

Full process from account creation to live book: under an hour.

### Copy Protection on Leanpub (Markdown Source)

Source Markdown   
Readers never see your `.md` source files. The Leanpub build pipeline reads from your private
Dropbox folder or private GitHub repo — keep it private and only Leanpub's system can access it.

Output Files (PDF/EPUB)   
Leanpub does not offer hard DRM. Copy protection on the distributed files works as follows:

- **Buyer watermarking (default)** — Leanpub embeds the buyer's name and email into every
  PDF and EPUB at download time. If a copy leaks, you can identify the source.
- **No hard DRM** — Leanpub intentionally omits DRM. It is user-hostile, easily stripped by
  determined pirates, and frustrates legitimate buyers more than bad actors.
- **Honor system + watermark** — The standard model for technical books on Leanpub. Most
  buyers are professionals who will not pirate a low-priced technical book.

Practical Advice    
- Leave watermarking enabled (it is on by default).
- Price reasonably — low friction pricing reduces the motivation to pirate.
- Accept residual risk; no distribution platform eliminates it entirely.

### Payment Methods for Non-US / Non-Local Bank Authors

Leanpub pays via Stripe or PayPal. Minimum payout threshold is $50.

| Method | Works? | Notes |
|---|---|---|
| PayPal | Yes | Supported in most PayPal-enabled countries; 0-2% receipt fee |
| Stripe | Yes | Connect a local bank account to Stripe; broader country support than PayPal in some regions |
| Wise (via Stripe) | Yes (workaround) | Link a Wise virtual bank account to your Stripe account if your country is not natively supported |
| Wire transfer | No | Not offered by Leanpub |

**Recommended for non-US authors on Leanpub:** PayPal if available in your country; Stripe +
Wise virtual account as fallback.




\newpage

## Amazon KDP Publishing (Manuscript Already Written)

### Steps to Publish

Step 1 — Convert Your Manuscript
- Use Pandoc to generate EPUB: `pandoc book.md -o book.epub`
- Or convert to DOCX: `pandoc book.md -o book.docx`
- EPUB is preferred; KDP accepts both but renders EPUB more reliably.
- For PDF (print-on-demand only), format to 6x9 inches with 0.5in margins.

Step 2 — Prepare Your Cover Image
- Minimum 1000px on shortest side; recommended 2560 x 1600px (1.6:1 ratio)
- JPEG or TIFF, RGB color space
- KDP provides a free Cover Creator tool if you don't have a design

Step 3 — Create a KDP Account
- Go to kdp.amazon.com and sign in with your Amazon account
- Complete tax interview (W-9 for US; W-8BEN for non-US) — required before any royalties paid
- Add a bank account for direct deposit

Step 4 — Create a New Kindle eBook Title
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

Step 5 — Publish
- Click **Publish Your Kindle eBook**
- Review takes 24–72 hours; you receive an email when live
- Your book appears on Amazon.com (and other Amazon stores) once approved

Step 6 — Print-on-Demand (Optional — KDP Paperback)
- After publishing the eBook, click **Create Paperback**
- Upload a print-ready PDF (6x9 recommended for technical books)
- Upload a cover via KDP's cover calculator (spine width depends on page count)
- Set paperback price — royalty is 60% minus printing cost (varies by page count and market)
- Paperback and eBook listings auto-link on Amazon's product page

Step 7 — Ongoing Management
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


### Payment Methods for Non-US / Non-Local Bank Authors

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



### Copy Protection

Amazon's approach differs significantly from Leanpub's watermarking model.

DRM (Digital Rights Management)  
- Enabled via a checkbox during Step 4 (Kindle eBook Content) at publish time
- Locks the file to the buyer's registered Kindle devices and apps
- Prevents opening on non-Amazon readers without stripping the DRM
- **Cannot be reversed after publishing** — enabling then disabling DRM requires unpublishing
  and republishing as a new title; existing buyers keep the DRM version

DRM Limitations   
- Determined pirates can strip Kindle DRM using freely available tools (e.g. Calibre + DeDRM plugin)
- DRM deters casual copying but not motivated bad actors
- Amazon does not embed buyer identity into the file — leaked copies cannot be traced to a
  specific buyer (unlike Leanpub's watermarking)

Third-Party Watermarking Options   
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




\newpage

## GitHub Self-Publishing — Automated PDF + GitHub Pages

GitHub provides a third approach to ebook publishing that is quite different from platforms such as Leanpub and Amazon KDP. Rather than uploading a finished book to a publishing service, the author can use GitHub as both the source repository and the foundation of an automated publishing system.

In this model, the Markdown manuscript remains the single source of truth. Changes are made directly to the Markdown file, committed to Git, and pushed to GitHub. From that point, GitHub Actions can automatically convert the manuscript into a PDF and publish the latest version through GitHub Pages.

This approach is particularly well suited to technical books that evolve continuously. Instead of manually rebuilding and uploading a new PDF every time the content changes, the publishing process becomes part of the normal Git workflow.

### Publishing Architecture

The publishing pipeline consists of a small number of components:

- `Learning.md` — the master manuscript
- `Cover.png` — the front cover
- `build-pdf.yaml` — the GitHub Actions workflow
- Pandoc — converts Markdown into the book format
- XeLaTeX — produces the final PDF
- GitHub Pages — hosts the public download page
- Ko-fi — provides optional reader contributions

The workflow file `build-pdf.yaml` is not provided by GitHub. It must be authored by the person setting up the repository and placed at `.github/workflows/build-pdf.yaml`. This file instructs GitHub Actions what to do when a push occurs — which tools to install, how to run Pandoc and XeLaTeX, and how to assemble and deploy the final PDF.

Because the workflow file is written in YAML and can run complex multi-step shell commands, it is well suited to being drafted with the help of a large language model. The author describes what the build should do — font requirements, cover page handling, TOC behaviour, table formatting — and the LLM generates the corresponding YAML. The resulting file is then committed to the repository alongside the manuscript.

The basic flow is:

```text
Learning.md
     ↓
git push
     ↓
GitHub Actions
     ↓
Pandoc + XeLaTeX
     ↓
Learning.pdf
     ↓
GitHub Pages
```

The author therefore spends most of their time working with the Markdown source rather than managing the publishing process itself.

### Markdown as the Book Source

The Markdown document can retain a conventional book hierarchy while remaining easy to read directly on GitHub. YAML metadata at the beginning of the document stores information such as the title and author, while Markdown heading levels represent the structure of the book.

For example:

```text
YAML metadata   Book title and author
#               Part
##              Chapter
###             Section
####            Subsection
```

This allows the same source file to serve two purposes. It remains readable as Markdown on GitHub, while Pandoc interprets the structure when generating the PDF.

A manually maintained table of contents can also remain in the Markdown version for GitHub readers. During the PDF build, that table of contents can be removed automatically and replaced with Pandoc's generated PDF table of contents.

### Automated PDF Generation

The automation is handled by GitHub Actions. The workflow can be configured to run whenever the manuscript, cover, images, or publishing workflow itself changes.

A normal publishing cycle therefore becomes very simple:

- Edit `Learning.md`
- Commit the changes
- Push them to GitHub
- GitHub Actions rebuilds the PDF
- GitHub Pages publishes the updated edition

No separate manual conversion or upload process is required.

It is important to understand where this work actually happens. When a push reaches GitHub, GitHub's own servers — not the author's local machine — take over. A fresh virtual machine running Ubuntu Linux is provisioned automatically in GitHub's cloud infrastructure. That machine installs the required tools (Pandoc, XeLaTeX, fonts), runs the build, generates the PDF, and deploys it to GitHub Pages. Once the push is made, the author's computer is no longer involved. The author does not need to have Pandoc or XeLaTeX installed locally.

The same workflow can also include safeguards needed for larger technical documents, including:

- Unicode and Korean font support
- Monospace fonts for code and text diagrams
- Support for deeply nested Markdown lists
- Automatic PDF table of contents
- Preservation of the intended heading hierarchy
- Handling of images and other book assets

### Setting Up the Workflow File

GitHub Actions looks for workflow definitions in a specific location within the repository: the `.github/workflows/` folder. Any `.yaml` file placed there is treated as a workflow by GitHub.

For this publishing pipeline, the file is named `build-pdf.yaml` and placed at `.github/workflows/build-pdf.yaml`. Once committed and pushed, GitHub detects it automatically — no registration or configuration inside the GitHub interface is required.

The workflow file specifies:

- Which events trigger the build (such as a push to `main` that touches `Learning.md`)
- What environment to use (`ubuntu-latest` — a fresh Linux virtual machine)
- Which tools to install (Pandoc, XeLaTeX, fonts)
- The exact commands to run in sequence
- Where to deploy the output (GitHub Pages)

The file is committed to the repository like any other source file and evolves alongside the manuscript. Changes to the build process — adding a new Lua filter, adjusting fonts, modifying the cover step — are made by editing `build-pdf.yaml` and pushing the update.

### Book Cover

The front cover can be stored as `Cover.png` alongside the Markdown manuscript. It does not need to be inserted into `Learning.md`.

During the automated build, the cover image can be converted into the first page of the final PDF and combined with the generated book body.

The resulting document follows this structure:

```text
Page 1     Front cover
Page 2+    Ebook content
```

The same `Cover.png` can also be copied into the GitHub Pages site and displayed on the ebook's public landing page. This means one image asset serves both the downloadable book and its online presentation.

### Publishing Through GitHub Pages

GitHub Pages provides the public-facing part of the system. After a successful build, GitHub Actions deploys the generated files to the Pages website.

A simple ebook landing page can contain:

- Book title
- Download PDF button
- Front-cover image
- Short description
- Ko-fi support button

The PDF has a stable public URL. When a new edition is generated, the file at that address is replaced by the latest version, so previously shared links continue to work.

### Optional Reader Contributions

The book does not have to be sold in order to accept financial support. A Ko-fi link can be placed on the GitHub Pages website while keeping the PDF freely available.

This creates a simple model:

> Read or download the book for free. If it was useful, optionally support the author.

Ko-fi can be connected to PayPal, making it suitable when the objective is voluntary contribution rather than a conventional checkout process.

### Zero-Upfront-Cost Publishing

One of the main advantages of this approach is that the core publishing infrastructure can operate without an upfront publishing fee.

The main components are:

- GitHub repository
- GitHub Actions
- GitHub Pages
- Pandoc
- XeLaTeX
- Ko-fi

There is no requirement to use an ebook marketplace or traditional publishing platform simply to make the book publicly available.

### Copy Protection

GitHub Pages offers no copy protection — this is by design.

- **No DRM** — the PDF is a plain downloadable file, open to anyone
- **No watermarking** — there is no buyer identity to embed; the book is free
- **No access control** — the public URL is open by design

The only indirect protection is keeping the source repository private — the Markdown manuscript remains hidden while the built PDF is publicly accessible.

This is a deliberate trade-off. The GitHub model assumes that free availability is itself the distribution strategy, with Ko-fi as optional reader support rather than a paywall. Copy protection is not the objective.

### Advantages and Limitations

The model provides considerable control to the author.

**Advantages include:**

- Markdown remains the single source of truth
- Publishing is integrated with Git
- New editions can be generated automatically
- No manual PDF conversion is required
- The author controls the public website
- Readers can obtain the book free of charge
- Optional financial support can be added
- Particularly suitable for frequently updated technical material

There are also trade-offs.

**Limitations include:**

- A public repository exposes its contents and history
- There is no built-in DRM
- There is no per-reader watermarking
- GitHub does not provide Amazon-style marketplace discovery
- Marketing remains the author's responsibility
- GitHub Pages is a distribution mechanism rather than an ebook marketplace

### Security Considerations

Before making a repository public, the complete repository and its history should be reviewed carefully. Public Git repositories should never contain credentials, private keys, API tokens, `.env` files, confidential material, or other sensitive information.

Deleting a secret from the current version of a file is not necessarily sufficient because the value may remain in earlier Git commits.

For a public ebook repository, it is safest to treat everything committed to Git as potentially visible to readers.

### Position Alongside Leanpub and Amazon KDP

GitHub self-publishing does not necessarily replace Leanpub or Amazon KDP. It can instead become the foundation of a broader publishing strategy.

GitHub can provide the continuously updated free edition, while Leanpub can support pay-what-you-want technical publishing and Amazon KDP can provide access to the much larger Kindle marketplace.

The Markdown manuscript can remain the authoritative source regardless of which additional distribution channels are used later.





\newpage

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
- **GitHub Pages** — free continuously updated edition; serves as the public-facing version
  and drives awareness to the paid channels

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
- **GitHub Pages** — push to Git and the PDF rebuilds automatically; readers always
  get the latest version at the same stable URL; no manual republishing required
- Maintain your master manuscript in one place (e.g. private GitHub repo) and export
  to each platform's required format from there



