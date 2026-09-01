# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Security Utilities

Provides security functions for OSDuo Business Connect.
"""

import frappe
from frappe import _
import re


def validate_file_upload(file_doc):
    """
    Validate file upload for security.
    
    Args:
        file_doc: File document
        
    Raises:
        frappe.ValidationError: If file is not allowed
    """
    # Allowed file types
    allowed_types = {
        "image": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
        "document": [".pdf", ".doc", ".docx", ".xls", ".xlsx"],
        "video": [".mp4", ".webm", ".ogg"],
        "audio": [".mp3", ".wav", ".ogg"],
    }
    
    # Get file extension
    file_name = file_doc.file_name or ""
    ext = "." + file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    
    # Check if extension is allowed
    all_allowed = []
    for types in allowed_types.values():
        all_allowed.extend(types)
    
    if ext not in all_allowed:
        frappe.throw(
            _("File type {0} is not allowed").format(ext),
            frappe.ValidationError
        )
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if file_doc.file_size and file_doc.file_size > max_size:
        frappe.throw(
            _("File size exceeds maximum limit of 10MB"),
            frappe.ValidationError
        )


def sanitize_slug(slug):
    """
    Sanitize a slug to prevent injection attacks.
    
    Args:
        slug: Raw slug string
        
    Returns:
        str: Sanitized slug
    """
    if not slug:
        return slug
    
    # Remove any HTML tags
    slug = re.sub(r'<[^>]+>', '', slug)
    
    # Remove any script-related content
    slug = re.sub(r'javascript:', '', slug, flags=re.IGNORECASE)
    slug = re.sub(r'on\w+\s*=', '', slug, flags=re.IGNORECASE)
    
    # Only allow lowercase letters, numbers, and hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug.lower())
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    
    return slug


def rate_limit(key, limit=10, window=60):
    """
    Simple rate limiting using Frappe's cache.
    
    Args:
        key: Rate limit key
        limit: Maximum requests per window
        window: Time window in seconds
        
    Returns:
        bool: True if allowed, False if rate limited
    """
    cache_key = f"osduo_rate_limit:{key}"
    
    # Get current count
    current = frappe.cache().get_value(cache_key)
    if current is None:
        current = 0
    
    # Check limit
    if current >= limit:
        return False
    
    # Increment counter
    frappe.cache().set_value(cache_key, current + 1, expires_in_sec=window)
    
    return True


def check_slug_enumeration(slug):
    """
    Check for slug enumeration attempts.
    
    Args:
        slug: Slug to check
        
    Returns:
        bool: True if suspicious, False if ok
    """
    # Check for common enumeration patterns
    suspicious_patterns = [
        r'^[0-9]+$',  # All numbers
        r'admin',
        r'test',
        r'root',
        r'system',
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, slug, re.IGNORECASE):
            return True
    
    return False


def get_client_ip():
    """
    Get client IP address from request.
    
    Returns:
        str: Client IP address
    """
    if not frappe.request:
        return "127.0.0.1"
    
    # Check for forwarded IP
    forwarded = frappe.request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check for real IP
    real_ip = frappe.request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return frappe.request.remote_addr or "127.0.0.1"


def validate_email(email):
    """
    Validate email format.
    
    Args:
        email: Email address
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    
    # Basic email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """
    Validate phone format.
    
    Args:
        phone: Phone number
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it contains only digits
    return cleaned.isdigit() and len(cleaned) >= 7


def log_security_event(event_type, details=None):
    """
    Log a security event for audit trail.
    
    Args:
        event_type: Type of security event
        details: Additional details
    """
    try:
        log_entry = {
            "event_type": event_type,
            "user": frappe.session.user,
            "ip": get_client_ip(),
            "timestamp": frappe.utils.now_datetime(),
            "details": details,
        }
        
        frappe.logger().info(f"Security Event: {event_type} | User: {log_entry['user']} | IP: {log_entry['ip']}")
        
    except Exception:
        pass  # Don't fail operations for logging
