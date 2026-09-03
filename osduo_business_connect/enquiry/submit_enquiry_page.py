import frappe
import json


def get_context(context):
    """Handle enquiry form POST submission via website route."""
    if frappe.request.method != "POST":
        frappe.throw("Method not allowed")

    try:
        data = json.loads(frappe.request.data)
    except (json.JSONDecodeError, TypeError):
        frappe.throw("Invalid request data")

    visitor_data = data.get("visitor_data", {})
    if isinstance(visitor_data, str):
        visitor_data = json.loads(visitor_data)

    references = data.get("references", {})
    if isinstance(references, str):
        references = json.loads(references)

    business_slug = data.get("business_slug")
    source = data.get("source", "Digital Card")

    from osduo_business_connect.enquiry.enquiry_service import create_enquiry

    # Get business by slug
    business = frappe.get_all(
        "Business",
        filters={"slug": business_slug, "status": "Published"},
        fields=["name"],
        limit=1,
    )
    if not business:
        frappe.throw("Business not found")

    result = create_enquiry(
        business_name=business[0].name,
        visitor_data=visitor_data,
        source=source,
        references=references,
    )

    frappe.response["content_type"] = "application/json"
    frappe.response["message"] = result
