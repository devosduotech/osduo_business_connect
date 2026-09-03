import frappe


def on_crm_lead_update(doc, method):
    """When CRM Lead status changes, update the linked Enquiry status."""
    if not doc.osduo_enquiry:
        return

    try:
        enquiry = frappe.get_doc("Enquiry", doc.osduo_enquiry)
    except frappe.DoesNotExistError:
        return

    status_map = {
        "New": "New",
        "Replied": "Synced",
        "Qualified": "Synced",
        "Converted": "Converted",
        "Closed": "Synced",
        "Lead": "Synced",
        "Opportunity": "Synced",
    }

    new_status = status_map.get(doc.status)
    if new_status and enquiry.status != new_status:
        frappe.db.set_value("Enquiry", enquiry.name, "status", new_status)
        frappe.db.commit()
