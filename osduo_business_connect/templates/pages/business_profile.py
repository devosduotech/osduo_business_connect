import frappe

def get_context(context):
    """Provide context for business profile page."""
    slug = frappe.form_dict.get("business_slug")
    if not slug:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    business = frappe.get_all(
        "Business",
        filters={"slug": slug, "status": "Published", "public_profile_enabled": 1},
        fields=[
            "name", "business_name", "legal_name", "slug", "status",
            "industry", "description", "logo", "cover_image",
            "website", "email", "phone", "whatsapp", "address",
            "city", "state", "country", "postal_code", "timezone",
            "public_profile_enabled", "seo_title", "seo_description"
        ],
        limit=1,
    )

    if not business:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    doc = business[0]
    context.doc = doc
    context.title = doc.get("business_name") or doc.get("name")
    context.no_breadcrumbs = 1
    context.no_header = 1

    # Fetch social links separately
    context.social_links = frappe.get_all(
        "Business Social Link",
        filters={"parent": doc.name},
        fields=["platform", "url"],
        order_by="idx asc",
    )

    # Fetch business hours separately
    context.business_hours = frappe.get_all(
        "Business Hour",
        filters={"parent": doc.name},
        fields=["day", "open_time", "close_time", "is_closed"],
        order_by="idx asc",
    )

    # Fetch cards
    context.cards = frappe.get_all(
        "Digital Card",
        filters={"business": doc.name, "status": "Published", "public_profile_enabled": 1},
        fields=["name", "display_name", "slug", "designation", "profile_image"],
        order_by="sort_order asc",
    )

    # Fetch products
    context.products = frappe.get_all(
        "Showcase Product",
        filters={"business": doc.name, "status": "Published"},
        fields=["name", "product_name", "slug", "image", "short_description", "price", "currency"],
        order_by="sort_order asc",
    )

    # Fetch services
    context.services = frappe.get_all(
        "Showcase Service",
        filters={"business": doc.name, "status": "Published"},
        fields=["name", "service_name", "slug", "image", "short_description", "price", "currency"],
        order_by="sort_order asc",
    )

    # SEO
    if doc.get("seo_title"):
        context.title = doc["seo_title"]
    if doc.get("seo_description"):
        context.meta_description = doc["seo_description"]
