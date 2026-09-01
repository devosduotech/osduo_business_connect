# OSDuo Business Connect

Digital business identity, product/service showcase, lead generation, and CRM integration for individuals and small businesses.

## Requirements

- Frappe Framework v16
- Frappe CRM

## Installation

```bash
bench get-app https://github.com/devosduotech/osduo_business_connect.git
bench install-app osduo_business_connect
```

## Module Structure

```
osduo_business_connect/
├── business/           # Business ownership and membership
│   ├── doctype/
│   │   ├── business/           # Root ownership record
│   │   ├── business_member/    # Team members with roles
│   │   ├── business_social_link/  # Child table for social links
│   │   └── business_hour/      # Child table for business hours
│   └── core.py         # Business class + helper functions
├── card/               # Digital business cards
│   └── doctype/
│       ├── digital_card/       # Public digital card
│       └── social_link/        # Child table for card social links
├── showcase/           # Product and service showcase
│   └── doctype/
│       ├── showcase_product/   # Product listings
│       ├── showcase_service/   # Service listings
│       ├── page_section/       # Custom page sections
│       └── theme/              # Card/page themes
├── analytics/          # Engagement analytics
│   └── doctype/
│       └── engagement_event/   # Track views, clicks, shares
├── enquiry/            # Lead generation
│   └── doctype/
│       └── enquiry/            # Public enquiry forms
├── crm_integration/    # Frappe CRM integration
│   ├── crm_permissions.py     # CRM Lead permission isolation
│   └── hooks.py               # CRM event handlers
├── permissions/        # Centralized permission dispatcher
├── services/           # Business logic layer
├── utils/              # Utility functions
└── templates/pages/    # Public web page templates
```

## DocTypes (14 total)

### Core DocTypes
| DocType | Module | Purpose |
|---------|--------|---------|
| Business | business | Root ownership record for all business data |
| Business Member | business | Team members with roles (Owner/Manager/Member/Marketing) |
| Digital Card | card | Public digital business card |
| Showcase Product | showcase | Product listings with pricing |
| Showcase Service | showcase | Service listings with pricing |
| Theme | theme | Card/page themes (CSS, colors) |
| Page Section | showcase | Custom page sections |
| Enquiry | enquiry | Public enquiry form submissions |
| Engagement Event | analytics | View/click/share tracking |

### Child Table DocTypes
| DocType | Parent | Purpose |
|---------|--------|---------|
| Business Social Link | Business | Social media links |
| Business Hour | Business | Operating hours |
| Social Link | Digital Card | Card social links |

## Custom Roles (7)

| Role | Purpose |
|------|---------|
| OSDuo Business Owner | Full control over business |
| OSDuo Business Manager | Manage members, cards, products |
| OSDuo Business Member | Read-only access |
| OSDuo Marketing Manager | Manage products, services, cards |
| OSDuo System Manager | Cross-business admin |
| OSDuo Enquiry Manager | Manage enquiries |
| OSDuo Analytics Viewer | View analytics |

## Key Features

### Completed
- [x] Full DocType structure (14 DocTypes, 7 roles)
- [x] Business ownership model with member roles
- [x] Digital card with slug-based public URLs
- [x] Product/service showcase with categories
- [x] Public enquiry forms with Guest access
- [x] CRM Lead integration with permission isolation
- [x] Naming series for all DocTypes (BIZ-.#####, CARD-.#####, etc.)
- [x] Custom permission system for multi-business security
- [x] GitHub repository with develop/main branches
- [x] `install.py` with DocType existence checks
- [x] Fixed ModuleNotFoundError by separating core logic from doctype files

### In Progress
- [ ] Web templates for public pages (404 routing issue)
- [ ] Workspace UI for desk navigation

### Pending
- [ ] Digital card QR code generation
- [ ] vCard download
- [ ] Theme customization engine
- [ ] Analytics dashboard
- [ ] Email notification templates

## Known Issues

### Web Page Routing (404)
Public web pages at `/b/<slug>` and `/c/<slug>` return 404 despite:
- Correct template files in `templates/pages/`
- Controller files providing context
- `website_route_rules` in hooks.py
- Guest permissions added to DocTypes

**Possible causes:**
- Frappe v16 web routing may not support custom `website_route_rules` as expected
- May need to use Frappe's standard web page convention instead of custom routes
- Cache not clearing properly between deploys

**Workaround:** Use desk UI for all operations. Public pages deferred.

## Architecture Decisions

1. **No `doc_events`** — Frappe auto-calls controller methods for own DocTypes
2. **Naming series** — All DocTypes use `naming_series` field with single defaults
3. **Permission separation** — Custom permission functions in `permissions/__init__.py`
4. **Core logic separation** — Business and Enquiry classes in `core.py` files to avoid Python import conflicts
5. **Guest access** — Web controllers use `frappe.db.get_value` to bypass permission hooks

## License

MIT
