# OSDuo Business Connect

Digital business identity, product/service showcase, lead generation, and CRM integration for individuals and small businesses.

## Requirements

- Frappe Framework v16
- Frappe CRM

## Installation

```bash
bench get-app https://github.com/devosduotech/osduo_business_connect.git
bench --site <site-name> migrate
bench build --app osduo_business_connect
bench restart
```

## URL Hierarchy

| URL | Page |
|-----|------|
| `/b/<business>` | Business landing page |
| `/b/<business>/team/<member>` | Team member / person page |
| `/b/<business>/products/<product>` | Product page |
| `/b/<business>/services/<service>` | Service page |
| `/c/<card>` | Digital Card (short QR/NFC URL) |

## Module Structure

```
osduo_business_connect/
├── business/              # Business ownership and membership
│   ├── core.py            # Business class + helper functions
│   └── doctype/
│       ├── business/
│       ├── business_member/
│       ├── business_social_link/
│       └── business_hour/
├── card/                  # Digital business cards
│   ├── public_api.py      # Public card API
│   └── doctype/
│       ├── digital_card/
│       └── digital_card_link/
├── showcase/              # Product/service showcase + themes
│   ├── service_route.py   # Service web route
│   ├── product_route.py   # Product web route
│   └── doctype/
│       ├── showcase_product/
│       ├── showcase_service/
│       ├── page_section/
│       └── theme/
├── analytics/             # Engagement analytics
│   └── doctype/
│       └── engagement_event/
├── enquiry/               # Lead generation
│   ├── core.py            # Enquiry class
│   ├── enquiry_service.py # Enquiry business logic
│   ├── public_enquiry_api.py
│   ├── enquiry_webhook.py
│   └── doctype/
│       └── enquiry/
├── crm_integration/       # Frappe CRM integration
│   ├── lead_mapper.py     # Enquiry → CRM Lead mapping
│   ├── crm_sync.py        # Background sync enqueue
│   └── crm_permissions.py # CRM permission isolation
├── services/              # Shared services
│   ├── theme_service.py   # Theme resolution + CSS vars
│   ├── qr_service.py      # QR code generation
│   ├── vcard_service.py   # vCard generation
│   └── scheduler.py       # Background task scheduler
├── permissions/           # Centralized permission dispatcher
├── utils/                 # Utility functions
├── patches/               # Frappe v16 bug fixes
└── templates/
    ├── base.html          # Minimal HTML base template
    └── pages/
        ├── business/      # Business landing page
        ├── product/       # Product page
        ├── service/       # Service page
        └── card/          # Digital card page
```

## DocTypes (14 total)

### Core
| DocType | Module | Purpose |
|---------|--------|---------|
| Business | business | Root ownership record |
| Business Member | business | Team members with roles |
| Digital Card | card | Public digital business card |
| Showcase Product | showcase | Product listings |
| Showcase Service | showcase | Service listings |
| Theme | theme | Page themes (template + colors) |
| Page Section | showcase | Custom page sections |
| Enquiry | enquiry | Public enquiry submissions |
| Engagement Event | analytics | View/click/share tracking |

### Child Tables
| DocType | Parent | Purpose |
|---------|--------|---------|
| Business Social Link | Business | Social media links |
| Business Hour | Business | Operating hours |
| Digital Card Link | Digital Card | Card social links |

## Theme System

**Templates:** Modern, Professional, Minimal, Classic — each with distinct hero layout via `{% include %}` partials.

**Color Schemes:** Violet, Indigo, Blue, Green, Yellow, Orange, Red, Custom — each defines primary/secondary/accent colors.

Themes supply CSS custom properties via inline style on `.bc-page`. Static CSS in `public/css/business_connect.css`.

## CRM Integration

```
Enquiry created → on_update() → crm_sync.enqueue_sync()
    → Background worker: lead_mapper.create_lead_from_enquiry()
        → Creates CRM Lead with custom fields
        → Updates Enquiry status: "New" → "Synced"
        → On failure: "Sync Failed" (retried hourly)
```

**Custom fields on CRM Lead:** `osduo_business`, `osduo_card`, `osduo_product`, `osduo_service`, `osduo_enquiry`, `osduo_campaign`, `osduo_source`, `osduo_landing_url`

## Testing

```bash
# Run on dev machine (no frappe required)
cd osduo_business_connect
python3 -m unittest discover -s tests -p "test_*.py" -v

# 109 tests across 9 files
```

## Deployment

```bash
cd ~/frappe-bench
rm -rf apps/osduo_business_connect
bench get-app https://github.com/devosduotech/osduo_business_connect.git --branch develop
bench --site business.local migrate
bench build --app osduo_business_connect
bench --site business.local clear-website-cache
bench restart
```

## License

MIT
