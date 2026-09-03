import frappe


def execute():
    """Register the Analytics desk page in the Page DocType."""

    page_name = "analytics"

    # Check if page already exists
    existing = frappe.db.exists("Page", page_name)
    if existing:
        return

    # Create the Page record
    page = frappe.get_doc(
        {
            "doctype": "Page",
            "name": page_name,
            "module": "Analytics",
            "page_name": page_name,
            "title": "Analytics Dashboard",
            "icon": "octicon octicon-graph",
            "label": "Analytics Dashboard",
            "public": 1,
            "system_page": 0,
        }
    )
    page.insert(ignore_permissions=True)
    frappe.db.commit()
