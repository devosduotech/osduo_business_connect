# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
QR Service

This module handles QR code generation for Digital Cards.
"""

import frappe
from frappe import _


def generate_qr_code(card_doc):
    """
    Generate QR code for a Digital Card.
    
    Uses direct DB update to avoid triggering lifecycle hooks.

    Args:
        card_doc: Digital Card document

    Returns:
        str: Path to generated QR code image
    """
    try:
        import qrcode
        from io import BytesIO
        import base64

        # Get public URL
        if not card_doc.public_url:
            frappe.throw("Public URL is required to generate QR code")

        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(card_doc.public_url)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Convert to base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Save as file
        file_name = f"qr_{card_doc.slug}.png"
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "content": img_base64,
            "is_private": 0,
            "attached_to_doctype": "Digital Card",
            "attached_to_name": card_doc.name,
        })
        file_doc.insert(ignore_permissions=True)
        file_doc.reload()

        # Update card document using direct DB update to avoid triggering lifecycle hooks
        frappe.db.set_value("Digital Card", card_doc.name, "qr_image", file_doc.file_url)
        frappe.db.commit()

        return file_doc.file_url

    except ImportError:
        frappe.throw(_("QR code generation requires 'qrcode' library. Please install it: pip install qrcode[pil]"))
    except Exception as e:
        frappe.log_error(
            message=f"Failed to generate QR code for card {card_doc.name}: {str(e)}",
            title="QR Code Generation Failed"
        )
        frappe.throw(_("Failed to generate QR code"))


def get_qr_code_url(card_doc):
    """
    Get QR code URL for a Digital Card.

    Args:
        card_doc: Digital Card document

    Returns:
        str: QR code image URL or None
    """
    if card_doc.qr_image:
        return card_doc.qr_image

    # Generate QR if enabled
    if card_doc.qr_enabled:
        return generate_qr_code(card_doc)

    return None
