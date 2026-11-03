# OSDuo Business Connect — Marketing Feature Inventory

**Status:** Internal Reference — source of truth for catalog, web page and social content
**Date:** November 2026
**Based on version:** 1.2.6 (shipped) + 1.3.0 (committed SEO scope, see [SEO Plan v1.3.0](SEO_PLAN_v1.3.0.md) and the single working list in [TODO](TODO.md))

> This document is deliberately conservative. Every "Shipped" row below exists in the
> code today. Section 5 lists claims that appear in older marketing material but are
> **not** implemented — do not publish those.

---

## 1. Master feature inventory

### 1.1 Shipped — Identity & public pages

| # | Feature | What it actually does | Marketing angle |
|---|---|---|---|
| 1 | **Business profile page** (`/b/<slug>`) | Logo, cover, description, phone/WhatsApp/email/website, full address, business hours, social links, products, services, enquiry form, theme | "A website for your business in 10 minutes — no developer, no hosting bill" |
| 2 | **Digital card** (`/c/<slug>`) | Personal microsite: photo, designation, bio, tap-to-call/email/WhatsApp, custom links, vCard download, QR | "A business card that can't be lost, and tells you who opened it" |
| 3 | **Product page** (`/b/<slug>/products/<slug>`) | Image, gallery, video, brochure, feature list, category, price modes, enquiry button | "Every product gets its own shareable page" |
| 4 | **Service page** (`/b/<slug>/services/<slug>`) | Image, gallery, brochure, feature list, category, location, enquiry button | "Sell expertise, not just stock" |
| 5 | **Stable public URLs** | Slugs frozen after submit; canonical origin independent of the request host | "Print it once. The QR keeps working forever" |

### 1.2 Shipped — Catalog

| # | Feature | What it actually does |
|---|---|---|
| 6 | **Product catalog** | Unlimited products per business; categories, featured flag, manual sort order, per-product enquiry toggle |
| 7 | **Service catalog** | Same, plus location and brochure attachment |
| 8 | **Category tree** | Hierarchical `Product Category` (e.g. Electronics → Mobiles) |
| 9 | **Price display modes** | `Fixed` (show price + currency), `Contact` (hide figure, invite enquiry), `Hidden` — one selector per product |
| 10 | **Rich product content** | Video URL, PDF brochure, image gallery, feature child-table with icons |

### 1.3 Shipped — Lead capture & CRM

| # | Feature | What it actually does |
|---|---|---|
| 11 | **Contextual enquiry forms** | Captures name, email, phone, company, message + `source` (Card / Business Profile / Product / Service / QR / Campaign / Other), `campaign`, `landing_url`, and the exact card/product/service that triggered it |
| 12 | **Consent capture** | Stores the consent flag **and the exact consent text shown** — audit-friendly for DPDP/GDPR conversations |
| 13 | **Pipeline statuses** | New → Contacted → Nurture → Qualified → Converted, plus Unqualified / Junk / Spam / Closed |
| 14 | **Enquiry Response log** | Timestamped responder/type/message trail per enquiry |
| 15 | **CRM Lead sync** | Auto-creates a Frappe CRM Lead; writes `osduo_campaign`, `osduo_business` and other attribution fields plus the enquiry message (`osduo_notes`); retries failures daily; isolates leads per business; places the fields on the CRM Lead side panel automatically |
| 16 | **Business-scoped permissions** | `BC System Manager` role + `has_permission` / permission query conditions — one tenant can never read another's leads |

### 1.4 Shipped — Sharing & offline-to-online

| # | Feature | What it actually does |
|---|---|---|
| 17 | **QR code generation** | PNG QR of the canonical card URL; downloadable; auto-regenerated when the URL changes; reuses the existing File row (no duplicate attachments) |
| 18 | **QR/NFC-ready URLs** | The hosted subdomain is the permanent anchor; adding a custom domain is additive, so printed QR codes and NFC tags never break |
| 19 | **vCard download** | One tap saves name, org, email, phone, website to the visitor's contacts |
| 20 | **Share sheet** | Copy link, WhatsApp, SMS, email pre-filled with the canonical URL |

### 1.5 Shipped — Analytics

| # | Feature | What it actually does |
|---|---|---|
| 21 | **13 tracked event types** | `profile_view`, `card_view`, `qr_landing`, `product_view`, `service_view`, `phone_click`, `email_click`, `whatsapp_click`, `website_click`, `brochure_download`, `enquiry_submitted`, `shared_link_open`, `contact_exchanged` |
| 22 | **Attribution** | Campaign, landing URL, referrer, session, device type, browser, country, city, share channel (`?ref=`), visitor type |
| 23 | **Dashboard** (`/analytics`) | Totals, events by type, events by day, top 5 products, top 5 services, top cards, visitor mix, recent event feed; optional "exclude owner/member views" filter |
| 24 | **Abuse protection** | Guest event logging rate-limited to 60/min/IP; login required for the dashboard |

### 1.6 Shipped — PWA & delivery

| # | Feature | What it actually does |
|---|---|---|
| 25 | **Installable PWA per site** | Every hostname gets its own manifest, icon set (192/512/maskable), service worker, install prompt, iOS add-to-home guidance |
| 26 | **Offline fallback** | Cached public pages + `/offline` page — a QR tap on bad event Wi-Fi still lands somewhere useful |
| 27 | **Sane cache policy** | Cache-first assets/files, network-first public pages, never cache `/api`, `/private`, `/app`, `/desk`, or `Set-Cookie` responses |
| 28 | **Versioned cache rollover** | Cache names stamped with `__version__`; a release rolls every installed app forward on next visit |

### 1.7 Shipped — Branding, theming, multi-tenancy

| # | Feature | What it actually does |
|---|---|---|
| 29 | **6 page templates** | Modern, Professional, Minimal, Classic, Luxury, Creative — per business and per card |
| 30 | **Theme controls** | Layout mode, 5 colors, button style, 12 font families, 3 font sizes, dark mode |
| 31 | **Bundled brand assets** | Logo/favicon/OG assets served from `/assets/osduo_business_connect/`; never copied into site files |
| 32 | **Auto-applied Website Theme** | `OSDuo Business Connect` theme + stable Color records created on install/migrate; existing custom themes never overwritten |
| 33 | **White-label ready** | App name, logo, favicon, colors resolved per site (Website Settings → System Settings → app defaults) |
| 34 | **Multi-tenant domains** | Hosted subdomains + bring-your-own-domain, both serving the same canonical content |
| 35 | **Publishing lifecycle** | Submit promotes Draft → Published; explicit Suspended/Archived/Unpublished preserved; drafts return 404 |

### 1.8 Shipped — Sharing, contact exchange, visitor insights (v1.2.5)

| # | Feature | What it actually does |
|---|---|---|
| 36 | **Universal share bar** | Copy / WhatsApp / SMS / Email / native share on business, card, product and service pages. Every link is the canonical public URL |
| 37 | **Share attribution** | Share links carry `?ref=share_whatsapp\|share_sms\|share_email\|share_copy\|mycard&by=<slug>`; only whitelisted refs are logged as `shared_link_open` |
| 38 | **Contact Exchange** | Login-only record of *who* a card/business/product/service was shared with (name, phone, email, company, channel, event). Every exchange is also created as an Enquiry via the public enquiry pipeline, so Enquiries + the CRM Lead follow automatically. Deliberately owner-entered — no app can read a recipient out of WhatsApp/SMS/email |
| 39 | **Visitor classification** | Every event is stamped Guest / Owner / Member / Other User / Unknown from the live session, never from client input. Dashboard shows the mix and can exclude internal views |
| 40 | **My Card** | `/my-card` lists the logged-in user's published cards and opens them with `?ref=mycard`; entry points in the desk navbar, analytics header and own public pages |

### 1.9 Committed next — v1.3.0 (SEO & brand attribution)

> **Prioritization (recommended, Nov 2026):** implementation order is Canonical
> & OG metadata → JSON-LD → Sitemap → Product/Service SEO fields → Core Web
> Vitals → footer attribution. Rationale: Business Connect creates multiple
> public URLs per business — a company with several products and services can
> build a meaningful search presence through the individual pages, so sharing
> metadata (owners of that visibility) comes first, then machine-readable
> understanding, then discovery, then catalogue control and performance.

| Priority | # | Feature | What it will do | Business impact |
|---|---|---|---|---|
| 1 | 41 | **Full on-page SEO layer** | Canonical, OG (title/description/url/image/type/site_name/locale), Twitter `summary_large_image`, robots meta, theme-color | Better sharing and indexing |
| 2 | 44 | **Structured data (JSON-LD)** | `Organization` + `WebSite` + `Brand`, `LocalBusiness` (address, hours, socials), `Product` + `Offer`, `Service`, `Person`, `BreadcrumbList` | Search engine understanding |
| 3 | 45 | **`/sitemap-profiles.xml`** | Every published business/product/service/card, `lastmod`, chunked at scale (45k URLs, 10k/chunk index) | Public page discovery |
| 4 | 42/43 | **SEO fields + smart fallbacks on Product & Service** | `seo_title` + `seo_description` (editable after submit, 50–60 / 150–160 char guidance) with unique fallbacks when blank | Better catalogue visibility |
| 5 | 48 | **Core Web Vitals** | Self-hosted woff2 theme fonts (1–3 files instead of 12 families), inline SVG icons instead of Font Awesome CDN, image dimensions + lazy loading + LCP priority, re-cut 1200×630 OG image | Performance |
| 6 | 49 | **OSDuo attribution** | Footer on every page and every tenant domain: "Powered by OSDuo Business Connect — A Product of OSDuo Tech LLP" → `https://www.osduotech.com` | Brand visibility |
| — | 46/47 | **robots.txt defaults + cache invalidation** | Non-destructive robots defaults; instant page-cache clearing when SEO text changes | Supporting items — ship with priorities 1–3 |

### 1.10 Roadmap — not built yet

> The live, tickable list lives in [TODO.md](TODO.md). The summary below is the
> marketing-facing view.

| Item | Status |
|---|---|
| SaaS tiers & quotas (`BC Subscription`), CRM module gating | Designed in [SAAS_IMPLEMENTATION_PLAN.md](SAAS_IMPLEMENTATION_PLAN.md), not coded |
| Web push notifications for installed PWAs | Roadmap |
| Play Store listing via TWA wrapper (`.well-known/assetlinks.json` still 404) | Roadmap |
| Multi-language content | Roadmap |
| AI product descriptions, predictive lead scoring, multi-touch attribution, ROI dashboard | Roadmap |
| Email signature generator, lead scoring, auto-enquiry responses, WhatsApp Business API | **Not built** — currently mis-marked as done in [MARKETING_FEATURES.md](MARKETING_FEATURES.md) |
| Team-member page | Templates exist but **deliberately unrouted** — reserved for a future app |

---

## 2. Catalog copy

**Product name:** OSDuo Business Connect
**Category:** Business website builder + digital business card + lead capture
**One-liner:** *Every business card becomes a lead — a profile, catalog, digital cards and CRM in one box.*

**Tagline options:**
- "Your business, online in minutes. Leads in your CRM automatically."
- "One link. Every product, every person, every enquiry."
- "Stop printing business cards nobody keeps."

### Short description (~45 words)

OSDuo Business Connect gives any small business a public profile, a product and service
catalog, and a digital business card for every team member — all shareable by QR, WhatsApp
or a single link. Enquiries land in a real CRM, with the campaign and page that produced
them attached.

### Long description (~120 words)

Most small businesses are invisible online because a website is expensive and a business
card is disposable. OSDuo Business Connect replaces both. Create a business profile with
your products, services, hours and contact details, then issue a digital card to every
team member. Each card and product gets a stable URL that works in a QR code, an NFC tag,
a WhatsApp message or an email signature. Visitors can call, WhatsApp, download your
contact, or send an enquiry in one tap. Every enquiry arrives in your CRM tagged with the
person, product, campaign and page that generated it. It installs as an app on any phone,
works offline, and needs no developer at any point.

### Feature bullets (listings / marketplaces)

- Business profile page with products, services, hours and social links
- Digital business cards with vCard download and QR sharing
- Product & service catalog with galleries, brochures and videos
- 6 themes, 12 fonts, full color control — no code
- Enquiry forms with consent capture and campaign attribution
- Automatic CRM Lead creation with daily retry
- QR codes that never break, even after you add a custom domain
- Built-in analytics: views, calls, WhatsApp clicks, brochure downloads
- Installable mobile app (PWA) with offline support
- Multi-tenant ready: hosted subdomain or your own domain

**Who it's for:** real estate agents, clinics, consultants, agencies, retailers,
manufacturers, event exhibitors, sales teams, and any SMB that meets customers offline.

**Differentiators (defensible, code-backed):**

1. **Printed assets never break** — canonical URLs are independent of domains; QR/NFC keeps working after a rebrand.
2. **Attribution is built in, not bolted on** — every enquiry carries source, campaign, product and landing page into CRM.
3. **Real CRM, not a form inbox** — leads are proper CRM records with retries and business-level isolation.
4. **Zero-setup branding** — theme, favicon and logo applied automatically on install; existing custom themes preserved.
5. **No app store required** — every site is an installable PWA with its own icon.

---

## 3. Web page copy — `/solutions/business-connect`

> The URL currently returns 404 (verified Nov 2026). Publish the page before any campaign
> drives traffic to it. The marketing site also 301-redirects to `http://` — fix that too.

**Meta title:** `OSDuo Business Connect — Business Profiles, Digital Cards & CRM`
**Meta description:** `Turn every business card into a lead. Business profiles, product catalogs, digital cards, QR sharing, enquiries and CRM — no code required.`

**H1:** Every business card should work while you sleep.
**Sub:** OSDuo Business Connect gives your business a profile, a catalog, a digital card
for every team member, and a CRM that captures the lead — all from one link.

**Primary CTA:** Book a demo · **Secondary CTA:** See a live profile

### Section outline

1. **The problem** — "You hand out 500 cards a year. Maybe 5 get a call. You have no idea which 5, or why."
2. **The fix** — one link that carries your catalog, your team, your contact details, and a QR that never expires.
3. **How it works** — Create profile → Add products/services → Issue cards → Share by QR/link → Leads land in CRM.
4. **For the business** — profile, catalog, hours, socials, themes.
5. **For the individual** — digital card, vCard, tap-to-call/WhatsApp, personal QR.
6. **For the sales manager** — attribution, pipeline, retries, isolation.
7. **Proof points** — 6 themes · 13 tracked events · installable app · offline support · zero third-party font/CDN calls (v1.3.0).
8. **FAQ** — Do I need a website? Can I use my own domain? Do QR codes break if I rebrand? Where do leads go? Is there an app?
9. **Footer CTA** — "Powered by OSDuo Business Connect — A Product of OSDuo Tech LLP"

### Keyword clusters to target

- `digital business card India`, `business card QR code`, `NFC business card alternative`
- `free business profile page`, `product catalog website for small business`
- `lead capture CRM for small business`, `QR code lead generation`
- `digital visiting card for real estate agents / doctors / consultants`

**Internal links:** `/solutions` hub, `/solutions/crm`,
`/solutions/customer-experience-engagement`, `/services/business-technology`.

---

## 4. Social media content

**Hashtags:** `#OSDuo #BusinessConnect #DigitalBusinessCard #QRCode #SmallBusiness #LeadGeneration #CRM #DigitalIndia #SMB #NetworkingTips`

### 10 post ideas

| # | Platform | Hook | Caption core |
|---|---|---|---|
| 1 | LinkedIn | "You handed out 40 cards at the expo. How many can you name?" | Attribution problem → every card is a trackable link → enquiries land in CRM |
| 2 | Instagram | Photo of a paper card in a drawer | "This is where 95% of business cards die." → one link that can't be lost |
| 3 | LinkedIn | "Your QR code shouldn't break when you rebrand." | Stable canonical URLs; custom domain added later, printed codes keep working |
| 4 | Instagram Reel | Screen recording: scan QR → profile → tap WhatsApp | 20-second "card to conversation" demo |
| 5 | LinkedIn carousel | "6 things your business card should do in 2026" | Call, WhatsApp, vCard, catalog, enquiry, analytics |
| 6 | X/Twitter | "A business card is a landing page that fits in a pocket." | Short thread on offline → online attribution |
| 7 | Instagram | Before/after: plain card vs digital card | Visual theme showcase (Luxury vs Minimal) |
| 8 | LinkedIn | "We put a CRM behind a business card." | Enquiry → CRM Lead, with campaign + product attached, auto-retry |
| 9 | Instagram Reel | "POV: you tap your phone on a card and your whole catalog opens" | NFC/QR tap demo |
| 10 | LinkedIn | "Your website isn't the first thing customers see. Your card is." | Profile page as the destination; no developer needed |

### Short-video scripts (15–30 s)

1. **"The drawer"** — Open a drawer full of cards → "None of these work." → tap phone on a card → catalog opens → "This one does."
2. **"The 3 a.m. lead"** — Phone buzzes at 3 a.m. → "Someone scanned your card after the event." → CRM shows product + campaign → "You were asleep. It still worked."
3. **"Rebrand without reprinting"** — Old logo → new logo on profile → "QR codes still work. Nothing reprinted."

### Carousel outline — "The offline-to-online funnel"

1. 500 cards handed out → 2. 5 calls → 3. 0 attribution → 4. One link instead → 5. Every scan tracked → 6. Every enquiry in CRM → 7. CTA.

### LinkedIn article outline

- Why offline marketing still has no analytics
- The three failures of the paper business card
- What "canonical URL" means for a printed QR code
- Attribution: campaign, product, page, person
- What to look for in a digital card tool
- CTA: OSDuo Business Connect

---

## 5. Claims guardrails — do not publish these yet

These appear as delivered in [MARKETING_FEATURES.md](MARKETING_FEATURES.md) but are
**not implemented**:

- ❌ Email signature generator
- ❌ Lead scoring (basic or predictive)
- ❌ Auto-enquiry responses
- ❌ WhatsApp Business API integration (only `wa.me` deep links exist)
- ❌ "OG Image" field (does not exist on any doctype — v1.3.0 uses cover/logo fallbacks)
- ❌ SEO fields on Product/Service (arriving in v1.3.0)
- ❌ Team-member pages (templates exist, but no route — they 404)
- ❌ SaaS tiers, quotas, push notifications, Play Store app, multi-language

Also avoid saying **"NFC business cards"** as a product feature. You support NFC *tags*
because URLs are stable — you do not sell or program NFC hardware. Say:
*"works with any NFC tag or QR code."*

**Action:** rewrite [MARKETING_FEATURES.md](MARKETING_FEATURES.md) §4 and the Phase 2/3
roadmap checkmarks to match this document before anyone uses it as a source of truth.
