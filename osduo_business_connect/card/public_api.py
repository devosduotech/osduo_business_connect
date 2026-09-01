# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Public Card API

This module provides the public API for accessing Digital Card data.
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_public_card(slug):
    """
    Get public card data by slug.

    This is a whitelisted API endpoint that allows guests to access public card data.

    Args:
        slug: Card slug

    Returns:
        dict: Public card data
    """
    if not slug:
        frappe.throw(_("Slug is required"))

    # Get card by slug
    card = frappe.get_all(
        "Digital Card",
        filters={
            "slug": slug,
            "status": "Published",
            "public_profile_enabled": 1,
        },
        fields=["name"],
        limit=1,
    )

    if not card:
        frappe.throw(_("Card not found"), frappe.DoesNotExistError)

    # Get full card document
    card_doc = frappe.get_doc("Digital Card", card[0].name)

    # Serialize card data
    return serialize_card(card_doc)


def serialize_card(card_doc):
    """
    Serialize card document for public API response.

    Args:
        card_doc: Digital Card document

    Returns:
        dict: Serialized card data
    """
    # Get business data
    business = frappe.get_doc("Business", card_doc.business)

    # Get social links
    social_links = []
    for link in card_doc.links:
        if link.enabled:
            social_links.append({
                "platform": link.link_type,
                "label": link.label,
                "value": link.value,
                "url": link.url,
            })

    # Build response
    data = {
        "name": card_doc.name,
        "display_name": card_doc.display_name,
        "designation": card_doc.designation,
        "bio": card_doc.bio,
        "profile_image": card_doc.profile_image,
        "phone": card_doc.phone,
        "email": card_doc.email,
        "whatsapp": card_doc.whatsapp,
        "website": card_doc.website,
        "public_url": card_doc.public_url,
        "qr_enabled": card_doc.qr_enabled,
        "vcard_enabled": card_doc.vcard_enabled,
        "social_links": social_links,
    }

    # Add business data if enabled
    if card_doc.show_business:
        data["business"] = {
            "name": business.name,
            "business_name": business.business_name,
            "logo": business.logo,
            "website": business.website,
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
