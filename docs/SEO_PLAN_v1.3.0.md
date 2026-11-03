# SEO Implementation Plan — v1.3.0

**Status:** Approved, ready for implementation
**Target release:** v1.3.0 (single release, all phases)
**Date:** November 2026
**Depends on:** v1.2.6 (`main`, this release)
**Mirrored in:** [TODO](TODO.md) §1 — the single working pending list
**Related:** [Marketing Feature Inventory](MARKETING_FEATURE_INVENTORY.md) · [SaaS Plan](SAAS_IMPLEMENTATION_PLAN.md) · [PWA](PWA.md)

---

## 0. Decisions locked

| # | Decision | Outcome |
|---|---|---|
| 1 | Sitemap shape | Separate `/sitemap-profiles.xml` + `robots.txt` pointer. **No override** of Frappe core `/sitemap.xml` |
| 2 | SEO fields | Added to **Showcase Product** and **Showcase Service**. **Digital Card inherits from Business** |
| 3 | Team-member page | Left as-is: no route rule, not in sitemap, templates untouched. Reserved for a future app |
| 4 | Scope | All phases in one release |
| 5 | Fonts/icons | Best-for-SEO option: self-hosted `woff2` subsets + inline SVG icons, zero third-party CDN calls |
| 6 | Title suffix | **None.** `<title>` carries page content only — no `| OSDuo`, no `| OSDuo Business Connect` |
| 7 | Brand attribution | Sitewide **footer credit** + `og:site_name` + `application-name` + JSON-LD `Organization`/`Brand` |
| 8 | Tenant domains | Vendor credit **stays on** custom/BYOD domains (toggleable via one constant) |
| 9 | Product page URL | Stored but **not linked** until live (`product_url_live`); footer and JSON-LD point to the vendor site meanwhile |

### Why no title suffix

- A brand suffix in `<title>` is a *very* weak ranking signal, and Google rewrites titles in
  SERPs regardless. Its only real effect is brand impressions — paid for with characters the
  tenant needs for their own keywords.
- A sitewide footer link is also not a strong ranking factor (Google discounts repeated
  boilerplate), but it does help **discovery** and **entity association**.
- The signal that actually moves brand/entity ranking is **structured data**
  (`Organization` + `sameAs` + `Brand` + `publisher`) plus a **live product page** on
  `www.osduotech.com` linked from `/solutions`. That is where the effort goes.

**Net:** brand lives in `og:site_name`, `meta application-name`, JSON-LD and the footer.
Title characters are reserved entirely for page content.

---

## 1. Current-state findings this plan closes

**P1**

1. `og:title` / `og:description` / `og:image` never render — `bc_base.html:8-10` guards on
   variables no controller ever sets. Cards are shared on WhatsApp/LinkedIn/X, so there is
   currently **no social preview at all**.
2. No `<link rel="canonical">`, no `og:url`. `PathResolver` strips leading/trailing slashes,
   so `/b/slug` and `/b/slug/` both serve 200 with identical content; so does every `?utm_*`
   variant → duplicate content.
3. `product.py:47-50` and `service.py:47-50` read `doc.seo_title` / `doc.seo_description`,
   which **do not exist** on those doctypes → dead code, and those pages emit no description.
4. Nothing app-related is in any sitemap. Frappe's `/sitemap.xml` only lists Web-View doctypes
   and static pages; all BC routes are dynamic and no controller sets `sitemap`. `/robots.txt`
   is empty → no `Sitemap:` directive.
5. Meta description quality: Business only when the field is filled (no fallback); Card is a
   hardcoded `f"Contact {display_name}"` (~15 chars); Product/Service emit none.
6. Invalid HTML: unclosed `<div>` in `product.html:26-33`.

**P2**

7. No structured data anywhere (zero `application/ld+json` matches).
8. `card.py:38-41` builds the share URL from `request.host` + `request.scheme` → emits
   `http://` share links behind a TLS-terminating proxy (and would feed a wrong `og:url`).
9. `/b/<slug>/team/<member_slug>` has no route rule and no inbound links (orphaned).
10. No crawl policy: `/login` (the site root), `/app`, `/api`, `/analytics`, `/offline` are
    all indexable.
11. SEO fields buried under "Branding & Theme" (`business.json` fields 28-29), no length
    guidance, `seo_title` never HTML-stripped (description is).
12. SEO fields are frozen after submit — nobody can fix their search snippet without
    cancel/amend. This is a bug.
13. Stale meta for up to 30 minutes after an SEO edit (Frappe caches rendered HTML in
    `website_page::<path>`); nothing invalidates it on save.

**P3 — Core Web Vitals**

14. 12 Google Font families + Font Awesome loaded render-blocking from CDNs on every page.
15. 0 of 46 `<img>` have `width`/`height` → CLS; no `srcset`; no `fetchpriority` on the LCP hero.
16. `og-image.png` is 1.3 MB / 1731×909 → should be ~1200×630 and <300 KB.

---

## 2. Workstreams

### A — `utils/seo.py` (new, single source of truth)

```python
build_seo(title, description, path, image=None, page_type="website",
          robots="index,follow,max-image-preview:large", business=None) -> dict
clean_text(html, limit=155)      # strip tags/entities, collapse whitespace, word-boundary cut
absolute_url(path)               # via get_canonical_base_url(); never request.host
jsonld(obj)                      # json.dumps(ensure_ascii=True).replace("<", "\\u003c")
vendor_org_jsonld()              # Organization(OSDuo Tech LLP) + WebSite + Brand
```

Returned dict keys: `title`, `description`, `canonical`, `robots`, `og_title`,
`og_description`, `og_url`, `og_image`, `og_type`, `og_site_name`, `twitter_card`,
`jsonld` (list of dicts).

No `brand_title()` suffix helper — decision 6 removes it.

### B — `<head>` in `templates/bc_base.html`

In order: `<title>` (page content only) · meta description · `<link rel="canonical">` ·
meta robots · `og:type/site_name/locale/title/description/url/image` (+
`og:image:width/height/alt`) · `twitter:card=summary_large_image` + title/description/image ·
`meta name="application-name"` · `meta name="generator"` · one
`<script type="application/ld+json">` per block · `meta name="theme-color"`.

Delete the dead `{% if og_title %}` / `og_description` / `og_image` guards and replace them
with the real `seo.*` context.

### C — per-page SEO precedence

| Page | `<title>` source | Description fallback chain | Image | `og:type` |
|---|---|---|---|---|
| Business | `seo_title` → `{name} — {industry}` | `seo_description` → `description` → `{name} in {city}` | `cover_image` → `logo` → bundled og-image | `website` |
| Product | `seo_title` → `{product} — {business}` | `seo_description` → `short_description` → `description` | `image` → business logo | `product` |
| Service | `seo_title` → `{service} — {business}` | `seo_description` → `short_description` → `description` | `image` → business logo | `website` |
| Digital Card | `{display_name} — {designation}` (+ business name) | **Business `seo_description`** → business `description` → `bio` | `profile_image` → business logo | `profile` |
| Team member | **untouched** (no route, not in sitemap) | — | — | — |

Canonical always from `public_url` / `utils/urls.py`. This also fixes finding 8
(`card.py:38-41`).

### D — DocType changes (additive, needs `bench migrate`)

- **Showcase Product / Showcase Service:** new `SEO` section with `seo_title` (Data) +
  `seo_description` (Small Text) — makes the existing dead reads functional.
- **Business:** move `seo_title` / `seo_description` out of "Branding & Theme" into their own
  **SEO** section.
- All three: help text ("50–60 characters", "150–160 characters") and
  **`allow_on_submit: 1`**.
- `core.py` / controllers: strip tags from `seo_title` (currently only description is
  sanitized); soft warning (orange `msgprint`) above 70 / 160 chars — **warn, never block**.
- No child-table or data migration; `migrate` is sufficient.

### E — `www/sitemap-profiles.xml` + `.py`

- URLs: published Businesses (`status='Published'`, `public_profile_enabled=1`,
  `docstatus < 2`, slug set), their published Products/Services, and published Cards whose
  business is public.
- `lastmod` from `modified`; XML-escaped; canonical origin; no query strings.
- Scales from day one: ≤ 45k URLs → single `urlset`; beyond that → `sitemapindex` +
  10k-per-chunk pages (`/sitemap-profiles-1.xml`, `-2.xml`, …) via `website_route_rules`,
  each redis-cached 6 h.
- Never exposes Draft, Suspended, Archived, Unpublished, cancelled, or unpublished-parent
  records.

### F — robots.txt + noindex

- `apply_branding_settings()` gains a **non-destructive** step: only when
  `Website Settings.robots_txt` is empty, set:

```
User-agent: *
Disallow: /app
Disallow: /api
Disallow: /login
Disallow: /printview
Disallow: /analytics
Allow: /assets
Allow: /files
Sitemap: https://<canonical>/sitemap-profiles.xml
```

- Existing custom robots text is **never** overwritten.
- `noindex,nofollow` on login (root is `home_page = "login"`), `/offline`, `/analytics`.
  Public pages get `index,follow,max-image-preview:large`.

### G — JSON-LD (rich results)

| Node | Where | Fields |
|---|---|---|
| `Organization` + `WebSite` + `Brand` | every page | OSDuo Tech LLP, `url`, `logo`, `sameAs`, `brand` = "OSDuo Business Connect", `brand.url` = vendor site until product page is live |
| `LocalBusiness` | business | name, url, logo/image, description, telephone, email, `address` (PostalAddress), `openingHoursSpecification` from `Business Hour`, `sameAs` from social links |
| `Product` + `Offer` | product | name, description, image, `brand` = business, `offers` **only when price is publicly displayed** (`price_display_mode = Fixed`): price, currency, availability `InStock`, url |
| `Service` | service | name, description, image, `provider` (business ref), `areaServed` |
| `Person` | card | name, jobTitle, image, `worksFor`, email, telephone, `sameAs` |
| `BreadcrumbList` | product/service/card | Business → Item (no fake home page, since the root is a login screen) |

All output through `jsonld()` so user-entered text can never break out of the `<script>` block.
Business Hour options are Monday–Sunday with `enabled`, `open_time`, `close_time`,
`is_24_hours` → maps cleanly to `openingHoursSpecification`.

### H — OSDuo brand attribution

- No title suffix (decision 6).
- `og:site_name` = `OSDuo Business Connect`; `meta name="application-name"` likewise.
- New partial `templates/pages/parts/vendor_footer.html`, included **once** in `bc_base.html`
  before `</body>` → appears on business, product, service, card and every future route with
  zero per-template edits:

```html
<footer class="bc-vendor-footer">
  <a href="https://www.osduotech.com" target="_blank" rel="noopener">
    Powered by OSDuo Business Connect — A Product of OSDuo Tech LLP
  </a>
</footer>
```

- Small, muted, centered, `<footer>` landmark, accessible name, **no `nofollow`** — the
  association is the point.
- Rendered on tenant custom domains too (decision 8), gated by `show_vendor_credit`.
- JSON-LD `Organization` ties every page to `https://www.osduotech.com`.

`hooks.py → OSDUO_BRANDING` additions:

```python
"vendor_name": "OSDuo Tech LLP",
"vendor_url": "https://www.osduotech.com",
"product_name": "OSDuo Business Connect",
"product_url": "https://www.osduotech.com/solutions/business-connect",  # under development
"product_url_live": False,      # flip to True the day the page goes live
"show_vendor_credit": True,     # on for tenant custom domains too
"vendor_credit_text": "Powered by OSDuo Business Connect — A Product of OSDuo Tech LLP",
"title_brand_suffix": "",       # deliberately empty
```

All strings read from `OSDUO_BRANDING`, so a white-label deployment changes one dict.
When the product page ships, `product_url_live = True` is the **only** edit — footer and
JSON-LD switch automatically.

### I — Core Web Vitals (best-for-SEO option)

- **Fonts:** self-host the 12 theme families as latin-subset `woff2` in `public/fonts/` + one
  `fonts.css` with `@font-face { font-display: swap }`. `@font-face` downloads lazily, so a
  page fetches only the selected family (+ Playfair Display / Space Grotesk when used) —
  1–3 files instead of 12 families plus render-blocking CSS. Remove
  `fonts.googleapis.com` / `fonts.gstatic.com` links and preconnects. Ship the OFL licence.
- **Icons:** drop the Font Awesome CDN. New Jinja macro `bc_icon(name)` with inline SVG —
  Simple Icons (CC0) for the brand icons in `Business Social Link.platform` /
  `Digital Card Link.link_type` (Facebook, Instagram, LinkedIn, X, YouTube, Telegram),
  Lucide (ISC) for the `fa-solid` uses (`fa-link`, `fa-globe`, `fa-briefcase`). Map existing
  `icon_class` values (`fa-brands fa-facebook` → `facebook`) with a generic fallback so
  existing records keep rendering.
- **Images:** `width`/`height` (or CSS `aspect-ratio`) on all 46 `<img>`, `decoding="async"`,
  `loading="lazy"` below the fold, `fetchpriority="high"` on the hero, `preload` for the hero
  cover. Upload guidance (≤1600 px, ≤300 KB) documented — Frappe has no on-the-fly resizing.
- **`og-image.png`:** re-cut 1731×909 / 1.3 MB → 1200×630 / <300 KB.
- Verify no render-blocking third-party CSS/JS remains above the fold.

### J — Cache invalidation

New `utils/cache.py`: on `on_update` / `on_submit` / `on_cancel` / `on_trash` of Business,
Showcase Product, Showcase Service, Digital Card → clear `website_page::<path>` for the pages
that embed them (a product edit must also clear the parent business page, which renders
products) and clear the sitemap caches. Closes finding 13.

### K — Tests (all runnable without a bench)

- `test_seo.py` — fallback chains, word-boundary truncation (155/160), absolute
  canonical/OG URLs, `jsonld()` escaping (`</script>` breakout impossible), robots values,
  **no brand suffix in `<title>`**.
- `test_sitemap.py` — filters exclude Draft/Suspended/Archived/cancelled/unpublished-parent;
  canonical base used; chunking threshold; XML escaping.
- `test_templates.py` — HTML tag balance across **all** templates (would have caught
  `product.html:26-33`), required head tags present, no `fonts.googleapis.com` / `cdnjs`
  references, canonical/OG/Twitter blocks emitted.
- `test_branding.py` / `test_install.py` — robots set only when empty; vendor/product URLs
  absolute; SEO fields exist on 3 doctypes with `allow_on_submit=1`; `team_member` has **no**
  route rule; JSON-LD never emits the product URL while `product_url_live` is false.
- Suite: 139 → ~165 passing, plus `compileall`, Ruff with **no new findings**
  (134 pre-existing baseline), `git diff --check`.

### L — Docs & release

- `docs/MARKETING_FEATURES.md` — rewrite §4 to match reality (it currently claims `og:url`,
  an OG Image field, and SEO fields on Product/Service, none of which existed).
- `docs/INSTALLATION_GUIDE.md` — new "SEO" section: `host_name`, robots defaults, sitemap URL,
  Search Console submission, cache-clear after SEO edits.
- `docs/USER_MANUAL.md` — how to write SEO title/description, cards inheriting from business,
  the noindex/root-login note.
- `docs/MARKETING_FEATURE_INVENTORY.md` — flip §1.8 rows from "committed" to shipped.
- `CHANGELOG.md`, `RELEASE_NOTES.md`, `__version__ = "1.3.0"`; commit to `develop` →
  fast-forward `main`; tag `v1.3.0`; GitHub release.

---

## 3. Acceptance criteria

1. `view-source` on `/b/<slug>`, product, service and card: page-content-only `<title>`,
   unique description, canonical, complete OG set, Twitter card, valid JSON-LD.
2. `/sitemap-profiles.xml` → 200 XML containing **only** public URLs; a Draft or Cancelled
   record never appears.
3. `/robots.txt` → disallows + `Sitemap:` line; an admin's custom robots text is untouched.
4. Rich Results Test: LocalBusiness, Product, Service, Person, BreadcrumbList, Organization —
   0 errors, 0 warnings.
5. Zero requests to `fonts.googleapis.com`, `fonts.gstatic.com`,
   `cdnjs.cloudflare.com`; Lighthouse mobile SEO 100, Performance ≥ 85.
6. Existing pages visually unchanged except the intended footer credit; all tests green.
7. Editing `seo_title` on a submitted record saves without amend, and the new title appears
   immediately (no 30-minute wait).
8. Footer credit renders on business, product, service and card pages, including tenant custom
   domains, and links to `https://www.osduotech.com`.

---

## 4. Deploy & verification

On the user's bench (`connect@connect:~/connect-bench`, site `osduo.connect`):

```bash
cd ~/connect-bench/apps/osduo_business_connect && git pull
bench --site osduo.connect migrate
bench --site osduo.connect build --app osduo_business_connect
bench --site osduo.connect clear-cache
bench --site osduo.connect clear-website-cache
```

Then: `curl -s https://<site>/sitemap-profiles.xml`, `curl -s https://<site>/robots.txt`,
view-source on a business page, Rich Results Test, Lighthouse. Submit
`sitemap-profiles.xml` in Google Search Console.

> `migrate` **and** `clear-website-cache` are both mandatory — DocType JSON changes plus
> the 30-minute HTML page cache.

Runtime verification must happen on the user's bench; the VM `192.168.122.49` is unreachable
from the dev machine (`ssh: No route to host`), so all local checks are structural /
pure-Python.

---

## 5. Risk notes

- The sitemap is a **new route** — no Frappe core file is overridden; only
  `website_route_rules` + `www/` additions.
- DocType changes are additive; `allow_on_submit` is the only behavioural change, and it is a
  fix, not a preference.
- Icon migration is the highest visual-regression risk — the `icon_class` mapping table plus a
  generic fallback keeps existing records rendering.
- Font self-hosting adds ~300 KB of `woff2` to the repo but **reduces** per-page payload
  (12 → 1–3 font files, no third-party CSS).
- The sitewide footer puts OSDuo branding on tenant custom domains (requested). If a tenant
  objects later, `show_vendor_credit = False` is the escape hatch — no code change.

---

## 6. Out of scope for v1.3.0

- SaaS tiers, `BC Subscription`, quotas, CRM module gating ([SaaS Plan](SAAS_IMPLEMENTATION_PLAN.md))
- Tiered SEO features (keyword tracking, per-tier SEO caps)
- Web push, TWA / `.well-known/assetlinks.json`, multi-language
- Team-member routing (deliberately deferred to a separate app)
- Automatic image resizing (Frappe has none; handled by upload guidance instead)

---

## 7. Separate fixes needed outside this app

1. `https://www.osduotech.com/sitemap.xml` and `/robots.txt` return **200 with empty bodies** —
   the marketing site is effectively unindexable via sitemap. Needs fixing in that codebase.
2. `https://www.osduotech.com/solution/business-connect/` **301s to `http://`** — a
   plain-HTTP redirect chain that undercuts the HTTPS setup.
3. `/solutions/business-connect` must go **live**, then set `product_url_live = True`.
