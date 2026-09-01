import frappe

def get_context(context):
    """Provide context for business profile page."""
    slug = frappe.form_dict.get("business_slug")
    if not slug:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    doc = frappe.db.get_value(
        "Business",
        {"slug": slug, "status": "Published", "public_profile_enabled": 1},
        ["name", "business_name", "legal_name", "slug", "status",
         "industry", "description", "logo", "cover_image",
         "website", "email", "phone", "whatsapp", "address",
         "city", "state", "country", "postal_code", "timezone",
         "public_profile_enabled", "seo_title", "seo_description"],
        as_dict=True,
    )

    if not doc:
        frappe.throw("Business not found", frappe.DoesNotExistError)

    context.doc = doc
    context.title = doc.get("business_name") or doc.get("name")
    context.no_breadcrumbs = 1
    context.no_header = 1

    # Fetch social links separately (child table - no permission check needed)
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

    # Fetch cards using db.get_list to bypass permission hooks
    context.cards = frappe.db.get_list(
        "Digital Card",
        filters={"business": doc.name, "status": "Published", "public_profile_enabled": 1},
        fields=["name", "display_name", "slug", "designation", "profile_image"],
        order_by="sort_order asc",
    )

    # Fetch products
    context.products = frappe.db.get_list(
        "Showcase Product",
        filters={"business": doc.name, "status": "Published"},
        fields=["name", "product_name", "slug", "image", "short_description", "price", "currency"],
        order_by="sort_order asc",
    )

    # Fetch services
    context.services = frappe.db.get_list(
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
