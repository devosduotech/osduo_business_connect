# Phase 3 — Theme Design System v2

**Target Release:** v1.0.2  
**Priority:** High  
**Source:** Design review (Sep 2026)

---

## Overview

Move from "four HTML designs" to "one coherent Business Connect design system with four visual personalities."

---

## Current Assessment

| Area | Themes | Status |
|------|--------|--------|
| Digital Card | Modern, Professional, Minimal, Classic | Good — strongest area |
| Business Profile | Modern, Professional, Minimal, Classic | Needs work |
| Product/Service | Modern, Professional, Minimal, Classic | Good foundation |
| Gallery | Shared component | Correct approach |
| Color schemes | 7 presets + Custom | Useful |
| Button styles | Multiple styles | Needs consolidation |

---

## P0 — Design System Foundation

### 1. Remove Inline CSS

Replace all `style="..."` with theme CSS classes:

| Before | After |
|--------|-------|
| `style="border-radius:0;"` | `class="bc-btn bc-btn-square"` |
| `style="background:var(--bc-primary);"` | `class="bc-nav-primary"` |
| `style="font-size:1.5rem;"` | `class="bc-text-xl"` |

### 2. Theme vs Color Scheme Separation

**Theme controls:** layout, typography, spacing, cards, navigation, hero, button shape, visual hierarchy

**Color Scheme controls:** primary, secondary, accent, background, text, borders

```
Theme + Color Scheme = Final Presentation

Examples:
  Modern + Blue
  Modern + Green
  Professional + Custom
```

### 3. Design Tokens

- Typography scale (common across all themes)
- Spacing scale (consistent tokens)
- Button system (theme-driven, not user-configurable)
- Card system (consistent components)

---

## P1 — Digital Card

### 1. Save Contact as Primary CTA

Current: Call / WhatsApp / Email / Website (all equal)

Proposed:
```
Primary:   [ Save Contact ]  (VCF download)
Secondary: [ WhatsApp ] [ Call ]
Tertiary:  [ Email ] [ Website ]
```

### 2. Improve Mobile-First Layout

Card optimized for 375px viewport.

### 3. Make Four Themes More Distinctive

| Theme | Visual Language |
|-------|----------------|
| Modern | Contemporary, digital, rounded, gradient |
| Professional | Corporate, structured, restrained, strong typography |
| Minimal | Whitespace, typography, almost no decoration |
| Classic | Traditional, elegant, framed sections, stronger typography |

### 4. Card Structure

```
┌─────────────────────────┐
│       COVER / BRAND     │
│          [PHOTO]        │
│     Name                │
│     Designation         │
│     Business            │
│     Short bio           │
│ [ Save Contact ]        │
│ [ WhatsApp ] [ Call ]   │
│ LinkedIn  Website       │
│       QR CODE           │
└─────────────────────────┘
```

---

## P1 — Business Profile

### 1. Strengthen Company Identity Hero

```
┌───────────────────────────────────────┐
│         COVER IMAGE / BRAND           │
│              [ LOGO ]                 │
│         Company Name                  │
│      Tagline / Industry               │
│         Chennai, India                │
│ [ WhatsApp ] [ Call ] [ Enquiry ]     │
├───────────────────────────────────────┤
│ About │ Products │ Services │ Contact │
└───────────────────────────────────────┘
```

### 2. Other Improvements

- Improve product/service cards (more visual)
- Add business facts/highlights (team size, products, customers)
- Improve mobile navigation
- Make Modern/Professional more premium

---

## P1 — Product/Service

### 1. Product Image Should Dominate

Hierarchy:
```
Product Image
     ↓
Product Name
     ↓
Short Description
     ↓
Price / Contact for Pricing
     ↓
Primary Enquiry Action
     ↓
Description
     ↓
Gallery / Video / Brochure
```

### 2. Other Improvements

- More prominent enquiry CTA
- Clearer price/contact-pricing visual treatment
- Better gallery (lightbox, captions, navigation)
- Related products/services section

---

## P2 — Configuration Simplification

Expose only:
```
Theme        [ Modern ▼ ]
Color Scheme [ Blue ▼ ]
Logo         [ Upload ]
Cover Image  [ Upload ]
Custom Brand [ Optional ]
```

Not: button border, shadow, typography, spacing, etc.

---

## Theme Scores

| Theme | Card | Business | Product |
|-------|------|----------|---------|
| Modern | 9/10 | 9/10 | 8.5/10 |
| Professional | 9/10 | 9/10 | 9/10 |
| Minimal | 8.5/10 | 8/10 | 8/10 |
| Classic | 7.5/10 | 7.5/10 | 7.5/10 |

## Recommended Default Combinations

| Combination | Target Audience |
|-------------|-----------------|
| Modern + Blue | Default |
| Professional + Blue | B2B/Industrial |
| Minimal + Custom | Professionals/Personal branding |
| Classic + Custom | Traditional businesses |

---

## Key Principle

> Four is enough. Make existing four genuinely distinctive. Let Color Scheme + Logo + Cover Image + Content create customer-specific identity. This gives hundreds of visual combinations without hundreds of templates.

---

## Implementation Order

1. P0: Design system foundation (CSS cleanup, tokens, variables)
2. P1: Digital Card (Save Contact, theme distinction)
3. P1: Business Profile (identity hero, cards, facts)
4. P1: Product/Service (image dominance, gallery, related)
5. P2: Configuration simplification
