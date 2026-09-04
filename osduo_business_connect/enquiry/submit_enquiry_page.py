import frappe
import json


def get_context(context):
    """Handle enquiry form POST submission via website route."""
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed")

    try:
        data = json.loads(frappe.request.data)
    except (json.JSONDecodeError, TypeError):
        frappe.response["type"] = "json"
        frappe.response["message"] = {"error": "Invalid request data"}
        return

    visitor_data = data.get("visitor_data", {})
    if isinstance(visitor_data, str):
        visitor_data = json.loads(visitor_data)

    references = data.get("references", {})
    if isinstance(references, str):
        references = json.loads(references)

    business_slug = data.get("business_slug")
    source = data.get("source", "Digital Card")

    try:
        from osduo_business_connect.enquiry.enquiry_service import create_enquiry
        from osduo_business_connect.business.core import get_public_business_by_slug

        # Get business by slug (requires Published + public_profile_enabled)
        business = get_public_business_by_slug(business_slug)
        if not business:
            frappe.response["type"] = "json"
            frappe.response["message"] = {"error": "Business not found"}
            return

        result = create_enquiry(
            business_name=business.name,
            visitor_data=visitor_data,
            source=source,
            references=references,
        )

        frappe.response["type"] = "json"
        frappe.response["message"] = result

    except Exception as e:
        frappe.log_error(f"Enquiry submission failed: {str(e)}", "Enquiry Error")
        frappe.response["type"] = "json"
        frappe.response["message"] = {"error": "An error occurred while submitting your enquiry. Please try again later."}
