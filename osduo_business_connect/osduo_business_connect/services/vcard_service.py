# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
vCard Service

This module handles vCard generation for Digital Cards.
"""

import frappe
from frappe import _


def generate_vcard(card_doc):
    """
    Generate vCard for a Digital Card.

    Args:
        card_doc: Digital Card document

    Returns:
        str: vCard content
    """
    try:
        # Build vCard
        vcard_lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"FN:{card_doc.display_name}",
        ]

        # Add designation
        if card_doc.designation:
            vcard_lines.append(f"TITLE:{card_doc.designation}")

        # Add organization (business name)
        if card_doc.show_business and card_doc.business:
            business = frappe.get_doc("Business", card_doc.business)
            vcard_lines.append(f"ORG:{business.business_name}")

        # Add contact information
        if card_doc.email:
            vcard_lines.append(f"EMAIL:{card_doc.email}")

        if card_doc.phone:
            vcard_lines.append(f"TEL:{card_doc.phone}")

        if card_doc.website:
            vcard_lines.append(f"URL:{card_doc.website}")

        # Add address
        if card_doc.business:
            business = frappe.get_doc("Business", card_doc.business)
            if business.address or business.city or business.state or business.country:
                address_parts = []
                if business.address:
                    address_parts.append(business.address)
                if business.city:
                    address_parts.append(business.city)
                if business.state:
                    address_parts.append(business.state)
                if business.country:
                    country = frappe.get_doc("Country", business.country)
                    address_parts.append(country.name)
                if business.postal_code:
                    address_parts.append(business.postal_code)

                address = ";".join(address_parts)
                vcard_lines.append(f"ADR:{address}")

        # Add photo
        if card_doc.profile_image:
            vcard_lines.append(f"PHOTO;TYPE=JPEG:{card_doc.profile_image}")

        # Add note (bio)
        if card_doc.bio:
            vcard_lines.append(f"NOTE:{card_doc.bio}")

        # End vCard
        vcard_lines.append("END:VCARD")

        return "\r\n".join(vcard_lines)

    except Exception as e:
        frappe.log_error(
            message=f"Failed to generate vCard for card {card_doc.name}: {str(e)}",
            title="vCard Generation Failed"
        )
        frappe.throw(_("Failed to generate vCard"))


def download_vcard(card_doc):
    """
    Download vCard for a Digital Card.

    Args:
        card_doc: Digital Card document

    Returns:
        None
    """
    vcard_content = generate_vcard(card_doc)

    # Set response headers
    frappe.response.filename = f"{card_doc.slug}.vcf"
    frappe.response.type = "download"
    frappe.response.filecontent = vcard_content
    frappe.response.headers["Content-Type"] = "text/vcard; charset=utf-8"
