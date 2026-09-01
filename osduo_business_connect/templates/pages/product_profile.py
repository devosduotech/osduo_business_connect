import frappe

def get_context(context):
    """Provide context for product profile page."""
    slug = frappe.form_dict.get("product_slug")
    business_slug = frappe.form_dict.get("business_slug")

    if not slug or not business_slug:
        frappe.throw("Product not found", frappe.DoesNotExistError)

    # Find business
    business = frappe.get_all(
        "Business",
        filters={"slug": business_slug, "status": "Published"},
        fields=["name", "business_name", "email"],
        limit=1,
    )
    if not business:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    # Find product
    product = frappe.get_all(
        "Showcase Product",
        filters={"slug": slug, "business": business[0].name, "status": "Published"},
        fields=["*"],
        limit=1,
    )
    if not product:
        frappe.throw("Product not found", frappe.DoesNotExistError)

    doc = product[0]
    context.doc = doc
    context.title = doc.get("product_name") or doc.get("name")
    context.business_slug = business_slug
    context.business_name = business[0].get("business_name")
    context.business_email = business[0].get("email")
    context.no_breadcrumbs = 1
    context.no_header = 1

    # SEO
    if doc.get("seo_title"):
        context.title = doc["seo_title"]
    if doc.get("seo_description"):
        context.meta_description = doc["seo_description"]
