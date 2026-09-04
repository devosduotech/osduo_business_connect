# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ShowcaseService(Document):
    """
    Showcase Service DocType - Public service catalogue entry.

    This controls the public display of services for a business.
    """

    def before_validate(self):
        """Pre-process data before validation."""
        self.normalize_fields()
        self.normalize_urls()
        self.sanitize_description()

    def validate(self):
        """Authoritative location for service validation."""
        self.validate_business()
        self.validate_slug()
        self.validate_brochure()

    def before_save(self):
        """Pre-save operations."""
        pass

    def on_update(self):
        """Post-save operations."""
        pass

    def normalize_fields(self):
        """Normalize field values."""
        # Normalize slug
        if self.slug:
            self.slug = self.slug.strip().lower()
            self.slug = self.slug.replace(" ", "-")

        # Normalize service name
        if self.service_name:
            self.service_name = self.service_name.strip()

    def normalize_urls(self):
        """Normalize URL fields to add https:// if missing."""
        from osduo_business_connect.utils.sanitize import normalize_url_fields
        normalize_url_fields(self)

    def sanitize_description(self):
        """Sanitize description field using Frappe's allowlist-based sanitizer."""
        if self.description:
            from osduo_business_connect.utils.sanitize import sanitize_rich_text
            self.description = sanitize_rich_text(self.description)

    def validate_business(self):
        """Validate that business exists and is published."""
        if not self.business:
            frappe.throw("Business is required")

        # Check if business exists
        business = frappe.get_doc("Business", self.business)
        if not business:
            frappe.throw("Business does not exist")

        # Published services require published business
        if self.status == "Published" and business.status != "Published":
            frappe.throw("Cannot publish service: Business is not published")

    def validate_slug(self):
        """Validate that slug is unique within business."""
        if not self.slug:
            frappe.throw("Slug is required")

        # Check for duplicate slug within business
        existing = frappe.get_all(
            "Showcase Service",
            filters={
                "business": self.business,
                "slug": self.slug,
                "name": ["!=", self.name],
            },
            fields=["name"],
        )
        if existing:
            frappe.throw(
                f"A service with slug '{self.slug}' already exists in this business"
            )

    def validate_brochure(self):
        """Validate brochure attachment."""
        if self.brochure:
            # Check file extension
            allowed_extensions = [".pdf"]
            file_ext = "." + self.brochure.rsplit(".", 1)[-1].lower() if "." in self.brochure else ""
            if file_ext not in allowed_extensions:
                frappe.throw("Brochure must be a PDF file")


def get_permission_query_conditions(user):
    """
    Return SQL conditions for filtering Showcase Service records.

    Users can only see services of businesses they belong to.
    Guest can see published services.
    """
    if not user:
        user = frappe.session.user

    # Guest can see published services
    if user == "Guest":
        return "`tabShowcase Service`.status = 'Published'"

    # System Manager can see all services
    if "System Manager" in frappe.get_roles(user):
        return ""

    # Get businesses where user is a member
    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)

    if not businesses:
        return "1=0"  # No access

    business_names = [frappe.db.escape(b["name"]) for b in businesses]
    return f"`tabShowcase Service`.business IN ({', '.join(business_names)})"


def has_permission(doc, user=None, ptype=None):
    """
    Check if user has permission on Showcase Service document.

    Business Owner/Manager/Marketing can manage services.
    Guest can read published services.
    True → do not deny | False → deny | None → fall back to normal permissions
    """
    if not user:
        user = frappe.session.user

    # Guest can only read published services
    if user == "Guest":
        if ptype == "read":
            return doc.status == "Published"
        return False

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
