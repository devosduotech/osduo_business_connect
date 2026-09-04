# OSDuo Business Connect v1.0.1 Release Notes

## Version 1.0.1 — Core Edition

**Release Date:** September 2026  
**Target Audience:** Small businesses and individuals (1-20 users)

---

## Overview

OSDuo Business Connect v1.0.1 is the initial production release of a Frappe Framework application that provides digital business identity, product/service showcase, lead generation, and CRM integration.

**Status:** Core functionality complete. All public web pages, analytics, CRM integration, and branding fully operational.

---

## Features

### Business Identity Management
- Create and manage business profiles with public slug
- Team member management with role-based access (Owner, Manager, Member, Marketing, CRM User)
- Business hours and social links
- Public business landing page at `/b/<slug>`
- Naming series: BIZ-.#####, BM-.#####

### Digital Business Cards
- Create digital cards for team members
- Public card pages at `/c/<slug>` (mobile-first, QR/NFC ready)
- 4 distinct templates: Modern, Professional, Minimal, Classic
- VCF download ("Add to Phone Book")
- Share via WhatsApp, email, SMS, or direct link
- QR code generation (print-ready)
- Naming series: CARD-.#####

### Product & Service Showcase
- Showcase products with galleries, pricing, and brochures
- Showcase services with benefits and descriptions
- Reusable product categories per business
- Product/service pages at `/b/<slug>/products/<product>` and `/b/<slug>/services/<service>`
- Gallery with click-to-open fullscreen, lazy loading, captions
- Naming series: PROD-.#####, SVC-.#####

### Branding & Theming
- 4 page templates (Modern, Professional, Minimal, Classic)
- 8 color scheme presets + custom palette
- 10 web font families (Inter, Roboto, Open Sans, Lato, Poppins, etc.)
- 3 font size presets (Small, Default, Large)
- 4 button styles (Filled, Outline, Rounded, Pill)
- Official OSDuo brand assets (logo, favicon, app icon, social sharing image)
- Desk sidebar branding and login page customization
- Naming series: THEME-.#####

### Lead Generation
- Enquiry capture from public forms (card, product, service pages)
- Guest can create enquiries
- Source tracking (Digital Card, Product, Service, QR, Campaign)
- Rate limiting: 10 enquiries per IP per business per hour
- CSRF protection via `allowed_referrers`
- Naming series: ENQ-.#####

### CRM Integration
- Automatic CRM Lead creation from enquiries (background job)
- Lead owner set to card owner (Digital Card → Business Member → user)
- Bidirectional status sync: CRM Lead status ↔ Enquiry status
- Custom fields on CRM Lead: business, card, product, service, enquiry, source, campaign, landing URL
- Idempotent sync (no duplicate leads)
- Failed syncs retried hourly
- Source attribution: "Business Connect"

### Analytics Dashboard
- Desk dashboard at `/app/analytics` with business selector and date range
- SVG line chart with gradient fill (visits by day)
- Summary cards: Link Visits, QR Scans, Cards, Products
- Top cards ranked by views with member names
- Recent activity with member name, device type, browser
- Enquiry pipeline: New → Ongoing → Converted → Lost
- Device type & browser tracking
- Non-blocking background event recording

### Page Section System
- Enable/disable, reorder, and control visibility of page sections
- Section types: Hero, About, Products, Services, Contact, Gallery, Custom
- Drag-and-drop ordering via sequence field

### Security & Permissions
- 7 custom roles: BC Manager, BC User, BC Viewer, BC Content, BC Analytics, BC Enquiry, BC Settings
- Centralized permission dispatcher for 9 DocTypes
- Cross-business data isolation
- Guest access for published records and enquiry creation
- Business-scoped CRM lead access

---

## URL Structure

| URL | Page |
|-----|------|
| `/b/<business>` | Business landing page |
| `/b/<business>/team/<member>` | Team member profile |
| `/b/<business>/products/<product>` | Product page |
| `/b/<business>/services/<service>` | Service page |
| `/c/<card>` | Digital Card (short QR/NFC URL) |
| `/app/analytics` | Analytics dashboard |

---

## How It Works

```
Customer scans QR code
        ↓
  Digital Card (/c/<card>)
  or Business Profile (/b/<business>)
        ↓
  Browses products, services, team
        ↓
  Submits enquiry form
        ↓
  Enquiry created → CRM Lead auto-created (background job)
        ↓
  Lead owner = card owner → Sales follow-up
        ↓
  Status sync: Lead status changes → Enquiry updated
        ↓
  Analytics tracked throughout
```

---

## Requirements

- Frappe Framework v16
- Frappe CRM
- Python 3.10+
- Node.js 18+
- MariaDB 10.3+
- Redis 6+

---

## Installation

```bash
# Get the app
bench get-app https://github.com/devosduotech/osduo_business_connect.git

# Install on site
bench --site <site-name> install-app osduo_business_connect

# Run migrations
bench --site <site-name> migrate

# Install QR code dependency
bench --site <site-name> pip install qrcode[pil]

# Build assets
bench build --app osduo_business_connect

# Restart
bench restart
```

### Deployment Notes

- `bench build` must use `--app osduo_business_connect` only (CRM build may exceed memory on small VMs)
- Roles created on install: **BC Manager**, **BC User**, **BC Viewer**
- 8 default themes auto-created (Violet, Indigo, Blue, Green, Yellow, Orange, Red + custom)
- CRM custom fields added to CRM Lead: business, card, product, service, enquiry, source, campaign, landing URL
- `allowed_referrers` must be set in site_config.json for production CSRF protection

---

## Configuration

### 1. Create Business
1. Go to Business Connect > Business
2. Create a new business with slug and contact information
3. Owner membership is automatically created via `after_insert` hook

### 2. Add Team Members
1. Open the business
2. Go to Members tab
3. Add team members with appropriate roles

### 3. Create Digital Cards
1. Go to Digital Card
2. Create cards for team members
3. Add links, bio, and social profiles

### 4. Add Products/Services
1. Go to Showcase Product or Showcase Service
2. Create products/services with descriptions and galleries
3. Set pricing and enquiry options

### 5. Configure Theme
1. Go to BC Theme
2. Select template, colors, fonts, and button style
3. Link theme to business

### 6. Publish
1. Set business status to "Published"
2. Enable "Public Profile" toggle
3. Share the QR code or link

---

## Architecture

- **15 DocTypes** across 6 modules (Business, Card, Showcase, Analytics, Enquiry, CRM Integration)
- **Core logic separation** — Business and Enquiry classes in `core.py` to avoid Python import conflicts
- **Permission separation** — Centralized dispatcher in `permissions/__init__.py`
- **Background jobs** — CRM sync via `frappe.enqueue` with retry logic
- **Theme service** — Guest-safe theme resolution via `frappe.db.get_value()`

---

## Testing

```bash
cd osduo_business_connect
python3 -m unittest discover -s tests -p "test_*.py" -v

# 103 tests across 9 files
```

---

## Upgrade from v1.0.0

```bash
bench --site <site-name> migrate
bench --site <site-name> execute osduo_business_connect.install.after_install
bench build --app osduo_business_connect
bench restart
```

---

## Known Issues

None at release.

---

## Support

- Repository: https://github.com/devosduotech/osduo_business_connect
- Issues: https://github.com/devosduotech/osduo_business_connect/issues

---

## License

MIT License
