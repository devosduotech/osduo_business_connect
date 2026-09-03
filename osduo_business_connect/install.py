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
            "description": "OSDuo Business that generated this lead",
        },
        {
            "fieldname": "osduo_card",
            "fieldtype": "Link",
            "label": "OSDuo Digital Card",
            "options": "Digital Card",
            "insert_after": "osduo_business",
            "description": "Digital Card that generated this lead",
        },
        {
            "fieldname": "osduo_product",
            "fieldtype": "Link",
            "label": "OSDuo Product",
            "options": "Showcase Product",
            "insert_after": "osduo_card",
            "description": "Product that generated this lead",
        },
        {
            "fieldname": "osduo_service",
            "fieldtype": "Link",
            "label": "OSDuo Service",
            "options": "Showcase Service",
            "insert_after": "osduo_product",
            "description": "Service that generated this lead",
        },
        {
            "fieldname": "osduo_enquiry",
            "fieldtype": "Link",
            "label": "OSDuo Enquiry",
            "options": "Enquiry",
            "insert_after": "osduo_service",
            "description": "Enquiry that generated this lead",
        },
        {
            "fieldname": "osduo_campaign",
            "fieldtype": "Data",
            "label": "OSDuo Campaign",
            "insert_after": "osduo_enquiry",
            "description": "Campaign attribution for this lead",
        },
        {
            "fieldname": "osduo_source",
            "fieldtype": "Data",
            "label": "OSDuo Source",
            "insert_after": "osduo_campaign",
            "description": "Specific source (Product page, Service page, etc.)",
        },
        {
            "fieldname": "osduo_landing_url",
            "fieldtype": "Data",
            "label": "OSDuo Landing URL",
            "options": "URL",
            "insert_after": "osduo_source",
            "description": "URL where the lead was captured",
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
        "unique": 0,
        "read_only": 0,
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
    create_default_roles()
    create_builtin_themes()
    create_crm_lead_source()


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
        if not frappe.db.exists("Theme", {"theme_name": display_name}):
            frappe.get_doc({
                "doctype": "Theme",
                "theme_name": display_name,
                "template": "Modern",
                "color_scheme": scheme,
                "primary_color": _get_scheme_primary(scheme),
                "secondary_color": "#FFFFFF",
                "accent_color": _get_scheme_accent(scheme),
                "button_style": "Filled",
                "active": 0,
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
