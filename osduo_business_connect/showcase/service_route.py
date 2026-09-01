# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Public Route for Showcase Services.

This module provides web page rendering for public service pages.
"""

import frappe
from frappe import _

from osduo_business_connect.showcase.public_api import get_public_service


def get_context(context):
    """
    Get context for service page rendering.

    Args:
        context: Page context

    Returns:
        dict: Updated context
    """
    # Get business slug and service slug from path
    business_slug = frappe.form_dict.get("business")
    service_slug = frappe.form_dict.get("service")

    if not business_slug or not service_slug:
        frappe.throw(_("Business and service are required"), frappe.DoesNotExistError)

    # Get service data
    service = get_public_service(business_slug, service_slug)

    if not service:
        frappe.throw(
            _("Service not found"), frappe.DoesNotExistError
        )

    # Add service data to context
    context.service = service
    context.business_slug = business_slug

    # Set page title
    context.title = service.get("service_name", "Service")

    # Get business data for header
    from osduo_business_connect.business.doctype.business.business import get_business_by_slug
    business = get_business_by_slug(business_slug)
    if business:
        context.business = business

    return context
