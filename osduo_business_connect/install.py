# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Installation hooks for OSDuo Business Connect.

Handles creation of CRM Custom Fields and initial setup.
"""

import json

import frappe

# Fieldnames of the attribution fields this app adds to CRM Lead. Keep in sync
# with the custom_fields list in create_crm_custom_fields(); used by
# ensure_crm_fields_layout() to place them on the CRM Lead side panel.
OSDUO_CRM_FIELDNAMES = (
    "osduo_business",
    "osduo_card",
    "osduo_product",
    "osduo_service",
    "osduo_enquiry",
    "osduo_campaign",
    "osduo_source",
    "osduo_landing_url",
    "osduo_notes",
)


def before_install():
    """Before install tasks."""
    pass


def after_install():
    """After install tasks."""
    # Create CRM Custom Fields
    create_crm_custom_fields()
    ensure_crm_fields_layout()
    
    # Create default roles
    create_default_roles()
    
    # Create built-in themes
    create_builtin_themes()
    
    # Create CRM Lead Source
    create_crm_lead_source()

    # Apply bundled logo/favicon/name defaults (no manual file copies)
    apply_branding_settings()


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
        {
            "fieldname": "osduo_notes",
            "fieldtype": "Small Text",
            "label": "OSDuo Message",
            "insert_after": "osduo_landing_url",
            "read_only": 1,
            "description": "Message captured on the Enquiry (website form message or the "
            "event/channel context of a shared card)",
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


def ensure_crm_fields_layout():
    """Show the osduo_* attribution fields on the CRM Lead side panel.

    Frappe CRM renders the Lead page from its own ``CRM Fields Layout`` record
    (``CRM Lead-Side Panel``). A new custom field stays invisible there until a
    user drags it in with the layout builder, so left alone every customer site
    would need manual customization after every install. This appends the
    fields to an existing layout — or, when none exists, plants a minimal
    default layout that includes them — idempotently, on install/migrate.
    """
    if not (
        frappe.db.exists("DocType", "CRM Fields Layout")
        and frappe.db.exists("DocType", "CRM Lead")
    ):
        return

    layout_name = frappe.db.get_value(
        "CRM Fields Layout", {"dt": "CRM Lead", "type": "Side Panel"}, "name"
    )
    if layout_name:
        doc = frappe.get_doc("CRM Fields Layout", layout_name)
        sections = json.loads(doc.layout or "[]")
        sections, changed = _integrate_osduo_section(sections)
        if not changed:
            return
        doc.layout = json.dumps(sections)
        doc.save(ignore_permissions=True)
    else:
        sections, changed = _integrate_osduo_section(_default_side_panel_sections("CRM Lead"))
        if not changed:
            return
        frappe.get_doc(
            {
                "doctype": "CRM Fields Layout",
                "dt": "CRM Lead",
                "type": "Side Panel",
                "layout": json.dumps(sections),
            }
        ).insert(ignore_permissions=True)
    frappe.db.commit()


def _entry_fieldname(entry):
    """Layout entries are fieldname strings (saved by the CRM builder) but
    tolerate dicts, which some CRM versions keep in the stored JSON."""
    if isinstance(entry, dict):
        return entry.get("fieldname")
    return str(entry)


def _fields_in_use(sections):
    """Every fieldname already placed anywhere in the layout."""
    found = set()
    for section in sections:
        for column in section.get("columns") or []:
            for entry in column.get("fields") or []:
                found.add(_entry_fieldname(entry))
        for entry in section.get("fields") or []:
            found.add(_entry_fieldname(entry))
    return found


def _integrate_osduo_section(sections):
    """Append one dedicated section with the missing osduo_* fields.

    Returns ``(sections, changed)``. The appended section reuses the shape of
    the last editable section — ``columns`` entries for the current CRM layout
    builder, the legacy top-level ``fields`` list for older versions — so the
    layout stays readable for the CRM version that created it.
    """
    sections = sections or []
    missing = [fn for fn in OSDUO_CRM_FIELDNAMES if fn not in _fields_in_use(sections)]
    if not missing:
        return sections, False

    last = next((s for s in reversed(sections) if s.get("name") != "contacts_section"), None)
    legacy_shape = bool(last and "columns" not in last and last.get("fields"))

    new_section = {
        "label": "OSDuo Attribution",
        "name": "osduo_attribution",
        "opened": True,
    }
    if legacy_shape:
        new_section["fields"] = list(missing)
    else:
        new_section["columns"] = [{"name": "osduo_attribution_column", "fields": list(missing)}]
    sections.append(new_section)
    return sections, True


def _default_side_panel_sections(doctype):
    """Minimal side-panel fallback for sites without a saved layout.

    Mirrors what the CRM layout builder would generate from the doctype meta:
    one section holding every renderable field, in field order. The dedicated
    OSDuo section is appended on top by _integrate_osduo_section().
    """
    excluded = (
        "Section Break",
        "Column Break",
        "Tab Break",
        "Table",
        "Table MultiSelect",
        "Signature",
        "Image",
    )
    fieldnames = [
        field.fieldname
        for field in frappe.get_meta(doctype).fields
        if field.fieldtype not in excluded and field.fieldname
    ]
    return [
        {
            "label": "Details",
            "name": "details",
            "opened": True,
            "columns": [{"name": "details_column", "fields": fieldnames}],
        }
    ]


def create_default_roles():
    """Create default OSDuo roles if they don't exist."""
    roles = [
        "BC Business Owner",
        "BC Business Manager",
        "BC Business Member",
        "BC Marketing Manager",
        "BC CRM User",
        "BC System Manager",
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
    ensure_crm_fields_layout()
    migrate_crm_custom_fields()
    create_default_roles()
    create_builtin_themes()
    create_crm_lead_source()
    apply_branding_settings()
    backfill_public_urls()
    remove_doctype_ux_customizations()


# DocTypes whose desk form layout is now defined in the app's doctype JSON.
# Any Customize Form records left on a site would override that standard layout.
DOCTYPE_UX_DOCTYPES = (
    "BC Theme",
    "Business",
    "Business Member",
    "Digital Card",
    "Product Category",
    "Showcase Product",
    "Showcase Service",
)


def remove_doctype_ux_customizations():
    """Delete the site-level Customize Form records that are now baked into the
    standard DocType JSON.

    This is intentionally idempotent: it runs after every migrate and does
    nothing when the records are already gone.
    """
    for doctype in DOCTYPE_UX_DOCTYPES:
        # Field order, naming-series visibility and import permission are now
        # part of the source DocType.
        for property_name in ("field_order", "allow_import"):
            for name in frappe.get_all(
                "Property Setter",
                filters={"doc_type": doctype, "property": property_name},
                pluck="name",
            ):
                frappe.delete_doc(
                    "Property Setter", name, force=True, ignore_permissions=True
                )

        # Naming-series default / options / hidden now come from the standard
        # field definition.
        for name in frappe.get_all(
            "Property Setter",
            filters={"doc_type": doctype, "field_name": "naming_series"},
            pluck="name",
        ):
            frappe.delete_doc(
                "Property Setter", name, force=True, ignore_permissions=True
            )

        # The About Us label is now declared on the standard field.
        for name in frappe.get_all(
            "Property Setter",
            filters={
                "doc_type": doctype,
                "field_name": "description",
                "property": "label",
            },
            pluck="name",
        ):
            frappe.delete_doc(
                "Property Setter", name, force=True, ignore_permissions=True
            )

        # The Enquiry and Purchase Link section label is now declared on the
        # standard field.
        for name in frappe.get_all(
            "Property Setter",
            filters={
                "doc_type": doctype,
                "field_name": "section_purchase",
                "property": "label",
            },
            pluck="name",
        ):
            frappe.delete_doc(
                "Property Setter", name, force=True, ignore_permissions=True
            )

        # Digital Card's sort_order drives backend card ordering, so the field
        # is hidden on the standard form.
        for name in frappe.get_all(
            "Property Setter",
            filters={
                "doc_type": doctype,
                "field_name": "sort_order",
                "property": "hidden",
            },
            pluck="name",
        ):
            frappe.delete_doc(
                "Property Setter", name, force=True, ignore_permissions=True
            )

    # Showcase Product / Service previously used auto-generated
    # `custom_column_break_*` Custom Fields. They are replaced by named
    # `column_break_*` fields in the standard DocType JSON.
    for doctype in ("Showcase Product", "Showcase Service"):
        for name in frappe.get_all(
            "Custom Field",
            filters={
                "dt": doctype,
                "fieldname": ["like", "custom_column_break_%"],
            },
            pluck="name",
        ):
            frappe.delete_doc(
                "Custom Field", name, force=True, ignore_permissions=True
            )

        for name in frappe.get_all(
            "Property Setter",
            filters={
                "doc_type": doctype,
                "field_name": ["like", "custom_column_break_%"],
            },
            pluck="name",
        ):
            frappe.delete_doc(
                "Property Setter", name, force=True, ignore_permissions=True
            )

    for doctype in DOCTYPE_UX_DOCTYPES:
        frappe.clear_cache(doctype=doctype)


def backfill_public_urls():
    """Populate the canonical public URLs on existing Business / Digital Card
    records whose slug is set but public_url is missing or stale.

    Runs after migrate so domain changes can be rolled out by re-saving
    (or re-running migrate) instead of editing hundreds of documents.
    """
    from osduo_business_connect.utils.urls import (
        get_business_public_url,
        get_card_public_url,
    )

    try:
        builders = {
            "Business": get_business_public_url,
            "Digital Card": get_card_public_url,
        }
        updated = 0
        stale_cards = []
        for doctype, build_url in builders.items():
            rows = frappe.get_all(
                doctype,
                filters={"slug": ["is", "set"]},
                fields=["name", "slug", "public_url"],
            )
            for row in rows:
                expected = build_url(row.slug)
                if expected and row.public_url != expected:
                    frappe.db.set_value(doctype, row.name, "public_url", expected, update_modified=False)
                    updated += 1
                    if doctype == "Digital Card":
                        stale_cards.append(row.name)
        if updated:
            frappe.db.commit()
        refresh_card_qr_codes(stale_cards)
    except Exception:
        frappe.log_error(title="BC public_url backfill failed")


def refresh_card_qr_codes(card_names):
    """Regenerate QR images whose encoded URL just changed.

    ``public_url`` is rewritten with ``db.set_value``, which skips controllers,
    so the QR image would otherwise keep encoding the old origin until someone
    re-saves the card. Failures are logged and never block migration.
    """
    if not card_names:
        return
    try:
        from osduo_business_connect.services.qr_service import generate_qr_code
    except Exception:
        frappe.log_error(title="BC QR refresh skipped (qr_service import failed)")
        return

    for name in card_names:
        try:
            card = frappe.get_doc("Digital Card", name)
            if card.qr_enabled and card.public_url:
                generate_qr_code(card)
        except Exception:
            frappe.log_error(
                title=f"BC QR refresh failed for card {name}",
                message=frappe.get_traceback(),
            )


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


def apply_branding_settings():
    """Apply bundled OSDuo branding to Website/System Settings.

    Kept as a stable import path; the implementation lives in
    ``osduo_business_connect.branding`` and is shared with ``after_install``
    and ``after_migrate``. No logo file needs to be copied into the site.
    """
    from osduo_business_connect.branding import apply_branding_settings as _apply

    return _apply()
