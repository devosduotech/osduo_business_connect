import frappe


def execute():
    """Rename Service Benefit DocType to Feature and update references."""

    # Only proceed if the old DocType exists
    if not frappe.db.exists("DocType", "Service Benefit"):
        return

    # Rename the DocType
    frappe.rename_doc("DocType", "Service Benefit", "Feature", force=True)

    # Update DocType references in Table fields
    # Showcase Service: benefits field options
    frappe.db.set_value(
        "DocField",
        {"parent": "Showcase Service", "fieldname": "benefits"},
        "options",
        "Feature",
    )
    frappe.db.set_value(
        "DocField",
        {"parent": "Showcase Service", "fieldname": "benefits"},
        "fieldname",
        "features",
    )
    frappe.db.set_value(
        "DocField",
        {"parent": "Showcase Service", "fieldname": "features"},
        "label",
        "Features",
    )

    frappe.db.commit()
