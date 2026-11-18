# Release Notes - business_connect (v1.3.2)

**Release Date:** 18 November 2026
**Version:** v1.3.2 (patch)

A Desk usability patch. Signed-in users now find OSDuo support resources directly
in the Desk avatar and header menus, and Frappe's built-in help links no longer
appear.

## What changed (v1.3.2)

### OSDuo support links in Desk
- **User Manual** → `https://www.osduotech.com/business-connect-manual` (new tab)
- **Support Email** → `mailto:connect@osduotech.com` (default mail client)
- **Support Portal** → `https://www.osduotech.com/contact` (new tab)

The same three rows now appear in both the Desk user menu (sidebar/dock avatar)
and the module-header menu. Destinations remain defined once in `OSDUO_BRANDING`
and published to the client as `frappe.boot.osduo_support`; the Desk JS has no
hard-coded URLs.

### Frappe help links removed
- **About**, **System Health** and **Frappe Support** are hidden in the stored
  `Navbar Settings` record, in both `help_dropdown` and `settings_dropdown`.
- The hard-coded **About** and **Frappe Support** rows in the Desktop/Workspace
  avatar menu are removed by a narrowly scoped client patch. Other Frappe
  dropdowns are untouched.

No public pages, canonical URLs, sitemaps, `robots.txt`, or printed QR/NFC
payloads are affected by this release.

## Upgrade

```bash
cd ~/frappe-bench/apps/osduo_business_connect && git pull
bench --site <site> migrate
bench --site <site> clear-cache
bench restart
```

Hard-refresh the browser after restart. `migrate` is required so the hidden help
rows are persisted in `Navbar Settings`. No `bench build` is needed.

---

# Release Notes - business_connect (v1.3.1)

**Release Date:** 17 November 2026
**Version:** v1.3.1 (patch)

A tracking-hygiene patch. Share links now use standard, search-safe **UTM**
parameters instead of the custom `?ref=` token — while every canonical, sitemap
and printed QR/NFC URL stays exactly as clean (and unchanged) as before.

## What changed (v1.3.1)

### Cleaner share links, zero SEO impact
- WhatsApp / SMS / Email / native / copy share buttons, the desk Contact
  Exchange links, and the *My Card* open now carry
  `?utm_source=<channel>&utm_medium=share&by=<slug>`. These are standard Google
  campaign tags — ignored by Search Console and never part of a page's
  canonical, so they can't dilute or dirty an indexed URL.
- The page canonical, `og:url`, sitemap URLs and the **printed QR / NFC** payload
  are unchanged and stay parameter-free, so nothing already in the market breaks.

### Nothing lost in analytics
- Old `?ref=share_*` links you've already shared or printed still attribute —
  the reader accepts both formats and records the **same** campaign labels, so
  your dashboards and historical reports don't shift.
- Per-sharer attribution (`by=`) is kept, so "who shared it" still shows.

### Housekeeping
- Removed a couple of dead branding config knobs that nothing read.

## What is intentionally *not* in this patch
- A fully parameter-free **Copy** link (would need a new analytics event type)
  and a `/q/` QR-scan redirect counter — both change live URL/analytics
  behaviour, so they're deferred rather than shipped in a patch.

## Upgrade

```bash
cd ~/frappe-bench/apps/osduo_business_connect && git pull
bench restart
bench --site <site> clear-website-cache
```

No `migrate`, no `bench build` (no schema or asset change). Newly shared links
use UTM; previously shared/printed links keep working.

---

# Release Notes - business_connect (v1.3.0)

**Release Date:** 17 November 2026
**Version:** v1.3.0 (minor)

The SEO & brand-attribution release. Business Connect pages are now fully
indexable, rich-result ready, faster, and carry the OSDuo attribution — six
phases delivered in one release.

## What's new (v1.3.0)

### Pages show up properly in search and when shared
- Every public page now emits a clean `<title>` (no brand clutter), a unique
  meta description, a canonical URL, the full Open Graph set and a Twitter
  card. Links shared to WhatsApp / LinkedIn / X render a proper preview with
  the page's own image.
- Private pages (login, offline, analytics, my-card) are marked `noindex` so
  they never appear in search results.

### Structured data for Google rich results
- Businesses, products, services and cards now carry schema.org JSON-LD:
  LocalBusiness (address, opening hours, socials), Product + price, Service,
  Person, plus organisation/brand, website and breadcrumb nodes. An unpriced
  product intentionally omits the price node so the Rich Results Test reports
  zero warnings.

### Editable SEO titles & descriptions on products and services
- Products and services (and businesses) now have an **SEO** section with
  *SEO Title* and *SEO Description*. They're the fallback-aware source for the
  page title/description; leave them blank and a sensible value is generated.
- Editable even on submitted records (no amend needed), with live character
  guidance and a non-blocking warning if you go long.

### Faster pages
- Fonts are self-hosted (subset to Latin + the ₹ sign) and the Font Awesome
  CDN was replaced with inline SVG icons — **no third-party render-blocking
  requests** remain. Images declare dimensions/async decoding, lazy-load below
  the fold, and the hero is prioritised. The Open Graph image was re-cut to
  1200×630. The stylesheet was split so each page only loads its own theme.
  Measured mobile Lighthouse Performance improved from 82 to 94 (LCP 4.3 s →
  2.9 s).

### "Powered by OSDuo Business Connect" attribution
- A small, tasteful credit now appears once at the foot of every public page,
  linking to the product page. White-label deployments turn it off with a single
  config flag (`show_vendor_credit`).

### SEO edits show instantly
- Publishing or editing a business, product, service or card now clears the
  affected cached pages automatically, so an SEO change is live on the next
  visit instead of after a delay.

## Upgrade

```bash
cd ~/frappe-bench/apps/osduo_business_connect && git pull
bench --site <site> migrate                 # required: SEO fields on Product/Service
bench --site <site> build --app osduo_business_connect   # fonts + split CSS
bench restart
bench --site <site> clear-cache
bench --site <site> clear-website-cache
```

`migrate` and `clear-website-cache` are both required. After deploy, run
Lighthouse and Google's Rich Results Test on a business, product, service and
card page to confirm.

---

# Release Notes - business_connect (v1.2.93)

**Release Date:** 17 November 2026
**Version:** v1.2.93 (patch)

A small CSS fix that gives every public page an even, symmetric section rhythm
and removes the stray white space that appeared between sections.

## Changes (v1.2.93)

### Even spacing on every public page
- `--bc-section-spacing` was a two-value shorthand applied as a three-value
  `padding`, which left the **bottom padding at 0** and leaked horizontal
  padding into each section. It is now a single vertical length, so sections
  have equal top and bottom breathing room and no side bleed.
- The per-template values were halved so the gap between sections stays exactly
  as it was — only the rhythm is now balanced.
- Covers all six themes (Modern, Professional, Minimal, Classic, Luxury,
  Creative) and both layouts, in light and dark mode, on desktop and mobile.

## Upgrade

```bash
bench --site <site> clear-website-cache
bench restart
```

CSS-only fix — no `migrate` needed.

---

# Release Notes - business_connect (v1.2.92)

**Release Date:** 17 November 2026
**Version:** v1.2.92 (patch)

A housekeeping patch that bakes the desk form layout into the app, so every
site gets the tidied forms on `migrate` without any Customize Form work.

## Changes (v1.2.92)

### Standard desk forms for every site
- The form layout tuned on the UAT site is now part of the app's own DocType
  definitions. Deploying and running `migrate` applies it everywhere.
- **BC Theme** fields are regrouped, the naming rule is corrected, **Import** is
  enabled, and the unused *Activation* section is removed.
- **Showcase Product** keeps its Purchase Link checkbox and button label
  together in a two-column block.
- **Showcase Service** now mirrors the Showcase Product form — media, pricing
  (with location) and status laid out in the same columns.
- Business, Business Member, Digital Card and Product Category were reviewed and
  are unchanged.
- `migrate` removes the old site-level Customize Form records (Custom Fields and
  Property Setters) that would otherwise override the standard layout.

## Upgrade

```bash
bench --site <site> migrate
bench --site <site> clear-cache
```

The layout is applied by `migrate`; existing data is untouched.

---

# Release Notes - business_connect (v1.2.91)

**Release Date:** 17 November 2026
**Version:** v1.2.91 (bug fix)

A fix release for product/service videos: YouTube links now embed correctly
instead of showing "Refused to connect", and Nextcloud / direct video-file
links now play in the page instead of rendering nothing.

## Changes (v1.2.91)

### Product videos now play
- **YouTube links work.** A watch / `youtu.be` / Shorts / Live link you paste is
  now turned into the proper embed, so it no longer shows "Refused to connect".
  Vimeo, Google Drive and Dailymotion share links are handled the same way.
- **Your own Nextcloud (or any direct video file) plays too.** A public-share
  link (`…/s/…`) or a direct `.mp4` / `.webm` / `.ogg` URL now streams in the
  page's built-in player instead of showing nothing.
- **Services can have videos too.** Showcase Service gains the same **Video URL**
  field as Showcase Product, shown on the public service page.
- Unsupported or unsafe links are skipped quietly rather than rendering a broken
  video box.

### Digital card page tidied
- Removed the fixed bottom navigation bar (Home / Products / Enquiry) from the
  digital card page — it was the only page that had one.

## Upgrade

```bash
bench --site <site> migrate
bench --site <site> clear-cache
bench --site <site> clear-website-cache
```

`migrate` refreshes the Video URL field help text; `clear-website-cache` makes
the new player markup show immediately.

---

# Release Notes - business_connect (v1.2.9)

**Release Date:** 11 November 2026
**Version:** v1.2.9

Business Connect now publishes its own XML sitemaps so search engines can find
every public page, and products and services can be priced "from" a starting
amount.

## Changes (v1.2.9)

### Search engines can now find your pages
- The app serves `/sitemap.xml` (a **sitemap index**) listing four sitemaps —
  `/sitemap-businesses.xml`, `/sitemap-products.xml`, `/sitemap-services.xml`
  and `/sitemap-cards.xml`.
- The URLs come **straight from your published records**, so there is no list to
  maintain: publish a business, product, service or card and it appears
  automatically. Drafts, suspended, archived, unpublished and cancelled records
  never appear, and a product/service/card is only listed when its business is
  public.
- Each URL has an accurate `<lastmod>` date. The address is resolved per request
  so every subdomain or custom domain gets its own correct `https://…` URLs.
- Sitemaps are cached for speed and refresh **immediately** when you publish or
  change anything; a full rebuild also runs automatically every third day.
- `robots.txt` is generated on the fly. Your own rules (if you set any) are
  preserved; a sensible default blocks the private routes (`/app`, `/api`,
  `/login`, `/printview`, `/dashboard`, `/analytics`) and the `Sitemap:` line
  always shows the correct address for the domain being crawled.
- Nothing is stored as a file — the sitemaps are always generated from your live
  data. We never submit them to Google; search engines discover them through
  `robots.txt` and crawl on their own schedule.

### "Start From" pricing
- Products and services gain a new price display mode: **Start From**. Set the
  starting price and currency and the page shows e.g. **"From INR 4,999"**.
- Choose it exactly like the existing modes (Hidden / Contact / Fixed) on the
  Showcase Product or Showcase Service form.
- **Services now support pricing too.** Previously a service had no pricing
  fields at all; it now has the same Hidden / Contact / Fixed / Start From
  choices as a product.
- Prices are shown with thousands separators, e.g. **INR 12,000**, matching the
  currency format instead of `INR 12000`.

## Upgrade

```bash
bench --site <site> migrate
bench --site <site> clear-cache
bench --site <site> clear-website-cache
```

`migrate` adds the new pricing fields. `clear-website-cache` is needed so the new
pricing shows immediately instead of after the 30-minute page cache expires.

---

# Release Notes - business_connect (v1.2.8)

**Release Date:** 8 November 2026
**Version:** v1.2.8

Product and service galleries are now clickable and zoomable, show every
image, and appear above the Features section.

## Changes (v1.2.8)

### Click to enlarge — fullscreen gallery lightbox
- Click any gallery thumbnail to open the image fullscreen instead of opening
  a new tab.
- **Previous / next** buttons, image counter and captions.
- **Zoom in / out / reset**, **drag to pan** when zoomed, **pinch-to-zoom** on
  phones, **double-click** to toggle zoom, **swipe** to navigate, and
  **keyboard** shortcuts (`Esc`, `←`, `→`, `+`, `-`, `0`).
- Thumbnails look clickable (zoom cursor + `+` badge) and are keyboard
  accessible.
- No external JavaScript library and no extra build step.

### Full gallery, before Features
- The gallery now shows **all** images, not just the first three. The section
  title shows the count, e.g. **"Gallery · 5 photos"**.
- The gallery sits **after Description / Buy Here and before Features** on
  both product and service detail pages.
- The hero now shows only the single cover image — gallery images no longer
  appear above the description and are shown only in the gallery section.
- The gallery section renders for **all templates**, including Professional.
- The gallery and Buy Here button now line up with the other sections and use
  the standard content width / button size.
- Fixed horizontal scrolling on mobile caused by the full-width purchase
  button overflowing its container.

### Standard desk form layout
- The form layout tuned on the UAT site with **Customize Form** is now shipped
  in the app itself, so every site gets the same layout on `migrate` — no
  manual Customize Form work.
- **Business**: Industry sits next to Slug, and the About Us / contact /
  branding / social / hours sections are rearranged. The description field is
  now labelled **About Us**.
- **Business Member**, **Digital Card**, **Product Category**, **Showcase
  Product** and **Showcase Service** forms have their fields regrouped into
  logical columns.
- **Showcase Product / Service**: the separate Enquiry and Purchase Link
  sections are merged into one **Enquiry and Purchase Link** section.
- `naming_series` is hidden on all seven forms, and import is enabled for
  Business, Business Member, Digital Card, Product Category, Showcase Product
  and Showcase Service.
- Digital Card hides **Sort Order** on the form — it still exists and drives
  backend card ordering, it is just set programmatically.
- Migration automatically removes the old site-level Customize Form records
  (Custom Fields / Property Setters) that would otherwise override the standard
  layout.

## Upgrade

```bash
bench --site <site> migrate
bench --site <site> clear-cache
bench --site <site> build
```

The desk form layout is applied by `migrate`; existing data is untouched.

---

# Release Notes - business_connect (v1.2.7)

**Release Date:** 6 November 2026
**Version:** v1.2.7

Adds a "Buy Here" purchase link on products and services and makes the
Featured flag and sort order actually influence the catalog.

## Changes (v1.2.7)

### Buy Here on Product and Service pages
- While creating a product or service, tick **Show Buy Here Button** under
  "Buy Here (Purchase Link)".
- If your whole business sells in one place, set the **Buying Portal Link**
  once on the Business record (custom location per business requirement).
- If an item sells somewhere else (its own Amazon listing, booking site…),
  override with the item's own **Shopping Portal Link**.
- The public page shows a button labelled **Buy Here** by default — put your
  own text in **Button Label** ("Book Now", "Order Here"…). It opens the
  shopping portal in a new tab.
- Taps are recorded as **buy clicks** in the analytics dashboard.
- Safety: every external link on public pages opens in a new tab with
  `rel="noopener"`, purchase URLs pass URL sanitization, and every rendered
  label/text is HTML-escaped.

### Featured and ordering actually working now
- Ticking **Featured** on a product or service now lifts it to the top of
  every listing (business page, card page and the public API) —
  ordering is `Featured first, then sort order`.
- A **★ Featured** chip shows on the tiles in the Business and Card page
  listings, plus on the detail page.
- Without Featured ticked, the previous sort-order arrangement continues to
  apply (lower numbers first).

## Upgrade

```bash
bench --site <site> migrate
bench --site <site> clear-cache
bench --site <site> build
```

No data changes — existing products/services keep their current behavior
until Buy Here or Featured is ticked.

---

# Release Notes - business_connect (v1.2.6)

**Release Date:** 3 November 2026
**Version:** v1.2.6

Polish release for v1.2.5: open public pages from the desk without copy-paste,
a mobile-friendly Share & Save Contact that matches Send a Message, and a
reliable My Card icon.

## Changes (v1.2.6)

### Open public pages straight from the desk
- Business, Digital Card, Showcase Product and Showcase Service forms have an
  **Open** button next to the read-only **Public URL** field. It opens the
  generated page in a new tab — no copying the link and pasting it into the
  browser.

### Share & Save Contact matches Send a Message
- The form now uses the same layout, fonts and sizes as the public "Send a
  Message" form, with the full-width **Save & Share** button styled
  identically. The old boxed look is gone.
- On phones the rows stack into one column, inputs render at 16px so iOS no
  longer auto-zooms on focus, and every control has a comfortable tap target.

### My Card icon fixed on mobile
- The inconsistent emoji icon on the My Card chip is replaced with a crisp
  inline SVG id-card graphic — the same icon in the desk navbar and on the
  analytics header — so it renders correctly on every mobile browser.
- The navbar insertion now covers asynchronously built mobile menus too.

## Upgrade

```bash
bench --site <site> migrate
bench --site <site> clear-cache
bench --site <site> build
```

(`bench build` refreshes the bundled CSS/JS used by the changes above.)

---

# Release Notes - business_connect (v1.2.5)

**Release Date:** 3 November 2026
**Version:** v1.2.5

Makes every public page easy to share, tells you **which channel** the visit came
from, records **who** you shared your card with, and separates real visitors from
your own team in analytics.

---

## Changes (v1.2.5)

### Share everything, from one place
- Business, card, product and service pages now use the same share bar: Copy,
  WhatsApp, SMS, Email and the native share sheet.
- Links always point at the canonical public URL, so sharing from a custom or
  staging host never changes the URL printed on a QR code or NFC tag.

### Know which channel worked
- Share links carry a small `ref=share_*` token. When the recipient opens the
  link, the app logs a `shared_link_open` event with that channel.
- Tokens are whitelisted server-side; arbitrary query strings are ignored.

### Contact Exchange — the consent-respecting way to capture a lead
- Logged-in owners/members can record **who** they shared a card, business,
  product or service with: name, company, phone, email, channel (WhatsApp / SMS /
  Email / In-person), event/meeting and notes.
- Every exchange is saved **as an Enquiry** — the same record and pipeline as the
  public "Send an Enquiry" form — so it appears under **Enquiries** and the CRM
  Lead is created automatically through the standard sync.
- Why owner-entered? No browser or operating system exposes the recipient of a
  WhatsApp, SMS or email message. Rather than pretend, the app captures what the
  owner actually knows at the exhibition or meeting.
- Desk access: **Contact Exchanges** under the Engagement section of the
  Business Connect workspace.

### Real visitors, not your own clicks
- Each event is stamped **Guest / Owner / Member / Other User / Unknown** based
  on the live session (never from client input).
- The dashboard shows the visitor mix and has an **Exclude owner/member views**
  toggle, so team testing no longer inflates the numbers.
- Older events without a classification are counted as Unknown.

### My Card
- `/my-card` lists your published cards and opens them with `?ref=mycard`, so
  your own visits are attributed too.
- Reachable from the desk navbar, the analytics header and a chip on your own
  public pages.

### CRM keeps the context
- The Enquiry's message arrives on the CRM Lead as a read-only **OSDuo Message**
  field — a website-form message or, for shared contacts, "Contact exchanged via
  WhatsApp · Event · Notes…".
- The OSDuo attribution fields appear as an **OSDuo Attribution** section on the
  CRM Lead side panel automatically — no per-site manual layout work.
- Leads already synced before this release get the message backfilled by
  `bench migrate`.

### Notes for operators
- New DocType **Contact Exchange** is created by migration; exchange rows now
  link to the Enquiry they produce (the redundant `crm_lead` field was removed).
- `shared_link_open` and `contact_exchanged` are internal event types; the
  public `/log_event` endpoint rejects them.
- No data migration is required. `visitor_type` starts as Unknown for historical
  rows.

## Upgrade

```bash
bench --site <site> migrate
bench --site <site> clear-cache
```

---

# Release Notes - business_connect (v1.2.4)

**Release Date:** 1 November 2026
**Version:** v1.2.4

Keeps generated URLs **and** QR images consistent after a canonical domain
change (for example switching to `https://` behind a TLS-terminating proxy).

---

## Changes (v1.2.4)

### QR images follow the canonical domain
- `bench migrate` re-backfills `public_url` when `host_name` changes. It now
  also regenerates the QR image for every card whose URL actually changed, so
  the printed code matches the new origin without re-saving each card.
- QR regeneration reuses the existing `/files/qr_<slug>.png` File row, so
  repeated regeneration no longer creates duplicate attachments.

### Documentation
- Explained why a site behind Nginx Proxy Manager / Caddy / Cloudflare still
  generates `http://` URLs: Frappe only infers `https` from `ssl_certificate` /
  `wildcard` in `site_config.json`, so a TLS-terminating proxy must set
  `"host_name": "https://your.domain"`.
- Merged the duplicate “Public page 404” troubleshooting rows.

## Upgrade

```bash
bench --site <site> migrate
bench --site <site> clear-cache
```

---

# Release Notes - business_connect (v1.2.3)

**Release Date:** 1 November 2026
**Version:** v1.2.3

Fixes an inconsistency where a **submitted** record could still have
`Status = Draft` and therefore be invisible on every public page
(`404 Business not found`).

---

## Changes (v1.2.3)

### Submitting now publishes
- **Business**, **Digital Card**, **Showcase Product** and **Showcase Service**
  all default `Status` to `Draft`. Submitting previously left that value
  untouched, creating a submitted-but-hidden record.
- Submit now promotes `Status` from `Draft` to `Published` automatically.
- An explicit `Suspended` / `Archived` / `Unpublished` status is preserved, so
  submitting a hidden record remains possible.

### Fixing existing records
- Already-submitted records can change **Status** directly — the field is
  editable after submit, so no cancel/amend is required:
  ```python
  doc = frappe.get_doc("Business", "<record>")
  doc.status = "Published"
  doc.save()
  frappe.db.commit()
  ```
- Run `bench --site <site> clear-cache` afterwards.

**Upgrade notes:** run `bench --site <site> migrate && bench --site <site> clear-cache`.

---

# Release Notes - business_connect (v1.2.2)

**Release Date:** 1 November 2026
**Version:** v1.2.2

Every newly provisioned site now arrives **fully branded by default**: the
bundled `OSDuo Business Connect` Website Theme is created and selected, and the
favicon, app logo and app name are applied automatically during install and
migrate. No manual Desk setup and no copying brand files into the site's
`public/files` directory.

---

## Changes (v1.2.2)

### Default Website Theme
- New **Website Theme** `OSDuo Business Connect` ships with the app: brand
  primary/secondary/accent colours, text and surface colours, rounded buttons,
  branded footer and card shadows.
- Applied automatically by `bench migrate` / install. New sites get the theme,
  favicon, app logo and app name with zero manual steps.
- **Non-destructive:** an existing theme with the same name is reused untouched,
  so per-site SCSS customisations survive. A site that has chosen a different
  theme keeps it; only an empty or `Standard` Website Settings → Theme is
  replaced.
- Theme colours reuse stable `Color` records, created once and shared across
  re-installs.
- No external font import — the theme stays fast and works offline. Desk and
  login styling continue to come from the app's own CSS.

**Upgrade notes:** run `bench --site <site> migrate && bench --site <site> clear-cache`.
The break-glass command is
`bench --site <site> execute osduo_business_connect.branding.apply_branding_settings`.
`node` must be available on the bench (Frappe compiles Website Theme SCSS with
it); if compilation fails, the theme is logged and the site keeps its current
theme instead of failing the migration.

---

# Release Notes - business_connect (v1.2.1)

**Release Date:** 1 November 2026  
**Version:** v1.2.1

This patch makes branding **fully self-contained in the app**. Login, the desk
app screen and PWA icons now read brand assets from
`/assets/osduo_business_connect/images/` instead of requiring a manual copy of
`logo_mark_512x512.png` (and the login panel image) into every site's
`public/files` directory.

---

## Changes (v1.2.1)

### Bundled branding
- Login, desk/app-screen and PWA icons use brand assets shipped in the app.
- `bench migrate` / install applies bundled defaults to **Website Settings**
  (App Logo, Favicon, App Name) and **System Settings** (App Name).
- Only empty/generic (`Frappe`) or unmistakably hand-copied brand files
  (`/files/logo*.png`, `/files/logo_mark_512x512.png`, …) are replaced;
  genuine per-site custom logos and names are left untouched.
- Login panel background is bundled and optimised (`login-panel.jpg`, 134 KB
  vs the previous 2.1 MB per-site upload).
- Optimised login/desk derivatives: `logo-mark-128.png`, `logo-mark-512.png`,
  `logo-512.png`, `logo-dark-512.png`, `favicon-256.png`.
- PWA icon endpoint now resolves both `/assets/...` and `/files/...` sources.

**Upgrade notes:** run `bench --site <site> migrate && bench --site <site> clear-cache`.
The service worker cache is stamped with `__version__`, so installed PWAs roll
to the new assets automatically on the next visit. No logo files need to be
uploaded or copied — the break-glass command is
`bench --site <site> execute osduo_business_connect.branding.apply_branding_settings`.

---

# Release Notes - business_connect (v1.2.0)

**Release Date:** 31 October 2026  
**Version:** v1.2.0

This release adds an installable **Progressive Web App** layer (per-customer
branding, offline support for card/business pages) and hardens the platform
for SaaS go-live: permission lifecycle, slug/amend safety, input
sanitization, and canonical NFC/QR URLs.

---

## New Features (v1.2.0)

### Progressive Web App (PWA)
- Every customer site becomes an installable mobile app — hosted subdomains
  (karthic.connect.osduotech.com) and bring-your-own domains work identically
  with zero per-customer setup.
- Dynamic per-site web app manifest (`/manifest.json`) — name, icon and theme
  follow the site's branding (Website Settings → System Settings → defaults).
- Root-scope service worker (`/sw.js`): instant repeat loads of card/business
  pages, offline viewing of previously visited public pages, branded
  `/offline` fallback. API and desk traffic are never cached.
- Auto-generated PWA icons (192/512/maskable) with PNG quality; iOS home
  screen guidance and Android install prompt on the login app entry.
- Deploys roll forward automatically: caches are stamped with the app version.

### Canonical URLs for NFC/QR
- `public_url` on Business and Digital Card is now auto-derived from the
  canonical base (`host_name` in site_config) — never typed and never taken
  from the request domain, so printed cards stay valid across domain changes.
- QR images regenerate automatically when the encoded URL changes.
- `bench migrate` backfills existing records.

## Hardening & Fixes (v1.2.0)
- **Permissions:** submit for Owner/Manager/Marketing, cancel/amend for Owner;
  BC System Manager treated as System Manager across all app permission checks;
  owner memberships and default theme auto-created on Business insert.
- **Slug lifecycle:** slugs are read-only after submission but preserved
  through cancel → amend; cancelled records no longer reserve slugs (NFC
  continuity restored).
- **Security:** stored rich text is sanitized on save; all public URL hrefs
  go through `safe_url`; cancelled documents are excluded from every public
  lookup and API.
- **Login page:** fixed oversized field icons overlapping the email/password
  inputs (custom Website Theme replacing Frappe's icon CSS).
- **Business profiles:** cover image now renders as a full-bleed banner
  behind all six hero variants, each visually distinct (Modern, Minimal,
  Classic, Luxury, Creative, Professional).
- Removed dead code and unused CSS blocks.

**Upgrade notes:** run `bench migrate` (required — DocType JSON changed) and
set `host_name` in each production site's `site_config.json` before printing
NFC cards or QR codes.

---

# Release Notes - business_connect (v1.1.0)

**Release Date:** 30 October 2026  
**Version:** v1.1.0

This release focuses on a comprehensive design overhaul of the public-facing pages, introducing a unified design system and professional templates for a superior user experience.

---

## New Features (v1.1.0)

### Theme Redesign & Unified UI
- Full redesign of the Professional, Modern, Minimal, and Classic templates across Digital Cards, Business Profiles, Product, and Service pages.
- Implementation of a coordinated design system with a focused layout (Centered/Wide/Split/Editorial).
- New high-contrast color schemes (Violet, Indigo, Blue, Green, Yellow, Orange, Red, Gold) with automatic contrast correction for accessibility.
- Unified header architecture across all pages for consistent branding (Logo + Company Name).

### Analytics & CRM Enhancements
- Integration of guest-safe client-side event tracking using `navigator.sendBeacon`.
- New analytics events: `card_view`, `product_view`, `service_view`, `phone_click`, `email_click`, `whatsapp_click`, `website_click`, `brochure_download`, and `enquiry_submitted`.
- Enhanced CRM context tracking (UTM campaigns and landing URLs) passed directly from the public pages to the lead generation pipeline.

### UI/UX Improvements
- Optimized Digital Card shell (420px) for mobile-first viewing.
- Improved image handling with `object-fit: cover` to ensure profile and product images are displayed correctly without distortion.
- Added read-only Public URLs in the admin panel for easy sharing of Business, Product, and Service pages.

---

# Release Notes - business_connect (v1.0.2)

**Release Date:** 28 October 2026  
**Version:** v1.0.2

This release introduces comprehensive features to streamline business management, including dynamic digital card generation, CRM integration with Frappe, real-time analytics dashboard, and a complete product showcase platform.

---

## New Features (v1.0.2)

### Digital Card Generation
- 6 professional templates: Simple, Business Professional, Corporate Blue, Minimalist Black, Modern Red, Luxury Gold
- QR code-enabled sharing for contactless business cards
- NFC tag support for premium card experiences  
- VCF file download capability for seamless contact importing

### Frappe CRM Integration
- Automatic lead management on enquiries received through the platform
- Seamless data synchronization between business connect and your Frappe ERP/CRM instance
- Real-time pipeline tracking of customer interactions

### Analytics Dashboard
- Track website visits in real time
- Monitor digital card scans and engagement metrics
- Identify top-performing cards and products
- View enquiry pipeline progress with visual analytics

---

## Product Showcase & Catalog

### Business Profile Management
- Hero section with customizable images and/or video background
- About section for business storytelling
- Products showcase with image gallery  
- Detailed product pages with pricing, descriptions, brochures (PDF download)
- Service listing pages highlighting features and locations

---

## Technical Improvements

- Enhanced lead generation engine powered by Frappe CRM
- Improved performance optimization across all modules  
- Better integration between product catalog and service listings
- Real-time data synchronization using webhooks

---

## Security Updates

All user-facing code has been reviewed against security best practices, with enhanced input validation for the lead generation pipeline.

---

## Known Issues & Future Roadmap

- Some advanced Frappe API features may require additional configuration  
- Scheduled release for v1.1.0 includes planned improvements to analytics depth and mobile responsiveness  

---

**For support:** [Contact Support](/support) | **Development updates:** [GitHub Repository](https://github.com/opencode-team/business_connect) | **Documentation:** [Full API Reference](/docs/api-reference.md)