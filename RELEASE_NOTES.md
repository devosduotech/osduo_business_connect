# Release Notes - business_connect (v1.4.11)

**Status:** Tagged as `v1.4.11` and pushed to `develop`; UAT and production
rollout still pending. Not deployed to production.
**Release:** v1.4.11.

## Changes (v1.4.11)

### Added

- **Share & Connect** on card, business, product and service pages: an
  authenticated content chooser, server-derived URLs, lazy server-side QR for
  all four content types, and fixed neutral share messages.
- Contact capture records the selected content type and preserves the sender
  identity; the CRM Lead receives five additional attribution fields.
- Request-ID idempotency prevents duplicate saves from double taps and retries.

### Changed / strengthened

- Public pages now render a cache-safe shell only. Personalized sharing data is
  loaded from a non-cacheable authenticated endpoint, so cached HTML never
  contains another user's form, sender details or CSRF token.
- The manifest read returns a safe empty response for guests and stale document
  IDs instead of a 404, accepts a Business ID or slug, and no longer skips the
  Business target because it has no child document ID. The normal public share
  bar keeps working when Share & Connect is unavailable.
- Exchange and Enquiry use one commit boundary with a savepoint; failed Enquiry
  creation is recorded, retried safely, and never created for an unchecked box.
- CRM Lead status (including `converted = 1`) reconciles to both Enquiry and
  Contact Exchange through immediate hooks and a bounded hourly job.
- Migration adds 13 fields across three existing DocTypes and a simple,
  idempotent, non-destructive attribution patch. Historical CRM Leads are not
  modified.

### Upgrade (when approved)

`bench migrate` is required on every site. Clear website cache after deploy;
the shared asset/service-worker revision is `2026-11-24-share-connect`.
`bench build` is only needed when assets are copied files, not symlinks.

---

# Release Notes - business_connect (v1.4.10)

**Release Date:** 24 November 2026
**Version:** v1.4.10 (patch)

Phone layout fixes for the private Team portal page.

## What changed (v1.4.10)

### Fixed

- `/portal/team` now adapts to phones. The five-column Members table lives in
  a horizontal scroll region with a 560px minimum width, so names and emails are
  readable instead of being squeezed into a 360px viewport. KPI cards stack,
  card padding tightens, and the invite form uses 16px inputs/selects to stop
  iOS Safari auto-zooming on focus.
- The shared private-portal chrome also reduces sidebar, top-nav and content
  spacing below 600px.

### Upgrade

From v1.4.9: pull, clear cache and run `bench migrate` once per site. The shared
asset revision is now `2026-11-24-team-mobile`, so clients and the service
worker fetch the new templates/CSS on their next navigation. `bench build` is
not required when `sites/assets/<app>` links to the app's `public/` folder.

```bash
cd ~/connect-bench/apps/osduo_business_connect
git fetch upstream --tags && git pull --ff-only upstream main
cd ~/connect-bench
bench --site <site> clear-cache
bench --site <site> clear-website-cache
bench --site <site> migrate
bench restart
```

## Verification

- 613 offline tests passed, including a new Team-phone layout regression test.
- `python3 -m compileall` passed.
- CSS split/verify: 653 original rules = 653 emitted rules.
- No schema, fixture, API, plan-gate or permission changes.

---

# Release Notes - business_connect (v1.4.9)

**Release Date:** 24 November 2026
**Version:** v1.4.9 (patch)

Touch devices no longer leave a sidebar row looking permanently selected.

## What changed (v1.4.9)

### Fixed

- On Android/Chrome, `:hover` stays on the last tapped row. The BC Desk sidebar
  used the same white chip for hover and active state, so after tapping
  `Card Event` it kept looking selected even while Frappe correctly marked
  `Home` as `active-sidebar`. Hover styling is now scoped to
  `@media (hover: hover)`; keyboard focus and the real active row are unchanged
  on every device.

### Upgrade

From v1.4.8: pull, clear cache and run `bench migrate` once per site. The shared
asset revision is now `2026-11-24-touch-hover`, so clients and the service
worker fetch the new CSS on their next navigation. `bench build` is not
required when `sites/assets/<app>` links to the app's `public/` folder.

```bash
cd ~/connect-bench/apps/osduo_business_connect
git fetch upstream --tags && git pull --ff-only upstream main
cd ~/connect-bench
bench --site <site> clear-cache
bench --site <site> clear-website-cache
bench --site <site> migrate
bench restart
```

## Verification

- 612 offline tests passed, including a pointer-only hover regression test.
- `python3 -m compileall` passed.
- CSS split/verify: 653 original rules = 653 emitted rules.
- No schema, fixture, API, plan-gate or permission changes.

---

# Release Notes - business_connect (v1.4.8)

**Release Date:** 24 November 2026
**Version:** v1.4.8 (patch)

Mobile BC workspace sidebar and PWA cache fixes.

## What changed (v1.4.8)

### Fixed

- On a phone, the collapsed BC workspace sidebar is now invisible again. Frappe
  v16 turns the Desk sidebar into an overlay drawer and hides the collapsed
  state with `background: transparent` plus `opacity: 0` on its contents. The
  BC dark rail rule was `!important` and won that cascade, leaving a blank slate
  panel over the page. A scoped `@media (max-width: 767px)` rule restores the
  transparent, non-interactive collapsed drawer; the dark rail still appears on
  desktop and when the drawer is opened.
- The service worker no longer tries to cache HTTP 206 Partial Content replies,
  which the Cache API rejects with `Partial response (status code 206) is
  unsupported`. Only complete 200 responses are stored, and cache writes are
  caught so a quota or storage error cannot become an uncaught promise error.

### Upgrade

From v1.4.7: pull, clear cache and run `bench migrate` once per site. The shared
asset revision is now `2026-11-24-mobile-drawer-sw`, so clients and the service
worker fetch the new CSS/JS on their next navigation. `bench build` is not
required when `sites/assets/<app>` links to the app's `public/` folder.

```bash
cd ~/connect-bench/apps/osduo_business_connect
git fetch upstream --tags && git pull --ff-only upstream main
cd ~/connect-bench
bench --site <site> clear-cache
bench --site <site> clear-website-cache
bench --site <site> migrate
bench restart
```

## Verification

- 611 offline tests passed, including new mobile-drawer and 206-response
  regression tests.
- `python3 -m compileall` passed.
- CSS split/verify: 653 original rules = 653 emitted rules.
- No schema, fixture, API, plan-gate or permission changes.

---

# Release Notes - business_connect (v1.4.7)

**Release Date:** 24 November 2026
**Version:** v1.4.7 (patch)

Light colour schemes now render readable dark text on public page headers.

## What changed (v1.4.7)

### Fixed

- Follow-up to v1.4.6: with a light scheme (Yellow, Gold or a light custom
  primary), the hero and nav bars used to keep white text, producing
  white-on-light text. `.bc-prof-band`, `.bc-prof-nav`, `.bc-prof-nav-link` and
  the Classic tagline now use `--bc-header-text`, which follows the scheme's
  `on_primary` value (dark for light schemes, white for dark ones).
- The profile nav bar base colour is now `--bc-primary` instead of a fixed
  slate. Template-specific nav overrides still apply.

### Upgrade

From v1.4.6: pull, clear cache and run `bench migrate` once per site. The shared
asset revision is now `2026-11-24-header-contrast`, so clients and the service
worker fetch the new CSS on their next navigation. `bench build` is not required
when `sites/assets/<app>` links to the app's `public/` folder.

```bash
cd ~/connect-bench/apps/osduo_business_connect
git fetch upstream --tags && git pull --ff-only upstream main
cd ~/connect-bench
bench --site <site> clear-cache
bench --site <site> migrate
bench restart
```

## Verification

- 609 offline tests passed (including new header-text contrast regression tests).
- `python3 -m compileall` passed.
- CSS split/verify: 653 original rules = 653 emitted rules.
- No schema, fixture, API, plan-gate or permission changes.

---

# Release Notes - business_connect (v1.4.6)

**Release Date:** 24 November 2026
**Version:** v1.4.6 (patch)

The public Business and Digital Card page headers now follow the selected colour
scheme instead of a template-hardcoded colour.

## What changed (v1.4.6)

### Fixed

- Removed hardcoded header colours from all six template hero variants. The
  header now consumes `--bc-header-bg`, which is derived from the chosen scheme
  and colour pickers: primary→accent gradient for Modern and Creative, vertical
  gradient for Classic, primary for Professional, theme surface for Minimal and
  a darkened primary tint for Luxury. Nav bars follow the same variables.
- Luxury Digital Card hero uses the same derived header colour.

### Upgrade

From v1.4.5: pull, clear cache and run `bench migrate` once per site. The shared
asset revision is now `2026-11-24-scheme-header`, so clients and the service
worker fetch the new CSS on their next navigation. `bench build` is not required
when `sites/assets/<app>` links to the app's `public/` folder.

```bash
cd ~/connect-bench/apps/osduo_business_connect
git fetch upstream --tags && git pull --ff-only upstream main
cd ~/connect-bench
bench --site <site> clear-cache
bench --site <site> migrate
bench restart
```

---

# Release Notes - business_connect (v1.4.5)

**Release Date:** 24 November 2026
**Version:** v1.4.5 (patch)

Two white-label polish fixes found during final test-site review: readable
sidebar selection on the customer BC workspace, and theme pickers that actually
drive the rendered colours for preset schemes.

## What changed (v1.4.5)

### Fixed

- Selected and hovered BC workspace sidebar rows now use dark portal text on a
  white chip. The previous white-on-white combination made the current item
  unreadable. The nested v16 `.sidebar-item-label` is covered too.
- `BC Theme` `background_color` and `font_color` are honoured for all preset
  schemes (Blue, Green, ...), not just `Custom`. Blank pickers still fall back
  to the template default; `dark_mode` still overrides both pickers.

### Upgrade

From v1.4.4: pull, clear cache and run `bench migrate` once per site. The shared
asset revision is now `2026-11-24-sidebar-contrast`, so existing clients and the
service worker pick up the new CSS/JS on their next navigation. `bench build` is
not required.

```bash
cd ~/connect-bench/apps/osduo_business_connect
git fetch upstream --tags && git pull --ff-only upstream main
cd ~/connect-bench
bench --site <site> clear-cache
bench --site <site> migrate
bench restart
```

---

# Release Notes - business_connect (v1.4.4)

**Release Date:** 24 November 2026
**Version:** v1.4.4 (patch)

The curated Business Connect Desk sidebar is now a standard part of the app, so
every new customer site receives the same navigation without developer-mode
exports or manual setup.

## What changed (v1.4.4)

### Added

- `osduo_business_connect/business/sidebar/business_connect/business_connect.json`
  is a standard `Sidebar` fixture for the `Business` module. Frappe v16 imports
  `<app>/<module>/sidebar/<name>/<name>.json` during install/migrate.
- Offline tests assert the fixture is standard, belongs to this app and module,
  keeps the 11-item order, and contains no `/app`, `/desk`, `/desk/build` or
  User/Role/Invitation links.

### Upgrade

From v1.4.3: pull, clear cache and run `bench migrate` once per site to import the
standard Sidebar document. No bundled asset changes; `bench build` is not needed.

```bash
cd ~/connect-bench/apps/osduo_business_connect
git fetch upstream --tags && git pull --ff-only upstream main
cd ~/connect-bench
bench --site <site> clear-cache
bench --site <site> migrate
bench restart
```

Existing sites with a locally created sidebar are left as-is; the standard
fixture is only inserted when that Sidebar does not exist yet.

---

# Release Notes - business_connect (v1.4.3)

**Release Date:** 23 November 2026
**Version:** v1.4.3 (patch)

A production-readiness cleanup: closes an unauthenticated quote endpoint, aligns
the provider role with its documented permissions, and removes code that had no
runtime entry point. Also corrects stale documentation left from earlier
releases.

## What changed (v1.4.3)

### Fixed

- `get_addon_quote` now rejects Guest/unauthenticated callers and checks
  `Add-on Order` read permission where Frappe exposes it. Previously an
  anonymous caller on an accessible site could read plan code, add-on prices and
  domain expiry.
- `BC Subscription Manager` is recognised as the subscription provider for
  Add-on Order status transitions and invoice attachment. The DocType's
  `read_only_depends_on` conditions now allow that role as well as Administrator.

### Removed

- Dead modules with no route, hook, whitelist or caller: `utils/security.py`,
  `enquiry/enquiry_webhook.py`, `enquiry/submit_enquiry_page.py`,
  `showcase/public_api.py`, the nested `crm_integration/crm_integration` package,
  the stale UAT harness, and the unused `tests/helpers.py`.
- Unreferenced `roles/*.json` files — Frappe v16 does not import them and roles
  are created by `install.py::create_default_roles()`.
- Legacy alias helpers and unused constants across `business`, `card`,
  `services`, `crm_integration`, `analytics`, `subscription` and `seo`.

### Documentation

- Removed the stale "sidebar colour pending" known issue (fixed in v1.4.0) from
  all published docs and the GitHub release body.
- Corrected the CRM branch, `--hostname` flag, role list, add-on ordering,
  trial semantics and dead links; removed broken mockup embeds and planned
  roadmap entries.
- Narrowed `MANIFEST.in` and tightened `scripts/check_md_links.py`.

### Upgrade

From v1.4.2: pull, clear cache, restart, then run `bench migrate` once to sync
the Add-on Order read-only conditions. No bundled asset change and no
`bench build` required.

```bash
cd ~/connect-bench/apps/osduo_business_connect
git fetch upstream --tags && git pull --ff-only upstream main
cd ~/connect-bench
bench --site <site> clear-cache
bench --site <site> migrate
bench restart
```

---

# Release Notes - business_connect (v1.4.2)

**Release Date:** 22 November 2026
**Version:** v1.4.2 (patch)

A migration fix for sites upgrading to the v1.4.0 subscription schema. The
first `bench migrate` on an already-installed site could skip the new
`Subscription` module's DocTypes because Frappe v16 cached the app-to-module map
before the Module Def was registered. This release makes that first migrate
import the DocTypes correctly.

## What changed (v1.4.2)

### Fixed

- Added `before_migrate` hook
  `osduo_business_connect.install.refresh_module_map_for_migrate`, which clears
  the cached `app_modules` map and calls `frappe.setup_module_map()` before
  DocTypes are synced.
- The hook runs after Frappe registers new Module Defs and before `sync_all`, so
  modules added by a later release are visible in the same migrate run.
- Added a regression test asserting the hook and its module-map refresh calls.

### Symptoms this resolves

- `ImportError: Module import failed for SaaS Plan ... No module named
  'frappe.core.doctype.saas_plan'` during `after_migrate`.
- `ImportError: Module import failed for Subscription ... No module named
  'frappe.core.doctype.subscription'` from the provisioning CLI.
- Subscription DocType rows missing from `tabDocType` after the first migrate.

## Upgrade

No schema, API or bundled asset changes. From v1.4.0 or v1.4.1:

```bash
cd ~/frappe-bench/apps/osduo_business_connect
git fetch upstream --tags && git pull --ff-only upstream main

cd ~/frappe-bench
bench --site <site> clear-cache
bench --site <site> clear-website-cache
bench restart
```

`bench build` is not required. Sites still on a pre-v1.4.0 version must run
`bench --site <site> migrate` once to create the subscription schema.

If a migrate already failed with the errors above, re-run it after clearing the
cache; the failed run left the subscription DocType rows uncreated:

```bash
bench --site <site> clear-cache
bench --site <site> migrate
bench --site <site> clear-cache
bench restart
```

---

# Release Notes - business_connect (v1.4.1)

**Release Date:** 21 November 2026
**Version:** v1.4.1 (patch)

A documentation release. It records the supported plan-provisioning procedure
for new and existing sites and tracks the remaining workspace sidebar text-colour
work as pending.

## What changed (v1.4.1)

### Documentation

- Added a provisioning quick-reference for new and existing sites to
  `README.md`.
- Expanded `docs/INSTALLATION_GUIDE.md` with a decision table, `--dry-run`
  examples, auto-seeding behaviour on upgrade, and `--force` plan changes.
- Clarified in `docs/USER_MANUAL.md` that plans are provider-managed and where
  customers can view their active plan, seats and usage.

### Known issue (historical)

- This entry was recorded before final verification. The selected-item colour
  had already been fixed in v1.4.0 (`8f418ae`) and is covered by
  `test_desk_sidebar_selected_text_matches_portal`; no work remains.

## Upgrade

This is a docs/version-only release. When upgrading from v1.4.0:

```bash
cd ~/frappe-bench/apps/osduo_business_connect
git pull

cd ~/frappe-bench
bench --site <site> clear-cache
bench --site <site> clear-website-cache
bench restart
```

`migrate` and `bench build` are not required for v1.4.1. If upgrading from a
version older than v1.4.0, follow the v1.4.0 upgrade steps below first.

---

# Release Notes - business_connect (v1.4.0)

**Release Date:** 21 November 2026
**Version:** v1.4.0 (minor)

A subscription and customer-workspace release. It introduces plan entitlements
and add-on ordering, moves customer onboarding to Frappe's User Invitation flow,
brings one sticky sidebar to every private portal page, and makes the Business
Desk workspace look like `/portal/team` without changing its links.

## What changed (v1.4.0)

### Plans, quotas and add-ons

- Plan entitlements are now frozen into snapshots and enforced at the HTTP
  boundary as well as in DocType hooks. Seat and Business quotas apply at
  creation time.
- Add-on orders, custom domain mappings, plan-specific Add-on Masters and a
  read-only My Subscription page are available to eligible plans.
- Restriction messages include the required plan and the canonical OSDuo
  pricing link.

### Team invitations and private portal

- Customer invitations go through Frappe `User Invitation` only. The selectable
  roles are `BC Business Member`, `BC Business Manager`, `BC CRM User` and
  `BC Marketing Manager`. Administrator, System Manager, BC System Manager,
  BC Subscription Manager and per-business Owner are never offered.
- Seats are reserved when the invitation is sent and checked again when it is
  accepted.
- All logged-in private pages share the same sticky portal sidebar. Public
  Business, Member, Product and Service pages are unchanged.
- Business logins land on `/desk/business-connect`; Professional logins land on
  `/my-card`. Generic Desk, native User/Role/User Invitation administration and
  provider routes remain blocked for customers.

### Branded BC workspace and login

- `/desk/business-connect`, its aliases and child routes use the portal palette:
  slate rail, brand-blue accents, white brand text and a semibold white selected
  item. The workspace's own links and sidebar items are not altered.
- `/login` is overridden inside the app with the branded split-screen layout.
  Guests visiting `/` are forwarded to `/login`.
- Desk and web assets now include a shared revision query string, and the
  service-worker cache revision is rotated with it. This makes Firefox refresh
  stale CSS/JS even where service workers are unavailable.
- Refreshing a workspace shortcut such as `/desk/business-connect/business` no
  longer returns `Not Permitted`; only BC-owned links are accepted under that
  shell, while `.../user`, `.../build` and unknown children remain blocked.

## Upgrade

```bash
cd ~/frappe-bench/apps/osduo_business_connect
git pull

cd ~/frappe-bench
bench build --app osduo_business_connect
bench --site <site> migrate
bench --site <site> clear-cache
bench --site <site> clear-website-cache
bench restart
```

Hard-refresh the browser once after the restart so the revisioned assets load.
`migrate` is required for the new and changed DocTypes; `bench build` is required
for the new CSS/JS. No canonical URLs, sitemaps, `robots.txt` or printed QR/NFC
payloads change in this release.

---

# Release Notes - business_connect (v1.3.4)

**Release Date:** 18 November 2026
**Version:** v1.3.4 (patch)

An analytics patch. Every shared link, QR scan, NFC tap and enquiry is now
counted once, and the Event / meeting you enter in Share & Save Contact becomes
the Campaign for the whole sharing funnel.

## What changed (v1.3.4)

### One event per action
- A card open no longer writes two `card_view` rows. The page's client beacon is
  the single writer, so visits still register on cached pages and offline PWA
  opens.
- Enquiries are recorded once by `create_enquiry()` for every submission path;
  the duplicate client beacon is removed.
- Clicking a product or service tile on a card no longer beacons a view that the
  destination page also records.
- **Link Visits** in the analytics dashboard now counts page views only.
  The `shared_link_open` attribution row for UTM links is kept, but is reported
  separately under *Events by Type* rather than as an extra visit.

### Event / meeting as Campaign
- The Event / meeting entered in Share & Save Contact is stored as Campaign on
  the exchange event and its Enquiry, and added as `utm_campaign` to the
  generated share link. Recipient views and enquiries for that share are
  grouped under the same campaign. Without an event name, the share channel
  remains the Campaign as before.

## Upgrade

```bash
cd ~/frappe-bench/apps/osduo_business_connect && git pull
bench --site <site> clear-cache
bench restart
```

Hard-refresh the browser after restart so the updated card page loads. No
`migrate` and no `bench build` are needed.

No canonical URLs, sitemaps, `robots.txt`, or printed QR/NFC payloads change in
this release.

---

# Release Notes - business_connect (v1.3.3)

**Release Date:** 18 November 2026
**Version:** v1.3.3 (patch)

A theme and stability patch. Business saves are reliable again, font-size presets
actually resize the public pages, the hero logo behaves consistently across all
six themes, and the colour you pick in BC Theme is what you see — including on
transparent logos.

## What changed (v1.3.3)

### Stability
- Saving a Business no longer fails with `TypeError: 'Business' object is not
  subscriptable` when the cache hook refreshes; it reads the document name via
  `.get("name")`.

### Appearance
- **Font-size presets work** on every themed page: the chosen size is applied to
  the root element so all `rem`-based theme styles scale together.
- **Hero logo sizing is consistent** across Modern, Professional, Minimal,
  Classic, Luxury and Creative; the shared rules now load for every theme, and
  Professional keeps its smaller mobile heading.
- **Your selected colour wins** — the Primary/Secondary/Accent pickers on BC
  Theme now drive the rendered page even with a preset scheme selected. Picking
  a preset updates the pickers; fine-tuning a picker takes effect immediately.
- **Transparent logos stay transparent** — the hero logo tile has no background
  of its own, so a transparent PNG shows no blue/gold backdrop. When no logo is
  selected, the brand-coloured letter tile is shown instead.

## Upgrade

```bash
cd ~/frappe-bench/apps/osduo_business_connect && git pull
bench --site <site> migrate
bench --site <site> clear-cache
bench restart
```

`migrate` is required once: it backfills preset colours into existing themes
whose pickers were never set, without touching colours a user has chosen.
Hard-refresh the browser after restart. No `bench build` is needed.

No canonical URLs, sitemaps, `robots.txt`, or printed QR/NFC payloads change in
this release.

---

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

**Support:** info@osduotech.com | **Repository:** https://github.com/devosduotech/osduo_business_connect | **Guides:** [Installation Guide](docs/INSTALLATION_GUIDE.md) · [User Manual](docs/USER_MANUAL.md)