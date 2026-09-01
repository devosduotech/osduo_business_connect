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
        "logo": "/assets/osduo_business_connect/images/logo.png",
        "title": "Business Connect",
        "route": "/app/business",
    }
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/osduo_business_connect/css/osduo_business_connect.css"
# app_include_js = "/assets/osduo_business_connect/js/osduo_business_connect.js"

# include js, css files in header of web template
# web_include_css = "/assets/osduo_business_connect/css/osduo_business_connect.css"
# web_include_js = "/assets/osduo_business_connect/js/osduo_business_connect.js"

# Website route rules
# ------------------

website_route_rules = [
    # Public business profile
    {
        "from_route": "/b/<path:business_slug>",
        "to_route": "business_profile",
        "defaults": {
            "doctype": "Business",
        },
    },
    # Public card
    {
        "from_route": "/c/<path:card_slug>",
        "to_route": "card_profile",
        "defaults": {
            "doctype": "Digital Card",
        },
    },
    # Public product
    {
        "from_route": "/b/<path:business_slug>/p/<path:product_slug>",
        "to_route": "product_profile",
        "defaults": {
            "doctype": "Showcase Product",
        },
    },
    # Public service
    {
        "from_route": "/b/<path:business_slug>/s/<path:service_slug>",
        "to_route": "service_profile",
        "defaults": {
            "doctype": "Showcase Service",
        },
    },
]

# Document Events
# ------------------
# Hook on document methods and events

# Note: All DocTypes are our own, so Frappe automatically calls their
# controller methods (validate, on_update, after_insert, etc.) from
# the controller files. No need to register them in doc_events.
doc_events = {}

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
# Permissions evaluated in scripted ways

has_permission = {
    "Business": "osduo_business_connect.permissions.has_permission",
    "Business Member": "osduo_business_connect.permissions.has_permission",
    "Digital Card": "osduo_business_connect.permissions.has_permission",
    "Showcase Product": "osduo_business_connect.permissions.has_permission",
    "Showcase Service": "osduo_business_connect.permissions.has_permission",
    "Theme": "osduo_business_connect.permissions.has_permission",
    "Page Section": "osduo_business_connect.permissions.has_permission",
    "Enquiry": "osduo_business_connect.permissions.has_permission",
    "Engagement Event": "osduo_business_connect.permissions.has_permission",
}

permission_query_conditions = {
    # CRM Lead isolation - critical for multi-business security
    "CRM Lead": "osduo_business_connect.crm_integration.crm_permissions.get_lead_permission_query_conditions",
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
