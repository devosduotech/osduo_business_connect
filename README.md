# OSDuo Business Connect

**Your digital identity. Your customers. Your growth.**

Business Connect transforms how small businesses and professionals establish their digital presence. Create a stunning business profile, showcase products and services, capture customer enquiries — all seamlessly integrated with Frappe CRM.

---

## What It Does

| Capability | Description |
|------------|-------------|
| **Digital Business Card** | Mobile-first card with VCF download, QR/NFC sharing, and 4 distinct templates |
| **Business Profile** | Public landing page with hero, about, products, services, gallery, and contact |
| **Product Showcase** | Product catalog with categories, galleries, pricing, and brochures |
| **Service Listings** | Service pages with benefits, locations, and descriptions |
| **Lead Generation** | Enquiry forms that auto-create CRM leads with full tracking |
| **Analytics Dashboard** | Real-time engagement metrics — visits, scans, top cards, enquiry pipeline |

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
  Enquiry created → CRM Lead auto-created
        ↓
  Lead owner = card owner → Sales follow-up
        ↓
  Analytics tracked throughout
```

---

## Card Templates

| Template | Style |
|----------|-------|
| **Modern** | Centered layout, rounded avatar, pill buttons, soft shadows |
| **Professional** | Colored header band, horizontal layout, outlined buttons |
| **Minimal** | Clean, uppercase labels, thin borders, square buttons |
| **Classic** | Gradient banner, overlapping avatar, decorative dividers |

Each template is fully customizable with:
- 7 color schemes + custom palette
- 10 web font families (Inter, Roboto, Open Sans, Lato, Poppins...)
- 3 font sizes (Small / Default / Large)
- 4 button styles (Filled / Outline / Rounded / Pill)

---

## Features

### Digital Card
- VCF download ("Add to Phone Book")
- QR code generation (print-ready)
- Contact details — phone, email, WhatsApp, website
- Social links with icons
- Products & services showcase
- Business address with map
- One-tap share — copy link, WhatsApp, SMS, email

### Business Profile
- Page Section system — enable/disable, reorder, visibility control
- Hero section — Modern, Professional, Minimal, Classic layouts
- About, Products, Services, Contact, Gallery, Custom sections
- Product & service cards with images and links
- Contact grid with phone, email, website, address
- Social links

### Product & Service Pages
- Rich descriptions with images
- Location field with Google Maps integration
- Reusable product categories
- Gallery — 4-column desktop, 2-column mobile, click-to-open fullscreen
- Video embedding and brochure downloads
- "About Business" section with description & address

### Analytics
- Desk dashboard at `/app/analytics` — business selector, date range
- SVG line chart with gradient fill (visits by day)
- Summary cards: Link Visits, QR Scans, Cards, Products
- Top cards ranked by views with member names
- Recent activity with member name, device type, browser
- Enquiry pipeline: New → Ongoing → Converted → Lost
- Device type & browser tracking
- Non-blocking background event recording

### CRM Integration
```
Enquiry → Background sync → CRM Lead
    → Lead owner = card owner (Digital Card → Business Member → user)
    → Status sync: CRM Lead status ≠ New → Enquiry marked "Converted"
    → Custom fields: business, card, product, service, enquiry
    → Source: "Business Connect"
    → Failed syncs retried hourly
```

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

## Requirements

- Frappe Framework v16
- Frappe CRM
- Python: `qrcode[pil]` (for QR code generation)

---

## Installation

### Prerequisites
- Frappe v16+ installed and running
- **Frappe CRM** must be installed first

### Step 1 — Install Frappe CRM (if not already installed)

```bash
bench get-app https://github.com/frappe/crm
bench --site <site-name> install-app crm
```

### Step 2 — Install Business Connect

```bash
bench get-app https://github.com/devosduotech/osduo_business_connect.git
bench --site <site-name> install-app osduo_business_connect
bench --site <site-name> migrate
bench --site <site-name> pip install qrcode[pil]
bench build --app osduo_business_connect
bench restart
```

### Deployment Notes

- CRM must be installed **before** Business Connect (`required_apps = ["crm"]`)
- `bench build` must use `--app osduo_business_connect` only (CRM build may exceed memory on small VMs)
- Roles created on install: **BC Manager**, **BC User**, **BC Viewer**
- 8 default themes auto-created (Violet, Indigo, Blue, Green, Yellow, Orange, Red + custom)
- CRM custom fields added to CRM Lead: business, card, product, service, enquiry, source, campaign, landing URL

---

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
│       ├── bc_theme/
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
├── patches/
└── templates/
    ├── bc_base.html       # BC-styled base template
    └── pages/
        ├── business/      # Business landing page
        ├── product/       # Product page
        ├── service/       # Service page
        └── card/          # Digital card + team member pages
```

---

## DocTypes (15 total)

| DocType | Module | Purpose |
|---------|--------|---------|
| Business | Business | Root ownership record |
| Business Member | Business | Team members with roles |
| Digital Card | Card | Public digital business card |
| Showcase Product | Showcase | Product listings |
| Showcase Service | Showcase | Service listings |
| BC Theme | Showcase | Page themes (template + colors + fonts) |
| Page Section | Showcase | Custom page sections (ordered, toggleable) |
| Product Category | Showcase | Reusable product categories |
| Enquiry | Enquiry | Public enquiry submissions |
| Engagement Event | Analytics | View/click/share tracking |
| Business Social Link | Business | Social media links (child) |
| Business Hour | Business | Operating hours (child) |
| Digital Card Link | Card | Card social links (child) |
| Product Gallery Item | Showcase | Product gallery images (child) |
| Service Benefit | Showcase | Service benefits list (child) |

---

## Testing

```bash
cd osduo_business_connect
python3 -m unittest discover -s tests -p "test_*.py" -v

# 103 tests across 9 files
```

---

## Built With

- [Frappe Framework](https://frappeframework.com/) — Full-stack web framework
- [Frappe CRM](https://crm.frappe.io/) — Open source CRM

---

## License

MIT
