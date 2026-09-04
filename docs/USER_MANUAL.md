# OSDuo Business Connect — User Manual

**Version:** 1.0.1  
**Last Updated:** September 2026

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Setting Up Your Business](#2-setting-up-your-business)
3. [Digital Business Cards](#3-digital-business-cards)
4. [Products & Services](#4-products--services)
5. [Theming & Branding](#5-theming--branding)
6. [Publishing & Sharing](#6-publishing--sharing)
7. [Managing Enquiries](#7-managing-enquiries)
8. [Analytics Dashboard](#8-analytics-dashboard)
9. [CRM Integration](#9-crm-integration)
10. [Roles & Permissions](#10-roles--permissions)
11. [Administration](#11-administration)
12. [FAQ](#12-faq)

---

## 1. Getting Started

### 1.1 What is Business Connect?

OSDuo Business Connect is a digital business identity platform that helps you:

- Create a **public business profile** that showcases your company
- Issue **digital business cards** for your team members
- Display your **products and services** with galleries and pricing
- Capture **customer enquiries** that auto-create CRM leads
- Track **engagement analytics** — who viewed your card, products, and services

### 1.2 How It Works

```
Customer scans QR code or clicks link
        ↓
  Views your Digital Card or Business Profile
        ↓
  Browses products, services, team
        ↓
  Submits enquiry form
        ↓
  Enquiry created → CRM Lead auto-created
        ↓
  You follow up and close the deal
```

### 1.3 System Requirements

- Frappe Framework v16
- Frappe CRM
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Mobile device for card sharing (QR/NFC)

---

## 2. Setting Up Your Business

### 2.1 Creating a Business Profile

<!-- Screenshot: 02_create_business_form.png -->

1. Go to **Business Connect > Business** from the desk
2. Click **Create New Business**
3. Fill in the required fields:

| Field | Description | Required |
|-------|-------------|----------|
| Business Name | Your company name | Yes |
| Slug | URL-friendly identifier (lowercase, hyphens only) | Yes |
| Business Owner | The user who owns this business | Yes |
| Description | About your business | No |
| Logo | Company logo image | No |
| Cover Image | Banner image for public page | No |

4. Add contact information:

| Field | Description |
|-------|-------------|
| Email | Business email address |
| Phone | Business phone number |
| WhatsApp | WhatsApp number (with country code) |
| Website | Company website URL |
| Address | Street address |
| City | City name |
| State | State/Province |
| Country | Country |

5. Click **Save**

**What happens automatically:**
- An Owner membership is created for the business owner
- A default theme (Modern + Blue) is created and linked

### 2.2 Adding Team Members

<!-- Screenshot: 04_add_member.png -->

1. Open your business record
2. Go to the **Members** tab
3. Click **Add Row**
4. Fill in:

| Field | Description | Required |
|-------|-------------|----------|
| User | Frappe user account | Yes |
| Person Name | Display name | Yes |
| Designation | Job title (e.g., "Sales Manager") | No |
| Role | Owner / Manager / Member / Marketing / CRM User | Yes |
| Phone | Contact number | No |

5. Click **Save**

**Role descriptions:**

| Role | Can Do |
|------|--------|
| **Owner** | Full control — create, edit, delete everything |
| **Manager** | Manage business content, team members, products, services |
| **Member** | Manage own card and content allowed by role |
| **Marketing** | Manage products, services, themes, analytics |
| **CRM User** | View and manage enquiries and CRM leads |

### 2.3 Business Hours

<!-- Screenshot: business_hours.png -->

1. Open your business
2. Go to **Business Hours** tab
3. Add operating hours for each day:

| Field | Description |
|-------|-------------|
| Day | Monday through Sunday |
| Enabled | Toggle on/off |
| Open Time | When business opens |
| Close Time | When business closes |
| Is 24 Hours | Toggle for 24-hour operation |

### 2.4 Social Links

1. Open your business
2. Go to **Social Links** tab
3. Add your social media profiles:

| Field | Description |
|-------|-------------|
| Platform | Facebook, Instagram, LinkedIn, X, YouTube, Telegram, Website, Portfolio, Other |
| Label | Display text (e.g., "Follow us on Instagram") |
| URL | Full URL to your profile |

---

## 3. Digital Business Cards

### 3.1 Creating a Card

<!-- Screenshot: 06_create_card.png -->

1. Go to **Business Connect > Digital Card**
2. Click **Create New Card**
3. Fill in the required fields:

| Field | Description | Required |
|-------|-------------|----------|
| Business | Select your business | Yes |
| Team Member | Select the team member | Yes |
| Display Name | Name shown on the card | Yes |
| Slug | URL for the card (e.g., "john-doe") | Yes |
| Designation | Job title | No |
| Profile Photo | Avatar image | No |
| Bio | Short professional bio (2-3 sentences) | No |

### 3.2 Contact Details

Add contact information for the card:

| Field | Description |
|-------|-------------|
| Phone | Phone number (clickable on card) |
| Email | Email address (clickable on card) |
| WhatsApp | WhatsApp number (opens WhatsApp) |
| Website | Website URL (clickable on card) |

### 3.3 Social Links

<!-- Screenshot: 08_card_links.png -->

1. Go to **Card Links** section
2. Add social profiles:

| Field | Description |
|-------|-------------|
| Platform | LinkedIn, Instagram, Facebook, X, YouTube, Telegram, Website, Portfolio, Other |
| Label | Display text |
| Value | Username or URL |
| Full URL | Auto-generated or manual URL |

### 3.4 Card Options

<!-- Screenshot: 09_card_options.png -->

| Option | Description | Default |
|--------|-------------|---------|
| Show Business | Display business name and link on card | On |
| Show Products | Display products section on card | Off |
| Show Services | Display services section on card | Off |
| QR Enabled | Auto-generate QR code on publish | On |
| VCF Enabled | Allow vCard download | On |

### 3.5 Choosing a Template

<!-- Screenshot: 18_template_dropdown.png -->

Click the **Template** dropdown and select:

| Template | Best For | Style |
|----------|----------|-------|
| **Modern** | Tech, consultants, startups | Gradient, rounded, pill buttons |
| **Professional** | Corporate, B2B, industrial | Dark header, structured, outlined |
| **Minimal** | Freelancers, designers, personal | White, thin borders, understated |
| **Classic** | Traditional, legal, real estate | Gradient banner, decorative |

### 3.6 Publishing Your Card

1. Set **Status** to **Published**
2. Enable **Public Profile** toggle
3. Click **Save**
4. The QR code auto-generates

**Your card is now live at:** `https://your-domain.com/c/<card-slug>`

### 3.7 QR Code & Sharing

<!-- Screenshot: 27_qr_code.png -->

Once published:
- **QR Code** appears on the card page — customers scan to view
- **Copy Link** — share the card URL directly
- **WhatsApp** — share via WhatsApp message
- **VCF Download** — "Add to Phone Book" saves contact to phone

---

## 4. Products & Services

### 4.1 Creating Products

<!-- Screenshot: 11_create_product.png -->

1. Go to **Business Connect > Showcase Product**
2. Click **Create New Product**
3. Fill in:

| Field | Description | Required |
|-------|-------------|----------|
| Business | Select your business | Yes |
| Product Name | Product name | Yes |
| Slug | URL-friendly identifier | Yes |
| Category | Product category (see 4.3) | No |
| Short Description | Brief summary | No |
| Description | Full product description | No |
| Featured Image | Main product image | No |

### 4.2 Product Pricing

<!-- Screenshot: 12_product_pricing.png -->

| Price Display Mode | What Customers See |
|--------------------|--------------------|
| **Hidden** | No pricing shown |
| **Contact for Pricing** | "Enquire for Pricing" button |
| **Fixed Price** | Actual price with currency |

For Fixed Price:
1. Select **Fixed Price** from dropdown
2. Enter **Price** amount
3. Select **Currency** (INR, USD, etc.)

### 4.3 Product Categories

<!-- Screenshot: 16_product_category.png -->

Categories help organize your products:

1. Go to **Business Connect > Product Category**
2. Click **Create New Category**
3. Fill in:

| Field | Description |
|-------|-------------|
| Category Name | e.g., "Electronics", "Software", "Consulting" |
| Business | Your business |
| Description | Brief category description |
| Sort Order | Display order (1, 2, 3...) |

### 4.4 Product Gallery

<!-- Screenshot: 13_product_gallery.png -->

Add multiple images to showcase your product:

1. Open your product
2. Go to **Gallery** section
3. Click **Add Row** for each image
4. Fill in:

| Field | Description |
|-------|-------------|
| Image | Upload or select image |
| Caption | Short description of the image |
| Alt Text | Accessibility text |
| Sort Order | Display order |

**Gallery features:**
- 4-column grid on desktop, 2-column on mobile
- Click to open fullscreen
- Lazy loading for fast page speed
- Sorted by sort order

### 4.5 Additional Product Options

| Field | Description |
|-------|-------------|
| Video URL | YouTube/Vimeo link for product video |
| Brochure | PDF file for download |
| Location | Google Maps URL for "View on Map" |
| Enquiry Enabled | Show enquiry form on product page |
| Featured | Highlight on business page |

### 4.6 Creating Services

<!-- Screenshot: 14_create_service.html -->

1. Go to **Business Connect > Showcase Service**
2. Click **Create New Service**
3. Fill in similar to products

**Services have additional:**

| Field | Description |
|-------|-------------|
| Benefits | List of service benefits (title + description) |
| Gallery | Same as product gallery |

### 4.7 Service Benefits

<!-- Screenshot: 15_service_benefits.html -->

1. Open your service
2. Go to **Benefits** section
3. Add each benefit:

| Field | Description |
|-------|-------------|
| Title | Benefit name (e.g., "Custom Design") |
| Description | What's included |
| Sort Order | Display order |

---

## 5. Theming & Branding

### 5.1 Choosing a Template

<!-- Screenshot: 17_theme_form.png -->

1. Go to **Business Connect > BC Theme**
2. Open a theme or create new
3. Select **Template**:

| Template | Layout Style |
|----------|-------------|
| **Modern** | Centered, rounded elements, gradient, soft shadows |
| **Professional** | Dark header band, horizontal layout, outlined buttons |
| **Minimal** | Clean whitespace, thin borders, understated |
| **Classic** | Gradient banner, overlapping elements, decorative |

### 5.2 Color Schemes

<!-- Screenshot: 19_color_schemes.png -->

Select a preset or create custom:

| Preset | Primary Color |
|--------|---------------|
| Violet | Purple tones |
| Indigo | Deep blue-purple |
| Blue | Classic blue |
| Green | Professional green |
| Yellow | Warm yellow |
| Orange | Vibrant orange |
| Red | Bold red |
| Custom | Your own colors |

### 5.3 Custom Colors

<!-- Screenshot: 20_custom_colors.png -->

Select **Custom** from Color Scheme dropdown, then set:

| Field | Description |
|-------|-------------|
| Primary Color | Main brand color (buttons, links) |
| Secondary Color | Supporting color |
| Accent Color | Highlight color |
| Background Color | Page background |

### 5.4 Fonts & Button Styles

<!-- Screenshot: 21_font_options.png, 22_button_styles.png -->

**Font Family:** Inter, Roboto, Open Sans, Lato, Poppins, Montserrat, Nunito, Source Sans 3, Raleway, System Default

**Font Size:** Small (14px) / Default (16px) / Large (18px)

**Button Style:**
| Style | Appearance |
|-------|------------|
| Filled | Solid background color |
| Outline | Border with transparent background |
| Rounded | Rounded corners |
| Pill | Fully rounded (stadium shape) |

### 5.5 Linking Theme to Business

1. Open your Business record
2. Select the theme in **Default Theme** field
3. Save

---

## 6. Publishing & Sharing

### 6.1 Publishing Your Business

1. Open your Business record
2. Set **Status** to **Published**
3. Enable **Public Profile** toggle
4. Save

### 6.2 Public URLs

| URL Pattern | Page |
|-------------|------|
| `/b/<business-slug>` | Business landing page |
| `/b/<business>/team/<member>` | Team member profile |
| `/b/<business>/products/<product>` | Product detail page |
| `/b/<business>/services/<service>` | Service detail page |
| `/c/<card-slug>` | Digital Card (short URL) |

### 6.3 Sharing Options

**For Digital Cards:**
- Share the short URL: `https://your-domain.com/c/<card>`
- Display QR code at your office or on print materials
- Share via WhatsApp, email, or SMS directly from the card page
- Customers can download your contact (VCF) with one tap

**For Business Profile:**
- Share: `https://your-domain.com/b/<business>`
- Link to specific products or services
- Add QR code to business cards or brochures

---

## 7. Managing Enquiries

### 7.1 Enquiry Forms

<!-- Screenshot: 28_enquiry_form.png -->

Enquiry forms appear automatically on:
- Digital card pages
- Product pages
- Service pages

**Form fields:**
- Full Name (required)
- Email (required)
- Phone
- Company
- Message
- Consent checkbox

**Source tracking:** Each enquiry records where it came from:
- Digital Card
- Business Profile
- Product
- Service
- QR Scan
- Campaign

### 7.2 Enquiry List

<!-- Screenshot: 29_enquiry_list.png -->

1. Go to **Business Connect > Enquiry**
2. View all enquiries with filters:

| Filter | Shows |
|--------|-------|
| All | Every enquiry |
| New | Unread, awaiting response |
| Ongoing | Contacted, Nurture, Qualified |
| Converted | Successfully closed |
| Lost | Unqualified, Junk |

### 7.3 Enquiry Detail

<!-- Screenshot: 30_enquiry_detail.png -->

Click any enquiry to see:
- Visitor contact information
- Message content
- Source and landing URL
- CRM Lead link (if synced)
- Sync status and errors

### 7.4 Responding to Enquiries

1. Open the enquiry
2. Review the visitor's message
3. Click the **CRM Lead** link to manage in CRM
4. Update the enquiry status as you progress:

| Status | Meaning |
|--------|---------|
| New | Just received |
| Contacted | You've reached out |
| Nurture | Building relationship |
| Qualified | Ready for sales |
| Converted | Deal closed |
| Unqualified | Not a fit |
| Junk | Spam or invalid |

### 7.5 Enquiry Pipeline

<!-- Screenshot: 31_enquiry_pipeline.png -->

Track your sales funnel:
- **New** → Fresh enquiries needing response
- **Ongoing** → Contacted, nurturing, qualified
- **Converted** → Successfully closed deals
- **Lost** → Unqualified or junk

---

## 8. Analytics Dashboard

### 8.1 Overview

<!-- Screenshot: 32_analytics_dashboard.png -->

1. Go to **/app/analytics** from the desk
2. Select your business from the dropdown
3. Choose date range: 7, 15, 30, 90, or 365 days

### 8.2 Visits & Scans

<!-- Screenshot: 33_analytics_chart.png, 34_analytics_summary.png -->

**Line Chart:** Shows daily visits over time with gradient fill.

**Summary Cards:**
| Card | Tracks |
|------|--------|
| Link Visits | Direct link clicks |
| QR Scans | QR code scans |
| Cards | Digital card views |
| Products | Product page views |

### 8.3 Top Cards

<!-- Screenshot: 35_analytics_top_cards.png -->

See which team members' cards get the most views:
- Member name
- View count
- Rank

### 8.4 Enquiry Pipeline

<!-- Screenshot: 36_analytics_pipeline.png -->

Visual overview of your sales funnel:
- New enquiries
- Ongoing (contacted, nurturing, qualified)
- Converted deals
- Lost opportunities

### 8.5 Recent Activity

<!-- Screenshot: 37_analytics_recent.png -->

See the latest events:
- Event type (Card View, Product View, Enquiry, etc.)
- Team member
- Device type (Desktop, Mobile, Tablet)
- Browser

---

## 9. CRM Integration

### 9.1 How It Works

```
Enquiry submitted on public page
        ↓
Background job creates CRM Lead
        ↓
Lead owner = Card owner (automatic)
        ↓
Lead source = "Business Connect"
        ↓
Custom fields added: business, card, product, service, enquiry
```

### 9.2 Lead Owner Assignment

When a customer submits an enquiry on a team member's card, the CRM Lead is automatically assigned to that team member.

**Chain:** Digital Card → Business Member → User account

### 9.3 Status Sync

Status changes sync bidirectionally:

| CRM Lead Status | Enquiry Status |
|-----------------|----------------|
| New | New |
| Contacted | Contacted |
| Nurture | Nurture |
| Qualified | Qualified |
| Converted | Converted |
| Unqualified | Unqualified |
| Junk | Junk |

### 9.4 Custom Fields on CRM Lead

<!-- Screenshot: 39_crm_lead_detail.png -->

| Field | Description |
|-------|-------------|
| OSDuo Business | Which business the lead belongs to |
| OSDuo Card | Which card generated the lead |
| OSDuo Product | Which product page (if applicable) |
| OSDuo Service | Which service page (if applicable) |
| OSDuo Enquiry | Link to the enquiry record |
| OSDuo Source | Where the lead came from |
| OSDuo Campaign | Campaign tracking code |
| OSDuo Landing URL | The page where enquiry was submitted |

---

## 10. Roles & Permissions

### 10.1 Role Overview

| Role | Description |
|------|-------------|
| **BC Manager** | Full business management |
| **BC User** | General user access |
| **BC Viewer** | Read-only access |
| **BC Content** | Manage products, services, galleries |
| **BC Analytics** | View analytics dashboard |
| **BC Enquiry** | Manage enquiries |
| **BC Settings** | System configuration |

### 10.2 Permission Matrix

**Business:**
| Action | Owner | Manager | Member | Marketing |
|--------|-------|---------|--------|-----------|
| Read | Yes | Yes | Yes | Yes |
| Write | Yes | Yes | No | Yes |
| Create | Yes | No | No | No |
| Delete | Yes | No | No | No |

**Digital Card:**
| Action | Owner | Manager | Member | Marketing |
|--------|-------|---------|--------|-----------|
| Read | Yes | Yes | Yes | Yes |
| Write | Yes | Yes | Own card only | Yes |
| Create | Yes | Yes | No | No |
| Delete | Yes | No | No | No |

**Products & Services:**
| Action | Owner | Manager | Marketing |
|--------|-------|---------|-----------|
| Read | Yes | Yes | Yes |
| Write | Yes | Yes | Yes |
| Create | Yes | Yes | Yes |
| Delete | Yes | No | No |

### 10.3 Data Isolation

- Each business sees only their own data
- System Managers see all businesses
- Guest users can only see Published records with Public Profile enabled
- CRM Leads are scoped to business members

---

## 11. Administration

### 11.1 Installation

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

### 11.2 CSRF Configuration

For production, add your domain to `site_config.json`:

```json
{
  "allowed_referrers": ["your-domain.com"]
}
```

### 11.3 Backup & Restore

Standard Frappe backup procedures apply:

```bash
# Backup
bench --site <site-name> backup

# Restore
bench --site <site-name> restore <backup-file>
```

### 11.4 Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code not generating | Install `qrcode[pil]`: `bench pip install qrcode[pil]` |
| Public page 404 | Check `bench clear-website-cache` |
| CRM Lead not created | Check background worker is running |
| Build fails | Use `bench build --app osduo_business_connect` only |
| Theme not applying | Check Business record has default_theme linked |

---

## 12. FAQ

**Q: Can I use Business Connect without CRM?**  
A: No, Frappe CRM is a required dependency.

**Q: How many businesses can I create?**  
A: Unlimited. Each business is independent with its own team, products, and cards.

**Q: Can guests see enquiry submissions?**  
A: No. Enquiries are only visible to business members with appropriate roles.

**Q: How do I change my card's URL?**  
A: Update the Slug field on the Digital Card. Old URLs will break.

**Q: Can I have multiple themes?**  
A: Yes. Create multiple BC Theme records and assign different ones to different businesses or cards.

**Q: How do I add my company logo to the card?**  
A: Upload a Profile Photo on the Digital Card, or a Logo on the Business record.

**Q: Can customers download my contact info?**  
A: Yes. The VCF download button saves your contact to their phone.

**Q: How do I track where enquiries come from?**  
A: Each enquiry records its source (Digital Card, Product, Service, QR, Campaign) automatically.

---

## Support

- **Repository:** https://github.com/devosduotech/osduo_business_connect
- **Issues:** https://github.com/devosduotech/osduo_business_connect/issues

---

## License

MIT License
