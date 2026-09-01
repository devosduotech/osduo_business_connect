# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Theme(Document):
    """
    Theme DocType - Defines presentation settings for a Business.

    This controls the visual appearance of:
    - Public profile pages
    - Digital cards
    - Product/service showcases
    """

    def before_validate(self):
        """Pre-process data before validation."""
        self.normalize_fields()

    def validate(self):
        """Authoritative location for theme validation."""
        self.validate_business()
        self.validate_colors()
        self.validate_custom_settings()
        self.validate_active_theme()

    def before_save(self):
        """Pre-save operations."""
        pass

    def on_update(self):
        """Post-save operations."""
        self.handle_activation()

    def normalize_fields(self):
        """Normalize field values."""
        # Normalize font family
        if self.font_family:
            self.font_family = self.font_family.strip()

    def validate_business(self):
        """Validate that business exists."""
        if not self.business:
            frappe.throw("Business is required")

        # Check if business exists
        business = frappe.get_doc("Business", self.business)
        if not business:
            frappe.throw("Business does not exist")

    def validate_colors(self):
        """Validate color values."""
        # Validate primary color
        if self.primary_color:
            if not self.is_valid_color(self.primary_color):
                frappe.throw("Primary color must be a valid hex color (e.g., #000000)")

        # Validate secondary color
        if self.secondary_color:
            if not self.is_valid_color(self.secondary_color):
                frappe.throw("Secondary color must be a valid hex color (e.g., #FFFFFF)")

        # Validate accent color
        if self.accent_color:
            if not self.is_valid_color(self.accent_color):
                frappe.throw("Accent color must be a valid hex color (e.g., #FF0000)")

    def is_valid_color(self, color):
        """
        Validate if a color is a valid hex color.

        Args:
            color: Color string to validate

        Returns:
            bool: True if valid, False otherwise
        """
        import re
        # Check if color is a valid hex color
        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))

    def validate_custom_settings(self):
        """Validate custom settings JSON."""
        if self.custom_settings:
            try:
                import json
                json.loads(self.custom_settings)
            except json.JSONDecodeError as e:
                frappe.throw(f"Invalid JSON in custom settings: {str(e)}")

            # Check for forbidden content
            forbidden_patterns = ['<script', 'javascript:', 'eval(', 'function(']
            for pattern in forbidden_patterns:
                if pattern.lower() in self.custom_settings.lower():
                    frappe.throw(f"Custom settings contains forbidden content: {pattern}")

    def validate_active_theme(self):
        """Validate that only one theme is active per business."""
        if self.active:
            # Deactivate other active themes for this business
            # This is the authoritative activation logic
            frappe.db.sql(
                """
                UPDATE `tabTheme`
                SET active = 0
                WHERE business = %s AND name != %s AND active = 1
                """,
                (self.business, self.name),
            )

    def handle_activation(self):
        """Handle theme activation."""
        if self.active:
            # Update Business default_theme
            frappe.db.set_value("Business", self.business, "default_theme", self.name)
            frappe.db.commit()


def get_permission_query_conditions(user):
    """
    Return SQL conditions for filtering Theme records.

    Users can only see themes of businesses they belong to.
    """
    if not user:
        user = frappe.session.user

    # System Manager can see all themes
    if "System Manager" in frappe.get_roles(user):
        return ""

    # Get businesses where user is a member
    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)

    if not businesses:
        return "1=0"  # No access

    business_names = [b["name"] for b in businesses]
    return f"`tabTheme`.business IN ({', '.join(['%s'] * len(business_names))})"


def has_permission(doc, ptype):
    """
    Check if user has permission on Theme document.

    Business Owner/Manager/Marketing can manage themes.
    """
    user = frappe.session.user

    # System Manager has full access
    if "System Manager" in frappe.get_roles(user):
        return True

    # Check if user is a member of this business
    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)
    business_names = [b["name"] for b in businesses]

    if doc.business not in business_names:
        return False

    # Get user's role in this business
    from osduo_business_connect.business.core import get_user_role_in_business
    member_role = get_user_role_in_business(user, doc.business)

    if not member_role:
        return False

    # Check permissions based on role
    if ptype == "read":
        return True
    elif ptype == "write":
        return member_role in ["Owner", "Manager", "Marketing"]
    elif ptype == "create":
        return member_role in ["Owner", "Manager", "Marketing"]
    elif ptype == "delete":
        return member_role == "Owner"

    return False
