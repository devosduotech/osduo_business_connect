import frappe


def execute():
    """Register the Analytics desk page in the Page DocType."""

    page_name = "analytics"

    if frappe.db.exists("Page", page_name):
        return

    frappe.flags.in_patch = True

    frappe.db.sql(
        """INSERT INTO `tabPage`
        (name, module, page_name, title, icon,
         creation, modified, modified_by, owner, docstatus)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, 0)""",
        (
            page_name,
            "Analytics",
            page_name,
            "Analytics Dashboard",
            "octicon octicon-graph",
            frappe.session.user,
            frappe.session.user,
        ),
    )
    frappe.db.commit()
    frappe.flags.in_patch = False
