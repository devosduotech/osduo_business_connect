# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EngagementEvent(Document):
    """
    Engagement Event DocType - Immutable event record for public engagement analytics.
    
    This is an append-only event record for tracking user interactions.
    Events are created through public API and should not be modified.
    """

    def before_validate(self):
        """Pre-process data before validation."""
        self.sanitize_data()

    def validate(self):
        """Authoritative location for event validation."""
        self.validate_business()
        self.validate_event_type()
        self.validate_references()

    def before_save(self):
        """Pre-save operations."""
        self.set_event_time()

    def on_update(self):
        """Post-save operations."""
        pass

    def sanitize_data(self):
        """Sanitize event data."""
        # Sanitize URLs
        if self.landing_url:
            self.landing_url = self.sanitize_url(self.landing_url)
        if self.referrer:
            self.referrer = self.sanitize_url(self.referrer)
        
        # Truncate session_id
        if self.session_id and len(self.session_id) > 255:
            self.session_id = self.session_id[:255]

    def sanitize_url(self, url):
        """
        Sanitize URL to prevent XSS.
        
        Args:
            url: URL to sanitize
            
        Returns:
            str: Sanitized URL
        """
        if not url:
            return url
        
        # Remove javascript: and other dangerous protocols
        import re
        url = re.sub(r'javascript:', '', url, flags=re.IGNORECASE)
        url = re.sub(r'data:', '', url, flags=re.IGNORECASE)
        
        return url

    def set_event_time(self):
        """Set event_time if not already set."""
        if not self.event_time:
            self.event_time = frappe.utils.now_datetime()

    def validate_business(self):
        """Validate that business exists."""
        if not self.business:
            frappe.throw("Business is required")

    def validate_event_type(self):
        """Validate event_type is allowed."""
        allowed_types = [
            "profile_view",
            "card_view",
            "qr_landing",
            "product_view",
            "service_view",
            "phone_click",
            "email_click",
            "whatsapp_click",
            "website_click",
            "brochure_download",
            "enquiry_submitted",
        ]
        
        if self.event_type not in allowed_types:
            frappe.throw(f"Invalid event type: {self.event_type}")

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
                },
                fields=["name"],
                limit=1,
            )
            if not product:
                frappe.throw("Product does not belong to this business")

        # Validate service
        if self.service:
            service = frappe.get_all(
                "Showcase Service",
                filters={
                    "name": self.service,
                    "business": self.business,
                },
                fields=["name"],
                limit=1,
            )
            if not service:
                frappe.throw("Service does not belong to this business")


def get_permission_query_conditions(user):
    """
    Return SQL conditions for filtering Engagement Event records.
    
    Users can only see events of businesses they belong to.
    """
    if not user:
        user = frappe.session.user

    # System Manager can see all events
    if "System Manager" in frappe.get_roles(user):
        return ""

    # Get businesses where user is a member
    from osduo_business_connect.business.core import get_user_businesses
    businesses = get_user_businesses(user)

    if not businesses:
        return "1=0"

    business_names = [frappe.db.escape(b["name"]) for b in businesses]
    return f"`tabEngagement Event`.business IN ({', '.join(business_names)})"


def has_permission(doc, user=None, ptype=None):
    """
    Check if user has permission on Engagement Event document.

    Events are read-only for business users.
    Guest has no access (events are internal analytics).
    True → do not deny | False → deny | None → fall back to normal permissions
    """
    if not user:
        user = frappe.session.user

    # Guest has no access to engagement events
    if user == "Guest":
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

    # Business users can only read events
    if ptype == "read":
        return True

    return False
