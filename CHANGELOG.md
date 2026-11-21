# Changelog - business_connect

All notable changes to this project will be documented in this file.

## v1.4.1 - 21 November 2026

### Documentation

- Documented the supported way to add or change a site's subscription plan for
  both new and existing sites, including the `--dry-run` preview and the
  `--force` requirement when a Subscription already exists.
- Added an operator quick-reference to the README and expanded the User Manual's
  Subscription section with the provider-managed plan workflow.

### Known issue

- The Business Connect workspace sidebar/menu item text colour has not passed
  final visual verification. The theme CSS and assets load, but visual parity
  with `/portal/team` for the selected item remains pending.

### Notes

- Documentation and version-only release: no schema, API or bundled asset
  changes. Clear the website cache and restart; `migrate` and `bench build` are
  not required when upgrading from v1.4.0.

## v1.4.0 - 21 November 2026

### Subscriptions and customer access

- Added plan entitlements, provisioning, frozen plan snapshots, request-level
  gates, seat/business quotas, add-on ordering, custom domains and a read-only
  My Subscription page.
- Customer team invitations now use Frappe `User Invitation` only. Customers can
  invite `BC Business Member`, `BC Business Manager`, `BC CRM User` and
  `BC Marketing Manager`; provider roles and per-business Owner stay excluded.
  Seats are reserved at invite and rechecked on acceptance.
- Logged-in private portal pages share one sticky sidebar while the public
  Business/Member/Product/Service pages are unchanged. Business customers land
  on `/desk/business-connect`; Professional customers remain portal-only and
  land on `/my-card`.

### Branded workspace

- `/desk/business-connect`, its accepted aliases and child routes now use the
  portal palette (dark slate rail, white brand text, semibold selected item).
  Original workspace links/sidebar items are untouched.
- `/login` is overridden in-app with the branded split-screen layout, and guest
  `/` forwards to `/login`.
- Desk and web assets carry a revision query string so browsers without service
  workers (for example Firefox over plain HTTP) fetch fresh CSS/JS after a
  deploy. The service-worker cache revision is rotated with the same value.
- Hard-refreshing a BC workspace link such as `/desk/business-connect/business`
  no longer returns `Not Permitted`; the gate now recognises the workspace's own
  shipped DocType shortcuts. Native User/Role/User Invitation and unknown child
  routes stay blocked.

### Notes

- Upgrade requires `bench migrate` (new/changed DocTypes), `bench build --app
  osduo_business_connect` (new assets), cache clears and a restart. Hard-refresh
  browsers once after the restart.
- All upgrade/pricing links remain on the canonical OSDuo pricing URL.

## v1.3.4 - 18 November 2026

### Analytics fixes

- **One view per visit** — a card open was written twice: once from the page
  controller and once from the card page's client beacon. QR scans and NFC taps
  (which carry no tracking params) therefore logged two identical `card_view`
  rows. The client beacon is now the single writer, so views still count when
  Frappe serves cached HTML or the PWA opens offline. The separate
  `shared_link_open` attribution row for UTM links is unchanged.
- **Enquiries are recorded once** — the card page beaconed `enquiry_submitted`
  on top of the server event from `create_enquiry()`. The client call is gone and
  the public beacon endpoint no longer accepts that event type.
- **Product/service tiles no longer double count** — clicking a tile on a card
  beaconed a view that the destination page controller also recorded. The
  destination view is now the only one.
- **Link Visits is accurate** — the dashboard headline now counts page views
  only; attribution and funnel events for the same visit no longer inflate it.

### Campaign tracking

- The **Event / meeting** field in the logged-in Share & Save Contact form is now
  used as the Campaign on the `contact_exchanged` event (falling back to the
  share channel when empty), on the linked Enquiry, and as `utm_campaign` on the
  generated WhatsApp/SMS/Email share link. Recipient card/product/service views
  and the resulting enquiry inherit the same campaign.

### Notes

- Canonical URLs, sitemaps, `robots.txt`, and printed QR/NFC payloads are
  unchanged. No `migrate` or `bench build` is needed.

## v1.3.3 - 18 November 2026

### Bug fixes

- **Business save no longer errors on cache refresh** — the cache hook indexed a
  Frappe `Document` like a dict (`doc["name"]`), which raised
  `TypeError: 'Business' object is not subscriptable`. It now uses `doc.get("name")`.
- **Font-size presets now take effect** — presets were applied to a wrapper
  variable that theme CSS (which uses `rem`) never read. The selected size is
  published by every themed page controller and applied to `<html>` via an
  escaped inline `font-size` rule on the base template.
- **Shared hero logo sizing works across all six themes** — the CSS splitter
  stranded the shared `.bc-prof-logo` rules in the Professional-only stylesheet.
  Shared `bc-prof-` rules now stay in the base CSS; Professional's mobile heading
  override is preserved with a more specific selector.
- **Selected Theme Colour is honoured** — `get_theme_data()` previously ignored
  the stored Colour pickers for preset schemes. They are now authoritative;
  choosing a preset syncs its palette into the pickers on create or scheme
  change, and `migrate` backfills legacy themes whose pickers still hold factory
  defaults (never overwriting a user's own colours).
- **Selected logos sit on no background** — the hero logo tile no longer paints
  a background, so transparent logos show no blue (or other colour) backdrop.
  The brand colour is applied only to the fallback letter shown when no logo is
  selected. Classic, Luxury and Minimal no longer hard-code a different tile
  colour.

### Notes

- `bench migrate` is required once to backfill legacy theme colours; no
  `bench build` is needed.
- Canonical URLs, sitemaps, `robots.txt`, and printed QR/NFC payloads are
  unchanged by this release.

## v1.3.2 - 18 November 2026

### Desk support links (end users)

- Added **User Manual**, **Support Email** and **Support Portal** to both Desk
  menus: the sidebar/dock avatar menu and the module-header menu. The rows are
  built from `OSDUO_BRANDING` via `frappe.boot.osduo_support`, with `mailto:` for
  email and `_blank` for the two web links; Frappe adds
  `rel="noopener noreferrer"` automatically.
- Removed Frappe's built-in **About**, **System Health** and **Frappe Support**
  help rows. They are hidden (not deleted) in the stored `Navbar Settings`
  record, so `sync_standard_items()` cannot re-add visible rows on migrate.
  Both `help_dropdown` and `settings_dropdown` are swept, including upgraded
  sites where a help row had drifted into `settings_dropdown`.
- Patched the separate Desktop/Workspace avatar menu that Frappe 16.54 hard-codes
  in `desktop.js`. `frappe.ui.Dropdown.prototype.open` is wrapped only when the
  trigger is `.desktop-avatar`; the hard-coded help rows are filtered and the
  OSDuo rows are inserted above **Logout**. Other dropdowns are unaffected, and
  rebuilding from `opts.options` on every open keeps the patch idempotent.
- Both client patches are installed independently with load-order polling.
- Tests: `TestDeskSupportMenu` and `TestFrappeHelpRowSweeper` cover the boot
  payload, href/target behaviour, both Navbar Settings tables, and the scoped
  Desktop/Workspace patch (including Node syntax/runtime verification).

### Upgrade

```bash
cd ~/frappe-bench/apps/osduo_business_connect && git pull
bench --site <site> migrate
bench --site <site> clear-cache
bench restart
```

`migrate` persists the hidden help rows; hard-refresh Desk afterwards. No
`bench build` and no public URL/QR/NFC change.

---

## v1.3.1 - 17 November 2026

### Share & tracking URL hygiene (Decision 12) — no URL format change to anything printed

Retired the custom `?ref=` share token in favour of standard UTM, while keeping
every indexable and printed URL byte-for-byte clean and every already-circulating
link attributable.

- **Share buttons now emit standard UTM** — `?utm_source=<channel>&utm_medium=share&by=<slug>`
  on the public share bar (WhatsApp/SMS/Email/native/copy) and the desk Contact
  Exchange links, replacing `?ref=share_<channel>`. `utm_*` is ignored by Google
  Search Console and never appears on a page's `rel=canonical` / `og:url`, so
  sharing stays clean without touching canonicals.
- **Canonical / sitemap / printed QR & NFC URLs are unchanged** — they never
  carried these params; `qr_service` still encodes the clean `public_url`
  (Decision 11 preserved, so existing printed media keeps working).
- **Backward-compatible inbound reader** — `utils.share.get_share_ref()` now
  accepts the standard `utm_source` **and** the legacy `?ref=share_*` tokens
  already in circulation on live/printed media, mapping both to the **same**
  stored campaign value, so analytics history stays comparable and no baseline
  shifts. A non-share `utm_medium` (e.g. `cpc`) is not mistaken for a share open.
- **`by=` retained** — per-sharer ("which teammate shared this") attribution is
  preserved rather than dropped.
- **Copy link keeps `utm_source=copy`** rather than going fully bare, so copy
  attribution isn't silently lost; a fully parameterless Copy (with an outbound
  `sendBeacon`) needs a new `event_type` (schema) and is deferred, along with the
  optional `/q/` scan-redirect counter.
- **Removed dead branding knobs** — the unused `title_brand_suffix` key and the
  `bc_vendor_name`/`bc_product_name` context injection (no template read them).

Tests: new `test_share_utm.py` (pure `build_share_url` + a stubbed-`form_dict`
reader verifying the UTM↔legacy round trip, stable campaign tokens, `by=`
capping, non-share media ignored); `test_v125_features.py` updated to the new
contract. Docs (README, USER_MANUAL, MARKETING_FEATURES/INVENTORY, SEO_PLAN
Decision 12) refreshed. No schema change — no `migrate`.

### Upgrade
```bash
cd ~/frappe-bench/apps/osduo_business_connect && git pull
bench restart                       # Python: utils/share.py + contact_exchange_api
bench --site <site> clear-website-cache
```
No `migrate` and no `bench build` needed (no schema or asset change). Legacy
`?ref=` links keep working; newly shared links use standard `utm_*`.

---

## v1.3.0 - 17 November 2026

### SEO & brand attribution (the v1.3.0 release)

The full SEO plan (kept with the project's internal docs, not published in this
repository) ships in one release. Sitemaps,
the dynamic `robots.txt` and the "Start From" price mode already shipped in
v1.2.9; everything below is new.

#### Canonical & Open Graph metadata on every public page (Phase A)
- New `utils/seo.py` — `build_seo()` produces the title, description,
  canonical, robots, the complete OG set (title/description/url/image/
  `image:alt`/type/site_name/locale `en_IN`) and the Twitter
  `summary_large_image` card. `clean_text()` cuts descriptions to a 155-char
  search snippet on a word boundary; `absolute_url()` always resolves against
  the canonical, `host_name`-first origin (never the request host, so printed
  QR/NFC links stay stable).
- `templates/bc_base.html` `<head>` rewritten: page-content-only `<title>` (no
  brand suffix), canonical, robots, the full OG + Twitter blocks,
  `application-name`, `generator`, `theme-color`, and a JSON-LD `<script>` per
  block. All values HTML-escaped (Frappe Jinja autoescape is off). The dead
  `og_title`/`og_description`/`og_image` guards are gone.
- Per-page precedence (SEO_PLAN §C) wired into the Business / Product / Service
  / Card controllers; the card share/landing URL now uses the canonical base.
- `noindex,nofollow` on the login screen (site root), `/offline`, `/analytics`
  and `/my-card`. Relocated the dead `www/analytics.py` controller to
  `templates/pages/analytics.py`, which also fixes its never-firing login gate.

#### Structured data / rich results (Phase B)
- New `seo/jsonld.py`: `Organization` + `Brand` (sitewide), `WebSite` (business
  pages only), `LocalBusiness` (address, opening hours, social `sameAs`),
  `Product` + `Offer`, `Service`, `Person` wrapped in `ProfilePage`, and
  `BreadcrumbList`. Prices are coerced to JSON-safe floats; every URL uses the
  canonical origin; serialisation escapes `<` so no `</script>` breakout.
- `Product` + `Offer` are emitted **only when a price is displayed** (Fixed /
  Start From, priced, currency set); an unpriced product emits a `WebPage` +
  `BreadcrumbList` instead, so Rich Results reports no "missing offers" warning.

#### Product & Service SEO fields (Phase C)
- `Showcase Product` and `Showcase Service` gain an **SEO** section with
  `seo_title` + `seo_description`; `Business`'s SEO fields move out of
  "Branding & Theme" into their own SEO section. All six fields are
  `allow_on_submit` — editable after submit without an amend — with
  50-60 / 150-160 character guidance.
- `utils/seo.normalize_seo_fields()` strips markup from the stored SEO fields
  and shows a non-blocking length warning past 70 / 160 characters; called from
  the Business / Product / Service controllers. The page controllers already
  prefer the explicit fields, so they feed `<title>`, OG and JSON-LD directly.
- **Schema change** — requires `bench migrate`.

#### Core Web Vitals (Phase D)
- **Self-hosted fonts**: the 12-family Google Fonts request is replaced with
  38 `woff2` faces in `public/fonts/` + `public/css/fonts.css`
  (`font-display: swap`), subset to **latin + latin-ext + `U+20B9` (₹)** by
  `scripts/gen_fonts.py`. `scripts/build_icons.py` regenerates `utils/icons.py`
  from the upstream SVGs (re-run after editing).
- **Font Awesome CDN removed**: `utils/icons.py` renders brand icons as inline
  SVG (Simple Icons, CC0) and the three generic glyphs from Lucide (ISC);
  templates use `{{ icon_class | bc_icon(...) }}` with a generic fallback.
- **Images**: every `<img>` gets `decoding="async"`; above-the-fold heroes
  `fetchpriority="high"`; below-the-fold / modal images `loading="lazy"`.
  `og-image.png` re-cut 1731×909 → **1200×630, ~279 KB**, and `og:image:width`
  `/height` are now emitted for the default image.
- The page hero is `<link rel=preload as=image>`d; a `<main>` landmark added.

#### Sitewide vendor attribution footer (Phase E)
- New `parts/vendor_footer.html` included **once** in `bc_base.html`, so it
  appears on every public route with zero per-template edits. It links the
  product page (`www.osduotech.com/solutions/business-connect`, now live), is
  gated by `show_vendor_credit`, uses no `nofollow`, and clears the fixed mobile
  action bar. The five old inline "Powered by … connect.osduotech.com" footers
  are removed; the link meets WCAG AA contrast.

#### Unused-CSS split (Phase D follow-up)
- `business_connect.css` is split into a shared base file (loaded everywhere)
  and one `theme-<name>.css` per theme (loaded only when active) via
  `scripts/split_css.py` — the source of truth is
  `styles/business_connect.src.css`. Served base went **89.6 KB → ~37 KB**; a
  themed page loads base + one theme file and never fetches the other five.
  Verified as a complete, isolated partition. Measured: mobile Lighthouse
  Performance **82 → 94** (LCP 4.3 s → 2.9 s).

#### Instant cache invalidation (Phase F)
- New `utils/cache.py` clears the Frappe website-page cache for the affected
  routes on any Business / Product / Service / Card change, **bidirectionally**
  (a child change clears its own page and the parent business page; a business
  change clears every child page). Wired into `doc_events` alongside the
  existing sitemap invalidation, so SEO edits show immediately (no 30-minute
  wait).

#### Configuration
- `OSDUO_BRANDING` gains the vendor/product identity keys (single source for
  the JSON-LD `Organization`/`Brand` and the footer) and `product_url_live` is
  now `True`.

### Upgrade
```bash
cd ~/frappe-bench/apps/osduo_business_connect && git pull
bench --site <site> migrate                 # Phase C SEO fields (schema)
bench --site <site> build --app osduo_business_connect   # self-hosted fonts + split CSS
bench restart                               # new Jinja filters, doc_events, utils
bench --site <site> clear-cache
bench --site <site> clear-website-cache
```

---

## v1.2.93 - 17 November 2026

### Bug fixes (v1.2.93)

#### Even section spacing on every public page
- `--bc-section-spacing` was a **two-value** shorthand (e.g. `2rem 1.5rem`) but
  `.bc-section` applied it as `padding: var(--bc-section-spacing) 0`. A
  two-value variable in a three-value padding expands to *top / sides / bottom*,
  so the **bottom padding was always 0** and the theme's horizontal value leaked
  in as side padding — the source of the uneven rhythm and stray white space.
- The token is now a **single vertical length**; `.bc-section` gets symmetric
  top/bottom padding and no horizontal leak (the inner `.bc-container` already
  supplies the side gutters).
- Per-template values were halved so the section-to-section rhythm is unchanged:
  Modern 2rem, Minimal 1rem, Classic 2rem, Luxury 3rem, Creative 2.5rem and
  Professional 5rem. The Professional / editorial `2.5rem` overrides are left in
  place.
- Verified across all six themes and both layouts, in light and dark mode, on
  desktop and mobile.

### Upgrade
```bash
bench --site <site> clear-website-cache
bench restart
```
CSS-only change (served straight from `/assets`); the per-template spacing
values come from `theme_service.py`, so `bench restart` picks them up. No
`migrate` required.

---

## v1.2.92 - 17 November 2026

### Changes (v1.2.92)

#### Desk form layout baked into the app
- The desk form layout tuned on `business.uat` with **Customize Form** is now
  part of the app's own DocType definitions, so every site gets it on `migrate`
  with no manual Customize Form work.
- **BC Theme**: field order regrouped; `naming_rule` corrected to
  `By "Naming Series" field`; **Import** enabled; the unused *Activation*
  section removed; four named column breaks added in place of the old
  `custom_column_break_*` records.
- **Showcase Product**: the Purchase Link checkbox and its button label now sit
  together in their own two-column block (`column_break_vacj`).
- **Showcase Service**: field order now mirrors Showcase Product — media
  (image · video · gallery | brochure · features), pricing with location below,
  and status · sort order on their own column.
- **Business, Business Member, Digital Card and Product Category** were reviewed
  and need no change.
- `migrate` deletes the leftover site-level Custom Fields / Property Setters
  (including the auto-generated `custom_column_break_*` records) so the source
  DocType stays the single truth.

### Upgrade
```bash
bench --site <site> migrate
bench --site <site> clear-cache
```
`migrate` rewrites the standard DocType layout and removes the stale Customize
Form records; existing data is untouched.

---

## v1.2.91 - 17 November 2026

### Bug fixes (v1.2.91)

#### Product / service video rendering
- **YouTube embeds now play.** A pasted watch / `youtu.be` / shorts / live link
  was placed straight into the `<iframe>` as a non-embeddable share URL, so it
  showed **"Refused to connect"**. It is now rewritten to the provider's embed
  URL (`youtube-nocookie.com/embed/…`). Vimeo, Google Drive and Dailymotion
  share links are converted to their frameable form the same way.
- **Nextcloud and direct video files now play.** A Nextcloud public-share link
  (`/s/<token>`) or any direct video file (`.mp4`, `.webm`, `.ogg`, …) matched
  none of the fixed provider allow-list and rendered nothing (no error either).
  These now play through an HTML5 `<video>` element — a Nextcloud share resolves
  to its direct download (`…/download?inline=true`).
- **No more empty video box.** A new `video_embed` Jinja filter
  (`utils/website.py`) returns `{kind: "iframe" | "file", src}`; the product and
  service templates render the matching player, and an unresolvable or unsafe
  URL renders nothing instead of a broken frame. `safe_video_url` is kept
  (iframe providers only) for backwards compatibility.
- **Services get videos too.** The **Video URL** field (identical to the product
  one) is added to **Showcase Service** — the service template and controller
  already supported it, only the field was missing. It also flows through the
  public service API.
- The Showcase Product and Service **Video URL** field descriptions list the
  supported sources.

### UI changes (v1.2.91)

#### Digital card page
- Removed the fixed **bottom navigation bar** (Home / Products / Enquiry) from
  the digital card page — it was the only page that carried one. The card
  content and its "Powered by" attribution are unchanged; the reserved bottom
  spacing was reduced to suit the removed bar.

### Upgrade
```bash
bench --site <site> migrate
bench --site <site> clear-website-cache
```
`migrate` adds the Service **Video URL** field and the field help text;
`clear-website-cache` refreshes the product/service HTML so the new player
markup renders.

---

## v1.2.9 - 11 November 2026

### Features (v1.2.9)

#### Database-driven sitemaps
- The app now serves its own XML sitemaps so search engines can discover every
  public Business Connect page. `/sitemap.xml` is a **sitemap index** that points
  at four per-type sitemaps:
  - `/sitemap-businesses.xml` — published business profiles (`/b/<slug>`)
  - `/sitemap-products.xml` — published products (`/b/<business>/products/<slug>`)
  - `/sitemap-services.xml` — published services (`/b/<business>/services/<slug>`)
  - `/sitemap-cards.xml` — published digital cards (`/c/<slug>`)
- URLs are generated **from the live records**, not a hand-maintained list: a
  business, product, service or card that is published appears automatically;
  drafts, suspended, archived, unpublished and cancelled records are never
  included, and a child URL is only listed when its parent business is public.
- Every URL carries an accurate `<lastmod>` (the record's `modified` date). The
  origin is resolved per request (`host_name` first, otherwise the host the
  sitemap was served on), so a multi-tenant subdomain site lists its own
  correct `https://<customer-domain>` URLs rather than the bare site name.
- Results are cached in Redis (6-hour safety TTL). Any publication change
  (create, update, submit, cancel or delete) clears the cache immediately, so a
  newly published page shows up on the next crawl instead of waiting for the
  next scheduled run.
- A full regeneration runs on the `0 2 */3 * *` cron (02:00 every third day) as
  a periodic safety net; it can also be run on demand with
  `bench --site <site> execute osduo_business_connect.seo.sitemap.generate_sitemaps`.
- Nothing is written to disk — the sitemaps are always generated from the
  database, so there is no stale file to replace. The app never pushes to
  Google; search engines find the sitemap through `robots.txt` and recrawl on
  their own schedule.
- `robots.txt` is now served **dynamically** by the app instead of Frappe core's
  verbatim dump of `Website Settings.robots_txt`. An administrator's custom rules
  are always respected, and the `Sitemap:` line is regenerated on every request
  from the host being served — so no stale or wrong-host declaration can leak.

#### "Start From" price display mode
- Showcase Product and Showcase Service gain a fourth price display mode,
  **Start From**. Enter the starting **Price** and **Currency** and the profile
  shows e.g. **"From INR 4,999"** — useful for services and made-to-order
  products that are priced from a minimum.
- The mode renders on all six product/service page themes, on the business card
  listings and in the public API, alongside the existing Hidden / Contact /
  Fixed modes.
- **Showcase Service** now has the full pricing block (Price Display Mode +
  Currency + Price). Previously services had no pricing fields at all, so a
  service could not show a price.

#### Price formatting
- Prices now render with thousands separators using the currency **code**, e.g.
  **INR 12,000** / **INR 140,000** instead of the previous `INR 12000` /
  `INR 140000`, across all six product/service themes and the card listings.
- Whole amounts drop the trailing decimals (`INR 12,000`); fractional amounts
  keep two (`INR 12,000.50`). Formatting follows the site's configured number
  format through a new `format_money` Jinja filter
  (`utils/money.py`), so no currency symbol is forced.

### Upgrade
```bash
bench --site <site> migrate
bench --site <site> clear-cache
bench --site <site> clear-website-cache
```
`migrate` applies the new DocType fields; `clear-website-cache` clears the
30-minute HTML page cache so the new pricing renders immediately. The sitemap
route is new — no Frappe core file is replaced.

---

## v1.2.8 - 8 November 2026

### Features (v1.2.8)

#### Fullscreen gallery lightbox
- Product and service galleries are now **clickable and zoomable**. Clicking a
  thumbnail opens a fullscreen lightbox instead of a new tab.
- The lightbox supports **previous / next navigation**, captions and an image
  counter, **zoom in / out / reset**, **drag to pan** when zoomed,
  **pinch-to-zoom** on touch devices, **double-click to toggle zoom**,
  **swipe** left/right to navigate, and **keyboard** controls
  (`Esc`, `←`, `→`, `+`, `-`, `0`).
- Gallery thumbnails are accessible buttons with a `zoom-in` cursor, a `+`
  zoom badge, focus outlines and descriptive `aria-label`s. Body scroll is
  locked while the lightbox is open and focus is restored on close.
- Implemented as a dependency-free partial
  (`templates/pages/product/parts/gallery_lightbox.html`) — no external JS
  library and no build step.

#### Full gallery above Features
- The gallery section now renders **every gallery image** (previously only the
  first three were shown in some templates) and displays the photo count in
  the section title, e.g. **"Gallery · 5 photos"**.
- Gallery section moved to sit **after Description / Buy Here and before
  Features** on both product and service detail pages, so visitors see visuals
  before the feature list.
- The hero now shows only the single cover image; gallery images are no longer
  rendered above the description and appear only in the gallery section.
- The full gallery section now renders for **all templates**, including
  Professional.
- The gallery section now uses the same content width as the other sections,
  and the Buy Here button uses the standard button size, so both line up with
  Description / Features.
- Fixed horizontal scrolling on mobile caused by the full-width purchase
  button overflowing its container.

#### Standard desk form layout
- The desk form layout tuned on the UAT site with **Customize Form** is now
  part of the app's DocType definitions, so every site gets it on `migrate`.
- **Business**: Industry moved next to Slug; the About Us, contact, branding,
  social and hours sections were rearranged, and the description field is now
  labelled **About Us**.
- **Business Member**, **Digital Card**, **Product Category**, **Showcase
  Product** and **Showcase Service**: fields regrouped into logical columns.
- **Showcase Product / Service**: the separate Enquiry and Purchase Link
  sections are merged into a single **Enquiry and Purchase Link** section.
- `naming_series` is hidden on all seven forms, and import is enabled for
  Business, Business Member, Digital Card, Product Category, Showcase Product
  and Showcase Service.
- Digital Card hides **Sort Order** on the form — it still exists and drives
  backend card ordering, it is just set programmatically.
- `after_migrate` now removes the redundant site-level `Custom Field` /
  `Property Setter` customizations so the standard DocType JSON remains the
  single source of truth.

### Upgrade
```bash
bench --site <site> migrate
bench --site <site> clear-cache
bench --site <site> build
```
The desk form layout is applied by `migrate`; existing data is untouched.

---

## v1.2.7 - 6 November 2026

### Features (v1.2.7)

#### Buy Here (purchase link)
- Showcase Product and Showcase Service gain a **Purchase Link** section
  (`purchase_enabled` checkbox) with three supporting fields: an optional per-item
  **Shopping Portal Link** override and an optional **Button Label**
  (defaults to "Buy Here"; e.g. "Book Now", "Order Here").
- Business gains an optional **Buying Portal Link** (`shop_url`) — "custom
  location as per business requirement" — so items only need the checkbox
  when the whole company sells in one place.
- Public product/service pages render a **Buy Here →** button when the
  checkbox is on and a link resolves (item override → business link). Every
  destination passes the app's `safe_url` sanitizer before rendering.
- **All external links on public pages now open in a new tab with
  `rel="noopener"`** (buy CTA + previously un-hardened map / brochure /
  website / member / social links).
- Button label and URL are HTML-escaped at render time; the event fires a new
  whitelisted client engagement event **`buy_click`** (product or service
  scope), so the analytics Events-by-type chart shows real purchase intent.

#### Featured & sort order now take effect
- Confirmed broken: `featured` was stored but never used in any template, and
  listings ignored it entirely. All four listing queries (business page
  products/services, card page products/services, both public API endpoints)
  now order by `featured desc, sort_order asc`.
- A **★ Featured** accent chip renders on the Business page product/service
  tiles and the Card page tiles (pinned top-right); detail pages stay clean.

### Upgrade
`bench --site <site> migrate && bench --site <site> clear-cache && bench --site <site> build`.

---

## v1.2.6 - 3 November 2026

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
- **v1.1.0** (Planned): New feature set TBD - see the project's local development plan

---

## Support & Resources

- **Full API Reference** — RESTful API documentation (maintained with the app's internal docs)
- **Development Roadmap** — future feature plans and timelines (maintained locally)
- **Architecture Decisions** — design choices for the project (maintained locally)
- Buy CTA now renders **below the Description/About section** with tightened
  spacing (no double section spacing) for better reading flow, instead of
  directly under the hero.
