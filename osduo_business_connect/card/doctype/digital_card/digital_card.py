# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DigitalCard(Document):
    """
    Digital Card DocType - Represents an individual public digital business card.

    This is the public-facing representation of a team member within a business.
    It provides:
    - Public profile with contact information
    - Social links
    - QR code generation
    - vCard download
    """

    def before_validate(self):
        """Pre-process data before validation."""
        self.normalize_fields()

    def validate(self):
        """Authoritative location for digital card validation."""
        self.validate_member()
        self.validate_slug()
        self.validate_contact_methods()
        self.generate_public_url()

    def before_save(self):
        """Pre-save operations."""
        pass

    def on_update(self):
        """Post-save operations."""
        self.handle_publish_status()

    def normalize_fields(self):
        """Normalize field values."""
        # Normalize slug to lowercase
        if self.slug:
            self.slug = self.slug.lower().strip()

        # Normalize email
        if self.email:
            self.email = self.email.lower().strip()

    def validate_member(self):
        """Validate that member belongs to business and is active."""
        if not self.member:
            frappe.throw("Member is required")

        if not self.business:
            frappe.throw("Business is required")

        # Check if member belongs to this business
        member = frappe.get_doc("Business Member", self.member)
        if member.business != self.business:
            frappe.throw("Member does not belong to this business")

        # Check if member is active
        if member.status != "Active":
            frappe.throw("Member must be active to create a digital card")

    def validate_slug(self):
        """Validate slug format and uniqueness."""
        if not self.slug:
            frappe.throw("Public Slug is required")

        # Check slug format: only lowercase letters, numbers, and hyphens
        import re
        if not re.match(r'^[a-z0-9-]+$', self.slug):
            frappe.throw("Slug can only contain lowercase letters, numbers, and hyphens")

        # Check for leading/trailing hyphen
        if self.slug.startswith('-') or self.slug.endswith('-'):
            frappe.throw("Slug cannot start or end with a hyphen")

        # Check uniqueness
        if self.is_new():
            exists = frappe.db.exists("Digital Card", {"slug": self.slug})
            if exists:
                frappe.throw(f"Slug '{self.slug}' is already taken")
        else:
            exists = frappe.db.exists(
                "Digital Card", {"slug": self.slug, "name": ["!=", self.name]}
            )
            if exists:
                frappe.throw(f"Slug '{self.slug}' is already taken")

    def validate_contact_methods(self):
        """Validate that at least one contact method exists."""
        has_contact = any([
            self.email,
            self.phone,
            self.whatsapp,
            self.website,
        ])
        if not has_contact:
            frappe.throw("At least one contact method (email, phone, WhatsApp, or website) is required")

    def generate_public_url(self):
        """Generate public URL for this card."""
        if self.slug:
            # Use the configured route pattern
            site_url = frappe.utils.get_url()
            self.public_url = f"{site_url}/c/{self.slug}"

    def handle_publish_status(self):
        """Handle publish/unpublish events."""
        if self.status == "Published":
            # Invalidate public cache
            self.invalidate_public_cache()
            # Generate QR if enabled
            if self.qr_enabled:
                self.generate_qr_code()
        elif self.status == "Unpublished":
            # Invalidate public cache
            self.invalidate_public_cache()

    def invalidate_public_cache(self):
        """Invalidate public cache for this card."""
        # Clear cache for public card route
        cache_key = f"public_card:{self.slug}"
        frappe.cache().delete_value(cache_key)

    def generate_qr_code(self):
        """Generate QR code for this card."""
        # This will be implemented in the QR service
        pass


def get_permission_query_conditions(user):
    """
    Return SQL conditions for filtering Digital Card records.

    Users can only see cards of businesses they belong to.
    """
    if not user:
        user = frappe.session.user

    # System Manager can see all cards
    if "System Manager" in frappe.get_roles(user):
        return ""

    # Get businesses where user is a member
    from osduo_business_connect.business.doctype.business.business import get_user_businesses
    businesses = get_user_businesses(user)

    if not businesses:
        return "1=0"  # No access

    business_names = [b["name"] for b in businesses]
    return f"`tabDigital Card`.business IN ({', '.join(['%s'] * len(business_names))})"


def has_permission(doc, ptype):
    """
    Check if user has permission on Digital Card document.

    Business Owner/Manager can manage all cards.
    Business Members can manage their own cards.
    """
    user = frappe.session.user

    # System Manager has full access
    if "System Manager" in frappe.get_roles(user):
        return True

    # Check if user is a member of this business
    from osduo_business_connect.business.doctype.business.business import get_user_businesses
    businesses = get_user_businesses(user)
    business_names = [b["name"] for b in businesses]

    if doc.business not in business_names:
        return False

    # Get user's role in this business
    from osduo_business_connect.business.doctype.business.business import get_user_role_in_business
    member_role = get_user_role_in_business(user, doc.business)

    if not member_role:
        return False

    # Check permissions based on role
    if ptype == "read":
        return True
    elif ptype == "write":
        # Owner/Manager can edit all cards
        if member_role in ["Owner", "Manager"]:
            return True
        # Members can edit their own cards
        if member_role == "Member":
            # Get member's card
            member_doc = frappe.get_doc("Business Member", doc.member)
            if member_doc.user == user:
                return True
        # Marketing can edit cards
        if member_role == "Marketing":
            return True
    elif ptype == "create":
        return member_role in ["Owner", "Manager"]
    elif ptype == "delete":
        return member_role == "Owner"

    return False
