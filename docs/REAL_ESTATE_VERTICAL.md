# Business Connect — Real Estate Vertical

**Status:** Future Work (Post v1.0.1)  
**Date:** September 2026  
**Author:** Product Strategy

---

## 1. Positioning

Business Connect should **not become a real-estate application**. Instead, make Real Estate a **vertical use case/profile type** on top of the existing platform.

### Current

> **Business Connect — Digital identity for businesses and professionals**

### Real Estate

> **Your digital property profile + digital visiting card + property catalogue + lead capture**

An agent gets:

```
Agent
  │
  ├── Digital Card
  │
  ├── Agent Profile
  │
  ├── Properties
  │     ├── For Sale (Products)
  │     ├── For Rent (Services)
  │     └── Sold / Rented
  │
  ├── Services
  │     ├── Property Sales
  │     ├── Rentals
  │     ├── Property Management
  │     └── Consultation
  │
  └── Leads
        ├── Enquiries
        ├── Property enquiries
        └── Follow-ups
```

---

## 2. Existing Product/Service as Property — The Shortcut

For the first Real Estate version, **do not create a separate Property DocType**. Use the existing Product and Service:

### Mapping

| Business Connect | Real Estate |
|-----------------|-------------|
| Product | Property for Sale |
| Service | Property for Rent |
| Benefits child table | Property Details |

### Normal Business

```
Product
  └── Product details

Service
  ├── Service details
  └── Benefits
```

### Real Estate

```
Product
  └── Property for Sale

Service
  └── Property for Rent
      └── Property Details (from Benefits child table)
```

---

## 3. Benefits → Property Details (Label + Value)

The existing `ServiceBenefit` child table should be conceptually treated as a generic **Label + Value** structure:

### Normal Service

```
Benefits

✓ Free consultation
✓ Installation support
✓ Annual maintenance
✓ 24×7 support
```

### Real Estate

```
Property Details

Bedrooms          3
Bathrooms         3
Built-up Area     1,850 sq.ft
Parking           2
Floor             8
Facing            East
Furnishing        Semi Furnished
```

### Other Verticals (Future)

| Business Type | Child table displayed as |
|---------------|--------------------------|
| General | Benefits |
| Real Estate | Property Details |
| Consultant | Key Benefits |
| Manufacturer | Technical Specifications |
| Professional | Highlights |
| Service Provider | Service Benefits |

---

## 4. Property Detail Fields (via Benefits child table)

```
Property Details
────────────────────────────
Label              Value
────────────────────────────
Bedrooms           3
Bathrooms          3
Built-up Area      1,850 sq.ft
Carpet Area        1,650 sq.ft
Parking            2 Cars
Floor              8
Total Floors       14
Facing             East
Furnishing         Semi Furnished
Property Status    Ready to Move
```

---

## 5. Additional Property Data Model

### Property (Product/Service)

Core fields already exist:

```
Property Name
Description
Price
Category (Property Type)
Location
Image
Gallery
Video
```

### Future: Dedicated Property DocType (Post-MVP)

If the Product/Service shortcut becomes limiting, a proper Property DocType would include:

```
Property
────────────────────────────
Property Name
Property Type        Apartment / Villa / Plot / Commercial
Listing Type         Sale / Rent
Status               Active / Sold / Rented / Draft

Location
Address
City
Area
Pincode
Latitude
Longitude

Pricing
Price
Price Type           Fixed / Negotiable / Contact

Property Details
Bedrooms / Bathrooms / Built-up Area / Carpet Area
Floor / Total Floors / Facing / Parking / Furnishing

Description
Cover Image / Gallery / Video / Virtual Tour
Amenities
Agent / Business
```

---

## 6. Business Type Concept

Introduce a **Business Type** field on the Business DocType:

```
Business Type
─────────────
General Business
Professional
Real Estate
Consultant
Service Provider
Manufacturer
Trader
Other
```

When `Business Type = Real Estate`:

- Terminology changes: Products → Properties for Sale, Services → Properties for Rent
- Property Details section renders instead of Benefits
- Property-specific filters activate on public pages
- Analytics dashboard shows property-specific metrics

---

## 7. Public Real Estate Pages

### Agent Business Profile

```
connect.osduotech.com/b/arun-properties

┌───────────────────────────────────────┐
│              [PHOTO]                  │
│                                       │
│          Arun Kumar                   │
│          Real Estate Consultant       │
│          Chennai                      │
│                                       │
│ [ WhatsApp ] [ Call ] [ Enquire ]    │
└───────────────────────────────────────┘

Home | Properties | Services | About

FEATURED PROPERTIES

┌─────────────────┐  ┌─────────────────┐
│     PHOTO       │  │     PHOTO       │
│                 │  │                 │
│  3 BHK Apartment│  │  Villa          │
│  Anna Nagar     │  │  ECR            │
│  ₹1.85 Cr       │  │  ₹3.20 Cr       │
│                 │  │                 │
│ [View Property] │  │ [View Property] │
└─────────────────┘  └─────────────────┘

SERVICES

Property Sales | Property Rentals | Consultation

CONTACT

[ Name ]
[ Phone ]
[ Interested Property ▼ ]
[ Message ]
[ Send Enquiry ]
```

### Individual Property Page

```
connect.osduotech.com/b/arun-properties/properties/anna-nagar-3bhk

┌───────────────────────────────────────────┐
│              PROPERTY IMAGE               │
└───────────────────────────────────────────┘

3 BHK Premium Apartment
Anna Nagar, Chennai

₹1.85 Crore

3 Beds   3 Baths   1,850 sq.ft

[ WhatsApp ]   [ Call ]
[ Schedule a Site Visit ]

PROPERTY DETAILS

┌─────────────────┬─────────────────┐
│ Bedrooms        │ 3               │
│ Bathrooms       │ 3               │
│ Built-up Area   │ 1,850 sq.ft     │
│ Parking         │ 2 Cars          │
│ Floor           │ 8               │
│ Facing          │ East            │
│ Furnishing      │ Semi Furnished  │
└─────────────────┴─────────────────┘

DESCRIPTION

Spacious premium apartment...

AMENITIES

✓ Swimming Pool  ✓ Gym  ✓ Security
✓ Club House     ✓ Parking

LOCATION
[ Map ] — Anna Nagar, Chennai

INTERESTED IN THIS PROPERTY?

[ Name ]
[ Phone ]
[ Email ]
[ Preferred Visit Date ]

[ Request Site Visit ]
```

---

## 8. Property Filters on Public Pages

Initially implement only:

- Sale / Rent toggle
- Property Type (Apartment, Villa, Plot, Commercial)
- Location
- Price range
- Bedrooms

Later:

- Area, Furnishing, Amenities, Facing, Possession, Developer, Project

---

## 9. Real Estate Digital Card

```
┌──────────────────────────────┐
│          [ PHOTO ]           │
│       ARUN KUMAR             │
│       Real Estate Consultant │
│       Chennai                │
│                              │
│ [ Save Contact ]             │
│ [ WhatsApp ] [ Call ]        │
│                              │
│ ───────────────────────────  │
│  Featured Properties         │
│  [ Apartment ] Anna Nagar · ₹1.85 Cr │
│  [ Villa ] ECR · ₹3.20 Cr   │
│ [ View All Properties ]      │
│          QR CODE             │
└──────────────────────────────┘
```

---

## 10. QR Code Use Cases

### Agent Card QR

```
connect.osduotech.com/c/arun
```

Opens: Agent card → Browse properties → View property → Enquire → Site visit

### Property Board QR

```
connect.osduotech.com/b/arun-properties/properties/anna-nagar-3bhk
```

Opens: Property detail page → WhatsApp/Call/Enquire

### Analytics Flow

```
QR scans → Property views → WhatsApp clicks → Calls → Enquiries → Site visits → Deals
```

---

## 11. Enquiry → CRM Flow

```
Property Page
    ↓
Enquiry (with property context)
    ↓
CRM Lead
    ↓
Site Visit
    ↓
Deal
```

CRM Lead would contain:

```
Lead Source:      Business Connect
Business:         Arun Properties
Property:         3 BHK Premium Apartment – Anna Nagar
Enquiry Type:     Property Enquiry
Customer Req:     Looking for 3 BHK
Preferred Location: Anna Nagar
Budget:           ₹1.5–2 Cr
```

---

## 12. "Schedule a Site Visit" CTA

Primary CTA instead of generic enquiry:

```
Schedule a Site Visit

Property:    3 BHK Premium Apartment
Name:        _______________
Phone:       _______________
Email:       _______________
Preferred Date: _______________
Preferred Time: _______________

[ Request Visit ]
```

Initial implementation: creates an enquiry.  
Future: Site Visit Request → Appointment → CRM Lead → Deal.

---

## 13. Real Estate Analytics Dashboard

```
REAL ESTATE DASHBOARD

Properties          28
Active Listings     21
Property Views    4,862
Enquiries           73
Site Visit Requests 18

TOP PROPERTIES
1. 3 BHK Anna Nagar — 1,284 views, 18 enquiries
2. Villa ECR — 942 views, 11 enquiries
3. 2 BHK Velachery — 731 views, 9 enquiries
```

---

## 14. Theme Support for Real Estate

Existing themes work with real estate. No separate theme engine needed.

| Theme | Real Estate Style | Best For |
|-------|-------------------|----------|
| Professional | Dark navy, large property photography, strong typography | Premium brokers, commercial, developers |
| Modern | Large imagery, rounded property cards, bright CTA | Residential agents, independent brokers |
| Minimal | Large photography, whitespace, typography | Luxury properties, boutique agents |
| Classic | Traditional typography, structured details | Established brokers, traditional agencies |

---

## 15. Commercial Positioning

| Segment | Product |
|---------|---------|
| Professionals | Digital Business Card + Business Profile |
| Businesses | Business Profile + Product/Service Showcase + Lead Capture |
| **Real Estate** | **Digital Agent Profile + Property Catalogue + Property Lead Generation** |
| Manufacturers | Digital Business Profile + Product Catalogue + Enquiry Generation |
| Consultants | Professional Profile + Services + Lead Generation |

### Tagline

> **Business Connect for Real Estate**
> Your digital card. Your property catalogue. Your leads — in one place.

---

## 16. Recommended MVP Scope

### Data

- Property (via Product/Service)
- Property Image/Gallery (existing)
- Property Details (via Benefits child table, renamed presentation)

### Public

- Agent Digital Card
- Agent Business Profile
- Properties listing with filters
- Property Detail page
- Enquiry / Site Visit form

### Actions

- Call, WhatsApp, Save Contact
- Request Details
- Schedule Site Visit

### Analytics

- Property Views, QR Scans
- WhatsApp Clicks, Calls
- Enquiries

### CRM

- Property → Enquiry → CRM Lead → Deal

---

## 17. Implementation Approach

### Phase 1: Terminology Layer (v1.1)

- Add `Business Type` field to Business DocType
- When `Real Estate`: change display labels (Products → Properties for Sale, Benefits → Property Details)
- No backend model changes

### Phase 2: Property Presentation (v1.2)

- Property detail page template with label/value grid
- Property filters on business page (Sale/Rent, Type, Location, Price, Bedrooms)
- Site Visit CTA form

### Phase 3: Real Estate Analytics (v1.3)

- Property-specific analytics (views per property, enquiry-to-visit ratio)
- Property QR code generation
- Top properties ranking

### Phase 4: Dedicated Property DocType (v2.0, if needed)

- Only if Product/Service shortcut becomes limiting
- Migrate existing data
- Add Property-specific fields (Latitude/Longitude, Virtual Tour, Developer, Project)

---

## 18. Key Principle

> Use the existing Business Connect foundation. Do not create a separate real-estate product.
> The existing Product/Service + Benefits architecture is sufficient for MVP.
> Add vertical-specific presentation and terminology layers on top.
