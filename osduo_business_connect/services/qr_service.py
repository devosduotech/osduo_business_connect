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

    Args:
        card_doc: Digital Card document

    Returns:
        str: Path to generated QR code image
    """
    try:
        import qrcode
        from io import BytesIO
        import os

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
        img_bytes = buffer.getvalue()
        buffer.close()

        # Write file directly to disk (public/files/)
        file_name = f"qr_{card_doc.slug}.png"
        file_path = frappe.get_site_path("public", "files", file_name)

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(img_bytes)

        # Create File doc pointing to existing file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_name,
            "file_url": f"/files/{file_name}",
            "is_private": 0,
            "attached_to_doctype": "Digital Card",
            "attached_to_name": card_doc.name,
        })
        file_doc.insert(ignore_permissions=True)

        # Update card document
        frappe.db.set_value("Digital Card", card_doc.name, "qr_image", f"/files/{file_name}")
        frappe.db.commit()

        return f"/files/{file_name}"

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
