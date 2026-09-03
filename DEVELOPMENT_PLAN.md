# Development Plan

## Current Status: v1.4.0 — Security Hardening & Status Alignment Complete

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
- [x] Analytics desk page (`/osduo_business_connect/analytics`)
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

### v1.4.0 — Security Hardening & Status Alignment
- [x] P0-1: Permission hooks restored for 9 DocTypes via centralized dispatcher
- [x] P0-2: Route monkey patch removed (native Frappe v16 routing)
- [x] P0-3: Enquiry Guest create permission removed (whitelisted API only)
- [x] P0-4: Rate limiting — 10 enquiries per IP per business per hour
- [x] P0-5: CRM sync idempotent (duplicate enqueue removed)
- [x] P0-6: Service query fixed (removed nonexistent price/currency)
- [x] CSRF fix: `allowed_referrers` replaces `ignore_csrf` (production-safe)
- [x] Analytics context auto-populated: session_id, landing_url, referrer
- [x] Enquiry status aligned 1:1 with CRM Lead statuses
- [x] CRM hook maps statuses bidirectionally (Lead ↔ Enquiry)
- [x] Enquiry forms added to product and service pages
- [x] CRM sync no longer changes enquiry status (status driven by Lead)
- [x] Enquiry stats updated: New, Ongoing, Converted, Lost pipeline
- [x] Dead route modules removed (public_route.py, product_route.py, service_route.py)

---

## Pending

### Verification
- [x] Analytics events recording — verify events appear after page visits
- [x] CRM Lead owner assignment — verify lead goes to card owner
- [x] CRM status sync — verify Enquiry updates when Lead status changes
- [x] End-to-end UAT on VM (all features)

### Deployment Notes
- [x] `bench build` uses `--app osduo_business_connect` only (CRM build exceeds VM memory)
- [x] `bench pip install qrcode[pil]` required for QR code generation
- [x] `allowed_referrers` must be set in site_config.json (replaces `ignore_csrf`)
- [x] After deploy: `bench migrate` needed to apply new Enquiry status options

### Future Enhancements
- [ ] Email notification templates (enquiry confirmation, CRM assignment)
- [ ] SEO metadata management (auto-generated meta tags)
- [ ] Multi-business SaaS billing
- [ ] Custom domain support
- [ ] Testimonials section (currently "Coming soon")

---

## Phase 2 — Planned

### Enquiry Status: Dynamic CRM Lead Status Sync
**Priority:** High
**Status:** Planned

Currently, Enquiry status options are hardcoded in the DocType JSON:
```
New, Contacted, Nurture, Qualified, Converted, Unqualified, Junk, Closed, Spam
```

CRM Lead uses a **Link field** to `CRM Lead Status` DocType — users can add, remove, rename, or reorder statuses as per their business requirements.

**Phase 2 goal:** Make Enquiry status dynamically pick up values from `CRM Lead Status` DocType so that:
1. When an admin adds/removes/renames a CRM Lead Status, Enquiry status options reflect the change automatically
2. Enquiry status is always in sync with CRM Lead status (no manual maintenance)
3. Form submission creates Enquiry with `status = "New"` (always)
4. Status updates propagate from CRM Lead → Enquiry via the `on_crm_lead_update` hook

**Implementation approach:**
- Replace hardcoded `status.options` in `enquiry.json` with a dynamic approach
- Use a `before_render` or `validate` hook to populate status options from `CRM Lead Status` records
- Or: keep a static fallback list but override with CRM Lead Status values at runtime
- Keep `Closed` and `Spam` as Enquiry-only statuses (not in CRM Lead)

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
/analytics                       → Analytics desk dashboard
```
