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
    
    if not exists:
        custom_field = frappe.get_doc({
            "doctype": "Custom Field",
            "dt": dt,
            "fieldname": field["fieldname"],
            "fieldtype": field["fieldtype"],
            "label": field["label"],
            "options": field.get("options"),
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
