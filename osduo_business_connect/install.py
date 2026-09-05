# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Installation hooks for OSDuo Business Connect.

Handles creation of CRM Custom Fields and initial setup.
"""

import frappe
from frappe import _


def before_install():
    """Before install tasks."""
    pass


def after_install():
    """After install tasks."""
    # Create CRM Custom Fields
    create_crm_custom_fields()
    
    # Create default roles
    create_default_roles()
    
    # Create built-in themes
    create_builtin_themes()
    
    # Create CRM Lead Source
    create_crm_lead_source()

    # Ensure desk pages exist
    ensure_desk_pages()


def create_crm_custom_fields():
    """
    Create custom fields on CRM Lead for OSDuo integration.
    
    These fields enable the link between OSDuo enquiries and CRM leads.
    """
    custom_fields = [
        {
            "fieldname": "osduo_business",
            "fieldtype": "Link",
            "label": "OSDuo Business",
            "options": "Business",
            "insert_after": "source",
            "read_only": 1,
            "description": "OSDuo Business that generated this lead (managed by Business Connect)",
        },
        {
            "fieldname": "osduo_card",
            "fieldtype": "Link",
            "label": "OSDuo Digital Card",
            "options": "Digital Card",
            "insert_after": "osduo_business",
            "read_only": 1,
            "description": "Digital Card that generated this lead (managed by Business Connect)",
        },
        {
            "fieldname": "osduo_product",
            "fieldtype": "Link",
            "label": "OSDuo Product",
            "options": "Showcase Product",
            "insert_after": "osduo_card",
            "read_only": 1,
            "description": "Product that generated this lead (managed by Business Connect)",
        },
        {
            "fieldname": "osduo_service",
            "fieldtype": "Link",
            "label": "OSDuo Service",
            "options": "Showcase Service",
            "insert_after": "osduo_product",
            "read_only": 1,
            "description": "Service that generated this lead (managed by Business Connect)",
        },
        {
            "fieldname": "osduo_enquiry",
            "fieldtype": "Link",
            "label": "OSDuo Enquiry",
            "options": "Enquiry",
            "insert_after": "osduo_service",
            "read_only": 1,
            "unique": 1,
            "description": "Enquiry that generated this lead (managed by Business Connect)",
        },
        {
            "fieldname": "osduo_campaign",
            "fieldtype": "Data",
            "label": "OSDuo Campaign",
            "insert_after": "osduo_enquiry",
            "read_only": 1,
            "description": "Campaign attribution for this lead (managed by Business Connect)",
        },
        {
            "fieldname": "osduo_source",
            "fieldtype": "Data",
            "label": "OSDuo Source",
            "insert_after": "osduo_campaign",
            "read_only": 1,
            "description": "Specific source (Product page, Service page, etc.) (managed by Business Connect)",
        },
        {
            "fieldname": "osduo_landing_url",
            "fieldtype": "Data",
            "label": "OSDuo Landing URL",
            "options": "URL",
            "insert_after": "osduo_source",
            "read_only": 1,
            "description": "URL where the lead was captured (managed by Business Connect)",
        },
    ]
    
    for field in custom_fields:
        create_custom_field_if_not_exists("CRM Lead", field)


def create_custom_field_if_not_exists(dt, field):
    """
    Create a custom field if it doesn't already exist.

    Args:
        dt: DocType name
        field: Dict with field properties
    """
    exists = frappe.db.exists(
        "Custom Field",
        {"dt": dt, "fieldname": field["fieldname"]},
    )

    if exists:
        return

    # If the field has a Link option, verify the target DocType exists
    options = field.get("options")
    if options and field.get("fieldtype") == "Link":
        if not frappe.db.exists("DocType", options):
            frappe.log_error(
                f"Skipping custom field {field['fieldname']}: "
                f"DocType '{options}' not found. Run 'bench migrate' after installation."
            )
            return

    custom_field = frappe.get_doc({
        "doctype": "Custom Field",
        "dt": dt,
        "fieldname": field["fieldname"],
        "fieldtype": field["fieldtype"],
        "label": field["label"],
        "options": options,
        "insert_after": field.get("insert_after"),
        "description": field.get("description"),
        "unique": field.get("unique", 0),
        "read_only": field.get("read_only", 0),
        "in_list_view": 0,
        "in_standard_filter": 0,
    })
    custom_field.insert(ignore_permissions=True)
    frappe.db.commit()


def create_default_roles():
    """Create default OSDuo roles if they don't exist."""
    roles = [
        "OSDuo Business Owner",
        "OSDuo Business Manager",
        "OSDuo Business Member",
        "OSDuo Marketing Manager",
        "OSDuo CRM User",
        "OSDuo System Manager",
    ]

    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            role = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1,
                "is_custom": 1,
            })
            role.insert(ignore_permissions=True)
            frappe.db.commit()


def after_migrate():
    """Run after bench migrate to ensure CRM custom fields are created."""
    create_crm_custom_fields()
    migrate_crm_custom_fields()
    create_default_roles()
    create_builtin_themes()
    create_crm_lead_source()
    ensure_desk_pages()


def migrate_crm_custom_fields():
    """
    Ensure existing CRM Custom Fields have correct read_only/unique attributes.

    Previous versions may have created fields with read_only=0 or unique=0
    due to a bug in create_custom_field_if_not_exists. This corrects them.
    Also deduplicates osduo_enquiry values before enforcing uniqueness.
    """
    fields_to_fix = {
        "osduo_enquiry": {"read_only": 1, "unique": 1},
        "osduo_business": {"read_only": 1, "unique": 0},
        "osduo_card": {"read_only": 1, "unique": 0},
        "osduo_product": {"read_only": 1, "unique": 0},
        "osduo_service": {"read_only": 1, "unique": 0},
        "osduo_campaign": {"read_only": 1, "unique": 0},
        "osduo_source": {"read_only": 1, "unique": 0},
        "osduo_landing_url": {"read_only": 1, "unique": 0},
    }

    # Deduplicate osduo_enquiry before enforcing uniqueness.
    # Keep the earliest CRM Lead for each enquiry value; clear duplicates.
    duplicates = frappe.db.sql(
        """SELECT osduo_enquiry, MIN(name) as keep_name
        FROM `tabCRM Lead`
        WHERE osduo_enquiry IS NOT NULL AND osduo_enquiry != ''
        GROUP BY osduo_enquiry
        HAVING COUNT(*) > 1""",
        as_dict=True,
    )
    for dup in duplicates:
        frappe.db.sql(
            """UPDATE `tabCRM Lead`
            SET osduo_enquiry = ''
            WHERE osduo_enquiry = %s AND name != %s""",
            (dup.osduo_enquiry, dup.keep_name),
        )

    for fieldname, attrs in fields_to_fix.items():
        cf_name = frappe.db.exists(
            "Custom Field", {"dt": "CRM Lead", "fieldname": fieldname}
        )
        if not cf_name:
            continue

        # Read current values
        current = frappe.db.get_value(
            "Custom Field", cf_name, ["read_only", "unique"], as_dict=True
        )
        if not current:
            continue

        updates = {}
        if current.read_only != attrs["read_only"]:
            updates["read_only"] = attrs["read_only"]
        if current.unique != attrs["unique"]:
            updates["unique"] = attrs["unique"]

        if updates:
            frappe.db.set_value("Custom Field", cf_name, updates)


def create_crm_lead_source():
    """Create 'Business Connect' CRM Lead Source if it doesn't exist."""
    try:
        if not frappe.db.exists("CRM Lead Source", "Business Connect"):
            frappe.get_doc({
                "doctype": "CRM Lead Source",
                "source_name": "Business Connect",
            }).insert(ignore_permissions=True)
            frappe.db.commit()
    except Exception:
        pass  # CRM Lead Source DocType may not exist in this CRM version


def create_builtin_themes():
    """Create built-in color scheme themes (no business assigned)."""
    schemes = ["Violet", "Indigo", "Blue", "Green", "Yellow", "Orange", "Red"]

    for scheme in schemes:
        display_name = f"Default {scheme}"
        if not frappe.db.exists("BC Theme", {"theme_name": display_name}):
            frappe.get_doc({
                "doctype": "BC Theme",
                "theme_name": display_name,
                "template": "Modern",
                "color_scheme": scheme,
                "primary_color": _get_scheme_primary(scheme),
                "secondary_color": "#FFFFFF",
                "accent_color": _get_scheme_accent(scheme),
                "button_style": "Filled",
            }).insert(ignore_permissions=True)
            frappe.db.commit()


def _get_scheme_primary(scheme):
    """Get primary color for a color scheme."""
    colors = {
        "Violet": "#7C3AED",
        "Indigo": "#4F46E5",
        "Blue": "#2563EB",
        "Green": "#16A34A",
        "Yellow": "#EAB308",
        "Orange": "#EA580C",
        "Red": "#DC2626",
    }
    return colors.get(scheme, "#2563EB")


def _get_scheme_accent(scheme):
    """Get accent color for a color scheme."""
    colors = {
        "Violet": "#A78BFA",
        "Indigo": "#818CF8",
        "Blue": "#60A5FA",
        "Green": "#4ADE80",
        "Yellow": "#FDE047",
        "Orange": "#FB923C",
        "Red": "#F87171",
    }
    return colors.get(scheme, "#60A5FA")


def ensure_desk_pages():
    """Ensure required Page records exist for desk pages."""
    pages = [
        {"name": "analytics", "title": "Analytics Dashboard", "icon": "octicon octicon-graph"},
    ]
    for page_cfg in pages:
        if not frappe.db.exists("Page", page_cfg["name"]):
            try:
                doc = frappe.get_doc({
                    "doctype": "Page",
                    "name": page_cfg["name"],
                    "module": "Osduo Business Connect",
                    "page_name": page_cfg["name"],
                    "title": page_cfg["title"],
                    "icon": page_cfg["icon"],
                    "docstatus": 0,
                })
                doc.insert(ignore_permissions=True)
            except Exception:
                frappe.log_error(f"Failed to create Page: {page_cfg['name']}")
    frappe.db.commit()


def apply_branding_settings():
    """
    Apply OSDuo branding to Frappe's Website Settings and System Settings.
    
    NOTE: This function is available but NOT called automatically.
    Branding is configured manually per deployment via:
    
    1. Website Settings → Set favicon to:
       /assets/osduo_business_connect/images/favicon.png
    2. Website Settings → Set app name to: "Business Connect"
    3. System Settings → Set app name to: "OSDuo Business Connect"
    
    The desk sidebar logo is controlled by add_to_apps_screen in hooks.py.
    The branding.css and branding.js files handle visual overrides once
    the base settings are configured.
    
    Called from after_install and after_migrate.
    """
    from osduo_business_connect.hooks import OSDUO_BRANDING
    
    # Website Settings — favicon and app name
    try:
        website_settings = frappe.get_single("Website Settings")
        website_settings.favicon = OSDUO_BRANDING["favicon"]
        website_settings.app_name = OSDUO_BRANDING["app_short_name"]
        website_settings.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        frappe.log_error("Failed to update Website Settings branding")
    
    # System Settings — app name and logo
    try:
        system_settings = frappe.get_single("System Settings")
        system_settings.app_name = OSDUO_BRANDING["app_name"]
        system_settings.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        frappe.log_error("Failed to update System Settings branding")