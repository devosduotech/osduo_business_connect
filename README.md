# OSDuo Business Connect

Digital business identity, product/service showcase, lead generation, and CRM integration for individuals and small businesses.

## Requirements

- Frappe Framework v16
- Frappe CRM
- Python: `qrcode[pil]` (for QR code generation)

## Installation

```bash
bench get-app https://github.com/devosduotech/osduo_business_connect.git
bench --site <site-name> migrate
bench --site <site-name> pip install qrcode[pil]
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
| `/app/analytics` | Analytics desk dashboard |

## Features

### 4 Distinct Card Templates
- **Modern:** Centered, rounded avatar with shadow, pill buttons
- **Professional:** Colored header band, horizontal layout, outlined buttons
- **Minimal:** No background, uppercase labels, thin borders, square buttons
- **Classic:** Gradient banner, avatar overlapping edge, decorative dividers

### Theme System
- Template layout (Modern/Professional/Minimal/Classic)
- 7 color scheme presets + Custom with full color control
- 10 web font families (Inter, Roboto, Open Sans, Lato, Poppins, etc.)
- 3 font size presets (Small/Default/Large)
- 4 button styles (Filled/Outline/Rounded/Pill)

### Digital Card Features
- VCF download ("Add to Phone Book")
- QR code generation
- Contact details (phone/email/WhatsApp/website)
- Social links
- Products & services showcase
- Business address
- Share section (copy link, WhatsApp, SMS, email)

### Business Landing Page
- Page Section system (enabled/disabled, ordered, visibility control)
- Hero, About, Products, Services, Contact, Gallery, Custom sections
- Product & service cards with links
- Contact grid with phone/email/website/address
- Social links

### Product & Service Pages
- Description section
- Location field (Google Maps link)
- Product categories (reusable per business)
- Gallery — 4-col desktop, 2-col mobile thumbnails, click-to-open full image
- Gallery sorted by sort_order, captions, alt text, lazy loading
- Video, brochure
- "About Business" section with description & address

### Analytics
- Desk page at `/app/analytics` (business selector, date range)
- SVG line chart with gradient fill (visits by day)
- Summary cards: Link Visits, QR Scans, Cards, Products
- Top cards with member name (not card number)
- Recent activity with member name, device, browser
- Event names capitalized (Card View, Profile View, etc.)
- Enquiry pipeline: New → Converted (manual + CRM sync)
- Device type & browser tracking
- Event recording on all public pages (non-blocking background jobs)

### CRM Integration
```
Enquiry → on_update() → Background sync → CRM Lead
    → Lead owner = card owner (Digital Card → Business Member → user)
    → Status sync: any CRM Lead status ≠ New → Enquiry "Converted"
    → Custom fields: business, card, product, service, enquiry
    → Source: "Business Connect"
    → Failed syncs retried hourly
```

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
│   ├── public_api.py      # Public card API + VCF download
│   └── doctype/
│       ├── digital_card/
│       └── digital_card_link/
├── showcase/              # Product/service showcase + themes
│   └── doctype/
│       ├── showcase_product/
│       ├── showcase_service/
│       ├── product_category/
│       ├── page_section/
│       ├── theme/
│       ├── product_gallery_item/
│       └── service_benefit/
├── analytics/             # Engagement analytics
│   ├── analytics_service.py
│   ├── page/
│   │   └── analytics/      # Desk page (JS + HTML)
│   └── doctype/
│       └── engagement_event/
├── enquiry/               # Lead generation
│   ├── core.py            # Enquiry class
│   ├── enquiry_service.py
│   ├── public_enquiry_api.py
│   └── doctype/
│       └── enquiry/
├── crm_integration/       # Frappe CRM integration
│   ├── lead_mapper.py
│   ├── crm_sync.py
│   └── crm_permissions.py
├── services/              # Shared services
│   ├── theme_service.py   # Theme resolution + CSS vars
│   ├── qr_service.py      # QR code generation
│   ├── vcard_service.py   # vCard generation
│   └── scheduler.py
├── pages/                 # Desk pages
│   └── analytics.py       # Analytics dashboard API
├── permissions/
├── utils/
├── patches/               # Frappe v16 bug fixes
└── templates/
    ├── base.html
    └── pages/
        ├── business/      # Business landing page
        ├── product/       # Product page
        ├── service/       # Service page
        └── card/          # Digital card + team member pages
```

## DocTypes (15 total)

| DocType | Module | Purpose |
|---------|--------|---------|
| Business | business | Root ownership record |
| Business Member | business | Team members with roles |
| Digital Card | card | Public digital business card |
| Showcase Product | showcase | Product listings |
| Showcase Service | showcase | Service listings |
| Theme | showcase | Page themes (template + colors + fonts) |
| Page Section | showcase | Custom page sections (ordered, toggleable) |
| Product Category | showcase | Reusable product categories |
| Enquiry | enquiry | Public enquiry submissions |
| Engagement Event | analytics | View/click/share tracking |
| Business Social Link | business | Social media links (child) |
| Business Hour | business | Operating hours (child) |
| Digital Card Link | card | Card social links (child) |
| Product Gallery Item | showcase | Product gallery images (child) |
| Service Benefit | showcase | Service benefits list (child) |

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
bench --site business.local pip install qrcode[pil]
bench build --app osduo_business_connect
bench --site business.local clear-website-cache
bench restart
```

## License

MIT
