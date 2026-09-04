# OSDuo Business Connect — Theme System

## Overview

Business Connect provides 4 distinct page templates (layouts) that control the visual structure of Business Profiles, Digital Cards, Product pages, and Service pages.

Each template can be customized with:
- **8 Color Schemes** (7 presets + Custom)
- **10 Font Families**
- **3 Font Sizes**
- **4 Button Styles**

---

## Templates (Layouts)

### 1. Modern
**Style:** Centered, rounded avatar with shadow, pill buttons, soft gradients

**Best for:** Tech startups, creative agencies, modern brands

**Key visual elements:**
- Centered layout
- Rounded avatar with subtle shadow
- Pill-shaped buttons
- Soft gradient backgrounds
- Card-based sections

**Files:**
- `card/hero_modern.html`
- `business/hero_modern.html`
- `product/hero_modern.html`

---

### 2. Professional
**Style:** Colored header band, horizontal layout, outlined buttons, clean lines

**Best for:** Corporate businesses, law firms, consulting, finance

**Key visual elements:**
- Colored header band
- Horizontal card layout
- Outlined/ghost buttons
- Clean geometric lines
- Professional typography

**Files:**
- `card/hero_professional.html`
- `business/hero_professional.html`
- `product/hero_professional.html`

---

### 3. Minimal
**Style:** No background, uppercase labels, thin borders, square buttons, whitespace-heavy

**Best for:** Photography, design studios, minimalist brands, luxury

**Key visual elements:**
- Clean whitespace
- Uppercase section labels
- Thin borders
- Square/rectangular buttons
- Subtle typography

**Files:**
- `card/hero_minimal.html`
- `business/hero_minimal.html`
- `product/hero_minimal.html`

---

### 4. Classic
**Style:** Gradient banner, avatar overlapping edge, decorative dividers, traditional layout

**Best for:** Restaurants, hospitality, traditional businesses, healthcare

**Key visual elements:**
- Gradient banner header
- Avatar overlapping header edge
- Decorative dividers
- Traditional column layout
- Warm, inviting feel

**Files:**
- `card/hero_classic.html`
- `business/hero_classic.html`
- `product/hero_classic.html`

---

## Color Schemes

| Scheme | Primary | Accent | Best For |
|--------|---------|--------|----------|
| Violet | #7C3AED | #A78BFA | Creative, luxury |
| Indigo | #4F46E5 | #818CF8 | Tech, SaaS |
| Blue | #2563EB | #60A5FA | Corporate, trust |
| Green | #16A34A | #4ADE80 | Health, eco, food |
| Yellow | #EAB308 | #FDE047 | Energy, youth |
| Orange | #EA580C | #FB923C | Food, retail |
| Red | #DC2626 | #F87171 | Bold, passion |
| Custom | User-defined | User-defined | Brand-specific |

---

## Font Families

| Font | Style |
|------|-------|
| System Default | OS-native |
| Inter | Modern, clean |
| Roboto | Google classic |
| Open Sans | Neutral, readable |
| Lato | Friendly, warm |
| Poppins | Geometric, modern |
| Montserrat | Elegant, bold |
| Nunito | Rounded, friendly |
| Source Sans 3 | Professional |
| Raleway | Thin, elegant |

---

## Button Styles

| Style | Description |
|-------|-------------|
| Filled | Solid background, white text |
| Outline | Border only, transparent background |
| Rounded | Rounded corners (12px) |
| Pill | Fully rounded (999px) |

---

## File Structure

```
business_connect_themes/
├── README.md                 # This file
├── card/                     # Digital Card themes
│   ├── card.html            # Main card template
│   ├── hero_modern.html     # Modern layout
│   ├── hero_professional.html
│   ├── hero_minimal.html
│   └── hero_classic.html
├── business/                 # Business Profile themes
│   ├── business.html        # Main business template
│   ├── hero_modern.html
│   ├── hero_professional.html
│   ├── hero_minimal.html
│   └── hero_classic.html
└── product/                  # Product/Service themes
    ├── product.html         # Main product template
    ├── hero_modern.html
    ├── hero_professional.html
    ├── hero_minimal.html
    └── hero_classic.html
```

---

## CSS Variables

Each theme generates CSS custom properties:

```css
--bc-primary: #2563EB;      /* Primary color */
--bc-secondary: #FFFFFF;    /* Secondary color */
--bc-accent: #60A5FA;       /* Accent color */
--bc-bg: #F8FAFC;           /* Background */
--bc-font: #1E293B;         /* Text color */
--bc-font-family: Inter;    /* Font family */
--bc-font-size: 16px;       /* Base font size */
--bc-button-style: Filled;  /* Button variant */
```

---

## Theme Resolution Priority

1. **Page-level theme** — Theme assigned to specific Business/Card/Product
2. **Business default** — Theme set on the Business record
3. **System default** — Fallback to Blue/Modern
