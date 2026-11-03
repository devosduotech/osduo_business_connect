# Changelog - business_connect

All notable changes to this project will be documented in this file.

## v1.2.6 - Unreleased

### Polish (v1.2.6)

- **Open button on desk forms beside Public URL** — Business, Digital Card,
  Showcase Product and Showcase Service forms now render an **Open** button
  next to the read-only `Public URL` field, letting staff open the public page
  (new tab, `noopener`) without copying the link manually.
- **Share & Save Contact now looks like Send a Message** — the form mirrors the
  enquiry form's format/fonts/sizes (`bc-card-form`, full-width `Save & Share`
  button), drops the old boxed card look, and uses 16px inputs on phones so
  iOS stops auto-zooming on focus; rows collapse to a single column on small
  screens.
- **My Card icon fixed** — the inconsistent emoji (~document) Chip on public
  pages and text-only links elsewhere are replaced with one inline SVG id-card
  icon (chip, desk navbar, analytics header). The desk navbar insertion now
  also covers asynchronously built mobile menus (extra retry) and keeps
  `nav-link` styling.

---

## v1.2.5 - 3 November 2026

### Features (v1.2.5)

#### Universal share bar
- One reusable share bar on **business, card, product and service** pages with
  Copy, WhatsApp, SMS, Email and the native share sheet (where supported).
- Every share link uses the **canonical public URL** from `utils/urls.py` — never
  the host of the current request — so printed QR/NFC material keeps working
  behind custom domains.
- Card sharing previously built its URL from `request.host`; it now uses the
  canonical card URL too.

#### Share attribution
- Share links carry `?ref=share_whatsapp|share_sms|share_email|share_copy|mycard`
  plus `&by=<slug>`. Only whitelisted refs are accepted server-side.
- `by=` now names the **person who shared** — the sharer's own card slug on
  business, product and service pages — instead of repeating the page slug.
- Opening an attributed link logs a server-side `shared_link_open` event, so the
  dashboard can answer "which channel brought this visit?".
- `shared_link_open` and `contact_exchanged` are **not** accepted from the public
  event endpoint — they can only be produced by the app.

#### Canonical URL scheme
- `utils/urls.py` now reads `host_name` directly: an explicit scheme is
  honoured, a scheme-less public host defaults to `https://`, and Frappe's
  developer-mode port (`:8000`) is no longer appended to a real domain.
- Diagnostics: `bench --site <site> execute
  osduo_business_connect.utils.urls.describe_canonical_url` shows the base the
  app will print into links and QR codes, and where it came from.

#### Contact Exchange (login only)
- New **Contact Exchange** DocType under Card: records the recipient of a shared
  card/business/product/service (name, company, phone, email, channel, event,
  notes). **Every exchange is also created as an Enquiry** through the same
  service the public "Send an Enquiry" form uses, so it lands in the Enquiries
  list and reaches CRM through the standard sync.
- New **Share & Save Contact** form on card/business/product/service pages,
  shown only to the business owner/member who is logged in.
- Recipient details are deliberately owner-entered. No browser or OS exposes the
  recipient of a WhatsApp/SMS/email message, so the owner records it at the
  exhibition, show or meeting instead.
- **Every exchange is also created as an Enquiry** through the same service the
  public "Send an Enquiry" form uses, so card contacts captured at an event land
  in the Enquiries list and reach CRM through the standard sync (the direct
  CRM-Lead path was removed; the Enquiry owns the Lead link).
- Owner/Manager/Member create, Owner delete, company-scoped query conditions.

#### CRM Lead context
- The Enquiry's message reaches the CRM Lead as a new read-only **OSDuo
  Message** field (`osduo_notes`, Small Text, after `OSDuo Landing URL`); a
  patch backfills it on Leads already synced.
- The osduo_* fields are placed on the **CRM Lead side panel automatically**
  (an "OSDuo Attribution" section in `CRM Lead-Side Panel`), so no per-site
  manual layout customization is needed after install.

#### Visitor classification
- Every engagement event now stores `visitor_type` (Guest / Owner / Member /
  Other User / Unknown) and a hidden `visitor_user`, classified from the live
  session in the web request before the background job.
- Analytics dashboard adds a visitor mix and a Visitor column in recent
  activity, plus an **Exclude owner/member views** filter.
- Legacy rows (`visitor_type` NULL) count as Unknown instead of disappearing.

#### My Card
- New `/my-card` page lists the logged-in user's published cards and opens them
  with `?ref=mycard&by=<slug>` for attribution.
- Entry points: desk navbar, analytics header and a chip on the user's own
  public pages.

### Upgrade
`bench --site <site> migrate && bench --site <site> clear-cache`.

---

## v1.2.4 - 1 November 2026

### Fixes (v1.2.4)

- **`bench migrate` now regenerates QR images when the canonical domain
  changes.** `public_url` is rewritten with `db.set_value`, which skips
  controllers, so the QR image kept encoding the old origin until the card was
  re-saved by hand. Migration now refreshes QR images for exactly the cards whose
  `public_url` changed.
- **QR regeneration no longer duplicates `File` attachments.** Regenerating a
  QR reuses the existing `/files/qr_<slug>.png` File row instead of inserting a
  new one on every save.
- Documented why a TLS-terminating proxy (Nginx Proxy Manager, Caddy,
  Cloudflare) still produces `http://` URLs without an explicit
  `"host_name": "https://…"`, and merged the duplicate “Public page 404”
  troubleshooting rows.

Upgrade: `bench --site <site> migrate && bench --site <site> clear-cache`.

---

## v1.2.3 - 1 November 2026

### Fixes (v1.2.3)

- **Submitted-but-Draft records were invisible on public pages.** Business,
  Digital Card, Showcase Product and Showcase Service default `Status` to
  `Draft`, and submitting did not change it. A submitted record could therefore
  return `404 Business not found` even though it existed.
- Submitting now automatically promotes `Status` from `Draft` to `Published`
  for all four doctypes. An explicit `Suspended` / `Archived` / `Unpublished`
  choice is preserved, so it is still possible to submit without publishing.
- Existing submitted records can be fixed by setting **Status = Published** and
  saving — `status` is editable after submit, so no amendment is required.
- Documented the publish behaviour and added a troubleshooting entry for
  “Business not found”.

Upgrade: `bench --site <site> migrate && bench --site <site> clear-cache`.

---

## v1.2.2 - 1 November 2026

### Fixes & Improvements (v1.2.2)

#### Default Website Theme on every new site
- Added the bundled **Website Theme** `OSDuo Business Connect` (brand colours,
  typography-friendly buttons, footer and card styling) and made it the default
  during install/migrate.
- A new site now gets the theme, favicon, app logo and app name with **zero
  manual setup**.
- Idempotent and non-destructive: an existing `OSDuo Business Connect` theme is
  reused as-is (per-site SCSS customisations survive), and a site that has
  deliberately chosen another theme keeps it. Only an empty or `Standard`
  Website Settings → Theme is replaced.
- Theme colour fields reuse stable `Color` records (`OSDuo Primary Blue`,
  `OSDuo Text`, `OSDuo Dark Blue`, `OSDuo Light`, `OSDuo Background`).
- No external font import: the theme stays fast and works offline.

Upgrade: `bench --site <site> migrate && bench --site <site> clear-cache`.

---

## v1.2.1 - 1 November 2026

### Fixes & Improvements (v1.2.1)

#### Branding bundled in the app
- Login, desk/app-screen and PWA icons now use brand assets shipped inside the
  app (`/assets/osduo_business_connect/images/`). No more copying
  `logo_mark_512x512.png` or the login panel image into each site's
  `public/files` directory.
- `bench migrate` / install automatically applies bundled defaults to
  Website Settings (App Logo, Favicon, App Name) and System Settings (App Name).
  Empty, generic (`Frappe`) and legacy hand-copied brand files are replaced;
  genuine per-site custom logos and names are preserved.
- The login split-screen background is now bundled (`login-panel.jpg`, 134 KB
  instead of a 2.1 MB per-site upload).
- Login/desk assets use optimised derivatives (`logo-mark-128/512.png`,
  `logo-512.png`, `favicon-256.png`) for faster first loads.
- PWA icon endpoint resolves both `/assets/...` and `/files/...` sources.

Upgrade: `bench --site <site> migrate && bench --site <site> clear-cache`
(applies branding and rolls the PWA cache to v1.2.1).

---

## v1.2.0 - 31 October 2026

### New Features (v1.2.0)

#### Progressive Web App
- Installable per-customer PWA: dynamic `/manifest.json`, root-scope `/sw.js`,
  branded `/offline` fallback, auto-generated 192/512/maskable icons.
- Offline support for previously visited public pages (cards, business
  profiles); API and desk traffic are never cached.
- Android install prompt and iOS "Add to Home Screen" guidance on login.

#### Canonical Public URLs
- Business / Digital Card `public_url` auto-derived from `host_name`
  (site_config) — stable for printed QR/NFC across custom-domain changes.
- QR images regenerate automatically when the encoded URL changes; existing
  records backfilled on `bench migrate`.

### Hardening (v1.2.0)
- Submit/cancel/amend permission lifecycle for Business, Card, Product,
  Service; BC System Manager parity with System Manager app-wide.
- Slug read-only after submission; preserved through cancel → amend.
- Rich-text sanitization on save; `safe_url` on all public hrefs; cancelled
  docs excluded from every public lookup.
- Fixed oversized login field icons; cover-image banner + distinct business
  hero variants; removed dead code and unused CSS.

---

## v1.0.2 - 28 October 2026

### New Features (v1.0.2)

#### Frappe CRM Integration
- Automatic lead management on enquiries received through the platform
- Seamless data synchronization between business connect and your Frappe ERP/CRM instance
- Real-time pipeline tracking of customer interactions

#### Digital Card Generation
- 6 professional templates: Simple, Business Professional, Corporate Blue, Minimalist Black, Modern Red, Luxury Gold
- QR code-enabled sharing for contactless business cards
- NFC tag support for premium card experiences  
- VCF file download capability for seamless contact importing

#### Analytics Dashboard
- Track website visits in real time
- Monitor digital card scans and engagement metrics
- Identify top-performing cards and products
- View enquiry pipeline progress with visual analytics

---

## v1.0.1 - 26 October 2026

### New Features (v1.0.1)

#### Product Showcase & Catalog Management
- Hero section with customizable images and/or video background
- About section for business storytelling
- Products showcase with image gallery  
- Detailed product pages with pricing, descriptions, brochures (PDF download)
- Service listing pages highlighting features and locations

---

## v1.0.0 - 24 October 2026

### Initial Release (v1.0.0)

#### Core Features
- **Dynamic Card Generation**: 6 professional templates for business card creation
- **Lead Generation Engine**: Automatic lead capture via Frappe CRM integration
- **Analytics Dashboard**: Real-time engagement metrics and website traffic tracking
- **Digital Card Sharing**: QR code-enabled sharing with NFC tag support
- **VCF Download**: Seamless contact importing to address books

#### Business Profile Management
- Hero section with customizable images and/or video background  
- About section for business storytelling
- Products showcase with image gallery
- Detailed product pages with pricing, descriptions, brochures (PDF download)
- Service listing pages highlighting features and locations

---

## v0.0 - 24 October 2026

### Initial Development (v0.0)

#### Core Features
- **Dynamic Card Generation**: Professional templates for business card creation
- **Lead Generation Engine**: Automatic lead capture via Frappe CRM integration
- **Analytics Dashboard**: Real-time engagement metrics and website traffic tracking  
- **Digital Card Sharing**: QR code-enabled sharing with NFC tag support
- **VCF Download**: Seamless contact importing to address books

---

## Development Roadmap

### Next Releases
- **v1.0.3** (Planned): Mobile responsiveness improvements, advanced analytics depth
- **v1.1.0** (Planned): New feature set TBD - watch for updates in [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)

---

## Support & Resources

- **[Full API Reference]**(/docs/api-reference.md) - Complete RESTful API documentation  
- **[Development Roadmap]**(DEVELOPMENT_PLAN.md) - Future feature plans and timelines
- **[Architecture Decisions]**(ARCHITECTURE_DECISIONS.md) - Design choices for the project