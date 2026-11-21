# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Static plan data and entitlement key names.

These constants are the fail-closed fallback used when a site has no
Subscription document or no seeded SaaS Plan records yet. They mirror the
locked plan matrix and must be kept in sync with ``seed.py``.
"""

BASE_FEATURES = (
    "digital_business_card",
    "business_profile",
    "qr_sharing",
    "product_showcase",
    "services_showcase",
    "lead_capture",
    "contact_management",
    "mobile_pwa",
    "social_media_integration",
    "nfc_integration",
)

EXTRA_FEATURES = (
    "multiple_business_profiles",
    "team_management",
    "crm_access",
    "analytics",
    "import_export",
    "crm_full_control",
    "email_configuration",
    "whatsapp_configuration",
    "advanced_admin",
)

FEATURE_KEYS = BASE_FEATURES + EXTRA_FEATURES

LIMIT_KEYS = (
    "max_businesses",
    "seat_cap",
    "min_billed_seats",
    "included_domain_mappings",
    "domain_mapping_price",
)

SUBSCRIPTION_STATUSES = (
    "Trial",
    "Active",
    "Past Due",
    "Suspended",
    "Cancelled",
)

PLAN_SOURCES = ("Manual Selection", "Marketplace")

DEFAULT_UPGRADE_URL = (
    "https://www.osduotech.com/solutions/business-connect#section_business-connect-pricing"
)
LEGACY_UPGRADE_URLS = frozenset({
    "https://www.osduotech.com/solutions/business-connect",
})
DOMAIN_MAPPING_PRICE = 5999
CUSTOM_DOMAIN_ADDON = "CUSTOM_DOMAIN_SERVICE"
DOMAIN_REGISTRATION_ADDON = "DOMAIN_REGISTRATION_RENEWAL"
ADDITIONAL_USER_ADDON = "ADDITIONAL_USER"
ADDON_ORDER_NOTIFICATION_CONFIG_KEY = "bc_addon_order_notification_email"
ADDON_ORDER_NOTIFICATION_EMAIL = "info@osduotech.com"

PLAN_SEEDS = {
    "PROFESSIONAL": {
        "plan_name": "Professional",
        "price_per_seat_per_year": 595,
        "min_seats": 1,
        "max_businesses": 1,
        "sort_order": 10,
        "features": {},
        "included_domain_mappings": 0,
    },
    "BUSINESS": {
        "plan_name": "Business",
        "price_per_seat_per_year": 895,
        "min_seats": 5,
        "max_businesses": 3,
        "sort_order": 20,
        "features": {
            "multiple_business_profiles": True,
            "team_management": True,
            "crm_access": True,
            "analytics": True,
            "import_export": True,
        },
        "included_domain_mappings": 0,
    },
    "ENTERPRISE": {
        "plan_name": "Enterprise",
        "price_per_seat_per_year": 1295,
        "min_seats": 10,
        "max_businesses": 5,
        "sort_order": 30,
        "features": {
            "multiple_business_profiles": True,
            "team_management": True,
            "crm_access": True,
            "analytics": True,
            "import_export": True,
            "crm_full_control": True,
            "email_configuration": True,
            "whatsapp_configuration": True,
            "advanced_admin": True,
        },
        "included_domain_mappings": 1,
    },
}

# DocType inventories used by the Phase 2 HTTP gate and its DocType-level
# fallback. Kept here (no frappe import) so hooks.py can build registrations
# from the same source instead of duplicating a partial list.
IMPORT_EXPORT_DOCTYPES = frozenset({"Data Import", "Data Export"})

ANALYTICS_DOCTYPES = frozenset({"Engagement Event"})

# Team/multi-profile surfaces are Business-and-above. Reads stay allowed so a
# Professional site can still use its own Business and owner membership row.
MULTI_BUSINESS_DOCTYPES = frozenset({"Business"})
TEAM_MANAGEMENT_DOCTYPES = frozenset({"Business Member"})

CRM_EXTRA_DOCTYPES = frozenset({
    "FCRM Note",
    "Lead Sync Source",
    "Failed Lead Sync Log",
    "Facebook Page",
    "Facebook Lead Form",
    "Facebook Lead Form Question",
})

# Writes to any of these require Enterprise. Reads are restricted for the
# credentials/configuration subset only; CRM layout DocTypes stay readable on
# Business so the CRM UI can render.
ADVANCED_ADMIN_DOCTYPES = frozenset({
    "Email Account",
    "Email Domain",
    "WhatsApp Settings",
    "WhatsApp Account",
    "WhatsApp Template",
    "FCRM Settings",
    "ERPNext CRM Settings",
    "CRM Global Settings",
    "CRM Fields Layout",
    "CRM Form Script",
    "CRM View Settings",
    "CRM Sales Hierarchy",
    "CRM Notification",
    "CRM Telephony Agent",
    "CRM Twilio Settings",
    "CRM Exotel Settings",
    "CRM Enrichment Settings",
})

ADVANCED_ADMIN_READ_DOCTYPES = frozenset({
    "Email Account",
    "Email Domain",
    "WhatsApp Settings",
    "WhatsApp Account",
    "WhatsApp Template",
    "FCRM Settings",
    # ERPNext CRM Settings is deliberately absent: CRM product/list logic reads
    # its `enabled` flag on Business plans, so only writes are Enterprise-only.
})

PLAN_GATE_HAS_PERMISSION_DOCTYPES = (
    IMPORT_EXPORT_DOCTYPES
    | ADVANCED_ADMIN_DOCTYPES
    | MULTI_BUSINESS_DOCTYPES
    | TEAM_MANAGEMENT_DOCTYPES
    | frozenset({"User"})
)
# Query conditions implement the read-deny half of the policy; layout DocTypes
# stay readable on Business so the CRM UI can render.
PLAN_GATE_QUERY_DOCTYPES = IMPORT_EXPORT_DOCTYPES | ADVANCED_ADMIN_READ_DOCTYPES

# Portal-only customer policy. A "customer" is an active BC business role; the
# provider roles below always win when both sets are present. Enterprise keeps
# its existing Desk-based administration, so only these two plans are locked.
CUSTOMER_ROLES = frozenset({
    "BC Business Owner",
    "BC Business Manager",
    "BC Business Member",
    "BC CRM User",
    "BC Marketing Manager",
})
PRIVILEGED_ROLES = frozenset({
    "Administrator",
    "System Manager",
    "BC System Manager",
    "BC Subscription Manager",
})
CUSTOMER_DESK_LOCKDOWN_PLANS = frozenset({"PROFESSIONAL", "BUSINESS"})

# Native User / Role DocTypes are never exposed to portal customers. BC keeps
# its own Business Member DocType as the authorization bridge; invitations are
# created only through the BC wrapper and Frappe's User Invitation flow.
CUSTOMER_USER_ADMIN_DOCTYPES = frozenset({
    "User",
    "User Invitation",
    "Role",
    "Role Profile",
    "Role Permission",
    "Role Permission for Page and Report",
    "User Role",
    "Has Role",
})


ADDITIONAL_USER_PRICES = {
    plan_code: PLAN_SEEDS[plan_code]["price_per_seat_per_year"]
    for plan_code in PLAN_SEEDS
}

ADDON_SEEDS = (
    {
        "code": "CUSTOM_DOMAIN_SERVICE",
        "add_on_name": "Custom Domain Service",
        "billing_type": "Annual",
        "price": DOMAIN_MAPPING_PRICE,
        "description": "Adds one custom domain mapping for the subscription year.",
        "applies_to_all_plans": 1,
        "applicable_plans": [],
    },
    {
        "code": "DOMAIN_REGISTRATION_RENEWAL",
        "add_on_name": "Domain Registration / Renewal",
        "billing_type": "Actual Cost",
        "price": 0,
        "description": "Domain registration and renewal, billed at actual vendor cost with no margin.",
        "applies_to_all_plans": 1,
        "applicable_plans": [],
    },
    {
        "code": ADDITIONAL_USER_ADDON,
        "add_on_name": "Additional User",
        "billing_type": "Annual",
        "price": 0,
        "description": (
            "Adds one billable user seat for the subscription year. Fulfilled "
            "by the provider after payment is confirmed in Aasriva."
        ),
        "applies_to_all_plans": 0,
        "applicable_plans": [
            {"plan": plan_code, "price": price}
            for plan_code, price in ADDITIONAL_USER_PRICES.items()
        ],
    },
)


def feature_defaults(plan_code):
    """Return the complete feature dict for a seeded plan code."""
    seed = PLAN_SEEDS.get(plan_code) or PLAN_SEEDS["PROFESSIONAL"]
    features = {key: True for key in BASE_FEATURES}
    for key in EXTRA_FEATURES:
        features[key] = bool(seed["features"].get(key, False))
    return features


def limit_defaults(plan_code):
    """Return the complete limit dict for a seeded plan code."""
    seed = PLAN_SEEDS.get(plan_code) or PLAN_SEEDS["PROFESSIONAL"]
    return {
        "max_businesses": seed["max_businesses"],
        "min_billed_seats": seed["min_seats"],
        "seat_cap": seed["min_seats"],
        "included_domain_mappings": seed["included_domain_mappings"],
        "domain_mapping_price": DOMAIN_MAPPING_PRICE,
    }


def snapshot_defaults(plan_code):
    """Return a frozen-snapshot-shaped dict for a seeded plan code."""
    return {
        "plan_code": plan_code,
        "plan_name": (PLAN_SEEDS.get(plan_code) or PLAN_SEEDS["PROFESSIONAL"])["plan_name"],
        "features": feature_defaults(plan_code),
        "limits": limit_defaults(plan_code),
        "source": "constants_fallback",
    }
