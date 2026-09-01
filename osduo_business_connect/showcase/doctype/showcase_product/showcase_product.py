# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ShowcaseProduct(Document):
    """
    Showcase Product DocType - Public-facing product catalogue entry.

    This controls the public display of products for a business.
    """

    def before_validate(self):
        """Pre-process data before validation."""
        self.normalize_fields()
        self.sanitize_description()

    def validate(self):
        """Authoritative location for product validation."""
        self.validate_business()
        self.validate_slug()
        self.validate_price_display()
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

        # Normalize product name
        if self.product_name:
            self.product_name = self.product_name.strip()

    def sanitize_description(self):
        """Sanitize description field."""
        if self.description:
            # Remove script tags and event handlers
            import re
            self.description = re.sub(r'<script[^>]*>.*?</script>', '', self.description, flags=re.DOTALL | re.IGNORECASE)
            self.description = re.sub(r'on\w+="[^"]*"', '', self.description)
            self.description = re.sub(r"on\w+='[^']*'", '', self.description)

    def validate_business(self):
        """Validate that business exists and is published."""
        if not self.business:
            frappe.throw("Business is required")

        # Check if business exists
        business = frappe.get_doc("Business", self.business)
        if not business:
            frappe.throw("Business does not exist")

        # Published products require published business
        if self.status == "Published" and business.status != "Published":
            frappe.throw("Cannot publish product: Business is not published")

    def validate_slug(self):
        """Validate that slug is unique within business."""
        if not self.slug:
            frappe.throw("Slug is required")

        # Check for duplicate slug within business
        existing = frappe.get_all(
            "Showcase Product",
            filters={
                "business": self.business,
                "slug": self.slug,
                "name": ["!=", self.name],
            },
            fields=["name"],
        )
        if existing:
            frappe.throw(
                f"A product with slug '{self.slug}' already exists in this business"
            )

    def validate_price_display(self):
        """Validate price display mode and price."""
        if self.price_display_mode == "Fixed":
            if not self.price:
                frappe.throw("Price is required when price display mode is Fixed")
            if not self.currency:
                frappe.throw("Currency is required when price display mode is Fixed")

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
    Return SQL conditions for filtering Showcase Product records.

    Users can only see products of businesses they belong to.
    """
    if not user:
        user = frappe.session.user

    # System Manager can see all products
    if "System Manager" in frappe.get_roles(user):
        return ""

    # Get businesses where user is a member
    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)

    if not businesses:
        return "1=0"  # No access

    business_names = [b["name"] for b in businesses]
    return f"`tabShowcase Product`.business IN ({', '.join(['%s'] * len(business_names))})"


def has_permission(doc, ptype):
    """
    Check if user has permission on Showcase Product document.

    Business Owner/Manager/Marketing can manage products.
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
