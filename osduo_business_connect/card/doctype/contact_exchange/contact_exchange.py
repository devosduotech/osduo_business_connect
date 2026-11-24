# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Contact Exchange DocType controller.

A Contact Exchange records the person a logged-in card/business owner shared
their details with — typically at an exhibition, show or meeting. It is the
consent-respecting alternative to trying to read the recipient from WhatsApp /
SMS / email apps, which no browser or OS exposes.
"""

import re

import frappe
from frappe.model.document import Document

from osduo_business_connect.utils.roles import is_system_manager


class ContactExchange(Document):
    def before_validate(self):
        self.normalize_fields()

    def validate(self):
        self.validate_business()
        self.validate_references()
        self.validate_shared_target()
        self.set_user()
        self.validate_contact()

    def before_save(self):
        if not self.exchanged_at:
            self.exchanged_at = frappe.utils.now_datetime()

    def normalize_fields(self):
        if self.recipient_name:
            self.recipient_name = self.recipient_name.strip()
        if self.recipient_company:
            self.recipient_company = self.recipient_company.strip()
        if self.recipient_email:
            self.recipient_email = self.recipient_email.strip().lower()
        if self.recipient_phone:
            self.recipient_phone = normalize_phone(self.recipient_phone)
        if self.event_name:
            self.event_name = self.event_name.strip()

    def validate_business(self):
        if not self.business:
            frappe.throw("Business is required")
        if not frappe.db.exists("Business", self.business):
            frappe.throw("Business does not exist")

    def validate_references(self):
        references = [
            ("Digital Card", self.card),
            ("Showcase Product", self.product),
            ("Showcase Service", self.service),
        ]
        for doctype, name in references:
            if not name:
                continue
            if not frappe.db.exists(doctype, {"name": name, "business": self.business}):
                frappe.throw(f"{doctype} does not belong to this business")

    def validate_shared_target(self):
        """Mirror the API's discriminator rules for direct Desk/REST writes.

        Legacy rows have no discriminator and are left alone. New rows must
        state exactly one typed reference matching the selected content type.
        """
        kind = getattr(self, "shared_content_type", None)
        if not kind:
            return
        if kind not in ("Card", "Business", "Product", "Service"):
            frappe.throw("Invalid shared content type")

        refs = {"Card": self.card, "Product": self.product, "Service": self.service}
        populated = [name for name in refs.values() if name]
        if kind == "Business":
            if populated:
                frappe.throw("Business sharing cannot include a card, product or service")
            fields = ["slug", "status", "public_profile_enabled"]
            row = frappe.db.get_value(
                "Business", {"name": self.business}, fields, as_dict=True
            )
        elif not refs[kind] or len(populated) != 1 or populated[0] != kind:
            frappe.throw("Selected content does not match the shared reference")
        elif kind == "Card":
            row = frappe.db.get_value(
                "Digital Card", {"name": self.card, "business": self.business},
                ["slug", "status", "public_profile_enabled"], as_dict=True,
            )
        elif kind == "Product":
            row = frappe.db.get_value(
                "Showcase Product", {"name": self.product, "business": self.business},
                ["slug", "status"], as_dict=True,
            )
        else:
            row = frappe.db.get_value(
                "Showcase Service", {"name": self.service, "business": self.business},
                ["slug", "status"], as_dict=True,
            )

        if not row:
            frappe.throw("Shared content not found for this business")
        if not row.get("slug"):
            frappe.throw("Shared content has no public link yet")
        if (row.get("status") or "Draft") != "Published":
            frappe.throw("Shared content is not published")
        if "public_profile_enabled" in row and not row.get("public_profile_enabled"):
            frappe.throw("Shared content is not publicly visible")

    def set_user(self):
        if not self.user and frappe.session.user and frappe.session.user != "Guest":
            self.user = frappe.session.user
        if self.card and not self.member:
            self.member = frappe.db.get_value("Digital Card", self.card, "member")

    def validate_contact(self):
        channel = self.channel or "In-person"
        phone_digits = re.sub(r"[^0-9]", "", self.recipient_phone or "")
        email = self.recipient_email or ""

        if channel in ("WhatsApp", "SMS"):
            if not phone_digits:
                frappe.throw("A mobile number is required for WhatsApp / SMS")
            if len(phone_digits) < 7 or len(phone_digits) > 15:
                frappe.throw("Contact number must be 7-15 digits")
        elif channel == "Email":
            if not email:
                frappe.throw("An email address is required for Email")
        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            frappe.throw("Enter a valid email address")


def normalize_phone(value):
    """Keep a leading + and digits only, so wa.me/sms links stay valid."""
    value = (value or "").strip()
    if not value:
        return ""
    digits = re.sub(r"[^0-9]", "", value)
    if value.startswith("+"):
        return "+" + digits
    return digits


def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    if user == "Guest":
        return "1=0"

    if is_system_manager(user):
        return ""

    from osduo_business_connect.business.core import get_user_businesses

    businesses = get_user_businesses(user)
    if not businesses:
        return "1=0"

    business_names = [frappe.db.escape(b["name"]) for b in businesses]
    return f"`tabContact Exchange`.business IN ({', '.join(business_names)})"


def has_permission(doc, user=None, ptype=None):
    if not user:
        user = frappe.session.user

    if user == "Guest":
        return False

    if is_system_manager(user):
        return True

    from osduo_business_connect.business.core import get_user_role_in_business

    role = get_user_role_in_business(user, doc.business)
    if not role:
        return False

    if ptype == "read":
        return True
    if ptype in ("write", "create"):
        return role in ("Owner", "Manager", "Member")
    if ptype in ("delete", "cancel", "amend"):
        return role == "Owner"

    return False
