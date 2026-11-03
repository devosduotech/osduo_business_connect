# Pending To-Do List — OSDuo Business Connect

**Last updated:** 3 November 2026 · **Shipped version:** 1.2.6 (`main`)

This is the single working list of everything pending across the project: the
committed next release, the product backlog, known tech debt and documentation
cleanups. Items elsewhere (e.g. the committed scope in
[SEO_PLAN_v1.3.0.md](SEO_PLAN_v1.3.0.md)) are mirrored here so the list stays
authoritative. Tick items off and re-date this header as they move.

---

## 1. Committed next — v1.3.0 (SEO & brand attribution)

Single release, all ten items planned in
[SEO_PLAN_v1.3.0.md](SEO_PLAN_v1.3.0.md). **Depends on v1.2.6 (`main`).**

> **Recommended priority order** (Nov 2026): the work below is listed in that
> order. Rationale — Business Connect creates multiple public URLs per business
> (a company with several products/services can build a meaningful search
> presence through the individual pages), so whoever owns the sharing metadata
> ships first, then machine readability, then discoverability, then catalogue
> control and performance.

- [ ] **P1 — Canonical & OG metadata on all public pages**: canonical, OG
  (title/description/url/image/type/site_name/locale), Twitter
  `summary_large_image`, robots meta, theme-color (*better sharing and
  indexing*)
- [ ] **P2 — Structured data (JSON-LD)**: `Organization`, `WebSite`, `Brand`,
  `LocalBusiness` (address, hours, socials), `Product` + `Offer`, `Service`,
  `Person`, `BreadcrumbList` (*search engine understanding*)
- [ ] **P3 — `/sitemap-profiles.xml`**: every published business/product/
  service/card, `lastmod`, chunked at scale (45k URLs, 10k/chunk index)
  (*public page discovery*); incl. non-destructive `robots.txt` defaults wired
  to the sitemap line
- [ ] **P4 — Product & Service SEO fields**: `seo_title` + `seo_description`
  (editable after submit, 50–60 / 150–160 char guidance), plus unique
  title/description fallbacks when blank (*better catalogue visibility*)
- [ ] **P5 — Core Web Vitals**: self-hosted woff2 theme fonts (1–3 files),
  inline SVG icons replacing the Font Awesome CDN call, image dimensions +
  lazy loading + LCP priority, re-cut 1200×630 OG image (*performance*)
- [ ] **P6 — OSDuo attribution footer** on every page and tenant domain:
  "Powered by OSDuo Business Connect — A Product of OSDuo Tech LLP" →
  `https://www.osduotech.com` (*brand visibility*; current footers still link
  `https://connect.osduotech.com` — deliberately unchanged until v1.3.0)
- [ ] Support item: instant cache invalidation when SEO text changes (no
  30-minute stale `<meta>`) — ships alongside P1–P3
- [ ] Post-shipping checklist for v1.3.0: Lighthouse before/after, Search
  Console validation, `bench build` note in docs

## 2. Product backlog (roadmap)

- [ ] SaaS tiers & quotas — `BC Subscription` DocType, plan gating of CRM /
  analytics modules by business role (designed in
  [SAAS_IMPLEMENTATION_PLAN.md](SAAS_IMPLEMENTATION_PLAN.md), not coded)
- [ ] Web push notifications for installed PWAs
- [ ] Play Store listing via TWA wrapper (`/well-known/assetlinks.json` still
  missing)
- [ ] Multi-language content/theme
- [ ] Team-member profile page (`/b/<business>/team/<member>`) — templates
  exist but are deliberately unrouted; reserved for a future app (locked
  decision, see SEO_PLAN decision #3)
- [ ] AI-assisted product descriptions; predictive lead scoring; multi-touch
  attribution; ROI dashboard on `/analytics`
- [ ] Email signature generator; auto-enquiry responses; WhatsApp Business API
  integration
- [ ] Custom-domain per-business sitemap rows when BYOD domains attach (vendor
  credit already promised in the footer task above)
- [ ] Combine SEO fields with the enquiry form consent questions (overview of
  what consent text is shown where) — small doc task first, then code

## 3. Ops / verification to keep an eye on

- [ ] Confirm `describe_canonical_url` output on every live site after the
  v1.2.5–v1.2.6 rollout (scheme + no stray dev port), per
  [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) troubleshooting table
- [ ] Watch Contact Exchange → Enquiry → CRM Lead flow on production traffic
  (first week): `enquiry_submitted` + `contact_exchanged` events, backfilled
  `osduo_notes` on historical Lead rows
- [ ] Monitor nightly `retry_failed_enquiries` for CRM-unavailable sites (the
  sync logs instead of failing silently)
- [ ] Verify the desk "Open" button renders on all four profile forms after
  `bench build` (asset bundle ships the client scripts)
- [ ] Re-run the v1.2.5 VM checklist items not yet exercised in production:
  visitor-mix filter on real traffic, `?ref=mycard` attribution

## 4. Tech debt & code hygiene

- [ ] Sweep remaining Ruff findings in untouched modules — F401 unused imports
  in `theme_service.py`, `crm_sync.py`, `enquiry_webhook.py`, `services/scheduler.py`
  and several DocType controller stubs; F841 (`layout_mode`, `shadow`) in
  `theme_service.py`; W293/PIE790 in `install.py` era code (all pre-existing,
  excluded from v1.2.5/1.2.6 "touched files only" cleanups)
- [ ] Retire or archive `tests/_test_uat_old.py` (kept as reference; it is not
  in the default test suite run) and re-base useful UAT scenarios into the
  structural suite
- [ ] Split `test_v125_features.py` by feature (share bar / My Card / contact
  exchange / CRM) once it passes ~250 tests
- [ ] Add `patches/v1_2/__init__.py`? (no — matches existing `v1_0` style; note
  kept so nobody re-asks)
- [ ] Add a bench `bench --site x build` reminder to the upgrade snippet in
  PWA.md and USER_MANUAL (asset bundle bump policy introduced in v1.2.6)
- [ ] Consider a `www/` route for `/analytics` mobile header reuse instead of
  inline styles in `templates/pages/analytics.html`

## 5. Documentation cleanups

- [ ] **MARKETING_FEATURES.md** still markets features that are *not* built
  (email signature generator, lead scoring, auto-responses, WhatsApp Business
  API) — rewrite or add a "roadmap" banner linking
  [MARKETING_FEATURE_INVENTORY.md](MARKETING_FEATURE_INVENTORY.md) §1.10
- [ ] Fold any remaining "Portable apps" phrasing into the PWA naming used by
  PWA.md before v1.3.0
- [ ] Add a short "Contact Exchange" walkthrough (screenshots) to USER_MANUAL
  §6.6 once production screenshots exist
- [ ] Keep MARKETING_FEATURE_INVENTORY in sync with each release (already
  done for v1.2.5/v1.2.6 evidence rows)
- [ ] Generate/refresh `docs/images/mockup/*` screens for the new Open button
  and exchange form (referenced placeholders)

---

### Priorities considering the next release

1. **v1.3.0 SEO items (section 1)** — the only blocking scope; one pass as
   decided. Everything else lands after.
2. **Documentation cleanups (section 5, first item)** — do not market the
   unshipped features; fix before the v1.3.0 marketing push.
3. Sections 2–4 are backlog — pick up opportunistically.
