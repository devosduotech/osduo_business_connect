import frappe

# Map CRM Lead status → Enquiry status (1:1)
LEAD_TO_ENQUIRY_STATUS = {
    "New": "New",
    "Contacted": "Contacted",
    "Nurture": "Nurture",
    "Qualified": "Qualified",
    "Converted": "Converted",
    "Unqualified": "Unqualified",
    "Junk": "Junk",
}


def on_crm_lead_update(doc, method):
    """When CRM Lead status changes, update the linked Enquiry status.

    Only applies to leads created from our application (have osduo_enquiry).
    """
    enquiry_name = doc.osduo_enquiry if hasattr(doc, "osduo_enquiry") else None
    if not enquiry_name:
        enquiry_name = frappe.db.get_value("CRM Lead", doc.name, "osduo_enquiry")
    if not enquiry_name:
        return

    crm_status = doc.status if doc.status else "New"
    new_status = LEAD_TO_ENQUIRY_STATUS.get(crm_status)

    if not new_status:
        return

    current_status = frappe.db.get_value("Enquiry", enquiry_name, "status")
    if current_status != new_status:
        frappe.db.set_value("Enquiry", enquiry_name, "status", new_status)
        frappe.db.commit()
