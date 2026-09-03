# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Theme(Document):
    """
    Theme DocType - Defines visual presentation for a Business.

    Template = layout structure (Modern, Professional, Minimal, Classic)
    Color Scheme = color palette (Violet, Indigo, Blue, etc.)
    """

    def validate(self):
        """Validate theme data."""
        self.validate_colors()
        self.validate_custom_settings()

    def validate_colors(self):
        """Validate color values if custom scheme."""
        if self.color_scheme == "Custom":
            for color_field in ["primary_color", "secondary_color", "accent_color"]:
                color = self.get(color_field)
                if color and not self.is_valid_color(color):
                    frappe.throw(f"{color_field} must be a valid hex color (e.g., #000000)")

    def is_valid_color(self, color):
        """Check if color is valid hex."""
        import re
        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))

    def validate_custom_settings(self):
        """Validate custom settings JSON."""
        if self.custom_settings:
            try:
                import json
                json.loads(self.custom_settings)
            except json.JSONDecodeError as e:
                frappe.throw(f"Invalid JSON in custom settings: {str(e)}")

            forbidden_patterns = ['<script', 'javascript:', 'eval(', 'function(']
            for pattern in forbidden_patterns:
                if pattern.lower() in self.custom_settings.lower():
                    frappe.throw(f"Custom settings contains forbidden content: {pattern}")


def get_permission_query_conditions(user):
    """Return SQL conditions for filtering Theme records."""
    if not user:
        user = frappe.session.user

    if "System Manager" in frappe.get_roles(user):
        return ""

    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)

    if not businesses:
        return "1=0"

    business_names = [frappe.db.escape(b["name"]) for b in businesses]
    return f"`tabTheme`.business IN ({', '.join(business_names)})"


def has_permission(doc, ptype):
    """Check if user has permission on Theme document."""
    user = frappe.session.user

    # Guest can read all themes (needed for public page rendering)
    if user == "Guest":
        if ptype == "read":
            return True
        return False

    if "System Manager" in frappe.get_roles(user):
        return True

    # System themes (no business) are read-only for non-System Managers
    if not doc.business:
        if ptype == "read":
            return True
        return False

    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)
    business_names = [b["name"] for b in businesses]

    if doc.business not in business_names:
        return False

    from osduo_business_connect.business.core import get_user_role_in_business
    member_role = get_user_role_in_business(user, doc.business)
    if not member_role:
        return False

    if ptype == "read":
        return True
    if ptype in ("write", "create"):
        return member_role in ["Owner", "Manager", "Marketing"]
    if ptype == "delete":
        return member_role == "Owner"

    return False
