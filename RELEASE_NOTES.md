# OSDuo Business Connect v1.0.1 Release Notes

## Version 1.0.1 - Core Edition

**Release Date:** September 2026  
**Target Audience:** Small businesses and individuals (1-20 users)

---

## Overview

OSDuo Business Connect v1.0.1 is the initial release of a Frappe Framework application that provides digital business identity, product/service showcase, lead generation, and CRM integration.

**Status:** Core functionality complete. Public web pages deferred due to Frappe v16 routing issues.

---

## Features

### Business Identity Management ✓
- Create and manage business profiles
- Team member management with role-based access (Owner, Manager, Member, Marketing)
- Business hours and social links
- Naming series: BIZ-.#####, BM-.#####

### Digital Business Cards ✓
- Create digital cards for team members
- Public card pages at `/c/<slug>` (routing issue pending)
- Share via WhatsApp, email, or direct link
- Naming series: CARD-.#####

### Product & Service Showcase ✓
- Showcase products with galleries and pricing
- Showcase services with benefits
- Naming series: PROD-.#####, SVC-.#####

### Branding & Theming ✓
- Customizable themes (colors, fonts, styles)
- Naming series: THM-.#####

### Lead Generation ✓
- Enquiry capture from public forms
- Guest can create enquiries
- Source tracking (Digital Card, Product, Service, QR, Campaign)
- Naming series: ENQ-.#####

### CRM Integration ✓
- Automatic CRM Lead creation from enquiries
- Background synchronization with retry
- Business attribution on leads
- Multi-business lead isolation

### Analytics ✓
- Engagement event tracking
- Page views, clicks, and enquiries
- Naming series: ENG-.#####

---

## Requirements

- Frappe Framework v16
- Frappe CRM
- Python 3.14+
- Node.js 24+
- MariaDB 11.8+
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
```

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
3. Add links and bio

### 4. Add Products/Services
1. Go to Showcase Product or Showcase Service
2. Create products/services with descriptions
3. Set pricing and enquiry options

### 5. Configure Theme
1. Go to Theme
2. Create a theme with colors and style
3. Activate the theme

---

## Security

- Role-based access control with 7 custom roles
- Cross-business data isolation
- Guest can read published records
- Guest can create enquiries (public forms)
- Web controllers use `frappe.db.get_value` to bypass permission hooks

---

## Known Issues

### Web Page Routing (Critical)
Public web pages at `/b/<slug>` and `/c/<slug>` return 404 despite correct template and controller files.

**Root cause:** Frappe v16's `website_route_rules` may not work as documented. The routes are defined but not resolving.

**Workaround:** Use desk UI for all operations. Public pages deferred to v1.0.2.

### Supervisor Group Name
`bench restart` fails because supervisor group is named `frappe:` not `frappe`. Use `bench restart` command instead of supervisorctl directly.

---

## Architecture Decisions

1. **No `doc_events`** — Frappe auto-calls controller methods for own DocTypes
2. **Naming series** — All DocTypes use `naming_series` field with single defaults
3. **Permission separation** — Custom permission functions in `permissions/__init__.py`
4. **Core logic separation** — Business and Enquiry classes in `core.py` files to avoid Python import conflicts when module name == doctype name == file name
5. **Guest access** — Web controllers use `frappe.db.get_value` to bypass permission hooks

---

## Upgrading

### From v1.0.0
```bash
bench --site <site-name> migrate
bench --site <site-name> execute osduo_business_connect.install.after_install
```

---

## Support

- Repository: https://github.com/devosduotech/osduo_business_connect
- Issues: https://github.com/devosduotech/osduo_business_connect/issues

---

## License

MIT License
