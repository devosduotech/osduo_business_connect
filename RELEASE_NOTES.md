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