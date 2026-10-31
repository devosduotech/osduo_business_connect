# SaaS Implementation Plan: OSDuo Business Connect

> **Status (v1.2.0):** The SaaS *foundation* is live — one bench serving many customer
> sites on hosted wildcard subdomains plus bring-your-own domains, per-customer branded
> installable PWAs with offline support, canonical NFC/QR public URLs, and hard
> per-business data isolation with a submit/cancel/amend lifecycle
> ([Installation Guide](INSTALLATION_GUIDE.md) · [PWA](PWA.md) ·
> [User Manual](USER_MANUAL.md)). The tier/quota enforcement (`BC Subscription`) and
> SEO-engine items below remain **planned**.

## 1. Objective
Transform OSDuo Business Connect from a feature-set application into a tiered SaaS product. This involves implementing strict resource quotas (users and businesses), gating advanced modules (CRM), and introducing an SEO engine to provide marketing value to the end-user.

---

## 2. SaaS Tier Architecture

### 2.1 Tier Definition Matrix

| Feature | **Solo / Professional** | **MSME** | **Enterprise** |
| :--- | :--- | :--- | :--- |
| **User Limit** | 1 User (Owner Only) | Multiple Users | Multiple Users |
| **Business Limit** | 1 Business Profile | 1 Business Profile | Multiple Business Profiles |
| **CRM Access** | ❌ Disabled | ✅ Enabled | ✅ Enabled |
| **SEO Tools** | Basic (Title/Desc) | Advanced (Analytics/Keywords) | Full (Multi-site SEO/Reporting) |
| **Target Audience** | Freelancers, Solo-preneurs | Small to Mid-sized Agencies | Conglomerates, Holding Co's |

---

## 3. Technical Implementation Roadmap

### 3.1 Subscription Management
- **New DocType: `BC Subscription`**
    - `user`: Link to User
    - `tier`: Select (Solo, MSME, Enterprise)
    - `status`: Select (Active, Expired, Trial)
    - `start_date` / `end_date`: Date fields
- **Default Assignment**: New users are automatically assigned to the `Solo` tier upon first sign-up/onboarding.

### 3.2 Resource Quota Enforcement (Logic Layer)
- **Business Creation Gate**:
    - Modify `osduo_business_connect/business/core.py`.
    - Implementation: Before inserting a new `Business` record, query the `BC Subscription` for the current user. If `tier == Solo` and `count(Business) >= 1`, throw a `frappe.ValidationError`.
- **User Assignment Gate**:
    - Modify `osduo_business_connect/business/doctype/business_member/business_member.py`.
    - Implementation: On adding a member, check the business owner's tier. If `Solo`, restrict addition of any member other than the owner.

### 3.3 CRM Module Gating
- **Access Guard**:
    - Create a utility function `check_crm_access()` in `osduo_business_connect/permissions/`.
    - Implementation: Check if `user.tier` is `MSME` or `Enterprise`.
- **Application Points**:
    - Wrap all controllers in `osduo_business_connect/enquiry/` and `osduo_business_connect/crm_integration/` with this guard.
    - Return a custom error/message: *"CRM features are available in MSME and Enterprise tiers. Please upgrade your plan."*

---

## 4. SEO Capability Implementation

To increase the value proposition for SaaS customers, the following SEO engine will be implemented for the public pages (Business, Product, Service).

### 4.1 On-Page SEO Metadata
- **Field Extensions**: Add the following fields to `Business`, `Showcase Product`, and `Showcase Service` DocTypes:
    - `seo_title`: Custom title for browser tabs/search results.
    - `seo_description`: Meta description for search snippets.
    - `seo_keywords`: Comma-separated keywords.
    - `og_image`: OpenGraph image for social media sharing.
- **Template Integration**: Update `bc_base.html` to dynamically inject these variables into the `<head>` section.

### 4.2 Search Engine Optimization Logic
- **Slug Optimization**: Ensure slugs are generated based on the `title_field` for better URL readability.
- **Sitemap Generation**: Implement a dynamic `sitemap.xml` generator that lists all "Published" business profiles, products, and services.
- **Canonical URLs**: Implementation of `<link rel="canonical">` tags to prevent duplicate content issues across different templates.

### 4.3 Tiered SEO Features
- **Solo**: Access to `seo_title` and `seo_description` only.
- **MSME/Enterprise**: Access to keyword tracking, OG image customization, and advanced SEO analytics (tracking how many users arrived via search vs. direct link).

---

## 5. Success Metrics & Validation
- [ ] **Test Solo**: Verify that a second business cannot be created.
- [ ] **Test Solo**: Verify that adding a business member is blocked.
- [ ] **Test Solo**: Verify that accessing `/api/method/.../crm_...` returns a tier restriction error.
- [ ] **Test MSME**: Verify that CRM access is granted but business count is limited to 1.
- [ ] **Test Enterprise**: Verify that multiple businesses can be created and managed.
- [ ] **Test SEO**: Verify that `<meta>` tags in the browser source match the DocType fields.
