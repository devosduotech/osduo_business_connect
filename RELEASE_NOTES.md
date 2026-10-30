# Release Notes - business_connect (v1.1.0)

**Release Date:** 30 October 2026  
**Version:** v1.1.0

This release focuses on a comprehensive design overhaul of the public-facing pages, introducing a unified design system and professional templates for a superior user experience.

---

## New Features (v1.1.0)

### Theme Redesign & Unified UI
- Full redesign of the Professional, Modern, Minimal, and Classic templates across Digital Cards, Business Profiles, Product, and Service pages.
- Implementation of a coordinated design system with a focused layout (Centered/Wide/Split/Editorial).
- New high-contrast color schemes (Violet, Indigo, Blue, Green, Yellow, Orange, Red, Gold) with automatic contrast correction for accessibility.
- Unified header architecture across all pages for consistent branding (Logo + Company Name).

### Analytics & CRM Enhancements
- Integration of guest-safe client-side event tracking using `navigator.sendBeacon`.
- New analytics events: `card_view`, `product_view`, `service_view`, `phone_click`, `email_click`, `whatsapp_click`, `website_click`, `brochure_download`, and `enquiry_submitted`.
- Enhanced CRM context tracking (UTM campaigns and landing URLs) passed directly from the public pages to the lead generation pipeline.

### UI/UX Improvements
- Optimized Digital Card shell (420px) for mobile-first viewing.
- Improved image handling with `object-fit: cover` to ensure profile and product images are displayed correctly without distortion.
- Added read-only Public URLs in the admin panel for easy sharing of Business, Product, and Service pages.

---

# Release Notes - business_connect (v1.0.2)

**Release Date:** 28 October 2026  
**Version:** v1.0.2

This release introduces comprehensive features to streamline business management, including dynamic digital card generation, CRM integration with Frappe, real-time analytics dashboard, and a complete product showcase platform.

---

## New Features (v1.0.2)

### Digital Card Generation
- 6 professional templates: Simple, Business Professional, Corporate Blue, Minimalist Black, Modern Red, Luxury Gold
- QR code-enabled sharing for contactless business cards
- NFC tag support for premium card experiences  
- VCF file download capability for seamless contact importing

### Frappe CRM Integration
- Automatic lead management on enquiries received through the platform
- Seamless data synchronization between business connect and your Frappe ERP/CRM instance
- Real-time pipeline tracking of customer interactions

### Analytics Dashboard
- Track website visits in real time
- Monitor digital card scans and engagement metrics
- Identify top-performing cards and products
- View enquiry pipeline progress with visual analytics

---

## Product Showcase & Catalog

### Business Profile Management
- Hero section with customizable images and/or video background
- About section for business storytelling
- Products showcase with image gallery  
- Detailed product pages with pricing, descriptions, brochures (PDF download)
- Service listing pages highlighting features and locations

---

## Technical Improvements

- Enhanced lead generation engine powered by Frappe CRM
- Improved performance optimization across all modules  
- Better integration between product catalog and service listings
- Real-time data synchronization using webhooks

---

## Security Updates

All user-facing code has been reviewed against security best practices, with enhanced input validation for the lead generation pipeline.

---

## Known Issues & Future Roadmap

- Some advanced Frappe API features may require additional configuration  
- Scheduled release for v1.1.0 includes planned improvements to analytics depth and mobile responsiveness  

---

**For support:** [Contact Support](/support) | **Development updates:** [GitHub Repository](https://github.com/opencode-team/business_connect) | **Documentation:** [Full API Reference](/docs/api-reference.md)