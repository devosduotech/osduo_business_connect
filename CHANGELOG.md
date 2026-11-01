# Changelog - business_connect

All notable changes to this project will be documented in this file.

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