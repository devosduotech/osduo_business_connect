# OSDuo Business Connect v1.0.1 Release Notes

## Version 1.0.1 - Core Edition

**Release Date:** TBD  
**Target Audience:** Small businesses and individuals (1-20 users)

---

## Overview

OSDuo Business Connect v1.0.1 is the initial release of a Frappe Framework application that provides digital business identity, product/service showcase, lead generation, and CRM integration.

---

## Features

### Business Identity Management
- Create and manage business profiles
- Public business pages at `/b/<slug>`
- Team member management with role-based access (Owner, Manager, Member, Marketing, CRM User)
- Business hours and social links

### Digital Business Cards
- Create digital cards for team members
- Public card pages at `/c/<slug>`
- QR code generation for easy sharing
- vCard download for contact saving
- Share via WhatsApp, email, or direct link

### Product & Service Showcase
- Showcase products with galleries and pricing
- Showcase services with benefits
- Public product pages at `/b/<business>/p/<product>`
- Public service pages at `/b/<business>/s/<service>`
- Enquiry buttons on products and services

### Branding & Theming
- Customizable themes (Modern, Professional, Minimal, Classic)
- Color customization (primary, secondary, accent)
- Button and card style options
- Font family customization

### Public Profile Pages
- Section-based configurable pages
- Hero, About, Products, Services, Contact, Gallery sections
- Mobile-first responsive design
- SEO metadata support

### Lead Generation
- Enquiry capture from public pages
- Source tracking (Digital Card, Product, Service, QR, Campaign)
- Visitor information collection
- Consent management

### CRM Integration
- Automatic CRM Lead creation from enquiries
- Background synchronization with retry
- Business attribution on leads
- Multi-business lead isolation

### Analytics
- Engagement event tracking
- Page views, clicks, and enquiries
- Device and browser detection
- Basic analytics dashboard

---

## Requirements

- Frappe Framework v16
- Frappe CRM
- Python 3.10+
- Node.js 16+

---

## Installation

```bash
# Get the app
bench get-app osduo_business_connect

# Install on site
bench --site <site-name> install-app osduo_business_connect

# Run migrations
bench --site <site-name] migrate
```

---

## Configuration

### 1. Create Business
1. Go to OSDuo Business Connect > Business
2. Create a new business with slug and contact information
3. Owner membership is automatically created

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

### 6. Configure Sections
1. Go to Page Section
2. Add sections (Hero, About, Products, etc.)
3. Configure section order and visibility

---

## API Reference

### Public APIs

#### Get Business Profile
```
GET /api/method/osduo_business_connect.public.resolver.resolve_business_profile?business_slug=<slug>
```

#### Get Digital Card
```
GET /api/method/osduo_business_connect.public.resolver.resolve_card_profile?card_slug=<slug>
```

#### Submit Enquiry
```
POST /api/method/osduo_business_connect.enquiry.enquiry.public_enquiry_api.submit_enquiry
```

---

## Security

- Role-based access control
- Cross-business data isolation
- File upload validation
- XSS prevention
- Rate limiting on public APIs
- CSRF protection

---

## Known Limitations

- Single business per user (v1.0.1)
- Basic analytics (v2.0.1 will have advanced analytics)
- No SaaS billing (v2.0.1 feature)
- No custom domain support (v2.0.1 feature)

---

## Upgrading

### From v1.0.0
```bash
bench --site <site-name> migrate
bench --site <site-name] execute osduo_business_connect.install.after_install
```

---

## Support

- Documentation: https://docs.osduo.com
- Issues: https://github.com/osduo/osduo_business_connect/issues
- Email: support@osduo.com

---

## License

MIT License
