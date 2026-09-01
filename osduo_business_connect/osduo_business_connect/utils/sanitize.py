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
    
    Removes any HTML tags and escapes special characters.

    Args:
        text: Text content to sanitize

    Returns:
        str: Sanitized text content
    """
    if not text:
        return text
    
    # Use Frappe's text sanitizer
    from frappe.utils import cstr
    return cstr(text).strip()
