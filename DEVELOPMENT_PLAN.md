# Development Plan

## Current Status: v1.0.1 — Core Edition Release Ready

**Date:** September 2026  
**Branch:** develop  
**VM:** 192.168.122.49 (business.local)

---

## Completed

### Core Infrastructure
- [x] Full project structure (15 DocTypes, 7 roles)
- [x] GitHub repository with develop/main branches
- [x] `.gitignore` configuration
- [x] `pyproject.toml` with setuptools
- [x] `install.py` with built-in themes and DocType checks
- [x] Core logic separation (core.py pattern)

### DocTypes
- [x] Business (BIZ-.#####)
- [x] Business Member (BM-.#####)
- [x] Digital Card (CARD-.#####)
- [x] Showcase Product (PROD-.#####)
- [x] Showcase Service (SVC-.#####)
- [x] Theme (THEME-.#####) — template, color scheme, font, button style
- [x] Page Section (SEC-.#####) — visibility, sequence, section types, Gallery config
- [x] Product Category (CAT-.#####) — reusable categories per business
- [x] Enquiry (ENQ-.#####)
- [x] Engagement Event (EVT-.#####)
- [x] Business Social Link, Business Hour, Digital Card Link, Product Gallery Item, Service Benefit, etc. (child tables)

### Web Pages
- [x] Business landing page (`/b/<slug>`)
- [x] Digital card page (`/c/<slug>`)
- [x] Product page (`/b/<slug>/products/<product>`)
- [x] Service page (`/b/<slug>/services/<service>`)
- [x] Team member page (`/b/<slug>/team/<member>`)
- [x] Analytics web page (`/analytics`) with sidebar navigation
- [x] Monkey-patch for Frappe v16 routing bug
- [x] Guest access without has_permission hook

### Theme System
- [x] Template variants (Modern/Professional/Minimal/Classic) — **truly distinct layouts**
  - Modern: centered, rounded avatar with shadow, pill buttons
  - Professional: colored header band, horizontal layout, outlined buttons
  - Minimal: no background, uppercase labels, thin borders, square buttons
  - Classic: gradient banner, avatar overlapping edge, decorative dividers
- [x] Color scheme presets (Violet/Indigo/Blue/Green/Yellow/Orange/Red)
- [x] Custom color scheme with background + font color pickers
- [x] Font family Select (10 web fonts: Inter, Roboto, Open Sans, Lato, Poppins, etc.)
- [x] Font size preset (Small/Default/Large → 14px/16px/18px)
- [x] Button style (Filled/Outline/Rounded/Pill)
- [x] CSS custom properties generation (--bc-font-family, --bc-font-size, etc.)

### Card Page Redesign (Tocard.in-inspired)
- [x] Horizontal action buttons (Call/WhatsApp/Email/Website)
- [x] VCF download ("Add to Phone Book")
- [x] Section separators (stripe dividers)
- [x] Fixed bottom navigation (Home/Products/Enquiry)
- [x] Share section (copy link, QR code, WhatsApp/SMS/Email)
- [x] Business link section with address
- [x] Contact details (phone/email) below bio
- [x] Show products/services sections on card

### Business Page
- [x] Hero with wave/stripe dividers
- [x] Navigation merged into hero
- [x] Product/service cards with "View" links
- [x] Contact grid (2-column)
- [x] Cover image max-height constraints
- [x] Social links section
- [x] Page Section visibility/order configuration (enabled, sequence, visibility)

### Product & Service Pages
- [x] "Description" section (renamed from "About This Product")
- [x] Location field (Google Maps link) with "View on Map" button
- [x] Product Category (reusable Link DocType, per-business or global)
- [x] "About Business" section with description, address, website, contact buttons
- [x] Video, Brochure sections
- [x] Gallery — 4-col desktop, 2-col mobile, thumbnails with click-to-open
- [x] Gallery sorted by sort_order, captions, alt text, lazy loading
- [x] Gallery reusable partial (`parts/gallery.html`) shared across product/service
- [x] Gallery CSS classes (`.bc-gallery-grid`, `.bc-gallery-img`, etc.)
- [x] Service DocType now has gallery field (Table: Product Gallery Item)
- [x] Business page gallery section — shows all product/service gallery images

### Analytics
- [x] Engagement Event DocType (11 event types)
- [x] `analytics_service.py` — record_engagement, get_business_analytics, get_top_cards
- [x] `enquiry_service.py` — get_enquiry_stats (total/new/synced/converted/by_source)
- [x] Desk dashboard (`/app/analytics`) with business selector, date range
- [x] Line chart (SVG with gradient fill, grid lines, dots)
- [x] Summary cards with colored left borders
- [x] Top cards showing member name (joined via Digital Card → Business Member)
- [x] Recent activity with member name
- [x] Event names capitalized (Card View, Profile View, etc.)
- [x] Enquiry pipeline counts manual Converted status
- [x] Enquiry pipeline counts CRM Lead Converted status
- [x] Event recording wired into all 4 web controllers (background, non-blocking)

### CRM Integration
- [x] Lead mapper (enquiry → CRM Lead)
- [x] CRM permissions (business-scoped leads)
- [x] Custom fields on CRM Lead
- [x] Retry logic for failed syncs
- [x] `on_update()` trigger on Enquiry DocType
- [x] `crm_sync.py` background job module
- [x] CRM Lead owner set to card owner (Digital Card → Business Member → user)
- [x] CRM Lead status sync back to Enquiry (any status ≠ New → Converted)
- [x] `doc_events` hook for CRM Lead on_update

### CSS Architecture
- [x] Static CSS in `public/css/business_connect.css`
- [x] Width token system (--bc-max-width, --bc-card-width, etc.)
- [x] Responsive breakpoints (768px, 480px)
- [x] Template-specific hero styles (4 variants with distinct layouts)
- [x] `bc-` namespace prefix
- [x] Mobile action bar

### Test Suite
- [x] 109 tests across 9 files (all passing)
- [x] Structural checks (no frappe required)
- [x] DocType JSON validation
- [x] Controller/module existence checks

### Recent Fixes & Improvements
- [x] Digital Card version conflict fix (removed self.reload from on_update)
- [x] Card hero templates made truly distinct (4 different layouts)
- [x] Removed confusing card_style field from Theme
- [x] Custom color scheme with background + font color pickers
- [x] Font family Select (10 web fonts) + font size preset
- [x] Product page "About This Product" → "Description"
- [x] Location field (Google Maps link) on products and services
- [x] Product Category DocType (reusable, per-business)
- [x] Business address shown on all public pages
- [x] Business description shown on product/service pages
- [x] `qrcode[pil]` added to pyproject.toml and docs
- [x] Analytics desk page with Page record patch
- [x] SVG line chart with gradient fill
- [x] Top cards show member name (not card number)
- [x] Event names capitalized
- [x] Enquiry pipeline counts both manual and CRM conversions
- [x] CRM Lead owner set to card owner
- [x] CRM status sync: any Lead status ≠ New → Enquiry Converted
- [x] `frappe.db.sql` replaces `frappe.get_all` for GROUP BY queries (Frappe v16)
- [x] Gallery thumbnails — 4 columns desktop, 2 columns mobile
- [x] Gallery click-to-open full image in new tab
- [x] Gallery aligned with content width (`.bc-container`)
- [x] Gallery sorted by sort_order field
- [x] Gallery captions and alt_text displayed
- [x] Gallery lazy loading
- [x] Gallery reusable partial template
- [x] Service DocType gallery field added
- [x] Business page gallery section (replaced "Coming soon" stub)
- [x] API gallery serialization includes sort_order
- [x] API service serialization includes gallery

### v1.0.1 — UI Fixes & Release Prep
- [x] Service page: benefits field name fix (`benefit` → `title`)
- [x] Service page: benefits description display (title + description)
- [x] Service page: gallery heading "Gallery" (not service name)
- [x] Product page: gallery heading "Gallery" (not product name)
- [x] Service page: "About This Service" → generic "About"
- [x] All section headings made generic (About, Benefits, Gallery, Location, Video, Contact)
- [x] Business DocType: `show_about_in_product_page` checkbox (default=1)
- [x] Business DocType: `show_about_in_service_page` checkbox (default=1)
- [x] Product/service pages: About Business section wrapped in conditional
- [x] `get_public_business_by_slug()` fetches both visibility flags
- [x] Gallery section removed from business page (images come from products/services)
- [x] `_get_gallery_images()` controller function removed from business.py
- [x] Category field added to Showcase Service (links to Product Category)
- [x] Service search_fields includes category
- [x] Analytics dashboard converted from desk page to web page at `/analytics`
- [x] Analytics: sidebar navigation, stat cards, bar chart, events, pipeline, recent activity
- [x] CSRF token embedded via `<meta>` tag in bc_base.html for web page API calls
- [x] Analytics API endpoints: `allow_guest=True` for web page access
- [x] Social link icons: `icon_class` field on Business Social Link and Digital Card Link
- [x] Social link icons: Font Awesome 6.5.1 CDN loaded in bc_base.html
- [x] Social link icons: auto-set server-side in `Business.before_save()` and `DigitalCard.before_save()`
- [x] Social link URL hints: static reference showing all platform formats
- [x] Footer link: "Powered by OSDuo Business Connect" → `https://connect.osduotech.com`
- [x] Footer link added to all 5 page templates (business, card, product, service, team_member)
- [x] Duplicate social links removed from card.html body (only hero partial renders them)
- [x] QR code removed from all 4 hero partials (modern, professional, minimal, classic)
- [x] Label field removed from Business Social Link (unused — card uses label, business uses platform)
- [x] `frappe.db.commit()` cleanup from business/core.py and crm_lead_hook.py

### v1.0.1 — Audit Fixes (Priority)
- [x] C-3: XSS sanitization for rich text fields (sanitize_rich_text utility)
- [x] C-5: Generic error messages in enquiry controllers (no stack traces to users)
- [x] M-1: Analytics event deduplication via tracking.py module
- [x] M-8: CRM sync logging via log_error instead of print
- [x] L-8: Test assertion fix (_test_uat_old.py result["status"] == "success")

---

## Pending

### Phase 1 — v1.0.1 Core Edition (Current Release)

| # | Task | Status |
|---|------|--------|
| 1 | VM smoke test | ✅ Done |
| 2 | User manual creation | ✅ Done (`docs/USER_MANUAL.md`) |
| 3 | Screenshot capture (43 images) | ⏳ In Progress (mockups in `docs/images/mockup/`) |
| 4 | Social link icons | ✅ Done (Font Awesome + auto-set) |
| 5 | Footer link | ✅ Done (connect.osduotech.com) |
| 6 | Service page benefits fix | ✅ Done (title + description) |
| 7 | Generic section headings | ✅ Done |
| 8 | About Business visibility toggles | ✅ Done (checkboxes on Business) |
| 9 | Gallery removed from business page | ✅ Done |
| 10 | Category field on services | ✅ Done |
| 11 | Analytics dashboard UI | ✅ Done (web page with sidebar) |

### Phase 2 — v1.0.2 Theme & UX (Next Release)

| # | Feature | Priority | Details |
|---|---------|----------|---------|
| 1 | Theme Design System v2 | High | Remove inline CSS, design tokens, typography/spacing scales |
| 2 | Save Contact as primary CTA | High | VCF download as first action on digital cards |
| 3 | Strengthen Business Profile hero | High | Company identity block with logo, tagline, location |
| 4 | Product image dominance | High | Image → Name → Description → Price → CTA hierarchy |
| 5 | Email notification templates | Medium | Enquiry confirmation, CRM assignment alerts |
| 6 | SEO metadata management | Medium | Auto-generated meta tags for public pages |
| 7 | Configuration simplification | Medium | Expose only Theme + Color + Logo + Cover |
| 8 | Testimonials section | Low | Customer testimonials on business page |
| 9 | Multi-business SaaS billing | Future | Subscription billing for multiple businesses |
| 10 | Custom domain support | Future | Custom domain mapping per business |

See `docs/THEME_DESIGN_SYSTEM_V2.md` for detailed theme requirements.

---

## Phase 3 — Theme Design System v2 (Planned for v1.0.2)

**Priority:** High  
**Status:** Planned — captured from design review (Sep 2026)

### Overview

Move from "four HTML designs" to "one coherent Business Connect design system with four visual personalities."

### P0 — Design System Foundation

1. **Remove inline CSS** — Replace all `style="..."` with theme CSS classes
   - `style="border-radius:0;"` → `class="bc-btn bc-btn-square"`
   - `style="background:var(--bc-primary);"` → `class="bc-nav-primary"`
2. **Establish theme CSS variables** — Separate Theme (layout/typography) from Color Scheme (colors)
   - Theme controls: layout, typography, spacing, cards, navigation, hero, button shape, visual hierarchy
   - Color Scheme controls: primary, secondary, accent, background, text, borders
3. **Typography scale** — Common type scale across all themes
4. **Spacing scale** — Consistent spacing tokens
5. **Button system** — Theme-driven button styles (not user-configurable)
6. **Card system** — Consistent card components

### P1 — Digital Card Improvements

1. **Save Contact as primary CTA** — VCF download should be the first action, not buried
   - Primary: Save Contact
   - Secondary: WhatsApp · Call · Email
2. **Improve mobile-first layout** — Card optimized for 375px viewport
3. **Make four themes more distinctive:**
   - Modern: Contemporary, digital, rounded, gradient
   - Professional: Corporate, structured, restrained, strong typography
   - Minimal: Whitespace, typography, almost no decoration
   - Classic: Traditional, elegant, framed sections, stronger typography
4. **Improve social/contact presentation**

### P1 — Business Profile Improvements

1. **Strengthen company identity hero** — Top section should communicate "This is the company's digital identity"
   ```
   COVER IMAGE / BRAND
   [ LOGO ]
   Company Name
   Tagline / Industry
   Location
   [ WhatsApp ] [ Call ] [ Send Enquiry ]
   ```
2. **Improve product/service cards** — More visual, less list-like
3. **Add business facts/highlights** — Team size, products, customers, years
4. **Improve mobile navigation**
5. **Make Modern/Professional more premium**

### P1 — Product/Service Improvements

1. **Product image should dominate** — Hierarchy: Image → Name → Description → Price → CTA
2. **Improve enquiry CTA** — More prominent, clearer action
3. **Price/contact-pricing hierarchy** — Clearer visual treatment
4. **Improve gallery** — Better lightbox, captions, navigation
5. **Add related products/services section**

### P2 — Configuration Simplification

Expose only:
```
Theme        [ Modern ▼ ]
Color Scheme [ Blue ▼ ]
Logo         [ Upload ]
Cover Image  [ Upload ]
Custom Brand [ Optional ]
```

Not: button border, shadow, typography, spacing, etc.

### Theme Scores (from review)

| Theme | Card | Business | Product |
|-------|------|----------|---------|
| Modern | 9/10 | 9/10 | 8.5/10 |
| Professional | 9/10 | 9/10 | 9/10 |
| Minimal | 8.5/10 | 8/10 | 8/10 |
| Classic | 7.5/10 | 7.5/10 | 7.5/10 |

### Recommended Default Combinations

- **Modern + Blue** — default
- **Professional + Blue** — recommended for B2B/industrial
- **Minimal + Custom** — professionals/personal branding
- **Classic + Custom** — traditional businesses

### Key Principle

> Four is enough. Make existing four genuinely distinctive. Let Color Scheme + Logo + Cover Image + Content create customer-specific identity. This gives hundreds of visual combinations without hundreds of templates.

---

## Phase 2 — Completed

### Enquiry Status: Dynamic CRM Lead Status Sync
**Priority:** High  
**Status:** ✅ Completed

Enquiry status options are hardcoded in the DocType JSON:
```
New, Contacted, Nurture, Qualified, Converted, Unqualified, Junk, Closed, Spam
```

CRM Lead uses a **Link field** to `CRM Lead Status` DocType — users can add, remove, rename, or reorder statuses as per their business requirements.

**Implementation:**
- `crm_lead_hook.py` maps CRM Lead status → Enquiry status bidirectionally
- `LEAD_TO_ENQUIRY_STATUS` dict provides 1:1 mapping (7 statuses)
- `on_crm_lead_update()` hook triggers on CRM Lead on_update
- Status changes propagate from CRM Lead → Enquiry automatically
- Enquiry-only statuses (Closed, Spam) preserved for internal use

---

## Phase 3 — v1.0.2 Audit Fixes (Pending)

### Critical
- [ ] C-1: Implement proper webhook API key validation (enquiry_webhook.py)
- [ ] C-2: Implement actual rate limiting for webhook endpoint (enquiry_webhook.py)
- [ ] C-4: Validate theme CSS variables against strict hex regex (theme_service.py)

### High
- [ ] H-1: Fix N+1 query in business page gallery loading (business.py)
- [ ] H-2: Fix N+1 query in showcase public API serialization (public_api.py)
- [ ] H-3: Lazy-generate vCard on download, not on every page load (card.py)
- [ ] H-4: Remove or fix dead central permission dispatcher (permissions/__init__.py)
- [ ] H-5: Add rate limiting to submit_enquiry_page.py web controller
- [ ] H-6: Validate `source` parameter against allowed values (public_enquiry_api.py)
- [ ] H-7: Fix rate limit race condition with atomic incr() (public_enquiry_api.py)

### Medium
- [ ] M-2: Integrate or remove unused security utility functions (utils/security.py)
- [ ] M-3: Integrate or remove unused webhook functions (enquiry_webhook.py)
- [ ] M-4: Integrate or remove unused enquiry API functions (public_enquiry_api.py)
- [ ] M-5: Wire apply_branding_settings() into install hooks or remove (install.py)
- [ ] M-6: Complete CRM-Enquiry status mapping for all statuses (crm_lead_hook.py)
- [ ] M-7: Add consistent Administrator checks across permission modules
- [ ] M-9: Batch install.py commits for faster/atomic installation
- [ ] M-10: Optimize enquiry stats to single COUNT query (enquiry_service.py)
- [ ] M-11: Validate source values in enquiry_service.py create_enquiry()

### Low
- [ ] L-1: Replace MD5 with SHA-256 for session IDs (analytics_service.py)
- [ ] L-2: Move `import re` to module level in 7 files
- [ ] L-3: Remove unused imports from child DocType stubs
- [ ] L-4: Remove empty scheduler placeholders or add actual tasks
- [ ] L-5: Add vCard special character escaping per RFC 2426
- [ ] L-6: Add configurable consent enforcement for GDPR compliance
- [ ] L-7: Add index:1 to frequently queried fields in DocType JSONs

### Config
- [ ] Verify required_apps = ["crm"] vs "frappe_crm" (hooks.py)
- [ ] Add "OSDuo Support" role to create_default_roles() (install.py)
- [ ] Add qrcode[pil] to requirements.txt
- [ ] Create LICENSE file at project root
- [ ] Add version prefix to patches.txt
- [ ] Fix __all__ in crm_integration/__init__.py and analytics/__init__.py

---

## Deployment Commands

### Standard Deploy
```bash
cd ~/frappe-bench
rm -rf apps/osduo_business_connect
bench get-app https://github.com/devosduotech/osduo_business_connect.git --branch develop
bench --site business.local migrate
bench --site business.local pip install qrcode[pil]
bench build --app osduo_business_connect
bench --site business.local clear-website-cache
bench restart
```

### Run Tests (on dev machine)
```bash
cd osduo_business_connect
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## VM Access

- **IP:** 192.168.122.49
- **User:** karthic
- **Bench:** ~/frappe-bench
- **Site:** business.local
- **Desk:** http://192.168.122.49:8000/desk
- **Public pages:** http://192.168.122.49:8000/b/osduo, http://192.168.122.49:8000/c/<card-slug>

---

## URL Hierarchy

```
/b/<business>                    → Business landing page
/b/<business>/team/<member>      → Team member / person page
/b/<business>/products/<product> → Product page
/b/<business>/services/<service> → Service page
/c/<card>                        → Digital Card (short QR/NFC URL)
/analytics                       → Analytics dashboard (requires login)
```
