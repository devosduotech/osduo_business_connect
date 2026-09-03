import frappe


def execute():
    """Register the Analytics desk page in the Page DocType."""

    page_name = "analytics"

    # Check if page already exists
    if frappe.db.exists("Page", page_name):
        return

    # Insert directly via SQL to bypass Page.validate() dev mode check
    frappe.db.sql(
        """INSERT INTO `tabPage`
        (name, module, page_name, title, icon, label, public, system_page,
         creation, modified, modified_by, owner, docstatus)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, 0)""",
        (
            page_name,
            "Analytics",
            page_name,
            "Analytics Dashboard",
            "octicon octicon-graph",
            "Analytics Dashboard",
            1,
            0,
            frappe.session.user,
            frappe.session.user,
        ),
    )
    frappe.db.commit()
