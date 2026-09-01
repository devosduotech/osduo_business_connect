# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Public Route for Showcase Products.

This module provides web page rendering for public product pages.
"""

import frappe
from frappe import _

from osduo_business_connect.showcase.public_api import get_public_product


def get_context(context):
    """
    Get context for product page rendering.

    Args:
        context: Page context

    Returns:
        dict: Updated context
    """
    # Get business slug and product slug from path
    business_slug = frappe.form_dict.get("business")
    product_slug = frappe.form_dict.get("product")

    if not business_slug or not product_slug:
        frappe.throw(_("Business and product are required"), frappe.DoesNotExistError)

    # Get product data
    product = get_public_product(business_slug, product_slug)

    if not product:
        frappe.throw(
            _("Product not found"), frappe.DoesNotExistError
        )

    # Add product data to context
    context.product = product
    context.business_slug = business_slug

    # Set page title
    context.title = product.get("product_name", "Product")

    # Get business data for header
    from osduo_business_connect.business.doctype.business.business import get_business_by_slug
    business = get_business_by_slug(business_slug)
    if business:
        context.business = business

    return context
