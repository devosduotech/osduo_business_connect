# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Enquiry Core Module

Contains the Enquiry class and all helper functions.
Separated from the doctype directory to avoid Python import conflicts
when module name == doctype name == file name (all 'enquiry').
"""

import frappe
from frappe.model.document import Document


class Enquiry(Document):
    """
    Enquiry DocType - Public enquiry record for lead capture.

    This bridges public acquisition and CRM integration.
    """

    def before_validate(self):
        """Pre-process data before validation."""
        self.normalize_fields()
        self.normalize_urls()
        self.sanitize_message()

    def validate(self):
        """Authoritative location for enquiry validation."""
        self.validate_business()
        self.validate_references()
        self.validate_visitor_info()
        self.validate_consent()

    def before_save(self):
        """Pre-save operations."""
        self.set_submitted_at()

    def on_update(self):
        """Post-save operations."""
        pass

    def normalize_fields(self):
        """Normalize field values."""
        # Normalize visitor name
        if self.visitor_name:
            self.visitor_name = self.visitor_name.strip()

        # Normalize email
        if self.visitor_email:
            self.visitor_email = self.visitor_email.strip().lower()

        # Normalize phone
        if self.visitor_phone:
            self.visitor_phone = self.visitor_phone.strip()

    def normalize_urls(self):
        """Normalize URL fields to add https:// if missing."""
        from osduo_business_connect.utils.sanitize import normalize_url_fields
        normalize_url_fields(self)

        # Normalize company
        if self.visitor_company:
            self.visitor_company = self.visitor_company.strip()

    def sanitize_message(self):
        """Sanitize message field."""
        if self.message:
            # Remove script tags and event handlers
            import re
            self.message = re.sub(r'<script[^>]*>.*?</script>', '', self.message, flags=re.DOTALL | re.IGNORECASE)
            self.message = re.sub(r'on\w+="[^"]*"', '', self.message)
            self.message = re.sub(r"on\w+='[^']*'", '', self.message)

    def set_submitted_at(self):
        """Set submitted_at if not already set."""
        if not self.submitted_at:
            self.submitted_at = frappe.utils.now_datetime()

    def validate_business(self):
        """Validate that business exists and is published."""
        if not self.business:
            frappe.throw("Business is required")

        # Check if business exists
        business = frappe.get_doc("Business", self.business)
        if not business:
            frappe.throw("Business does not exist")

        # Published enquiries require published business
        if business.status != "Published":
            frappe.throw("Cannot submit enquiry: Business is not published")

    def validate_references(self):
        """Validate that referenced records belong to business."""
        # Validate card
        if self.card:
            card = frappe.get_all(
                "Digital Card",
                filters={
                    "name": self.card,
                    "business": self.business,
                },
                fields=["name"],
                limit=1,
            )
            if not card:
                frappe.throw("Digital Card does not belong to this business")

        # Validate product
        if self.product:
            product = frappe.get_all(
                "Showcase Product",
                filters={
                    "name": self.product,
                    "business": self.business,
                    "status": "Published",
                },
                fields=["name"],
                limit=1,
            )
            if not product:
                frappe.throw("Product does not belong to this business or is not published")

        # Validate service
        if self.service:
            service = frappe.get_all(
                "Showcase Service",
                filters={
                    "name": self.service,
                    "business": self.business,
                    "status": "Published",
                },
                fields=["name"],
                limit=1,
            )
            if not service:
                frappe.throw("Service does not belong to this business or is not published")

    def validate_visitor_info(self):
        """Validate visitor information."""
        if not self.visitor_name:
            frappe.throw("Visitor name is required")

        # Validate email format if provided
        if self.visitor_email:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.visitor_email):
                frappe.throw("Invalid email address")

        # Recommend at least email or phone
        if not self.visitor_email and not self.visitor_phone:
            frappe.msgprint(
                "Warning: No email or phone provided. This may limit follow-up options.",
                alert=True,
            )

        # Message length limit
        if self.message and len(self.message) > 5000:
            frappe.throw("Message is too long (maximum 5000 characters)")

    def validate_consent(self):
        """Validate consent requirements."""
        # Consent validation depends on deployment/jurisdiction
        # In v1, we just log a warning if consent is not given
        if not self.consent:
            frappe.msgprint(
                "Warning: Visitor consent not recorded.",
                alert=True,
            )


def get_permission_query_conditions(user):
    """
    Return SQL conditions for filtering Enquiry records.

    Users can only see enquiries of businesses they belong to.
    Guest cannot see enquiries (only create).
    """
    if not user:
        user = frappe.session.user

    # Guest cannot see enquiries
    if user == "Guest":
        return "1=0"

    # System Manager can see all enquiries
    if "System Manager" in frappe.get_roles(user):
        return ""

    # Get businesses where user is a member
    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)

    if not businesses:
        return "1=0"  # No access

    business_names = [b["name"] for b in businesses]
    return f"`tabEnquiry`.business IN ({', '.join(['%s'] * len(business_names))})"


def has_permission(doc, ptype):
    """
    Check if user has permission on Enquiry document.

    Business Owner/Manager can manage enquiries.
    Guest can create enquiries (public forms).
    """
    user = frappe.session.user

    # Guest can only create enquiries
    if user == "Guest":
        if ptype == "create":
            return True
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
        return member_role in ["Owner", "Manager"]
    elif ptype == "create":
        return False  # Enquiries are created through public API
    elif ptype == "delete":
        return member_role == "Owner"

    return False
