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
    sync_workspace()


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


def sync_workspace():
    """Create Business Connect workspace if missing.

    Frappe's auto-sync skips it because ``module: "OSDuo Business Connect"``
    is not in modules.txt.  Reads the workspace JSON and inserts the record
    with child tables mapped to actual DB column names.
    """
    import json
    import os

    if frappe.db.exists("Workspace", "Business Connect"):
        return

    json_path = os.path.join(
        frappe.get_app_path("osduo_business_connect"),
        "osduo_business_connect",
        "workspace",
        "business_connect.json",
    )
    if not os.path.exists(json_path):
        return

    with open(json_path) as f:
        ws_def = json.load(f)

    # Workspace Link columns: type, label, icon, description, hidden,
    #   link_type, link_to, report_ref_doctype, dependencies, only_for,
    #   onboard, is_query_report, link_count
    links = []
    for link in ws_def.get("links", []):
        entry = {
            "doctype": "Workspace Link",
            "type": link.get("type", "DocType"),
            "label": link.get("label", ""),
            "description": link.get("description", ""),
        }
        if link.get("type") in ("DocType", "Page"):
            entry["link_to"] = link.get("name", "")
            entry["link_type"] = link.get("type")
        links.append(entry)

    # Workspace Shortcut columns: type, link_to, url, doc_view,
    #   kanban_board, label, icon, restrict_to_domain, report_ref_doctype,
    #   stats_filter, color, format
    shortcuts = []
    for sc in ws_def.get("shortcuts", []):
        shortcuts.append({
            "doctype": "Workspace Shortcut",
            "label": sc.get("label", ""),
            "type": sc.get("type", "DocType"),
            "link_to": sc.get("name", ""),
            "url": sc.get("link", ""),
            "icon": sc.get("icon", ""),
            "description": sc.get("description", ""),
            "color": sc.get("color", ""),
        })

    try:
        ws = frappe.get_doc({
            "doctype": "Workspace",
            "name": ws_def.get("name", "Business Connect"),
            "module": ws_def.get("module", "OSDuo Business Connect"),
            "label": ws_def.get("label", "Business Connect"),
            "icon": ws_def.get("icon", "octicon octicon-briefcase"),
            "type": ws_def.get("type", "Workspace"),
            "system_manager": ws_def.get("system_manager", 1),
            "restrict_to_role": ws_def.get("restrict_to_role", 0),
            "is_hidden": ws_def.get("is_hidden", 0),
            "links": links,
            "shortcuts": shortcuts,
        })
        ws.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        frappe.log_error("sync_business_connect_workspace")