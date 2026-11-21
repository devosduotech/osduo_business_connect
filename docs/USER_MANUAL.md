# OSDuo Business Connect — User Manual

**Version:** 1.3.4
**Last Updated:** 18 November 2026

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
11. [Mobile App (PWA)](#11-mobile-app-pwa)
12. [Troubleshooting](#12-troubleshooting)
13. [FAQ](#13-faq)

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

- Modern web browser (Chrome, Firefox, Safari, Edge)
- A stable internet connection
- Mobile device for card sharing (QR/NFC)

### 1.4 Importing Existing Data

The underlying platform supports the standard **Data Import** tool for
Businesses, Business Members, Digital Cards, Product Categories and Showcase
Products / Services from CSV or XLSX. This is a Desk tool, so it is available
to **Enterprise** users and to the provider during onboarding — not to
Professional or Business customers in their day-to-day portal. Ask the provider
to load an initial CSV if you need bulk setup.

---

## 2. Setting Up Your Business

### 2.1 Creating a Business Profile

![Business Creation Form](./images/mockup/02_create_business_form.html)

1. The provider creates the first Business during onboarding. Enterprise users
   can also use **Business Connect > Business** in the Desk.
2. Click **Create New Business**
3. Fill in the required fields:

| Field | Description | Required |
|-------|-------------|----------|
| Business Name | Your company name | Yes |
| Slug | URL-friendly identifier (lowercase, hyphens only) | Yes |
| Industry | What the business does (free text, one per line of business) | No |
| Business Owner | The user who owns this business | Yes |
| About Us | About your business (shown on the public page) | No |
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
- An **Owner membership** is created for the business owner
- The built-in **Default Blue** theme is linked to the business
- A canonical **Public URL** (`/b/<slug>`) is generated and kept read-only

**Draft → Submit workflow**

Businesses, Digital Cards, Products and Services are *submittable* records:

1. Create and edit freely while the record is a **draft**
2. Click **Submit** — the record enters the approval lifecycle and its
   **Public Slug locks** (read-only), protecting every QR/NFC link already printed
3. Need changes later? **Cancel** the submitted record, then **Amend** it. The
   amendment keeps the **same slug and public URL**, reopens as a draft for edits,
   and goes live again at the same address once re-submitted
4. Only the Owner (or BC System Manager) can cancel/amend; Owner/Manager/Marketing
   can submit — see [Roles & Permissions](#10-roles--permissions)

> A cancelled record disappears from public pages until its amendment is submitted.
> Plan changes around peak times, or amend quickly — the URL never changes.

### 2.2 Adding Team Members

Team members are invited from the private portal at **`/portal/team`**. The
Frappe Desk and the native **User** list/form are never used for this — the
invitation is created and validated entirely inside Business Connect.

1. Sign in and open `/portal/team`
2. Choose the Business and enter the teammate's **Email**, **First Name**,
   optional **Last Name**, and one Business Connect role
3. Click **Send invitation**

| Field | Description | Required |
|-------|-------------|----------|
| Business | The business the teammate will join | Yes |
| Email | Their login/email address | Yes |
| First Name | Used on their user account and digital card | Yes |
| Last Name | Used on their user account and digital card | No |
| Business Connect role | `BC Business Member`, `BC Business Manager`, `BC CRM User` or `BC Marketing Manager` | Yes |

The invitation email contains a one-time acceptance link. The teammate opens
it, sets a password, and is then added as an active **Business Member** with
the role you chose. Until then the invite reserves one billable seat and
appears as a pending reservation in the portal.

**Role descriptions:**

| Portal role | Business Member role | Can Do |
|-------------|----------------------|--------|
| **BC Business Member** | Member | Manage own card and content allowed by role |
| **BC Business Manager** | Manager | Manage business content, team members, products, services |
| **BC Marketing Manager** | Marketing | Manage products, services, themes, analytics |
| **BC CRM User** | CRM User | View and manage enquiries and CRM leads |

> The per-business **Owner** role, **Administrator**, **System Manager**,
> **BC System Manager** and **BC Subscription Manager** are never offered in
> the team invite form. Only the Business Owner can invite teammates.

### 2.5 Page Visibility Settings

Control what appears on your public product and service pages:

| Field | Default | Description |
|-------|---------|-------------|
| Show About Business in Product Pages | On | Display "About {business}" section on product pages |
| Show About Business in Service Pages | On | Display "About {business}" section on service pages |

Both are enabled by default. Uncheck to hide the "About Business" section on specific page types.

### 2.6 Business Hours

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

### 2.7 Social Links

1. Open your business
2. Go to **Social Links** tab
3. Add your social media profiles:

| Field | Description |
|-------|-------------|
| Platform | Facebook, Instagram, LinkedIn, X, YouTube, Telegram, Website, Portfolio, Other |
| URL | Full URL to your profile |
| Icon Class | Auto-set based on platform (Font Awesome icon) |

**Platform icons are auto-detected:**
- Facebook → `fa-brands fa-facebook`
- Instagram → `fa-brands fa-instagram`
- LinkedIn → `fa-brands fa-linkedin`
- X → `fa-brands fa-x-twitter`
- YouTube → `fa-brands fa-youtube`
- Telegram → `fa-brands fa-telegram`
- Website → `fa-solid fa-globe`

---

## 3. Digital Business Cards

### 3.1 Creating a Card

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

1. Go to **Card Links** section
2. Add social profiles:

| Field | Description |
|-------|-------------|
| Platform | LinkedIn, Instagram, Facebook, X, YouTube, Telegram, Website, Portfolio, Other |
| Label | Display text |
| Value | Username or URL |
| Full URL | Auto-generated or manual URL |

### 3.4 Card Options

| Option | Description | Default |
|--------|-------------|---------|
| Show Business | Display business name and link on card | On |
| Show Products | Display products section on card | Off |
| Show Services | Display services section on card | Off |
| QR Enabled | Auto-generate QR code on publish | On |
| VCF Enabled | Allow vCard download | On |

### 3.5 Choosing a Template

Click the **Template** dropdown and select:

| Template | Best For | Style |
|----------|----------|-------|
| **Modern** | Tech, consultants, startups | Gradient, rounded, pill buttons |
| **Professional** | Corporate, B2B, industrial | Dark header, structured, outlined |
| **Minimal** | Freelancers, designers, personal | White, thin borders, understated |
| **Classic** | Traditional, legal, real estate | Gradient banner, decorative |
| **Luxury** | Premium, high-end, editorial | Dark backgrounds, serif typography, cinematic |
| **Creative** | Agencies, designers, innovators | Asymmetric layouts, bold typography, editorial |

### 3.6 Publishing Your Card

1. Enable **Public Profile** toggle
2. Click **Save**, then **Submit**
3. Submitting automatically changes a **Draft** status to **Published**. Choose
   **Suspended** before submitting if you want to keep it hidden.
4. The **Public URL** field is filled automatically from the canonical domain,
   and the **QR code auto-generates** encoding exactly that URL

**Your card is now live at:** `https://your-domain.com/c/<card-slug>`

The slug becomes read-only on submit. If card details need changes later,
**Cancel → Amend** — the amendment keeps the same slug, so the QR/NFC and Public URL
field update in place; the printed card is unaffected. If the canonical domain ever
changes, the QR regenerates automatically the next time the card is saved.

### 3.7 QR Code & Sharing

Once published:
- **QR Code** appears on the card page — customers scan to view
- **Copy Link** — share the card URL directly
- **WhatsApp** — share via WhatsApp message
- **VCF Download** — "Add to Phone Book" saves contact to phone

The full card also carries the same share bar and **Send a Message** form used on
business, product and service pages, plus — for logged-in team members — the
**Share & Save Contact** strip described in §6.6. In the desk, the card record's
**Open** button beside **Public URL** opens the published card in one click (§6.2),
and §6.4 documents writing an NFC card or tag with that same URL.

---

## 4. Products & Services

### 4.1 Creating Products

![Create Product](./images/mockup/11_create_product.html)

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

![Product Pricing](./images/mockup/12_product_pricing.html)

| Price Display Mode | What Customers See |
|--------------------|--------------------|
| **Hidden** | No pricing shown |
| **Contact for Pricing** | "Contact for pricing" text, inviting an enquiry |
| **Fixed Price** | Actual price with currency |
| **Start From** | A starting price, e.g. "From INR 4,999" |

For **Fixed Price** and **Start From**:
1. Select the mode from the dropdown
2. Enter **Price** amount
3. Select **Currency** (INR, USD, etc.)

Use **Start From** for made-to-order products or anything priced from a minimum
(the page shows **"From INR 4,999"**). The Price and Currency fields only appear for
Fixed Price and Start From — Hidden and Contact need no amount.

> Services use the same four price modes. See [4.6 Creating Services](#46-creating-services).

### 4.3 Product Categories

![Product Category](./images/mockup/16_product_category.html)

Categories help organize your products:

1. Go to **Business Connect > Product Category**
2. Click **Create New Category**
3. Fill in:

| Field | Description |
|-------|-------------|
| Category Name | e.g., "Electronics", "Software", "Consulting" |
| Business | Your business |
| Description | Brief category description |
| Sort Order | Display order (lower numbers appear first; see [Featured & Sort Order](#48-featured--sort-order--how-it-works)) |

### 4.4 Product Gallery

![Product Gallery](./images/mockup/13_product_gallery.html)

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
| Sort Order | Display order (lower numbers first, Featured items above; see [Featured & Sort Order](#48-featured--sort-order--how-it-works)) |

**Gallery features:**
- Gallery thumbnails open a **fullscreen lightbox** — previous / next buttons,
  an image counter, captions, **zoom in / out / reset**, drag to pan when
  zoomed, pinch-to-zoom on phones, double-click to toggle zoom, swipe and
  keyboard shortcuts (`Esc`, `←`, `→`, `+`, `-`, `0`)
- 4-column grid on desktop, 2-column on mobile
- Lazy loading for fast page speed
- Sorted by sort order

### 4.5 Additional Product Options

| Field | Description |
|-------|-------------|
| Video URL | Embed a video on the page: a YouTube / Vimeo / Google Drive / Dailymotion link, a Nextcloud public share (`/s/…`). The player is chosen automatically. Available on products **and** services |
| Brochure | PDF file for download |
| Location | Google Maps URL for "View on Map" |
| Enquiry Enabled | Show enquiry form on product page |
| Featured | Highlight on business page (lifts the item to the top of listings — Featured items sort before everything else, then sort order) |

### 4.5a Buy Here (Purchase Link)

Sell a product from your own shopping portal:

1. On the Product (or Service) record, tick **Show Buy Here Button** under the
   **Enquiry and Purchase Link** section (one combined section covering the
   enquiry form toggle and the Buy Here button).
2. If your whole business sells in one place (Flipkart / Amazon / hosted
   store), set the **Buying Portal Link** once on the **Business** record —
   that is the default destination for every enabled item.
3. For an item that lives somewhere else, override it with the item's own
   **Shopping Portal Link**.
4. Optional **Button Label** to rename the button — e.g. "Book Now",
   "Order Here". Default is **Buy Here**.

The public page then shows the button (opens in a new tab), each tap is
counted as a **buy click** in analytics, and nothing renders for items where
the checkbox is off or no link exists.

### 4.6 Creating Services

![Create Service](./images/mockup/14_create_service.html)

1. Go to **Business Connect > Showcase Service**
2. Click **Create New Service**
3. Fill in similar to products

**Services have additional:**

| Field | Description |
|-------|-------------|
| Category | Service category (same as Product Category) |
| Features | List of features (title + description + image) |
| Gallery | Same as product gallery |
| Pricing | Price Display Mode (Hidden / Contact / Fixed / **Start From**) + Currency + Price — see [4.2 Product Pricing](#42-product-pricing) |

### 4.7 Features

Features display on both product and service pages with an optional icon beside the title.

1. Open your product or service
2. Go to **Features** section
3. Add each feature:

| Field | Description |
|-------|-------------|
| Title | Feature name (e.g., "Custom Design") |
| Description | What's included |
| Image | Optional icon or photo (48x48 displayed) |
| Sort Order | Display order |

Features display on the page with an optional image icon beside the bold title and description below it.

### 4.8 Featured & Sort Order — How It Works

Two fields control the order of products and services on the public listings:
**Featured** (a checkbox) and **Sort Order** (a number). The rule, in one line:

> **Featured first, then sort order (lowest number first).**

| Placement | Works as |
|---|---|
| Business page (`/b/<slug>`) product & service grids | Featured checkbox lifts the item to the top; Sort Order arranges the rest |
| Digital Card page (`/c/<slug>`) product & service lists | Same rule — Featured items come first, then sort order |
| Public API feeds (`/api` product/service lists) | Same rule |
| Product / Service detail pages | Not affected — every item has its own page in full |

**How Sort Order works:**
- Each Product and Service has a **Sort Order** field — a whole number, default `0`.
- **Lower numbers appear first** in listings: `5` before `10`.
- Sort order only compares items of the **same kind and same business** (products among products, services among services).
- If two items have the same sort order, they keep form order until you change the numbers.
- To interleave categories as you like, a practical pattern is numbering in steps of 10 — `10, 20, 30…` — so you can slot a new item at `15` later without renumbering everything.

**How Featured works (v1.2.7):**
- Tick **Featured** on any Published product or service.
- It moves **above all non-featured items** in every listing, regardless of sort order.
- A **★ Featured** chip appears on the item's tile in the Business page grid and the Digital Card list.
- The chip is intentionally **not shown on the item's own detail page** — the detail pages stay clean; the chip signals prominence on the list.
- Featured is a presentation signal only: it does not change search behavior, hide items, or affect whether a detail page exists.

**Where the chip shows up:**

| Page | Chip |
|---|---|
| Business product/service tile | ★ Featured (top-right of the tile) |
| Digital Card item list | ★ (compact star, top-right) |
| Product / Service detail page | none |

**Good practice:** tick Featured sparingly — most businesses run one to three featured items; re-check the listing after changes since "Featured first" also means "everything else below".

### 4.9 SEO Title & Description

Each **Business**, **Product** and **Service** has an **SEO** section with two
optional fields that control how the page appears in search results and when
shared on social apps:

| Field | Aim | What it becomes |
|---|---|---|
| **SEO Title** | 50–60 characters | The page `<title>` / `og:title` (the blue link text in Google) |
| **SEO Description** | 150–160 characters | The `meta description` / `og:description` (the snippet under the title) |

**Leave them blank and good defaults are generated:**
- Title — Product/Service: *"<Name> — <Business>"*; Business: *"<Name> — <Industry>"*
  (or *"<Name> in <City>"*).
- Description — the item's Short Description, then its full Description, then a
  location line. Any pasted formatting is stripped automatically.

Notes:
- Both are editable **even on a submitted record** — change them and save; no
  amend needed. A soft warning appears only if you go well past the suggested
  length; it never blocks saving.
- Changes appear on the live page **immediately** (the cache clears itself),
  though Google re-crawls on its own schedule before search results refresh.
- **Cards** have no SEO fields: they use the person's name and designation as
  the title and **inherit the business's SEO description** (falling back to the
  card bio) for the search snippet.
- The site root is the login screen and is intentionally hidden from search, as
  are `/offline`, `/analytics` and `/my-card`. Only published business, product,
  service and card pages are indexed, and all of them are listed in
  `/sitemap.xml`.

---

## 5. Theming & Branding

### 5.1 Choosing a Template

![Theme Form](./images/mockup/17_theme_form.html)

1. Go to **Business Connect > BC Theme**
2. Open a theme or create new
3. Select **Template**:

| Template | Layout Style |
|----------|-------------|
| **Modern** | Centered, rounded elements, gradient, soft shadows |
| **Professional** | Dark header band, horizontal layout, outlined buttons |
| **Minimal** | Clean whitespace, thin borders, understated |
| **Classic** | Gradient banner, overlapping elements, decorative |
| **Luxury** | Dark backgrounds, serif typography, cinematic |
| **Creative** | Asymmetric layouts, bold typography, editorial |

### 5.2 Layout Mode

Each theme sets a default layout mode. You can override it:

| Layout Mode | Description |
|-------------|-------------|
| **Centered** | Content centered, max-width container |
| **Wide** | Full-width sections, edge-to-edge |
| **Split** | Side-by-side grid layouts |
| **Editorial** | Magazine-style, large typography |

### 5.3 Font Category

Themes restrict available fonts:

| Font Category | Fonts | Default Theme |
|---------------|-------|---------------|
| **Sans** | Inter, Roboto, Open Sans, Lato, Poppins, Montserrat, Nunito, Raleway, Source Sans 3, Space Grotesk | Modern, Professional, Minimal, Classic |
| **Serif** | Playfair Display, Merriweather | Luxury |
| **Editorial** | Space Grotesk, Playfair Display | Creative |

### 5.4 Dark Mode

Toggle dark mode for supported themes. **Luxury** defaults to dark mode ON.

### 5.5 Color Schemes

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
| Gold | Premium gold tones |
| Custom | Your own colors |

### 5.6 Custom Colors

Select **Custom** from Color Scheme dropdown, then set:

| Field | Description |
|-------|-------------|
| Primary Color | Main brand color (buttons, links) |
| Secondary Color | Supporting color |
| Accent Color | Highlight color |
| Background Color | Page background |

### 5.7 Fonts & Button Styles

**Font Family:** Inter, Roboto, Open Sans, Lato, Poppins, Montserrat, Nunito, Source Sans 3, Raleway, Space Grotesk, Playfair Display, Merriweather, System Default

**Font Size:** Small (14px) / Default (16px) / Large (18px)

**Button Style:**
| Style | Appearance |
|-------|------------|
| Filled | Solid background color |
| Outline | Border with transparent background |
| Rounded | Rounded corners |
| Pill | Fully rounded (stadium shape) |

### 5.8 Linking Theme to Business

1. Open your Business record
2. Select the theme in **Default Theme** field
3. Save

---

## 6. Publishing & Sharing

### 6.1 Publishing Your Business

1. Open your Business record
2. Enable **Public Profile** toggle
3. Click **Save**, then **Submit**
4. Submitting automatically promotes **Status** from **Draft** to **Published**.
   If you explicitly chose **Suspended**, it stays suspended.

The business is public when it is submitted, has **Status = Published**, has
**Public Profile** enabled and is not cancelled. An already-submitted record can
still change **Status** directly — no amendment is needed.

### 6.2 Public URLs

| URL Pattern | Page |
|-------------|------|
| `/b/<business-slug>` | Business landing page |
| `/b/<business>/team/<member>` | Team member profile |
| `/b/<business>/products/<product>` | Product detail page |
| `/b/<business>/services/<service>` | Service detail page |
| `/c/<card-slug>` | Digital Card (short URL) |

All public URLs are generated automatically from the site's **canonical domain**.
You never type them, and they are the same URLs encoded in QR codes and NFC tags.
Adding a custom domain is *additive* — both addresses serve the same pages — so keep
the original address serving and already-printed links keep resolving. (Changing the
canonical domain itself re-derives the URLs; see §6.4.)

**Opening a public page from the desk:** every Business, Digital Card, Showcase
Product and Showcase Service form has an **Open** button right beside the
**Public URL** field — one click opens the live page in a new tab. No copying
the URL into the browser.

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

Every public page (business, card, product and service) has the same share bar:
**Copy**, **WhatsApp**, **SMS**, **Email** and the device's native share sheet.
Share links carry standard `utm_source=<channel>&utm_medium=share` (and
`by=<your card slug>`) so analytics can show which channel brought the visit —
and who shared it. These `utm_*` tags are ignored by Google Search Console and
never appear on the page's canonical URL, so sharing and indexing stay clean.
The copied link always uses the canonical domain, never the host you happen to
be browsing from. The Share & Save Contact form below the bar is styled to match
the public "Send a Message" form, with large tap targets on phones.

### 6.4 NFC Cards & Tags

Anything a QR code can do, an NFC card or tag can do too — and a tap feels more
premium than a scan. No special hardware is needed beyond a tag writer.

**What fits where:**

| Medium | Typical choice | Capacity notes |
|---|---|---|
| **NFC business card / collector card** (NTAG213, 144 B) | Card short URL `/c/<card-slug>` | Fits comfortably; keep it to the bare URL, no tracking params |
| **NTAG215 / sticker on a podium, reception desk, vehicle** | Business profile `/b/<business-slug>` | round stickers are the most economical; a bare URL needs ~30 B, an optional `?utm_campaign=<tag>` ~50–70 B |
| **NTAG216 or NFC key chain / wristband** (504 B+) | Product or service page for a specific line | plenty of room for long URLs + an optional `?utm_campaign=` tag |

**How to write a tag:**

1. Get the exact public URL from the desk — open the record and use the **Open**
   button beside **Public URL** (or copy it from the page's share bar; both show
   the canonical URL).
2. Optional: to measure a specific print run, append `?utm_campaign=<tag>` (e.g.
   `?utm_campaign=conf2026`). `utm_*` is ignored by search engines and never
   affects the canonical. Prefer a bare canonical URL for anything you expect to
   reprint or reuse, so the printed media stays stable.
3. Write the tag with any standards-compliant **NXP TagWriter** — as an
   **URI record**. Choose the card type the tool asks for (Web URL), paste the
   URL, lock the tag afterwards.
4. **Lock it.** Once written and encrypted-lock the tag so nobody overwrites your
   printed material with a different link.
5. Test by tapping with Android (reads the URI record directly) and an iPhone XR+
   (iOS shows a notification when a background NFC scan picks up the tag).

**Ordering blank cards:** write to info@osduotech.com for the same.

Everything above inherits the URL-safety model: slugs lock on submit, so editing
content never changes a printed URL. Adding a custom domain is additive — keep the
original hosted address serving and locked tags keep resolving. Note that changing the
canonical domain itself re-derives the public URL and regenerates the QR images, so
treat a domain switch as a migration, not a casual edit.

### 6.5 My Card

Open **/my-card** (also linked from the desk navbar and the analytics header) to
see every published card that belongs to you. **Open Card** launches it with
`?utm_source=mycard&utm_medium=share`, so your own visits are labelled correctly
in analytics.

### 6.6 Contact Exchange (login only)

When you share your card at an exhibition, show or meeting, record who you gave
it to:

1. Open your card, business, product or service page while **logged in**.
2. Fill in **Share & Save Contact**: recipient name, company, mobile, email,
   channel (WhatsApp / SMS / Email / In person), event/meeting and notes.
3. The contact is saved **as an Enquiry** — the same record and pipeline as the
   public "Send an Enquiry" form — so it appears under **Enquiries** and a CRM
   Lead is created automatically through the standard sync. Untick
   **Save as an Enquiry** if you only want to record the exchange without creating
   an enquiry.
4. Choose **Save & Share** — the app saves the exchange and opens the chosen
   channel pre-addressed to the recipient.

Only the business owner and active members see this form. Recipient details are
entered by you; the app never tries to read them out of WhatsApp, SMS or email,
because those apps do not expose that information to a browser.

Past exchanges are listed in the desk under **Contact Exchanges**
(Engagement section of the Business Connect workspace).

---

## 7. Managing Enquiries

### 7.1 Enquiry Forms

![Enquiry Form](./images/mockup/28_enquiry_form.html)

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

![Enquiry List](./images/mockup/29_enquiry_list.html)

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

![Enquiry Detail](./images/mockup/30_enquiry_detail.html)

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

![Enquiry Pipeline](./images/mockup/31_enquiry_pipeline.html)

Track your sales funnel:
- **New** → Fresh enquiries needing response
- **Ongoing** → Contacted, nurturing, qualified
- **Converted** → Successfully closed deals
- **Lost** → Unqualified or junk

---

## 8. Analytics Dashboard
(Visible only for Business and Enterprise Plan Subscription Customers)

### 8.1 Overview

![Analytics Dashboard](./images/mockup/32_analytics_dashboard.html)

1. Go to **/analytics** from the desk (requires login)
2. Select your business from the dropdown
3. Choose date range: 7, 15, 30, 90, or 365 days
4. Optionally tick **Exclude owner/member views** to hide your own team's visits

The dashboard also shows a **visitor mix** (Guest / Owner / Member / Other User /
Unknown) so you can separate real customers from internal testing.

### 8.2 Visits & Scans

**Line Chart:** Shows daily visits over time with gradient fill.

**Summary Cards:**
| Card | Tracks |
|------|--------|
| Link Visits | Direct link clicks |
| QR Scans | QR code scans |
| Cards | Digital card views |
| Products | Product page views |

### 8.3 Top Cards

See which team members' cards get the most views:
- Member name
- View count
- Rank

### 8.4 Enquiry Pipeline

Visual overview of your sales funnel:
- New enquiries
- Ongoing (contacted, nurturing, qualified)
- Converted deals
- Lost opportunities

### 8.5 Recent Activity

See the latest events:
- Event type (Card View, Product View, Enquiry, etc.)
- Visitor type (Guest, Owner, Member, Other User, Unknown)
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

![CRM Lead Detail](./images/mockup/39_crm_lead_detail.html)

| Field | Description |
|-------|-------------|
| OSDuo Business | Which business the lead belongs to |
| OSDuo Card | Which card generated the lead |
| OSDuo Product | Which product page (if applicable) |
| OSDuo Service | Which service page (if applicable) |
| OSDuo Enquiry | Link to the enquiry record |
| OSDuo Source | Where the lead came from |
| OSDuo Campaign | Campaign tracking code (or the event/meeting name for shared contacts) |
| OSDuo Landing URL | The page where enquiry was submitted |
| OSDuo Message | Message copied from the enquiry — website-form message or the channel/event notes of a Share & Save Contact exchange |

All of these are added to the **CRM Lead side panel automatically** as an
"OSDuo Attribution" section — no per-site manual layout work. If you edited the
CRM layout builder yourself, the fields are only appended when they are still
missing.

---

## 10. Roles & Permissions

### 10.1 Role Overview

| Role | Description |
|------|-------------|
| **BC Business Owner** | Full business management |
| **BC Business Manager** | Business management access |
| **BC Business Member** | General user access |
| **BC Marketing Manager** | Marketing and content management |
| **BC CRM User** | CRM integration access |
| **BC System Manager** | System configuration |

### 10.2 Permission Matrix

Actions apply within a business the user is an active member of (plus the global
`BC *` role for desk access). **BC System Manager** has full access to every business.

**Business:**
| Action | Owner | Manager | Member | Marketing |
|--------|-------|---------|--------|-----------|
| Read | Yes | Yes | Yes | Yes |
| Write | Yes | Yes | No | Yes |
| Create | Yes | No | No | No |
| Submit | Yes | Yes | No | Yes |
| Cancel / Amend | Yes | No | No | No |
| Delete | Yes | No | No | No |

**Digital Card:**
| Action | Owner | Manager | Member | Marketing |
|--------|-------|---------|--------|-----------|
| Read | Yes | Yes | Yes | – |
| Write | Yes | Yes | No | – |
| Create | Yes | Yes | No | – |
| Submit | Yes | Yes | No | – |
| Cancel / Amend | Yes | No | No | – |
| Delete | Yes | No | No | – |

**Products & Services:**
| Action | Owner | Manager | Marketing |
|--------|-------|---------|-----------|
| Read | Yes | Yes | Yes |
| Write | Yes | Yes | Yes |
| Create | Yes | Yes | Yes |
| Submit | Yes | Yes | Yes |
| Cancel / Amend | Yes | No | No |
| Delete | Yes | No | No |

**Slug lifecycle reminders**
- Slugs are free to edit while a record is a **draft**
- On **submit**, the slug becomes read-only — printed QR/NFC links can't break silently
- **Cancel → Amend** reopens a copy of the record *with the same slug* for edits
- A cancelled record no longer reserves its slug, so the amendment can reuse the URL

### 10.3 Data Isolation

- Each business sees only their own data
- BC System Managers (and System Manager) see all businesses
- Guest users can only see Published, submitted records with Public Profile enabled —
  drafts and cancelled documents are never public
- CRM Leads are scoped to business members

### 10.4 Private pages and the BC workspace

**Professional** customers stay entirely in the private portal. **Business**
customer roles (`BC Business Owner`, `BC Business Manager`, `BC Business Member`,
`BC CRM User` and `BC Marketing Manager`) may also open the Business Connect
workspace at `/desk/business-connect`. That Desk surface is themed to match the
portal and keeps its existing workspace menu and sidebar links. Public child
workspaces under the same prefix, such as `/desk/business-connect/business` and
`/desk/business-connect/member`, keep the same theme. Direct requests to other
Desk routes, including `/desk/build` and DocType paths such as
`/desk/business-connect/user`, return **Not Permitted**. The legacy
`/app/business-connect` alias and the module-qualified
`/desk/business/business-connect` spelling are also accepted so a Desk router
rewrite or refresh does not produce a 403. Because the Desk can change routes
client-side, protected data remains protected by the API and DocType plan gates
rather than by the URL alone.

| Page | Purpose |
|------|---------|
| `/desk/business-connect` | Business Connect workspace (Business customer roles, themed like the portal) |
| `/portal/team` | Invite teammates, see members and seat usage |
| `/portal/subscription` | Read-only plan, usage and upgrade information |
| `/my-card` | Own digital cards |
| `/crm`, `/crm-form/*` | Frappe CRM (Business only, plan-gated) |
| `/analytics` | Analytics dashboard (Business only) |

All private portal pages share the same left sidebar. It shows only the
sections included in your plan, plus a **Business Connect** entry for Business
customer roles. Provider users and Enterprise sites also see **Advanced admin**;
Professional customers never see Desk links.

The native **User**, **User Invitation**, **Role** and **Role Permission**
forms and lists are blocked for these customers. Frappe creates the login only
after an invitation is accepted; no `User` DocPerms are granted to customers.
Enterprise sites keep their existing Desk-based advanced administration.

After sign-in, Professional customers land on `/my-card`; Business customer
roles land on `/desk/business-connect`. Direct requests to generic Desk routes
such as `/app`, `/desk` and `/desk/build` still show **Not Permitted**.

---

## 11. Mobile App (PWA)

Every Business Connect site is an **installable Progressive Web App** — no app-store
download, no per-customer build. Each customer domain installs as its own app with its
own name, icon, and data.

### 11.1 Install on Android (Chrome)

1. Open your site's **/login** page in Chrome
2. Tap **Install** on the prompt chip — or Chrome menu (⋮) → **Install app**
3. Launch from the home-screen icon; you stay signed in like a native app

### 11.2 Install on iPhone / iPad (Safari)

1. Open your site's **/login** page in Safari
2. Tap the **Share** button → **Add to Home Screen** → **Add**
3. The app guidance chip on the login page walks you through this in-app too

### 11.3 What works offline

- Business profiles, digital cards, product and service pages you've **opened at least
  once** load instantly and still work with no connection (great for event Wi-Fi)
- Images (logos, covers, QR codes) are cached too
- Anything requiring data — logins, enquiries, desk edits — shows the branded
  **offline page** until you reconnect
- API/desk traffic is never cached, so you always see live data when online

### 11.4 Updates

App updates deploy server-side; installed apps pick them up automatically on the next
visit — no reinstall. (Bump of the app version rotates the offline cache.)

### 11.5 PWA troubleshooting

| Symptom | Fix |
|---|---|
| Chrome shows no Install prompt | The site must be served over HTTPS; also make sure you are not in a private/incognito window |
| App still shows old content after an upgrade | Hard-refresh once — the offline cache rotates on the next visit |
| The app misbehaves in other ways | Contact support — see the [Support](#support) section |

---

## 12. Troubleshooting

| Issue | Solution |
|-------|----------|
| Theme not applying | Check the Business record has a **Default Theme** selected |
| PWA does not install | The site must be served over HTTPS; see §11.5 |
| Desk **Open** button missing beside Public URL | Enterprise/Desk users: hard-refresh (Ctrl/Cmd + Shift + R). Customers should open the public `/c/<slug>` URL directly; generic Desk routes are intentionally unavailable for customer roles |
| `/app`, `/desk` or `/desk/build` shows **Not Permitted** | Expected for customer roles. Professional users stay in `/my-card`; Business users can open `/desk/business-connect` plus `/portal/team`, `/portal/subscription`, `/crm` and `/analytics` |
| Invitation email not received | Ask the provider/support to confirm outgoing SMTP is configured for the site and resend the invitation |
| Video does not play on a product or service page | Check the link is a supported share link — YouTube, Vimeo, Google Drive, Dailymotion, a Nextcloud **single-file** public share (`/s/…`). A Nextcloud **folder** share returns a zip and cannot play, and unsupported or unsafe links are skipped quietly — the page renders no video box rather than a broken one |

Anything not listed here — a QR code that won't generate, a public page that won't
open, the wrong domain in a shared link, a CRM lead that wasn't created, or any other
server-side problem — is handled for you. Just reach out:

- **Email:** connect@osduotech.com
- **Support portal:** https://www.osduotech.com/contact

---

## 13. FAQ

**Q: Can I use Business Connect without CRM?**  
A: No — Business Connect relies on the integrated CRM to manage leads, so CRM is a
required part of the platform.

**Q: How many businesses can I create?**  
A: The limit depends on your subscription plan:

- **Professional Plan:** 1 business
- **Business Plan:** 3 businesses
- **Enterprise Plan:** 5 businesses

**Each business is independent with its own team, products, and cards.**

**Q: Can guests see enquiry submissions?**  
A: No. Enquiries are only visible to business members with appropriate roles.

**Q: How do I change my card's URL?**  
A: Edit the **Slug** while the card is still a draft. Once submitted the slug locks —
that's intentional, because QR codes and NFC tags may already reference it. To change
content on a submitted card use **Cancel → Amend**; the amendment keeps the same URL.

**Q: I already printed cards with my QR codes — can I still add a custom domain?**  
A: Yes — as long as the original hosted address keeps serving. Adding a custom
domain is additive (both addresses serve the same site), so printed QR/NFC links
keep resolving through the original subdomain. Do **not** move the site to the new
domain and decommission the old one: that re-derives the URLs and breaks the printed
codes.

**Q: Is there a mobile app?**  
A: Yes — Business Connect is an installable PWA (see
[Mobile App (PWA)](#11-mobile-app-pwa)). One tap installs your domain app on Android
or iPhone, with offline viewing of previously opened pages.

**Q: Who can submit, cancel, or amend a business/card/product?**  
A: Owner, Manager, and Marketing can **submit**. Only the **Owner** (or BC System
Manager) can **cancel** or **amend**.

**Q: Can I have multiple themes?**  
A: Yes. Create multiple BC Theme records and assign different ones to different businesses or cards.

**Q: How do I add my company logo to the card?**  
A: Upload a Profile Photo on the Digital Card, or a Logo on the Business record.

**Q: Can customers download my contact info?**  
A: Yes. The VCF download button saves your contact to their phone.

**Q: How do I track where enquiries come from?**  
A: Each enquiry records its source (Digital Card, Product, Service, QR, Campaign) automatically. Share links additionally stamp the channel — `utm_source=whatsapp|sms|email|copy` (legacy `ref=share_*` links still resolve to the same labels) plus `by=<sharer's card slug>` — and Contact Exchanges flow in as Enquiries with the channel, event and notes attached.

**Q: Does it support NFC business cards?**  
A: Yes. Write your public URL to any standard NTAG21x NFC card or tag — a tap opens your digital profile exactly like a QR scan, and the tap lands with the same analytics attribution (see [NFC Cards & Tags](#64-nfc-cards--tags) for choosing, writing and locking tags).

**Q: How can I share my digital business card?**  
A: Through the personalized public URL, the QR code generated from it, an NFC card or tag, or the share bar on every public page (Copy / WhatsApp / SMS / Email / native share). Every route uses the same canonical URL, so all links stay valid.

**Q: Can customers contact my business directly?**  
A: Yes. Every public page offers one-tap channels matching what you filled in: WhatsApp, phone, email and website links, plus the enquiry form.

**Q: Is it suitable for individual professionals?**  
A: Yes. It supports individual professionals, consultants, entrepreneurs, small businesses and enterprises.

**Q: Can I customize my business profile?**  
A: Yes. Choose from the professional theme templates (BC Theme: layout, color schemes, dark mode, custom colors) to match your brand. New businesses start on the bundled default theme, and per-site branding (logo, favicon) comes built-in.

**Q: Is the platform mobile-friendly?**  
A: Yes. Every public page is designed for smartphones, tablets and desktops — and the whole site installs as your branded PWA (see [Mobile App (PWA)](#11-mobile-app-pwa)).

**Q: How much does OSDuo Business Connect cost?**  
A: Refer to https://www.osduotech.com/solutions/business-connect#section_business-connect-pricing for plan and pricing details.

**Q: How is the subscription billed?**  
A: Annually, based on the plan's minimum user commitment.

**Q: Where do I order, or change my plan?**  
A: Online at the AASRIVA marketplace (**https://www.aasriva.in**) or by contacting OSDuo Tech LLP (https://www.osduotech.com/contact).

**Q: Which plan is right for me?**  
A: All plans include the digital card, business profile, QR/NFC sharing, product & service showcase, lead capture, contact management and the mobile PWA. Higher plans add **Multiple Business Profiles**, **Team Management**, **CRM** and **Analytics** (Business), and **Advanced Administration** (Enterprise). Professional and Business customers use private portal pages; only Enterprise keeps Desk-based advanced administration. As always, feature availability is subject to the final plan configuration — confirm the entitlements for your site when you order.

**Q: How do I open my profile page without typing its URL?**  
A: Open `/my-card` in the portal and use the public card link shown there. Enterprise/Desk users can also open a Digital Card record and click **Open** beside **Public URL**.

**Q: Why do my own visits show up as "Owner"/"Member"?**  
A: Events are classified from the live session for people who are logged in. You can hide those from the dashboard with the **Exclude owner/member views** checkbox (see the Analytics Dashboard section).

---

## 14. Subscription & Add-ons

**My Subscription** (`/portal/subscription`; the legacy Desk page is still
available to provider/Enterprise users) is a read-only summary of the site's
plan, billed seats, business-profile usage and custom domains. It never shows
payment or checkout controls — billing is handled by Aasriva. The **View plans
on Aasriva** link opens the configured upgrade URL.

- Billed seats and business profiles are shown as *used of cap*. Cancelled businesses are not counted.
- Each Business Member can have exactly one Digital Card. Changing a card's display name does not create another card.
- Custom domains expire with the subscription period end. Adding a domain never changes printed QR/NFC URLs or the site's existing hostname.

**Request add-on** is a Desk workflow. Enterprise users can open the native
**Add-on Order** form; Professional/Business customers should contact the
provider/support with the add-on they need after confirming payment in Aasriva.
Available add-ons:

| Add-on | Price | Notes |
|--------|-------|-------|
| Additional User | ₹595 / ₹895 / ₹1,295 per year | One order adds one user seat. Price depends on your active plan; the provider applies the seat after confirming payment in Aasriva. |
| Custom Domain Service | ₹5,999 / year | First Enterprise mapping is included at ₹0; every other mapping is paid. |
| Domain Registration / Renewal | Actual cost | Attach a quote or vendor invoice; the provider bills at cost. |

Only add-ons available for your **current active plan** are shown. Higher-plan add-ons appear after the provider upgrades the site through Aasriva; you cannot choose another plan in an Add-on Order.

You can only submit an order as **Requested**. The Administrator reviews it and moves it through **Requested → Approved → Configured → Verified → Active**. Domain Registration orders let you attach supporting documents and require a quote; the **Invoice** attachment is Administrator-only. An Active custom-domain order creates a domain mapping automatically; expired mappings and orders are handled by the daily scheduler.

---

## Support

- **User Manual:** https://www.osduotech.com/business-connect-manual
- **Email:** connect@osduotech.com
- **Support portal:** https://www.osduotech.com/contact

