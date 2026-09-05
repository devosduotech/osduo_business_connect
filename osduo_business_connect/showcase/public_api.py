# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Public API for Showcase Products and Services.

This module provides API functions for public access to products and services.
Uses get_public_business_by_slug() for consistent Business visibility checks.
"""

import frappe
from frappe import _

from osduo_business_connect.business.core import get_public_business_by_slug


def get_public_product(business_slug, product_slug):
    """
    Get a published product by business slug and product slug.

    Args:
        business_slug: Business slug
        product_slug: Product slug

    Returns:
        dict: Product data or None if not found
    """
    business = get_public_business_by_slug(business_slug)
    if not business:
        return None

    product = frappe.db.get_value(
        "Showcase Product",
        {
            "business": business.name,
            "slug": product_slug,
            "status": "Published",
        },
        ["name"],
        as_dict=True,
    )
    if not product:
        return None

    return serialize_product(product.name)


def get_public_products(business_slug, limit=20, offset=0):
    """
    Get published products for a business.

    Args:
        business_slug: Business slug
        limit: Maximum number of products to return
        offset: Offset for pagination

    Returns:
        list: List of product data
    """
    business = get_public_business_by_slug(business_slug)
    if not business:
        return []

    products = frappe.get_all(
        "Showcase Product",
        filters={
            "business": business.name,
            "status": "Published",
        },
        fields=["name"],
        order_by="sort_order ASC",
        limit_page_length=limit,
        limit_start=offset,
    )

    return [serialize_product(p.name) for p in products]


def get_public_service(business_slug, service_slug):
    """
    Get a published service by business slug and service slug.

    Args:
        business_slug: Business slug
        service_slug: Service slug

    Returns:
        dict: Service data or None if not found
    """
    business = get_public_business_by_slug(business_slug)
    if not business:
        return None

    service = frappe.db.get_value(
        "Showcase Service",
        {
            "business": business.name,
            "slug": service_slug,
            "status": "Published",
        },
        ["name"],
        as_dict=True,
    )
    if not service:
        return None

    return serialize_service(service.name)


def get_public_services(business_slug, limit=20, offset=0):
    """
    Get published services for a business.

    Args:
        business_slug: Business slug
        limit: Maximum number of services to return
        offset: Offset for pagination

    Returns:
        list: List of service data
    """
    business = get_public_business_by_slug(business_slug)
    if not business:
        return []

    services = frappe.get_all(
        "Showcase Service",
        filters={
            "business": business.name,
            "status": "Published",
        },
        fields=["name"],
        order_by="sort_order ASC",
        limit_page_length=limit,
        limit_start=offset,
    )

    return [serialize_service(s.name) for s in services]


def serialize_product(product_name):
    """
    Serialize a product document for API response.

    Args:
        product_name: Product name

    Returns:
        dict: Serialized product data
    """
    product = frappe.get_doc("Showcase Product", product_name)

    data = {
        "name": product.name,
        "business": product.business,
        "product_name": product.product_name,
        "slug": product.slug,
        "short_description": product.short_description,
        "description": product.description,
        "image": product.image,
        "video_url": product.video_url,
        "category": product.category,
        "price_display_mode": product.price_display_mode,
        "enquiry_enabled": product.enquiry_enabled,
        "featured": product.featured,
        "status": product.status,
    }

    # Include price only if Fixed
    if product.price_display_mode == "Fixed":
        data["price"] = product.price
        data["currency"] = product.currency

    # Include gallery
    if product.gallery:
        sorted_gallery = sorted(product.gallery, key=lambda x: x.sort_order or 0)
        data["gallery"] = [
            {
                "image": item.image,
                "caption": item.caption,
                "alt_text": item.alt_text,
                "sort_order": item.sort_order,
            }
            for item in sorted_gallery
        ]

    # Include features
    if hasattr(product, "features") and product.features:
        sorted_features = sorted(product.features, key=lambda x: x.sort_order or 0)
        data["features"] = [
            {
                "title": feature.title,
                "description": feature.description,
                "image": feature.image,
            }
            for feature in sorted_features
        ]

    return data


def serialize_service(service_name):
    """
    Serialize a service document for API response.

    Args:
        service_name: Service name

    Returns:
        dict: Serialized service data
    """
    service = frappe.get_doc("Showcase Service", service_name)

    data = {
        "name": service.name,
        "business": service.business,
        "service_name": service.service_name,
        "slug": service.slug,
        "short_description": service.short_description,
        "description": service.description,
        "image": service.image,
        "enquiry_enabled": service.enquiry_enabled,
        "featured": service.featured,
        "status": service.status,
    }

    # Include features
    if hasattr(service, "features") and service.features:
        sorted_features = sorted(service.features, key=lambda x: x.sort_order or 0)
        data["features"] = [
            {
                "title": feature.title,
                "description": feature.description,
                "image": feature.image,
            }
            for feature in sorted_features
        ]

    # Include gallery
    if hasattr(service, "gallery") and service.gallery:
        sorted_gallery = sorted(service.gallery, key=lambda x: x.sort_order or 0)
        data["gallery"] = [
            {
                "image": item.image,
                "caption": item.caption,
                "alt_text": item.alt_text,
                "sort_order": item.sort_order,
            }
            for item in sorted_gallery
        ]

    return data
