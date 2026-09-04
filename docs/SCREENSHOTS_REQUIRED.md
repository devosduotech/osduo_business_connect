# OSDuo Business Connect — Screenshots Required

**Purpose:** Visual guide for User Manual  
**Total Images:** 43  
**Naming Convention:** `XX_description.png` (XX = sequence number)  
**Output Directory:** `docs/images/`

---

## Capture Settings

| Context | Viewport | Format |
|---------|----------|--------|
| Desk pages | 1280 × 800 | PNG |
| Public pages (mobile) | 375 × 812 | PNG |
| Public pages (desktop) | 1280 × 800 | PNG |
| Mockups (HTML files) | 1280 × auto height | PNG |

---

## Section 2: Setting Up Your Business

| # | Filename | Description | How to Capture | Viewport | Notes |
|---|----------|-------------|----------------|----------|-------|
| 01 | `01_workspace_overview.png` | Business Connect workspace with shortcuts and card sections | Navigate to `/app/business-connect` | Desktop | Full page, show all 8 shortcuts and 4 card sections |
| 02 | `02_create_business_form.png` | Business creation form with all fields | Click "Create New Business" from workspace or list | Desktop | Show slug, name, owner_user, contact fields |
| 03 | `03_business_list.png` | Business list view showing existing businesses | Navigate to `/app/business` | Desktop | Show list with status column |
| 04 | `04_add_member.png` | Business Member creation form | Open Business > Members tab > Add Member | Desktop | Show user, person_name, role, designation fields |
| 05 | `05_member_roles.png` | Role dropdown with all 5 options | Click Role dropdown on Business Member form | Desktop | Show Owner/Manager/Member/Marketing/CRM User |

---

## Section 3: Digital Business Cards

| # | Filename | Description | How to Capture | Viewport | Notes |
|---|----------|-------------|----------------|----------|-------|
| 06 | `06_create_card.png` | Digital Card creation form | Navigate to `/app/digital-card` > Create | Desktop | Show business, member, display_name, slug fields |
| 07 | `07_card_slug.png` | Slug field with validation message | Enter invalid slug (uppercase, spaces) to trigger validation | Desktop | Show error message |
| 08 | `08_card_links.png` | Social links child table | Add 2-3 links in Digital Card Links table | Desktop | Show platform dropdown, label, value columns |
| 09 | `09_card_options.png` | Show products/services toggles | Scroll to display options section | Desktop | Show show_business, show_products, show_services checkboxes |
| 10 | `10_card_published.png` | Card in Published status with QR | Set card to Published, save, show QR section | Desktop | Show status badge and QR image |

---

## Section 4: Products & Services

| # | Filename | Description | How to Capture | Viewport | Notes |
|---|----------|-------------|----------------|----------|-------|
| 11 | `11_create_product.png` | Product creation form | Navigate to `/app/showcase-product` > Create | Desktop | Show business, product_name, slug, description fields |
| 12 | `12_product_pricing.png` | Price display mode dropdown | Click Price Display Mode dropdown | Desktop | Show Hidden / Contact for Pricing / Fixed Price options |
| 13 | `13_product_gallery.png` | Gallery child table with images | Add 3-4 images to Product Gallery Items | Desktop | Show image thumbnails, caption, alt_text, sort_order |
| 14 | `14_create_service.png` | Service creation form | Navigate to `/app/showcase-service` > Create | Desktop | Show business, service_name, slug, description fields |
| 15 | `15_service_benefits.png` | Benefits child table | Add 3-4 benefits to Service Benefits | Desktop | Show title, description columns |
| 16 | `16_product_category.png` | Product Category creation form | Navigate to `/app/product-category` > Create | Desktop | Show category_name, business, description fields |

---

## Section 5: Theming & Branding

| # | Filename | Description | How to Capture | Viewport | Notes |
|---|----------|-------------|----------------|----------|-------|
| 17 | `17_theme_form.png` | BC Theme form with all options | Navigate to `/app/bc-theme` > Open existing theme | Desktop | Show all fields: template, colors, fonts, buttons |
| 18 | `18_template_dropdown.png` | Template selection dropdown | Click Template dropdown | Desktop | Show Modern / Professional / Minimal / Classic |
| 19 | `19_color_schemes.png` | Color scheme dropdown | Click Color Scheme dropdown | Desktop | Show all 8 presets + Custom |
| 20 | `20_custom_colors.png` | Custom color pickers | Select "Custom" color scheme | Desktop | Show primary_color, secondary_color, accent_color, background_color pickers |
| 21 | `21_font_options.png` | Font family and size dropdowns | Click Font Family dropdown | Desktop | Show all 10 font options and 3 size presets |
| 22 | `22_button_styles.png` | Button style dropdown | Click Button Style dropdown | Desktop | Show Filled / Outline / Rounded / Pill |

---

## Section 6: Public Pages

| # | Filename | Description | How to Capture | Viewport | Notes |
|---|----------|-------------|----------------|----------|-------|
| 23 | `23_public_card.png` | Full digital card page | Visit `/c/<card-slug>` | **Mobile** | Full page scroll, show avatar, name, buttons, social links |
| 24 | `24_public_business.png` | Business landing page | Visit `/b/<business-slug>` | **Mobile** | Hero, about, products, services, contact sections |
| 25 | `25_public_product.png` | Product detail page | Visit `/b/<biz>/products/<product>` | **Mobile** | Description, gallery, pricing, enquiry form |
| 26 | `26_public_service.png` | Service detail page | Visit `/b/<biz>/services/<service>` | **Mobile** | Description, benefits, enquiry form |
| 27 | `27_qr_code.png` | QR code display on card page | Scroll to QR section on card page | **Mobile** | Show QR code image and "Scan to view card" text |

---

## Section 7: Managing Enquiries

| # | Filename | Description | How to Capture | Viewport | Notes |
|---|----------|-------------|----------------|----------|-------|
| 28 | `28_enquiry_form.png` | Enquiry form on public page | Visit any card/product/service page, scroll to enquiry form | **Mobile** | Show name, email, phone, message fields and submit button |
| 29 | `29_enquiry_list.png` | Enquiry list in desk | Navigate to `/app/enquiry` | Desktop | Show list with status, visitor_name, source columns |
| 30 | `30_enquiry_detail.png` | Enquiry detail with CRM Lead link | Open an enquiry that has CRM sync | Desktop | Show visitor info, CRM Lead link, status, submitted_at |
| 31 | `31_enquiry_pipeline.png` | Enquiry status pipeline | Show Enquiry list filtered by status | Desktop | Show counts for New / Ongoing / Converted / Lost |

---

## Section 8: Analytics Dashboard

| # | Filename | Description | How to Capture | Viewport | Notes |
|---|----------|-------------|----------------|----------|-------|
| 32 | `32_analytics_dashboard.png` | Full analytics dashboard | Navigate to `/app/analytics` | Desktop | Full page showing all sections |
| 33 | `33_analytics_chart.png` | SVG line chart closeup | Scroll to chart section | Desktop | Show line chart with gradient fill and dots |
| 34 | `34_analytics_summary.png` | Summary cards | Show top section of analytics | Desktop | 4 cards: Link Visits, QR Scans, Cards, Products |
| 35 | `35_analytics_top_cards.png` | Top cards table | Scroll to Top Cards section | Desktop | Show member name, views, rank |
| 36 | `36_analytics_pipeline.png` | Enquiry pipeline section | Scroll to Enquiry Pipeline | Desktop | Show New / Ongoing / Converted / Lost counts |
| 37 | `37_analytics_recent.png` | Recent activity table | Scroll to Recent Activity | Desktop | Show event type, member, device, browser columns |

---

## Section 9: CRM Integration

| # | Filename | Description | How to Capture | Viewport | Notes |
|---|----------|-------------|----------------|----------|-------|
| 38 | `38_crm_lead_list.png` | CRM Lead list with BC columns | Navigate to CRM Lead list, add custom columns | Desktop | Show lead_name, osduo_business, osduo_source, status |
| 39 | `39_crm_lead_detail.png` | CRM Lead detail with custom fields | Open a lead created from enquiry | Desktop | Show OSDuo Business, Card, Product, Service, Enquiry fields |
| 40 | `40_crm_status_sync.png` | Status dropdown showing sync | Change CRM Lead status from "New" to "Contacted" | Desktop | Show status change and note about enquiry sync |

---

## Section 10: Roles & Permissions

| # | Filename | Description | How to Capture | Viewport | Notes |
|---|----------|-------------|----------------|----------|-------|
| 41 | `41_roles_list.png` | BC roles in System Settings | Navigate to `/app/role` and search "OSDuo" | Desktop | Show all 7 OSDuo roles |

---

## Section 11: Administration

| # | Filename | Description | How to Capture | Viewport | Notes |
|---|----------|-------------|----------------|----------|-------|
| 42 | `42_site_config.png` | allowed_referrers in site_config.json | Open site_config.json in editor | Desktop | Show `allowed_referrers` array with domain |
| 43 | `43_theme_comparison.png` | Side-by-side theme comparison | Open `business_connect_themes/mockups/all_themes_comparison.html` in browser | Desktop | Show all 4 card themes and 4 business themes |

---

## Mockup Screenshots (from existing HTML)

These can be screenshotted directly from the mockup HTML files:

| # | Source File | Description |
|---|-------------|-------------|
| 43 | `business_connect_themes/mockups/all_themes_comparison.html` | Theme comparison grid |
| — | `business_connect_themes/mockups/card_modern.html` | Modern card template |
| — | `business_connect_themes/mockups/card_professional.html` | Professional card template |
| — | `business_connect_themes/mockups/card_minimal.html` | Minimal card template |
| — | `business_connect_themes/mockups/card_classic.html` | Classic card template |
| — | `business_connect_themes/mockups/business_modern.html` | Modern business profile |
| — | `business_connect_themes/mockups/product_modern.html` | Modern product page |
| — | `business_connect_themes/mockups/service_modern.html` | Modern service page |
| — | `business_connect_themes/mockups/color_schemes.html` | 8 color scheme swatches |
| — | `business_connect_themes/mockups/button_styles.html` | 4 button style variants |

---

## Capture Checklist

- [ ] Desk screenshots (01–22, 29–42): 28 images
- [ ] Public page screenshots (23–28): 6 images at mobile viewport
- [ ] Mockup screenshots (43 + 10 extras): 11 images
- [ ] Total: 45 images (43 required + 2 bonus)

## Post-Processing

- [ ] Crop to relevant area if full-page is too long
- [ ] Add red border/arrow annotations for form fields (optional)
- [ ] Ensure text is readable at 100% zoom
- [ ] Save as PNG, max 1MB per image
- [ ] Place in `docs/images/` directory
