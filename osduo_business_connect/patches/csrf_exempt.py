"""
Monkey-patch Frappe v16 CSRF validation to exempt guest enquiry submission.

Frappe v16 validates CSRF in HTTPRequest.__init__() BEFORE checking if
the endpoint is whitelisted. Guest users have no CSRF token, so all
POST API calls fail.

Solution: Replace validate_csrf_token with a version that checks if
the request path is in the exempt list before throwing CSRF error.
"""

import frappe
import frappe.auth


_original_validate_csrf_token = frappe.auth.HTTPRequest.validate_csrf_token

# Paths that should bypass CSRF validation (guest form submissions)
CSRF_EXEMPT_PATHS = ["/submit-enquiry"]


def _patched_validate_csrf_token(self):
    """Skip CSRF for exempt paths, otherwise call original validation."""
    try:
        import flask
        path = flask.request.path
        method = flask.request.method
        if method == "POST" and any(path.startswith(p) for p in CSRF_EXEMPT_PATHS):
            return  # Skip CSRF for exempt paths
    except Exception:
        pass

    _original_validate_csrf_token(self)


def apply_patch():
    """Apply the CSRF exemption monkey-patch."""
    frappe.auth.HTTPRequest.validate_csrf_token = _patched_validate_csrf_token
