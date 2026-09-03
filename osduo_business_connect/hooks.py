app_name = "osduo_business_connect"
app_title = "OSDuo Business Connect"
app_publisher = "OSDuo"
app_description = "Digital business identity, product/service showcase, lead generation, and CRM integration for individuals and small businesses"
app_email = "info@osduo.com"
app_license = "MIT"

# Apps
# ------------------

required_apps = ["crm"]

add_to_apps_screen = [
    {
        "name": "osduo_business_connect",
        "logo": "/assets/osduo_business_connect/images/logo.svg",
        "title": "Business Connect",
        "route": "/app/business-connect",
        "type": "Workspace",
    }
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/osduo_business_connect/css/osduo_business_connect.css"
# app_include_js = "/assets/osduo_business_connect/js/osduo_business_connect.js"

# include js, css files in header of web template
web_include_css = "/assets/osduo_business_connect/css/business_connect.css"

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
    "Page Section": "osduo_business_connect.permissions.has_permission",
    "Theme": "osduo_business_connect.permissions.has_permission",
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
    "Page Section": "osduo_business_connect.showcase.doctype.page_section.page_section.get_permission_query_conditions",
    "Theme": "osduo_business_connect.showcase.doctype.theme.theme.get_permission_query_conditions",
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
