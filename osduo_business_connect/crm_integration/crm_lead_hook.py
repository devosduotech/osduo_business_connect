import frappe


def on_crm_lead_update(doc, method):
    """When CRM Lead status changes, update the linked Enquiry status."""
    enquiry_name = doc.osduo_enquiry if hasattr(doc, "osduo_enquiry") else None
    if not enquiry_name:
        # Try fetching from DB in case field not loaded
        enquiry_name = frappe.db.get_value("CRM Lead", doc.name, "osduo_enquiry")
    if not enquiry_name:
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
    if not new_status:
        return

    current_status = frappe.db.get_value("Enquiry", enquiry_name, "status")
    if current_status != new_status:
        frappe.db.set_value("Enquiry", enquiry_name, "status", new_status)
        frappe.db.commit()
