# Copyright (c) 2026, OSDuo and contributors
import re

import frappe
from frappe.model.document import Document

from osduo_business_connect.utils.roles import is_system_manager
from osduo_business_connect.utils.sanitize import (
    normalize_url_fields,
    sanitize_text,
    sanitize_url,
)
from osduo_business_connect.utils.urls import get_card_public_url


class DigitalCard(Document):
    def before_validate(self):
        if self.slug:
            self.slug = self.slug.lower().strip()
        if self.bio:
            self.bio = sanitize_text(self.bio)
        normalize_url_fields(self)
        if self.website:
            self.website = sanitize_url(self.website)

    def validate(self):
        self.validate_slug_immutable()
        self.validate_slug()
        self.set_public_url()

    def on_update(self):
        self.ensure_qr_image()

    def set_public_url(self):
        """Derive the canonical public URL from the slug (field is read-only)."""
        if self.slug:
            self.public_url = get_card_public_url(self.slug)

    def ensure_qr_image(self):
        """Generate (or regenerate) the QR image when QR is enabled and the
        encoded URL changed. Failures are logged, never block saving."""
        if not (self.qr_enabled and self.slug):
            return

        old_doc = self.get_doc_before_save()
        url_changed = old_doc is None or (old_doc.public_url or "") != (self.public_url or "")

        if not (url_changed or not self.qr_image):
            return

        try:
            from osduo_business_connect.services.qr_service import generate_qr_code

            generate_qr_code(self)
        except Exception:
            frappe.log_error(
                title=f"QR generation failed for card {self.name}",
                message=frappe.get_traceback(),
            )

    def validate_slug_immutable(self):
        """The card URL stays stable after submission; amendments may reuse it."""
        if self.is_new() or not self.name:
            return
        old_doc = self.get_doc_before_save()
        if old_doc and old_doc.docstatus >= 1 and old_doc.slug != self.slug:
            frappe.throw(
                "The Public Slug cannot be changed after submission. "
                "Cancel the card and amend it instead."
            )

    def validate_slug(self):
        if not self.slug:
            frappe.throw("Slug is required")
        if not re.match(r"^[a-z0-9-]+$", self.slug):
            frappe.throw("Slug can only contain lowercase letters, numbers, and hyphens")
        if self.slug.startswith("-") or self.slug.endswith("-"):
            frappe.throw("Slug cannot start or end with a hyphen")

        # Cancelled cards do not reserve their slug so amendments keep the
        # original NFC URL working.
        filters = {"slug": self.slug, "docstatus": ["<", 2]}
        if not self.is_new():
            filters["name"] = ["!=", self.name]
        if frappe.db.exists("Digital Card", filters):
            frappe.throw(f"Slug '{self.slug}' is already taken")


def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    if user == "Guest":
        return (
            "`tabDigital Card`.`status` = 'Published' "
            "and `tabDigital Card`.docstatus < 2"
        )

    if is_system_manager(user):
        return ""

    from osduo_business_connect.business.core import get_user_businesses

    businesses = get_user_businesses(user)
    if not businesses:
        return "1=0"

    business_names = [frappe.db.escape(b["name"]) for b in businesses]
    # Digital Card belongs to a business, so we filter by the business field
    return f"`tabDigital Card`.business IN ({', '.join(business_names)})"


def has_permission(doc, user=None, ptype=None):
    if not user:
        user = frappe.session.user

    if user == "Guest":
        return ptype == "read" and doc.status == "Published" and doc.docstatus < 2

    if is_system_manager(user):
        return True

    from osduo_business_connect.business.core import get_user_role_in_business

    member_role = get_user_role_in_business(user, doc.business)
    if not member_role:
        return False

    if ptype == "read":
        return True
    if ptype in ("write", "create", "submit"):
        return member_role in ["Owner", "Manager"]
    if ptype in ("cancel", "amend", "delete"):
        return member_role == "Owner"

    return False
