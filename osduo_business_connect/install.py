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


def create_builtin_themes():
    """Create 8 built-in VIBGYOR themes if they don't exist."""
    themes = [
        {
            "theme_name": "Violet",
            "template": "Violet",
            "primary_color": "#7C3AED",
            "secondary_color": "#FFFFFF",
            "accent_color": "#A78BFA",
            "button_style": "Filled",
            "card_style": "Modern",
        },
        {
            "theme_name": "Indigo",
            "template": "Indigo",
            "primary_color": "#4F46E5",
            "secondary_color": "#FFFFFF",
            "accent_color": "#818CF8",
            "button_style": "Filled",
            "card_style": "Modern",
        },
        {
            "theme_name": "Blue",
            "template": "Blue",
            "primary_color": "#2563EB",
            "secondary_color": "#FFFFFF",
            "accent_color": "#60A5FA",
            "button_style": "Filled",
            "card_style": "Modern",
        },
        {
            "theme_name": "Green",
            "template": "Green",
            "primary_color": "#16A34A",
            "secondary_color": "#FFFFFF",
            "accent_color": "#4ADE80",
            "button_style": "Filled",
            "card_style": "Modern",
        },
        {
            "theme_name": "Yellow",
            "template": "Yellow",
            "primary_color": "#EAB308",
            "secondary_color": "#FFFFFF",
            "accent_color": "#FDE047",
            "button_style": "Filled",
            "card_style": "Modern",
        },
        {
            "theme_name": "Orange",
            "template": "Orange",
            "primary_color": "#EA580C",
            "secondary_color": "#FFFFFF",
            "accent_color": "#FB923C",
            "button_style": "Filled",
            "card_style": "Modern",
        },
        {
            "theme_name": "Red",
            "template": "Red",
            "primary_color": "#DC2626",
            "secondary_color": "#FFFFFF",
            "accent_color": "#F87171",
            "button_style": "Filled",
            "card_style": "Modern",
        },
        {
            "theme_name": "Professional",
            "template": "Professional",
            "primary_color": "#1E293B",
            "secondary_color": "#FFFFFF",
            "accent_color": "#64748B",
            "button_style": "Filled",
            "card_style": "Professional",
        },
    ]

    for theme_data in themes:
        if not frappe.db.exists("Theme", {"theme_name": theme_data["theme_name"]}):
            theme = frappe.get_doc({
                "doctype": "Theme",
                "theme_name": theme_data["theme_name"],
                "template": theme_data["template"],
                "primary_color": theme_data["primary_color"],
                "secondary_color": theme_data["secondary_color"],
                "accent_color": theme_data["accent_color"],
                "button_style": theme_data["button_style"],
                "card_style": theme_data["card_style"],
                "active": 0,
            })
            theme.insert(ignore_permissions=True)
            frappe.db.commit()
