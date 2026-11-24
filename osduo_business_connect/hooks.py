app_name = "osduo_business_connect"
app_title = "OSDuo Business Connect"
app_publisher = "OSDuo"
app_description = "Digital business identity, product/service showcase, lead generation, and CRM integration for individuals and small businesses"
app_email = "info@osduo.com"
app_license = "MIT"

from osduo_business_connect.subscription.constants import (
    IMPORT_EXPORT_DOCTYPES,
    PLAN_GATE_HAS_PERMISSION_DOCTYPES,
    PLAN_GATE_QUERY_DOCTYPES,
)

# Cache-busting suffix for every app asset. Frappe serves /assets/... with long
# cache lifetimes; a plain path means Firefox can keep an old desk JS/CSS even
# after a deploy when service workers are unavailable (e.g. plain HTTP). Bump
# this string with each asset change so every browser requests a fresh URL.
BC_ASSET_REVISION = "2026-11-24-touch-hover"

# Branding Configuration — single source of truth
# ------------------------------------------------
# Change these values to white-label the application.
# All paths are bundled inside the app package (public/images) and served from
# /assets/... — never copy logo files into a site's public/files directory.
# The -512/-256 derivatives keep login/desk payloads small; the full-resolution
# originals remain in the repo for print/social use.
OSDUO_BRANDING = {
    "app_name": "OSDuo Business Connect",
    "app_short_name": "Business Connect",
    "tagline": "Business \u00b7 People \u00b7 Opportunities",
    "logo": "/assets/osduo_business_connect/images/logo-512.png",
    "logo_dark": "/assets/osduo_business_connect/images/logo-dark-512.png",
    "favicon": "/assets/osduo_business_connect/images/favicon-256.png",
    "logo_mark": "/assets/osduo_business_connect/images/logo-mark-512.png",
    "logo_mark_small": "/assets/osduo_business_connect/images/logo-mark-128.png",
    "login_panel": "/assets/osduo_business_connect/images/login-panel.jpg",
    "og_image": "/assets/osduo_business_connect/images/og-image.png",
    "primary_color": "#0B3D91",
    "secondary_color": "#1677FF",
    "accent_color": "#00C49A",
    "background_color": "#F4F6F8",
    "text_color": "#333333",
    # Vendor / product identity — single source of truth for the JSON-LD
    # Organization+Brand node (Phase B) and the footer credit (Phase E).
    # product_url_live is True and the product page is live, so Brand.url and
    # the footer credit link straight to product_url. Flip it back to False only
    # if that page ever goes away — the JSON-LD and footer fall back to
    # vendor_url automatically.
    "vendor_name": "OSDuo Tech LLP",
    "vendor_url": "https://www.osduotech.com",
    "product_name": "OSDuo Business Connect",
    "product_url": "https://www.osduotech.com/solutions/business-connect#section_business-connect-pricing",
    "product_url_live": True,
    "show_vendor_credit": True,
    "vendor_credit_text": "Powered by OSDuo Business Connect \u2014 A Product of OSDuo Tech LLP",
    # Support resources for the desk menus (sidebar avatar menu and the module
    # header menu). support_email is the SUPPORT address and is deliberately
    # distinct from app_email above, which is the general enquiries address.
    "support_manual_url": "https://www.osduotech.com/business-connect-manual",
    "support_email": "connect@osduotech.com",
    "support_portal_url": "https://www.osduotech.com/contact",
}

# Apps
# ------------------

required_apps = ["crm"]

add_to_apps_screen = [
    {
        "name": "osduo_business_connect",
        "logo": OSDUO_BRANDING["logo_mark"],
        "title": "Business Connect",
        "route": "/app/business-connect",
        "type": "Workspace",
    }
]

# Includes in <head>
# ------------------
home_page = "login"
web_include_css = [
    f"/assets/osduo_business_connect/css/login.css?v={BC_ASSET_REVISION}"
]

web_include_js = [
    f"/assets/osduo_business_connect/js/login-layout.js?v={BC_ASSET_REVISION}",
    f"/assets/osduo_business_connect/js/pwa.js?v={BC_ASSET_REVISION}",
]

# Desk branding CSS (sidebar logo, app title, browser title)
app_include_css = (
    f"/assets/osduo_business_connect/css/branding.css?v={BC_ASSET_REVISION}"
)
app_include_js = (
    f"/assets/osduo_business_connect/js/branding.js?v={BC_ASSET_REVISION}"
)

# Desk support menu: publishes the OSDuo support rows the avatar-menu patch in
# public/js/branding.js reads. The module-header menu and the hiding of Frappe's
# own help rows are driven from the Navbar Settings record instead, applied by
# osduo_business_connect.branding.apply_navbar_support() on install/migrate —
# see that module for why a boot_session hook cannot do it.
boot_session = "osduo_business_connect.branding.boot_session"

# web_include_css above is deliberately limited to login.css: page-specific
# stylesheets are included directly by the BC templates.

# Website route rules
# ------------------

website_route_rules = [
    # Business landing page
    {
        "from_route": "/b/<business_slug>",
        "to_route": "business/business",
    },
    # Digital Card (short URL)
    {
        "from_route": "/c/<card_slug>",
        "to_route": "card/card",
    },
    # Product page (under business)
    {
        "from_route": "/b/<business_slug>/products/<product_slug>",
        "to_route": "product/product",
    },
    # Service page (under business)
    {
        "from_route": "/b/<business_slug>/services/<service_slug>",
        "to_route": "service/service",
    },
    # Private customer portal pages. These are deliberately outside the Desk so
    # Professional/Business customers never load the Frappe framework UI.
    {
        "from_route": "/portal/team",
        "to_route": "portal/team",
    },
    {
        "from_route": "/portal/subscription",
        "to_route": "portal/subscription",
    },
]

# Document Events
# ------------------
# Hook on document methods and events

# Note: All DocTypes are our own, so Frappe automatically calls their
# controller methods (validate, on_update, after_insert, etc.) from
# the controller files. No need to register them in doc_events.
#
# The only doc_events we register are cross-cutting concerns that must not
# live in a single controller: the CRM Lead hook, publication cache
# invalidation, and the User Invitation guard below.
_SITEMAP_INVALIDATE = "osduo_business_connect.seo.sitemap.invalidate_sitemap_cache"
_PAGE_CACHE_INVALIDATE = "osduo_business_connect.utils.cache.on_publication_change"
_PUBLICATION_EVENTS = [_SITEMAP_INVALIDATE, _PAGE_CACHE_INVALIDATE]

doc_events = {
    "CRM Lead": {
        "on_update": "osduo_business_connect.crm_integration.crm_lead_hook.on_crm_lead_update",
    },
    # Any publication change (create/update/submit/cancel/delete) drops the
    # cached sitemaps so new URLs appear — and removed ones disappear — on the
    # next crawl, and clears the cached HTML of the affected public pages so an
    # edit (including SEO text) is served immediately, not after the 30-minute
    # page-cache TTL (SEO_PLAN acceptance #7).
    "Business": {
        "on_update": _PUBLICATION_EVENTS,
        "on_submit": _PUBLICATION_EVENTS,
        "on_cancel": _PUBLICATION_EVENTS,
        "on_trash": _PUBLICATION_EVENTS,
    },
    "Showcase Product": {
        "on_update": _PUBLICATION_EVENTS,
        "on_submit": _PUBLICATION_EVENTS,
        "on_cancel": _PUBLICATION_EVENTS,
        "on_trash": _PUBLICATION_EVENTS,
    },
    "Showcase Service": {
        "on_update": _PUBLICATION_EVENTS,
        "on_submit": _PUBLICATION_EVENTS,
        "on_cancel": _PUBLICATION_EVENTS,
        "on_trash": _PUBLICATION_EVENTS,
    },
    "Digital Card": {
        "on_update": _PUBLICATION_EVENTS,
        "on_submit": _PUBLICATION_EVENTS,
        "on_cancel": _PUBLICATION_EVENTS,
        "on_trash": _PUBLICATION_EVENTS,
    },
    # Re-validate BC context even when Frappe core's invite API is called
    # directly: it inserts User Invitation with ignore_permissions=True.
    "User Invitation": {
        "before_insert": "osduo_business_connect.subscription.team_invite.validate_invitation_context",
    },
}

# Frappe User Invitation integration
# ----------------------------------
# Customers never receive DocPerms on User. Frappe creates the User only after
# the invitee accepts, and our after_accept hook creates the Business Member.
# Invitee roles only. Administrator, System Manager, BC System Manager, BC
# Subscription Manager and the per-business Owner role are deliberately absent.
_BC_INVITABLE_ROLES = [
    "BC Business Member",
    "BC Business Manager",
    "BC CRM User",
    "BC Marketing Manager",
]
user_invitation = {
    # Roles allowed to send an invitation. Provider roles are included so
    # Frappe's native invite flow still works for Enterprise/provider admins.
    "allowed_roles": {
        "BC Business Owner": _BC_INVITABLE_ROLES,
        "BC System Manager": _BC_INVITABLE_ROLES,
        "BC Subscription Manager": _BC_INVITABLE_ROLES,
        "System Manager": _BC_INVITABLE_ROLES,
        "Administrator": _BC_INVITABLE_ROLES,
    },
    "extra_invite_params": [
        "bc_business",
        "bc_member_role",
        "bc_first_name",
        "bc_last_name",
    ],
    "after_accept": [
        "osduo_business_connect.subscription.team_invite.after_accept_create_member",
    ],
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    # Daily tasks - retry failed CRM sync
    "daily": [
        "osduo_business_connect.services.scheduler.daily_tasks",
    ],
    # Hourly tasks
    "hourly": [
        "osduo_business_connect.services.scheduler.hourly_tasks",
    ],
    # Weekly tasks
    "weekly": [
        "osduo_business_connect.services.scheduler.weekly_tasks",
    ],
    # Full sitemap regeneration — 02:00 on every third day of the month.
    # Publication changes are picked up immediately by the doc_events above;
    # this cron is the periodic safety net that rebuilds and warms the cache.
    "cron": {
        "0 2 */3 * *": [
            "osduo_business_connect.seo.sitemap.generate_sitemaps",
        ],
    },
}

# Testing
# -------

# before_tests = "osduo_business_connect.utils.before_tests"

# Overriding Methods
# ------------------------------

# override_whitelisted_methods = {
#     "frappe.desk.doctype.event.event.get_events": "osduo_business_connect.event.get_events"
# }

# Plan gates
# ----------
# v16 calls before_request hooks but ignores their return values; the gate
# raises PermissionError (403). DocType hooks below are defence in depth only.
before_request = [
    "osduo_business_connect.subscription.plan_gates.enforce_plan_gates",
]

# Frappe v16 builds the login response's home_page before the login JavaScript
# navigates. Customers land in their private portal; Business customer roles
# land in the BC workspace, never the generic Desk.
on_login = [
    "osduo_business_connect.subscription.plan_gates.set_customer_login_home",
]

# The before_request gate raises a 403, but v16's HTML error page uses a fixed
# generic message. This hook puts the plan name and upgrade link back on it.
# The rewrite hook normalises the automatic /login -> /app/business-connect
# redirect (get_default_path) to the v16 BC workspace for Business customers,
# or to the private portal for Professional customers.
after_request = [
    "osduo_business_connect.subscription.plan_gates.rewrite_customer_desk_redirect",
    "osduo_business_connect.subscription.plan_gates.render_plan_gate_message",
]

# Permissions
# -----------

has_permission = {
    "Business": "osduo_business_connect.permissions.has_permission",
    "Business Member": "osduo_business_connect.permissions.has_permission",
    "Digital Card": "osduo_business_connect.permissions.has_permission",
    "Contact Exchange": "osduo_business_connect.permissions.has_permission",
    "Showcase Product": "osduo_business_connect.permissions.has_permission",
    "Showcase Service": "osduo_business_connect.permissions.has_permission",
    "Enquiry": "osduo_business_connect.permissions.has_permission",
    "BC Theme": "osduo_business_connect.permissions.has_permission",
    "Engagement Event": "osduo_business_connect.permissions.has_permission",
    # CRM Lead: OSDuo permission layer on top of CRM's native model
    "CRM Lead": "osduo_business_connect.crm_integration.crm_permissions.has_permission",
    # Subscription module: standard DocPerms apply (the dispatcher returns True
    # for these DocTypes, since v16 treats None as a deny). The authoritative
    # plan gates are the before_request hook added in phase 2.
    "SaaS Plan": "osduo_business_connect.permissions.has_permission",
    "Add-on Master": "osduo_business_connect.permissions.has_permission",
    "Subscription": "osduo_business_connect.permissions.has_permission",
    "Add-on Order": "osduo_business_connect.permissions.has_permission",
    "Plan Restriction Log": "osduo_business_connect.permissions.has_permission",
    # Plan-gated DocTypes (defence in depth). Never returns None: v16 treats a
    # falsy controller-permission result as a deny. Generated from the same
    # inventory the HTTP gate uses so new gated DocTypes cannot be missed.
}

has_permission.update({
    doctype: "osduo_business_connect.subscription.plan_gates.has_permission_for_doctype"
    for doctype in sorted(PLAN_GATE_HAS_PERMISSION_DOCTYPES)
})

permission_query_conditions = {
    "Business": "osduo_business_connect.business.core.get_permission_query_conditions",
    "Business Member": "osduo_business_connect.business.doctype.business_member.business_member.get_permission_query_conditions",
    "Digital Card": "osduo_business_connect.card.doctype.digital_card.digital_card.get_permission_query_conditions",
    "Contact Exchange": "osduo_business_connect.card.doctype.contact_exchange.contact_exchange.get_permission_query_conditions",
    "Showcase Product": "osduo_business_connect.showcase.doctype.showcase_product.showcase_product.get_permission_query_conditions",
    "Showcase Service": "osduo_business_connect.showcase.doctype.showcase_service.showcase_service.get_permission_query_conditions",
    "Enquiry": "osduo_business_connect.enquiry.core.get_permission_query_conditions",
    "BC Theme": "osduo_business_connect.showcase.doctype.bc_theme.bc_theme.get_permission_query_conditions",
    "Engagement Event": "osduo_business_connect.analytics.doctype.engagement_event.engagement_event.get_permission_query_conditions",
    # CRM Lead: OSDuo business isolation
    "CRM Lead": "osduo_business_connect.crm_integration.crm_permissions.get_permission_query_conditions",
}

permission_query_conditions.update({
    doctype: (
        "osduo_business_connect.subscription.plan_gates."
        + ("import_export_query_conditions" if doctype in IMPORT_EXPORT_DOCTYPES
           else "advanced_admin_query_conditions")
    )
    for doctype in sorted(PLAN_GATE_QUERY_DOCTYPES)
})

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#     "Business": "osduo_business_connect.overrides.business.Business",
# }

# Installation
# ------------

before_install = "osduo_business_connect.install.before_install"
after_install = "osduo_business_connect.install.after_install"
# Runs before schema updates: rebuild the module map so DocTypes in modules added
# after install are synced on the first migrate, then repair legacy Website Theme
# colour links before Frappe's own after_migrate hook re-saves the active theme.
before_migrate = [
    "osduo_business_connect.install.refresh_module_map_for_migrate",
    "osduo_business_connect.install.repair_website_theme_colors",
]
after_migrate = "osduo_business_connect.install.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "osduo_business_connect.uninstall.before_uninstall"
# after_uninstall = "osduo_business_connect.uninstall.after_uninstall"

# User Data Protection
# --------------------

# user_data_fields = [
#     {
#         "doctype": "{doctype_1}",
#         "filter_by": "{filter_by}",
#         "redact_fields": ["{field_1}", "{field_2}"],
#         "partial": 1,
#     },
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#     "osduo_business_connect.auth.validate",
# ]

# Jinja
# ----------

jinja = {
    "filters": [
        "osduo_business_connect.utils.website",
        "osduo_business_connect.utils.money",
        "osduo_business_connect.utils.seo",
        "osduo_business_connect.utils.icons",
    ],
}

# Template Overrides
# ------------------
# Override Frappe's login page with Business Connect branding.
# Frappe v16 resolves /login from www/login.html, so the app override lives at
# osduo_business_connect/www/login.html and extends
# osduo_business_connect/templates/login.html (which in turn extends Frappe's
# v16 login template). The old template_overrides hook is intentionally unused:
# it targeted the pre-v16 template path and would bypass the stock login forms.

#template_overrides = {
#    "login.html": "osduo_business_connect.templates.login",
#}

# Website context
# ---------------
# Inject branding variables into all web templates.

update_website_context = "osduo_business_connect.utils.website.get_branding_context"
