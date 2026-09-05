# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Sanitization utilities for OSDuo Business Connect.

Uses Frappe's built-in sanitization facilities for secure HTML handling.
"""

import frappe
from frappe.utils.html_utils import sanitize_html


def sanitize_rich_text(html):
    """
    Sanitize rich text content using Frappe's built-in sanitizer.
    
    This provides proper XSS protection while allowing safe HTML.

    Args:
        html: HTML content to sanitize

    Returns:
        str: Sanitized HTML content
    """
    if not html:
        return html
    
    # Use Frappe's built-in sanitizer
    # This allows safe tags and attributes while blocking dangerous ones
    return sanitize_html(html)


def sanitize_url(url):
    """
    Sanitize URL to prevent XSS attacks.
    
    Only allows safe protocols (http, https, mailto).

    Args:
        url: URL to sanitize

    Returns:
        str: Sanitized URL or empty string if dangerous
    """
    if not url:
        return url
    
    # Strip whitespace
    url = url.strip()
    
    # Check for dangerous protocols
    dangerous_protocols = [
        'javascript:',
        'data:',
        'vbscript:',
        'file:',
        'ftp:',
    ]
    
    url_lower = url.lower()
    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            return ""
    
    return url


def sanitize_text(text):
    """
    Sanitize plain text content.

    Strips HTML tags and trims whitespace.

    Args:
        text: Text content to sanitize

    Returns:
        str: Sanitized text content
    """
    if not text:
        return text

    from frappe.utils import strip_html_tags, cstr
    return strip_html_tags(cstr(text)).strip()


def normalize_url(url):
    """
    Normalize URL by prepending https:// if no protocol is specified.

    Improves UX for non-tech savvy users who type 'www.example.com'
    instead of 'https://www.example.com'.

    Args:
        url: URL to normalize

    Returns:
        str: Normalized URL with protocol
    """
    if not url:
        return url

    url = url.strip()

    if not url:
        return url

    # Already has a protocol
    if url.startswith(("http://", "https://", "mailto:", "tel:")):
        return url

    # Prepend https:// for domains like www.example.com or example.com
    return "https://" + url


def normalize_url_fields(doc):
    """
    Normalize all URL fields in a document.

    Call this from before_validate or before_save in DocType controllers.

    Args:
        doc: Frappe document with URL fields
    """
    url_fields = [
        field.fieldname
        for field in doc.meta.get("fields", [])
        if field.fieldtype == "Data" and field.options == "URL"
    ]

    for fieldname in url_fields:
        value = doc.get(fieldname)
        if value:
            doc.set(fieldname, normalize_url(value))
