# OSDuo Business Connect

Digital business identity, product/service showcase, lead generation, and CRM integration for individuals and small businesses.

## Requirements

- Frappe Framework v16
- Frappe CRM

## Installation

```bash
bench get-app osduo_business_connect
bench install-app osduo_business_connect
```

## Configuration

After installation, configure the following:

1. Set up Business DocType
2. Configure CRM integration
3. Set up public routes

## Development

This app follows the Frappe Framework conventions:

- `business/` - Business ownership and membership
- `card/` - Digital business cards
- `showcase/` - Product and service showcase
- `analytics/` - Engagement analytics
- `crm_integration/` - Frappe CRM integration
- `services/` - Business logic layer
- `permissions/` - Access control
- `utils/` - Utility functions

## License

MIT
