# Business Connect — Marketing Feature Document

**Status:** Internal Reference  
**Date:** September 2026  
**Version:** 1.0

---

## 1. Executive Summary

Business Connect is a **digital marketing platform** that enables businesses to create professional web presence, product/service catalogs, and lead generation systems — without needing a website developer.

### Core Value Proposition

> **One platform. Every marketing channel. Measurable results.**

| Traditional Marketing | Business Connect |
|----------------------|------------------|
| Static website | Dynamic, auto-updating pages |
| Business cards | Interactive digital cards with QR |
| PDF catalogs | Live, shareable product catalogs |
| Generic contact forms | Context-aware lead capture |
| No analytics | Full engagement tracking |
| Developer dependent | Self-service, no code |

---

## 2. Web Page Creation

### 2.1 Page Types Available

| Page | URL Pattern | Purpose |
|------|-------------|---------|
| Business Profile | `/b/<slug>` | Company landing page, brand story |
| Digital Card | `/c/<slug>` | Personal networking, vCard |
| Product Page | `/b/<slug>/products/<slug>` | Individual product showcase |
| Service Page | `/b/<slug>/services/<slug>` | Individual service showcase |
| Analytics | `/analytics` | Marketing performance dashboard |

### 2.2 Business Profile Page

The primary marketing asset — a complete company profile.

**Sections:**
```
Hero Header
├── Logo
├── Business Name
├── Tagline
├── Cover Image
└── Primary CTA (WhatsApp / Call / Enquiry)

Navigation
├── About
├── Products
├── Services
├── Team
├── Hours
└── Contact

About Section
├── Company Description
├── Key Highlights
└── Business Hours

Product Catalog
├── Product Grid (4 columns)
├── Product Card: Image + Name + Price
└── "View All" Link

Service Catalog
├── Service Grid
├── Service Card: Image + Name + Description
└── "View All" Link

Team Section
├── Team Member Grid
├── Member: Photo + Name + Designation
└── Links to individual cards

Contact Section
├── Email
├── Phone
├── WhatsApp
├── Website
├── Address
└── Social Links

Footer
└── Powered by OSDuo Business Connect
```

### 2.3 Digital Card Page

Personal marketing asset for networking.

**Sections:**
```
Hero (4 theme options)
├── Profile Photo
├── Name
├── Designation
├── Business Name
├── Bio
├── Contact Details
├── Social Links
└── QR Code

Featured Products (optional)
├── Top 10 Products
└── Links to product pages

Featured Services (optional)
├── Top 10 Services
└── Links to service pages

Actions
├── Save Contact (VCF download)
├── WhatsApp
├── Call
├── Email
└── Share Card
```

### 2.4 Product Page

Individual product marketing page.

**Sections:**
```
Product Hero
├── Product Image (large)
├── Product Name
├── Category
├── Price
├── Short Description
└── CTA (WhatsApp / Call / Enquire)

Product Details
├── Full Description
├── Specifications (Benefits/Details table)
├── Pricing Info
└── Additional Images (Gallery)

Business Context
├── "About {Business}" section (optional)
├── Business contact info
└── Link to business profile

Enquiry Form
├── Name
├── Phone
├── Email
├── Message
└── Submit
```

### 2.5 Service Page

Individual service marketing page.

**Sections:**
```
Service Hero
├── Service Image
├── Service Name
├── Category
├── Short Description
└── CTA (WhatsApp / Call / Enquire)

Service Details
├── Full Description
├── Benefits / Features
└── Additional Images (Gallery)

Business Context
├── "About {Business}" section (optional)
├── Business contact info
└── Link to business profile

Enquiry Form
├── Name
├── Phone
├── Email
├── Message
└── Submit
```

---

## 3. Catalog System

### 3.1 Product Catalog

**Purpose:** Showcase products to potential customers.

**Features:**
- Grid display (4 columns desktop, 2 tablet, 1 mobile)
- Product images with hover effects
- Price display with currency
- Category filtering
- Sort by: Name, Price, Sort Order
- Individual product pages with full details

**Catalog Entry:**
```
Product
├── Product Name
├── Slug (URL-friendly)
├── Category (Product Category)
├── Short Description (for catalog cards)
├── Full Description (for product page)
├── Price
├── Currency
├── Price Display Mode (Fixed / On Request / Starting From)
├── Cover Image
├── Gallery Images
├── Video URL
├── Brochure (PDF)
├── Status (Draft / Published / Archived)
└── Sort Order
```

### 3.2 Service Catalog

**Purpose:** Showcase services to potential customers.

**Features:**
- Grid display
- Service images
- Category filtering
- Individual service pages with benefits
- Service-specific CTAs

**Catalog Entry:**
```
Service
├── Service Name
├── Slug
├── Category (Product Category)
├── Short Description
├── Full Description
├── Cover Image
├── Gallery Images
├── Benefits (Child Table)
│   ├── Title
│   └── Description
├── Status
└── Sort Order
```

### 3.3 Category System

**Purpose:** Organize products/services for filtering and navigation.

```
Product Category
├── Category Name
├── Slug
├── Description
├── Parent Category (for hierarchy)
├── Sort Order
└── Status
```

**Use Cases:**
- Products > Electronics > Mobile Phones
- Services > Consulting > ERP Implementation
- Properties > Residential > Apartments

---

## 4. SEO & Discoverability

### 4.1 URL Structure

All public pages have clean, SEO-friendly URLs:

```
Business:    /b/arun-properties
Card:        /c/arun-kumar
Product:     /b/arun-properties/products/anna-nagar-apartment
Service:     /b/arun-properties/services/property-consultation
```

### 4.2 Meta Tags

Each page automatically includes:

```html
<title>{Page Title} | {Business Name}</title>
<meta name="description" content="{SEO Description}">
<meta property="og:title" content="{Page Title}">
<meta property="og:description" content="{SEO Description}">
<meta property="og:image" content="{OG Image}">
<meta property="og:url" content="{Page URL}">
```

### 4.3 SEO Fields

Available on Business, Product, and Service:

| Field | Purpose |
|-------|---------|
| SEO Title | Custom page title (overrides default) |
| SEO Description | Custom meta description |
| OG Image | Custom image for social sharing |

### 4.4 Search Engine Optimization

- Clean HTML structure
- Semantic markup
- Fast loading (static assets, optimized images)
- Mobile-responsive (Google mobile-first indexing)
- Structured data ready (future enhancement)

---

## 5. Social Sharing

### 5.1 Shareable Links

Every page has a unique, shareable URL:

```
Business:    https://connect.osduotech.com/b/arun-properties
Card:        https://connect.osduotech.com/c/arun-kumar
Product:     https://connect.osduotech.com/b/arun-properties/products/3bhk-apartment
```

### 5.2 Social Meta Tags

Open Graph tags for rich previews on:

- WhatsApp
- Facebook
- LinkedIn
- Twitter/X
- Telegram
- Email clients

### 5.3 Share Features

**Digital Card:**
- Copy link button
- QR code display
- VCF download (save contact)
- WhatsApp share
- Email share

**Product/Service:**
- Direct link sharing
- WhatsApp enquiry
- Email enquiry

---

## 6. QR Code Marketing

### 6.1 Business Card QR

```
┌─────────────────────────────┐
│                             │
│         [PHOTO]             │
│       ARUN KUMAR            │
│    Real Estate Consultant   │
│                             │
│    ┌─────────────────┐      │
│    │    QR CODE      │      │
│    └─────────────────┘      │
│   Scan to save contact      │
│                             │
│ [WhatsApp] [Call] [Website] │
└─────────────────────────────┘
```

**QR Code Content:** `https://connect.osduotech.com/c/arun-kumar`

**Visitor Journey:**
```
Scan QR
  ↓
View Digital Card
  ↓
Save Contact (VCF)
  ↓
WhatsApp / Call / Email
  ↓
View Products/Services
  ↓
Submit Enquiry
  ↓
CRM Lead
```

### 6.2 Property Board QR (Real Estate)

```
┌─────────────────────────────┐
│                             │
│        FOR SALE             │
│                             │
│    3 BHK PREMIUM HOME       │
│      ₹1.85 CRORE            │
│                             │
│       ┌─────────┐           │
│       │ QR CODE │           │
│       └─────────┘           │
│    Scan for details         │
│                             │
└─────────────────────────────┘
```

**QR Code Content:** `https://connect.osduotech.com/b/arun-properties/properties/3bhk-apartment`

### 6.3 Product QR (Retail)

```
┌─────────────────────────────┐
│                             │
│      [PRODUCT IMAGE]        │
│                             │
│    Premium Widget Pro        │
│      ₹2,499                 │
│                             │
│       ┌─────────┐           │
│       │ QR CODE │           │
│       └─────────┘           │
│    Scan for specs & enquiry │
│                             │
└─────────────────────────────┘
```

### 6.4 QR Code Use Cases

| Location | QR Content | Purpose |
|----------|------------|---------|
| Business Card | Digital Card URL | Save contact, view profile |
| Product Packaging | Product Page URL | Specs, warranty, support |
| Store Display | Business Profile URL | Full catalog |
| Property Board | Property Page URL | Details, enquiry |
| Brochure | Business Profile URL | Digital catalog |
| Email Signature | Digital Card URL | Networking |
| Social Media Bio | Business Profile URL | Link in bio |
| Receipt/Invoice | Business Profile URL | Upsell, reviews |

---

## 7. Lead Generation

### 7.1 Enquiry Forms

Every public page includes context-aware enquiry forms:

| Page | Form Fields | Context |
|------|-------------|---------|
| Business Profile | Name, Phone, Email, Message | General enquiry |
| Digital Card | Name, Phone, Email, Message | Contact request |
| Product Page | Name, Phone, Email, Message | Product enquiry |
| Service Page | Name, Phone, Email, Message | Service enquiry |

### 7.2 Context Capture

Each enquiry automatically captures:

```
Enquiry
├── Visitor Data
│   ├── Name
│   ├── Phone
│   ├── Email
│   └── Message
├── Source Context
│   ├── Business
│   ├── Card (if from card page)
│   ├── Product (if from product page)
│   ├── Service (if from service page)
│   └── Source Type (WhatsApp, Call, Form)
├── Attribution
│   ├── Landing URL
│   ├── Referrer
│   ├── Device Type
│   └── Browser
└── CRM Integration
    └── CRM Lead (auto-created)
```

### 7.3 WhatsApp Integration

**WhatsApp Click Tracking:**
```
User clicks WhatsApp button
  ↓
Engagement Event recorded
  ↓
WhatsApp opens with pre-filled message
  ↓
Conversation begins
```

**Pre-filled Messages:**
```
Product: "Hi, I'm interested in {Product Name}. Price: {Price}"
Service: "Hi, I'd like to know more about {Service Name}"
General: "Hi, I found your business on {Source}"
```

### 7.4 VCF Download (Save Contact)

Digital cards include vCard download:

```
User clicks "Save Contact"
  ↓
VCF file downloads
  ↓
Phone opens contact
  ↓
Contact saved
  ↓
Future communication possible
```

---

## 8. Analytics & Tracking

### 8.1 Engagement Events

| Event | Description | Where Tracked |
|-------|-------------|---------------|
| `profile_view` | Business page visited | Business page |
| `card_view` | Digital card viewed | Card page |
| `product_view` | Product page viewed | Product page |
| `service_view` | Service page viewed | Service page |
| `qr_landing` | QR code scanned | All pages (via QR param) |
| `whatsapp_click` | WhatsApp button clicked | All pages |
| `call_click` | Call button clicked | All pages |
| `vcard_download` | VCF downloaded | Card page |
| `enquiry_submitted` | Enquiry form submitted | All pages |

### 8.2 Analytics Dashboard

**URL:** `/analytics`

**Metrics Available:**
```
Summary Cards
├── Total Link Visits
├── QR Scans
├── Active Cards
├── Published Products
└── Published Services

Charts
├── Visits by Day (line chart)
├── Events by Type (horizontal bars)
├── Top Cards (table)
├── Enquiry Pipeline (status cards)
└── Recent Activity (table)
```

### 8.3 Attribution Tracking

Every engagement event captures:

```python
{
    "business": "arun-properties",
    "event_type": "product_view",
    "landing_url": "https://connect.osduotech.com/b/arun-properties/products/3bhk",
    "referrer": "https://google.com",
    "device_type": "Mobile",
    "browser": "Chrome",
    "event_time": "2026-09-05 10:30:00"
}
```

### 8.4 Marketing ROI Measurement

| Metric | How to Measure |
|--------|----------------|
| Campaign effectiveness | Track QR scans per campaign |
| Channel performance | Compare referrer sources |
| Content engagement | Product/service views |
| Conversion rate | Enquiries / Total views |
| Lead quality | Enquiry → CRM Lead → Deal |

---

## 9. Marketing Campaign Support

### 9.1 Campaign Types Supported

| Campaign Type | BC Feature | How It Works |
|---------------|------------|--------------|
| Print Ads | QR Codes | QR in newspaper/magazine → Digital Card |
| Business Cards | QR + VCF | Card QR → Save Contact |
| Billboards | QR Code | Large QR → Business Profile |
| Product Flyers | QR per product | QR → Product Page |
| Email Marketing | Shareable Links | Link in email → Page |
| Social Media | OG Tags | Rich previews on social |
| Events/Exhibitions | QR on badge | QR → Digital Card |
| WhatsApp Marketing | Shareable Links | Forward link → Page |

### 9.2 Campaign Tracking

**Using QR Parameters:**
```
Campaign: Monsoon Sale 2026
QR URL: https://connect.osduotech.com/c/arun?ref=monsoon2026

When scanned:
- ref parameter captured
- Event recorded with campaign attribution
- Analytics show campaign performance
```

### 9.3 Multi-Channel Strategy

```
                    BUSINESS CONNECT
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    DIGITAL           PHYSICAL         SHARED
         │                │                │
    ┌────┴────┐     ┌────┴────┐     ┌────┴────┐
    │ Website │     │ QR Code │     │WhatsApp │
    │ Social  │     │ Business│     │ Email   │
    │ Email   │     │ Cards   │     │ SMS     │
    │ Ads     │     │ Flyers  │     │ Links   │
    └────┬────┘     └────┬────┘     └────┬────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
                    ENGAGEMENT
                          │
                    ┌─────┴─────┐
                    │ Analytics │
                    │ Leads     │
                    │ Deals     │
                    └───────────┘
```

---

## 10. Content Marketing

### 10.1 Product Stories

Each product page can tell a story:

```
Product Page
├── Hero Image (visual impact)
├── Product Name (clear identity)
├── Price (transparent)
├── Description (story/features)
├── Gallery (multiple angles)
├── Specifications (details)
├── CTA (take action)
└── Related Products (cross-sell)
```

### 10.2 Service Positioning

Each service page positions expertise:

```
Service Page
├── Service Image (professional)
├── Service Name (clear offering)
├── Description (value proposition)
├── Benefits (why choose us)
├── Gallery (work samples)
├── CTA (get started)
└── Related Services (upsell)
```

### 10.3 Team Marketing

Team members as individual marketing assets:

```
Digital Card
├── Personal brand (photo, name, designation)
├── Professional bio
├── Direct contact (WhatsApp, Call)
├── Featured products/services
├── QR code for networking
└── VCF for contact saving
```

---

## 11. Industry-Specific Marketing

### 11.1 Real Estate

```
Agent Profile
├── Property Catalog
│   ├── For Sale (Products)
│   ├── For Rent (Services)
│   └── Featured Properties
├── Property Details
│   ├── Bedrooms, Bathrooms, Area
│   ├── Price
│   ├── Location
│   └── Amenities
├── Lead Capture
│   ├── Property Enquiry
│   ├── Site Visit Request
│   └── WhatsApp Enquiry
└── Analytics
    ├── Property Views
    ├── QR Scans
    └── Enquiry Conversion
```

### 11.2 Retail / E-commerce

```
Product Catalog
├── Product Categories
├── Product Pages
│   ├── Images
│   ├── Price
│   ├── Description
│   └── Enquiry/Order
├── Featured Products
└── Seasonal Collections
```

### 11.3 Professional Services

```
Consultant Profile
├── Service Catalog
│   ├── Consulting Services
│   ├── Implementation
│   └── Support
├── Credentials
│   ├── Experience
│   ├── Certifications
│   └── Client Logos
├── Case Studies (via products)
└── Lead Capture
```

### 11.4 Manufacturing

```
Company Profile
├── Product Catalog
│   ├── Product Categories
│   ├── Technical Specs
│   └── Brochures
├── Certifications
├── Factory Tour (video)
└── B2B Enquiry Form
```

---

## 12. Marketing Automation (Future)

### 12.1 Planned Features

| Feature | Description | Priority |
|---------|-------------|----------|
| Email Campaigns | Send product updates to leads | High |
| WhatsApp Broadcast | Share catalog via WhatsApp | High |
| Lead Scoring | Rank leads by engagement | Medium |
| Auto-followup | Automated enquiry responses | Medium |
| Campaign Landing Pages | Custom pages for campaigns | Low |
| A/B Testing | Test different page versions | Low |

### 12.2 Integration Points

```
Business Connect
├── Email Marketing (via CRM)
├── WhatsApp Business API
├── Google Analytics (via UTM)
├── Facebook Pixel (via OG tags)
└── CRM Automation (via Frappe CRM)
```

---

## 13. Deployment & Distribution

### 13.1 Hosting Options

| Option | URL | Best For |
|--------|-----|----------|
| Self-hosted | `business.yourdomain.com` | Full control |
| Shared platform | `connect.osduotech.com/b/<slug>` | Multi-tenant SaaS |
| Subdomain | `arun.yourdomain.com` | Brand consistency |

### 13.2 Distribution Channels

```
DIGITAL DISTRIBUTION
├── Website embedding
├── Social media sharing
├── Email signatures
├── WhatsApp forwards
├── QR code scanning
└── Direct link sharing

PHYSICAL DISTRIBUTION
├── Business cards
├── Product flyers
├── Brochures
├── Billboards
├── Event badges
└── Store displays
```

---

## 14. Success Metrics

### 14.1 Key Performance Indicators

| KPI | Target | How to Measure |
|-----|--------|----------------|
| Page Views | Increase monthly | Analytics dashboard |
| QR Scans | Track per campaign | QR event tracking |
| Enquiry Rate | >2% of views | Enquiries / Views |
| Response Time | <1 hour | CRM tracking |
| Conversion Rate | >10% of enquiries | CRM Lead → Deal |
| WhatsApp Response | >80% reply rate | WhatsApp tracking |

### 14.2 Reporting

**Weekly Report:**
```
Week: Sep 1-7, 2026

Page Views:      1,240 (+15%)
QR Scans:          89 (+22%)
Enquiries:         27 (+8%)
WhatsApp Clicks:   94 (+12%)
Calls:             41 (+5%)

Top Products:
1. 3BHK Apartment - 342 views, 12 enquiries
2. Villa Plot - 218 views, 8 enquiries
3. Commercial Space - 156 views, 7 enquiries
```

---

## 15. Implementation Roadmap

### Phase 1: Foundation (v1.0) ✅
- Business Profile pages
- Digital Card pages
- Product/Service pages
- Basic enquiry forms
- QR code generation
- Basic analytics

### Phase 2: Marketing (v1.1)
- Campaign tracking (UTM/QR params)
- Email signature generator
- Social sharing optimization
- Lead scoring basics

### Phase 3: Automation (v1.2)
- Auto-enquiry responses
- WhatsApp Business API
- Email campaign integration
- Lead nurturing workflows

### Phase 4: Intelligence (v2.0)
- AI-powered product descriptions
- Predictive lead scoring
- Multi-touch attribution
- Marketing ROI dashboard

---

## Appendix A: Page Templates

### Business Profile Template
```
 bc_base.html
 └── business/business.html
     ├── hero_modern.html / hero_professional.html / hero_minimal.html / hero_classic.html
     ├── products section
     ├── services section
     ├── team section
     ├── hours section
     ├── contact section
     └── footer
```

### Digital Card Template
```
 bc_base.html
 └── card/card.html
     ├── hero_modern.html / hero_professional.html / hero_minimal.html / hero_classic.html
     ├── products section (optional)
     ├── services section (optional)
     ├── share section
     └── footer
```

### Product Template
```
 bc_base.html
 └── product/product.html
     ├── hero section
     ├── details section
     ├── gallery section
     ├── about business section
     ├── enquiry form
     └── footer
```

---

## Appendix B: Event Types Reference

| Event Type | Trigger | Data Captured |
|------------|---------|---------------|
| `profile_view` | Business page load | Business, URL, referrer, device |
| `card_view` | Card page load | Card, business, URL, device |
| `product_view` | Product page load | Product, business, URL, device |
| `service_view` | Service page load | Service, business, URL, device |
| `qr_landing` | QR code scan | QR type, source page, device |
| `whatsapp_click` | WhatsApp button click | Page type, contact info |
| `call_click` | Call button click | Page type, phone number |
| `vcard_download` | VCF download | Card, business |
| `enquiry_submitted` | Form submission | Business, source, visitor data |

---

*This document is for internal reference only. Not for public distribution.*
