app_name = "osduo_business_connect"
app_title = "OSDuo Business Connect"
app_publisher = "OSDuo"
app_description = "Digital business identity, product/service showcase, lead generation, and CRM integration for individuals and small businesses"
app_email = "info@osduo.com"
app_license = "MIT"

# Branding Configuration — single source of truth
# ------------------------------------------------
# Change these values to white-label the application.
OSDUO_BRANDING = {
    "app_name": "OSDuo Business Connect",
    "app_short_name": "Business Connect",
    "tagline": "Connect \u00b7 Showcase \u00b7 Grow",
    "logo": "/assets/osduo_business_connect/images/logo.svg",
    "logo_white": "/assets/osduo_business_connect/images/logo-white.svg",
    "favicon": "/assets/osduo_business_connect/images/favicon.svg",
    "logo_mark": "/assets/osduo_business_connect/images/logo-mark.svg",
    "primary_color": "#0B3D91",
    "secondary_color": "#1677FF",
    "accent_color": "#00C49A",
    "background_color": "#F4F6F8",
    "text_color": "#333333",
}

# Apps
# ------------------

required_apps = ["crm"]

add_to_apps_screen = [
    {
        "name": "osduo_business_connect",
        "logo": OSDUO_BRANDING["logo"],
        "title": "Business Connect",
        "route": "/app/business-connect",
        "type": "Workspace",
    }
]

# Includes in <head>
# ------------------

# Desk branding CSS (sidebar logo, app title, browser title)
app_include_css = "/assets/osduo_business_connect/css/branding.css"

# include js, css files in header of web template
# NOT using web_include_css — it injects into login/auth pages too.
# CSS is included directly in each BC page template.

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
]

# Document Events
# ------------------
# Hook on document methods and events

# Note: All DocTypes are our own, so Frappe automatically calls their
# controller methods (validate, on_update, after_insert, etc.) from
# the controller files. No need to register them in doc_events.
doc_events = {
    "CRM Lead": {
        "on_update": "osduo_business_connect.crm_integration.crm_lead_hook.on_crm_lead_update",
    },
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
}

# Testing
# -------

# before_tests = "osduo_business_connect.utils.before_tests"

# Overriding Methods
# ------------------------------

# override_whitelisted_methods = {
#     "frappe.desk.doctype.event.event.get_events": "osduo_business_connect.event.get_events"
# }

# Permissions
# -----------

has_permission = {
    "Business": "osduo_business_connect.permissions.has_permission",
    "Business Member": "osduo_business_connect.permissions.has_permission",
    "Digital Card": "osduo_business_connect.permissions.has_permission",
    "Showcase Product": "osduo_business_connect.permissions.has_permission",
    "Showcase Service": "osduo_business_connect.permissions.has_permission",
    "Enquiry": "osduo_business_connect.permissions.has_permission",
    "BC Theme": "osduo_business_connect.permissions.has_permission",
    "Engagement Event": "osduo_business_connect.permissions.has_permission",
    # CRM Lead: OSDuo permission layer on top of CRM's native model
    "CRM Lead": "osduo_business_connect.crm_integration.crm_permissions.has_permission",
}

permission_query_conditions = {
    "Business": "osduo_business_connect.business.core.get_permission_query_conditions",
    "Business Member": "osduo_business_connect.business.doctype.business_member.business_member.get_permission_query_conditions",
    "Digital Card": "osduo_business_connect.card.doctype.digital_card.digital_card.get_permission_query_conditions",
    "Showcase Product": "osduo_business_connect.showcase.doctype.showcase_product.showcase_product.get_permission_query_conditions",
    "Showcase Service": "osduo_business_connect.showcase.doctype.showcase_service.showcase_service.get_permission_query_conditions",
    "Enquiry": "osduo_business_connect.enquiry.core.get_permission_query_conditions",
    "BC Theme": "osduo_business_connect.showcase.doctype.bc_theme.bc_theme.get_permission_query_conditions",
    "Engagement Event": "osduo_business_connect.analytics.doctype.engagement_event.engagement_event.get_permission_query_conditions",
    # CRM Lead: OSDuo business isolation
    "CRM Lead": "osduo_business_connect.crm_integration.crm_permissions.get_permission_query_conditions",
}

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

# add methods and filters to jinja environment
# jinja = {
#     "methods": "osduo_business_connect.utils.jinja_methods",
#     "filters": "osduo_business_connect.utils.jinja_filters",
# }

# Template Overrides
# ------------------
# Override Frappe's login page with Business Connect branding.
# This does NOT modify Frappe core files — it uses the template override hook.

template_overrides = {
    "login.html": "osduo_business_connect.templates.login",
}

# Website context
# ---------------
# Inject branding variables into all web templates.

update_website_context = "osduo_business_connect.utils.website.get_branding_context"
