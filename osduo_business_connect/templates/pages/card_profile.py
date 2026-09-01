import frappe

def get_context(context):
    """Provide context for digital card profile page."""
    slug = frappe.form_dict.get("card_slug")
    if not slug:
        frappe.throw("Card not found", frappe.DoesNotExistError)

    card = frappe.get_all(
        "Digital Card",
        filters={"slug": slug, "status": "Published", "public_profile_enabled": 1},
        fields=["*"],
        limit=1,
    )

    if not card:
        frappe.throw("Card not found", frappe.DoesNotExistError)

    doc = card[0]
    context.doc = doc
    context.title = doc.get("display_name") or doc.get("name")
    context.no_breadcrumbs = 1
    context.no_header = 1

    # Fetch business info for the link
    if doc.get("business"):
        business = frappe.get_all(
            "Business",
            filters={"name": doc["business"]},
            fields=["business_name", "slug"],
            limit=1,
        )
        if business:
            doc["business_name"] = business[0].get("business_name")
            doc["business_slug"] = business[0].get("slug")

    # SEO
    context.meta_description = f"Contact {doc.get('display_name', '')}"
