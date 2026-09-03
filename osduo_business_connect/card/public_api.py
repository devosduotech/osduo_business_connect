# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Public Card API

Provides public access to Digital Card data.
Verifies both Card AND Business are Published + public_profile_enabled.
"""

import frappe
from frappe import _

from osduo_business_connect.business.core import get_public_business_by_slug


def get_public_card_by_slug(slug):
    """
    Get a public card by slug with full visibility check.

    Verifies:
    - Card: Published, public_profile_enabled
    - Business: Published, public_profile_enabled

    Uses frappe.db.get_value to bypass permission_query_conditions.

    Args:
        slug: Card slug

    Returns:
        dict: Card data with business info, or None
    """
    if not slug:
        return None

    card = frappe.db.get_value(
        "Digital Card",
        {"slug": slug, "status": "Published", "public_profile_enabled": 1},
        ["name", "business", "display_name", "slug", "designation",
         "profile_image", "bio", "phone", "email", "whatsapp", "website",
         "qr_enabled", "qr_image", "vcard_enabled", "show_business",
         "public_url"],
        as_dict=True,
    )
    if not card:
        return None

    # Verify Business is also Published + public_profile_enabled
    if not card.get("business"):
        return None

    business = frappe.db.get_value(
        "Business",
        {"name": card["business"], "status": "Published", "public_profile_enabled": 1},
        ["name", "business_name", "slug", "logo", "website"],
        as_dict=True,
    )
    if not business:
        return None

    card["business_data"] = business
    return card


@frappe.whitelist(allow_guest=True)
def get_public_card(slug):
    """
    Get public card data by slug.

    Args:
        slug: Card slug

    Returns:
        dict: Public card data
    """
    if not slug:
        frappe.throw(_("Slug is required"))

    card = get_public_card_by_slug(slug)
    if not card:
        frappe.throw(_("Card not found"), frappe.DoesNotExistError)

    # Get social links
    social_links = frappe.get_all(
        "Digital Card Link",
        filters={"parent": card.name, "enabled": 1},
        fields=["link_type", "label", "value", "url"],
        order_by="sort_order asc",
    )

    # Build response
    data = {
        "name": card.name,
        "display_name": card.display_name,
        "designation": card.designation,
        "bio": card.bio,
        "profile_image": card.profile_image,
        "phone": card.phone,
        "email": card.email,
        "whatsapp": card.whatsapp,
        "website": card.website,
        "public_url": card.public_url,
        "qr_enabled": card.qr_enabled,
        "vcard_enabled": card.vcard_enabled,
        "social_links": [
            {
                "platform": link.link_type,
                "label": link.label,
                "value": link.value,
                "url": link.url,
            }
            for link in social_links
        ],
    }

    if card.show_business and card.get("business_data"):
        data["business"] = {
            "name": card["business_data"].name,
            "business_name": card["business_data"].business_name,
            "logo": card["business_data"].logo,
            "website": card["business_data"].website,
        }

    return data


def get_card_download_url(card_doc, download_type):
    """
    Get download URL for card resources (QR, vCard).

    Args:
        card_doc: Digital Card document
        download_type: Type of download (qr, vcard)

    Returns:
        str: Download URL
    """
    site_url = frappe.utils.get_url()

    if download_type == "qr":
        if card_doc.qr_image:
            return card_doc.qr_image
        return None
    elif download_type == "vcard":
        return f"{site_url}/api/method/osduo_business_connect.card.public_api.download_vcard?slug={card_doc.slug}"

    return None


@frappe.whitelist(allow_guest=True)
def download_vcard(slug):
    """
    Download vCard for a Digital Card by slug.

    Args:
        slug: Card slug

    Returns:
        None (sets frappe.response for file download)
    """
    if not slug:
        frappe.throw(_("Slug is required"))

    card = get_public_card_by_slug(slug)
    if not card:
        frappe.throw(_("Card not found"), frappe.DoesNotExistError)

    # Also check vcard_enabled
    if not card.get("vcard_enabled"):
        frappe.throw(_("vCard download is not enabled for this card"))

    card_doc = frappe.get_doc("Digital Card", card.name)
    from osduo_business_connect.services.vcard_service import download_vcard as _download
    _download(card_doc)
