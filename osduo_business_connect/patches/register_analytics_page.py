import frappe


def execute():
    """Register the Analytics desk page in the Page DocType."""
    page_name = "analytics"

    if frappe.db.exists("Page", page_name):
        return

    doc = frappe.get_doc({
        "doctype": "Page",
        "name": page_name,
        "module": "Osduo Business Connect",
        "page_name": page_name,
        "title": "Analytics Dashboard",
        "icon": "octicon octicon-graph",
        "docstatus": 0,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
