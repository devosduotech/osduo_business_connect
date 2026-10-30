# Theme Redesign Plan — Based on "Theme Designs Ideas"

Status: Draft for approval
Scope: Digital Card, Business Profile, Product Page, Service Page
First implementation slice: **Professional template + all color schemes**

---

## 1. Audit — current state vs. designs

### What the design pack contains

| Design | Card | Business | Product | Service |
|---|---|---|---|---|
| Professional | yes | yes | yes | yes |
| Modern | yes | yes | yes | yes |
| Minimal | yes | yes | yes | yes |
| Classic | yes | yes | yes | yes |
| Luxury | **missing** | **missing** | **missing** | **missing** |
| Creative | **missing** | **missing** | **missing** | **missing** |

Supporting sheets: `color_schemes.html` (7 presets + Custom), `button_styles.html`
(Filled, Outline, Rounded, Pill).

### Critical issues found

1. **`templates/pages/card/card.html` is corrupted in the working tree.**
   The `{% block page_content %}` opener and the `{% if template_type == "Professional" %}`
   branch were replaced by a leftover `debug_mode` / `prod_template` snippet.
   The rest of the file still has `{% elif %}` branches → the template cannot render.
2. **Card page is not a card.** Current layout is a full-width page of stacked blocks
   (`var(--bc-card-width)` = 480px, section "stripes", many inline styles). The designs
   show one contained white card (420px, 12px radius, soft shadow) with a coloured header band.
3. **Professional hero does not match its design.** Current: 90px round avatar, solid
   primary header, vertical contact list, single-row buttons. Design: 72px rounded-square
   avatar, gradient header, bio + contact tiles in body, two-column outlined action grid.
4. **Hard-coded colours bypass the theme.** Several templates use `#475569`, `#64748b`,
   `#e2e8f0`, `#EFF6FF`, `#25D366`, `#EA4335` directly. Dark mode and Custom schemes
   cannot adapt.
5. **Colour scheme set is out of sync.** `color_schemes.html` defines Violet, Indigo, Blue,
   Green, Yellow, Orange, Red, Custom. `theme_service.py` / BC Theme defines those plus
   **Gold**, and there is no dedicated dark/soft token per scheme.
6. **No analytics/CRM hidden fields** on the card page yet (business, card, landing URL,
   campaign/UTM parameters) — required from the earlier task.
7. **Missing design inputs** for Luxury and Creative. Options: (a) user supplies designs,
   (b) we keep the current interpretation and only align tokens, (c) we derive them from
   the existing Luxury/Creative CSS until designs arrive.

### Current key files

- `osduo_business_connect/templates/pages/card/card.html` (+ `parts/hero_*.html`)
- `osduo_business_connect/templates/pages/business/business.html` (+ `parts/hero_*.html`)
- `osduo_business_connect/templates/pages/product/product.html` (+ `parts/hero_*.html`)
- `osduo_business_connect/templates/pages/service/service.html`
- `osduo_business_connect/public/css/business_connect.css` (2303 lines)
- `osduo_business_connect/services/theme_service.py` (scheme map + CSS variables)

---

## 2. Design system to extract (shared foundation)

### 2.1 Typography
- Family: Inter (already loaded in `bc_base.html`), fall back to theme `font_family`.
- Scale: 1.6–1.8rem page H1, 1.25rem card name, 0.95rem section title,
  0.85rem body, 0.75–0.8rem meta/labels.
- Professional section headers: uppercase, 0.85rem, letter-spacing 0.1em,
  muted colour, 2px bottom border + short primary rule.
- Minimal section labels: uppercase 0.7rem, letter-spacing 0.1em.

### 2.2 Spacing / radius / elevation
- Card width: 420px (desktop), full width − 32px (mobile).
- Radius: 12px card (Professional 12px, Minimal 2px, Classic 16px, Modern 16px).
- Section padding: 24px.
- Shadow: `0 4px 24px rgba(0,0,0,0.06)` (soft), hover `0 6px 20px rgba(0,0,0,0.10)`.

### 2.3 Colour schemes (8)
Keep every scheme variable-driven. Add per-scheme derived tokens:

| Scheme | primary | primary-dark | accent | on-primary |
|---|---|---|---|---|
| Violet | #7C3AED | #6D28D9 | #A78BFA | white |
| Indigo | #4F46E5 | #4338CA | #818CF8 | white |
| Blue | #2563EB | #1E40AF | #60A5FA | white |
| Green | #16A34A | #15803D | #4ADE80 | white |
| Yellow | #EAB308 | #CA8A04 | #FDE047 | #1E293B |
| Orange | #EA580C | #C2410C | #FB923C | white |
| Red | #DC2626 | #B91C1C | #F87171 | white |
| Gold (keep) | #D4AF37 | #B8860B | #F5D060 | #1A1A2E |
| Custom | user | derived | user | auto contrast |

New CSS custom properties (generated in `get_theme_variables`):
`--bc-primary-dark`, `--bc-primary-soft` (≈ 8 % primary tint), `--bc-primary-tint`
(≈ 14 %), `--bc-on-primary`, `--bc-success` (#16A34A), `--bc-danger` (#DC2626),
`--bc-text-strong`, `--bc-text-muted`, `--bc-text-faint`,
`--bc-radius-sm/md/lg`, `--bc-shadow-sm/md`.

Dark mode overrides: surface `#1E293B`, background `#0F172A`, border `#334155`,
text `#E2E8F0`, muted `#94A3B8`; soft tints become `rgba(primary, .18)`.

### 2.4 Buttons (`button_styles.html`)
- Filled: primary bg, white text (dark text for Yellow/Gold).
- Outline: transparent, 1.5px primary border, primary text.
- Rounded: 12px radius variant of Filled.
- Pill: 999px radius variant of Filled.
- WhatsApp / Email action buttons keep their semantic green/red **but** use soft
  tinted surfaces (`#F0FDF4` / `#FEF2F2` + matching border/text) as in the designs.

### 2.5 Shared components
- `.bc-card-shell` — the 420px white card frame (single card, not stacked blocks).
- `.bc-section-head` — title + primary rule.
- `.bc-tile` — bordered surface card used by products, services, contact, details.
- `.bc-action-grid` — 2-column outlined action buttons (Professional) vs
  column stack (Minimal) vs pill row (Modern).
- `.bc-chip` — outlined social/link chips.

---

## 3. Gap analysis per page (Professional)

### Card (`/c/<slug>`)
Design: gradient header (primary → primary-dark), 72px rounded-square avatar,
name/designation/business; body with bio; contact list as icon tiles; divider;
2×2 outlined actions (Call, WhatsApp tinted, Email tinted, Website); outline link chips.
Missing in current template: bio block, contained card frame, tinted action styles,
consistent section headers. Body sections (products/services/enquiry/share/VCF/nav)
need to inherit the same frame and section-head rules.

### Business (`/b/<slug>`)
Design: dark slate header band (`#1E293B`) with primary logo tile, name, tagline,
stats row; sections with title + primary rule; 3-col bordered product cards;
2-col contact tiles; light footer.
Gaps: current hero is a flat primary bar with cover image; no stats; sections use
generic `.bc-section-title`. Need a professional page shell (header band, container,
section head), plus `business.py` stats (`team_members`, `products`, `services` counts).

### Product (`/b/.../products/<slug>`)
Design: dark breadcrumb bar + category chip; split hero (gallery 2-up left, info right
with title, tagline, price, outlined CTA); description/details sections; details as
left-border tiles; light footer.
Gaps: current hero is a stacked block inside primary header; no gallery split; no
details grid.

### Service (`/b/.../services/<slug>`)
Design: top bar + dark header band; split hero (info left, visual right); benefits
2-col bordered tiles; pricing block; footer.
Gaps: shares product hero; no benefits grid/pricing block.

---

## 4. Implementation phases

### Phase 0 — Stabilise (must be first)
1. Restore/rebuild `card.html` from `HEAD`, remove `debug_mode`/`prod_template` leftovers.
2. Add a template smoke test that renders each of the 6 templates.
3. Capture screenshots for all 4 pages × 6 templates as baseline.

### Phase 1 — Foundation (tokens + colour schemes + buttons)
1. Extend `COLOR_SCHEMES` with `primary_dark`, `on_primary`; keep Gold, add Custom.
2. Add contrast/tint helpers + new tokens in `get_theme_variables`.
3. Add dark-mode overrides and `.bc-btn` variants for all 4 button styles.
4. Update `bc_theme.json` colour_scheme options if Gold/Custom change.
5. Verify each scheme on one page (visual matrix: 9 schemes × light/dark).

### Phase 2 — **Professional (first slice)**
1. `card.html`: new `.bc-card-shell` structure; section order — hero → vcf → business
   link → products → services → enquiry → share → footer → bottom nav. Replace inline
   styles with classes. Add analytics hidden inputs + `sendBeacon` payload.
2. `card/parts/hero_professional.html`: gradient band, 72px rounded-square avatar,
   name/designation/business, no duplicate contact block (contact lives in body).
3. `business/parts/hero_professional.html`: dark slate band, logo tile, tagline, stats;
   remove wave; section nav as underline tabs.
4. `business.html`: professional section head, product/service tiles, contact grid,
   footer; add stats to `business.py`.
5. `product/parts/hero_professional.html`: dark bar + split hero with gallery;
   category chip; price; outlined CTAs.
6. `product.html`: details grid (left-border tiles), section heads, footer.
7. `service`: same split hero + benefits grid + pricing block.
8. CSS: new `.bc-template-professional` card-frame / page-shell block; remove/replace
   old `.bc-hero-professional-*` rules; responsive rules for 360/390/768/1024.
9. Verify: 9 schemes × 4 pages × light/dark; keyboard focus; contrast; no inline hex.

### Phase 3 — Modern
Centered hero, 120px round avatar, pill buttons, rounded 16px cards, soft shadows;
business centered hero with gradient + rounded 32px bottom; product/service gradient
header + benefit cards + pill CTA.

### Phase 4 — Minimal
Whitespace-led, 1px dividers, square 2–4px corners, uppercase section labels,
column action buttons, row-style product list; business centered avatar + stats.

### Phase 5 — Classic
Gradient banner, overlapping avatar, decorative dividers, traditional grid,
16px radius, filled buttons.

### Phase 6 — Luxury & Creative
Blocked on design assets. Until supplied: keep current layouts, migrate to new tokens,
fix hard-coded colours, ensure no regressions.

### Phase 7 — Cross-cutting QA
- Responsive: 360, 390, 768, 1024, 1440.
- Dark mode + Yellow/Gold on-primary contrast.
- RTL-safe spacing (logical properties).
- Analytics: card_view/product_view/service_view/profile_view + click events.
- Accessibility: focus-visible, labels, alt text, reduced motion.
- Performance: single CSS file, no new JS libs; `sendBeacon` only.
- Regression: print/share preview, vCard download, QR.

---

## 5. Phase 2 file-by-file checklist (Professional)

| File | Change |
|---|---|
| `templates/pages/card/card.html` | rebuild shell, sections, analytics |
| `templates/pages/card/parts/hero_professional.html` | new hero |
| `templates/pages/business/parts/hero_professional.html` | new band + stats |
| `templates/pages/business/business.html` | section heads, tiles, footer |
| `templates/pages/business/business.py` | stats counts |
| `templates/pages/product/parts/hero_professional.html` | split hero + gallery |
| `templates/pages/product/product.html` | details grid, footer |
| `templates/pages/service/service.html` | split hero + benefits + pricing |
| `public/css/business_connect.css` | tokens, card shell, professional blocks, responsive |
| `services/theme_service.py` | scheme table + tokens (already in Phase 1) |

---

## 6. Decisions needed

1. **Gold scheme** — keep as a 9th preset, or drop it to match the 8 designs?
2. **Luxury / Creative** — supply designs, or approve the current interpretation?
3. **Card width** — designs use 420px; current token is 480px. Confirm 420px.
4. **Stats on business page** — which counts? (team members / products / services / years)
5. **Emoji vs. icon font** — designs use emoji; site already loads Font Awesome.
   Recommend Font Awesome for crisp rendering, emoji as fallback.
6. **Approval to start Phase 2** after Phase 0/1 (or Phase 0+1+2 in one branch).

---

## 7. Suggested branch/PR sequence

1. `fix/card-template-restore` — Phase 0.
2. `feat/theme-tokens-color-schemes` — Phase 1.
3. `feat/professional-redesign` — Phase 2 (card + business + product + service).
4. `feat/modern-redesign`, `feat/minimal-redesign`, `feat/classic-redesign`.
5. `feat/luxury-creative-redesign` once designs exist.

Each PR: screenshots before/after, scheme matrix, mobile + dark mode, no inline hex.
