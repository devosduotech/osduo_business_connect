# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Plan enforcement at the HTTP boundary.

Frappe v16 calls ``before_request`` hooks but **ignores their return value**;
the only way to stop a request is to raise. ``frappe.PermissionError`` maps to
HTTP 403.

This is the authoritative gate because ``frappe.permissions.has_permission``
returns True immediately for Administrator and never calls DocType hooks for
that user. The DocType hooks and query conditions at the bottom of this module
are defence in depth for ordinary users, not the security boundary.

Public pages (/, /b/*, /c/*, lead capture APIs called as Guest) are never
blocked by the subscription-status check so a Suspended site stays reachable.
"""

import json
from urllib.parse import unquote

import frappe
from frappe import _

from osduo_business_connect.subscription.entitlements import (
    get_entitlements,
    has_feature,
)

# ---------------------------------------------------------------------------
# Route / method inventory (verified against Frappe v16 and Frappe CRM)
# ---------------------------------------------------------------------------

CRM_PAGE_PREFIXES = ("/crm/", "/crm-form/")
CRM_PAGES = frozenset({"/crm"})
CRM_DESK_PREFIXES = (
    "/app/crm-",
    "/app/fcrm-note",
    "/app/lead-sync-",
    "/app/failed-lead-sync-log",
)
CRM_METHOD_PREFIX = "crm."
CRM_DOCTYPE_PREFIX = "CRM "
CRM_EXTRA_DOCTYPES = frozenset({"FCRM Note", "Lead Sync Source", "Failed Lead Sync Log"})

ANALYTICS_PAGES = ("/analytics", "/app/analytics", "/app/engagement-event")
ANALYTICS_DOCTYPES = frozenset({"Engagement Event"})
ANALYTICS_METHODS = frozenset({
    "osduo_business_connect.pages.analytics.get_analytics",
    "osduo_business_connect.pages.analytics.get_business_list",
})

DATA_IMPORT_METHOD_PREFIX = "frappe.core.doctype.data_import.data_import."
DATA_IMPORT_METHODS = frozenset({
    "get_preview_from_template",
    "form_start_import",
    "stop_data_import",
    "get_import_fields",
    "download_template",
    "get_export_count",
    "download_errored_template",
    "download_skipped_rows",
    "download_import_log",
    "get_import_status",
    "get_import_log_count",
    "get_import_logs",
})
GRID_IMPORT_METHOD_PREFIX = "frappe.desk.form.grid_import."
GRID_IMPORT_METHODS = frozenset({
    "download_template",
    "parse_file",
    "parse_google_sheet",
    "get_column_map",
    "validate_rows",
})
IMPORT_EXPORT_PAGES = ("/app/data-import", "/app/data-export")
IMPORT_EXPORT_DOCTYPES = frozenset({"Data Import", "Data Export"})

ADVANCED_ADMIN_DESK_PREFIXES = (
    "/app/email-account",
    "/app/email-domain",
    "/app/whatsapp-",
    "/app/fcrm-settings",
    "/app/crm-global-settings",
    "/app/crm-fields-layout",
    "/app/crm-form-script",
    "/app/crm-view-settings",
    "/app/crm-sales-hierarchy",
    "/app/crm-notification",
    "/app/crm-telephony-agent",
    "/app/crm-twilio-settings",
    "/app/crm-exotel-settings",
    "/app/crm-enrichment-settings",
    "/app/erpnext-crm-settings",
)

# Configuration surfaces of "Advanced Administration" (Enterprise only).
ADVANCED_ADMIN_METHODS = frozenset({
    "crm.api.settings.create_email_account",
    "crm.api.user.add_existing_users",
    "crm.api.user.update_user_role",
    "crm.api.user.remove_crm_roles_from_user",
    "crm.api.assignment_rule.duplicate_assignment_rule",
    "crm.api.form.save_form",
    "crm.api.form.set_published",
    "crm.api.form.delete_form",
    "crm.api.form.grant_guest_link_access",
    "crm.api.dashboard.reset_to_default",
})
ADVANCED_ADMIN_DOCTYPES = frozenset({
    "Email Account",
    "Email Domain",
    "WhatsApp Settings",
    "WhatsApp Account",
    "WhatsApp Template",
    "FCRM Settings",
    "CRM Global Settings",
    "CRM Fields Layout",
    "CRM Form Script",
    "CRM View Settings",
    "CRM Sales Hierarchy",
    "CRM Notification",
    "CRM Telephony Agent",
    "CRM Twilio Settings",
    "CRM Exotel Settings",
    "CRM Enrichment Settings",
    "ERPNext CRM Settings",
})

API_TOKEN_METHOD = "frappe.core.doctype.user.user.generate_keys"
API_TOKEN_FIELDS = frozenset({"api_key", "api_secret"})

# Generic Frappe client methods that can write an arbitrary DocType. The target
# DocType has to be recovered from form_dict before DocType-level gates apply.
GENERIC_WRITE_METHODS = frozenset({
    "frappe.client.insert",
    "frappe.client.insert_many",
    "frappe.client.save",
    "frappe.client.set_value",
    "frappe.client.delete",
    "frappe.client.submit",
    "frappe.client.cancel",
    "frappe.client.bulk_update",
    "frappe.client.rename_doc",
})
# Reads too: they carry a doctype in form_dict and could otherwise reach a
# gated DocType without using /api/resource/<Doctype>.
GENERIC_DOCTYPE_METHODS = GENERIC_WRITE_METHODS | frozenset({
    "frappe.client.get_list",
    "frappe.client.get_count",
    "frappe.client.get",
    "frappe.client.get_value",
    "frappe.client.has_permission",
    "frappe.client.get_doc_permissions",
    "frappe.desk.form.load.getdoc",
})

FEATURE_MESSAGES = {
    "crm_access": ("CRM", "Business"),
    "analytics": ("Analytics", "Business"),
    "import_export": ("Import and export", "Business"),
    "advanced_admin": ("Advanced administration", "Enterprise"),
}

WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _path():
    request = getattr(frappe.local, "request", None)
    return (getattr(request, "path", "") or "").split("?", 1)[0].rstrip("/") or "/"


def _request_method():
    request = getattr(frappe.local, "request", None)
    return str(getattr(request, "method", "GET") or "GET").upper()


def _method_name(path):
    if path.startswith("/api/method/"):
        return unquote(path[len("/api/method/"):]).replace("/", ".")
    cmd = frappe.form_dict.get("cmd") if hasattr(frappe.form_dict, "get") else None
    return str(cmd) if cmd else ""


def _resource_doctype(path):
    if not path.startswith("/api/resource/"):
        return ""
    value = unquote(path[len("/api/resource/"):]).split("/", 1)[0]
    return value.strip()


def _payload():
    request = getattr(frappe.local, "request", None)
    if request is None:
        return {}
    try:
        data = request.get_json(silent=True)
    except Exception:
        data = None
    return data if isinstance(data, dict) else {}


def _target_doctype(path):
    """Recover the DocType a request will write, from route or generic payload."""
    direct = _resource_doctype(path)
    if direct:
        return direct

    data = dict(frappe.form_dict or {})
    payload = _payload()
    for source in (payload, data):
        doctype = source.get("doctype")
        if doctype:
            return str(doctype)
        for key in ("doc", "docs"):
            raw = source.get(key)
            if not raw:
                continue
            try:
                parsed = json.loads(raw) if isinstance(raw, str) else raw
            except (TypeError, ValueError):
                continue
            if isinstance(parsed, dict) and parsed.get("doctype"):
                return str(parsed["doctype"])
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict) and item.get("doctype"):
                        return str(item["doctype"])
    return ""


def _payload_has_api_key_fields():
    data = dict(frappe.form_dict or {})
    data.update(_payload())
    return bool(API_TOKEN_FIELDS & {str(key) for key in data.keys()})


def _upgrade_link(entitlements):
    url = entitlements.get("upgrade_url") or ""
    return f" <a href='{url}'>View plans</a>" if url else ""


def _deny(feature_key, message, path):
    """Log and raise a 403. Never let logging mask the real denial."""
    _log_restriction(feature_key, path, message)
    raise frappe.PermissionError(message)


def _log_restriction(feature_key, path, message):
    if getattr(frappe.flags, "in_install", False) or getattr(frappe.flags, "in_migrate", False):
        return
    try:
        frappe.get_doc({
            "doctype": "Plan Restriction Log",
            "timestamp": frappe.utils.now_datetime(),
            "site": frappe.local.site,
            "user": frappe.session.user,
            "feature_key": feature_key,
            "attempted_route": path,
            "message": str(message)[:500],
        }).insert(ignore_permissions=True)
    except Exception:
        pass


def _private_surface(path):
    """Surfaces that must not be usable while the subscription is inaccessible."""
    public_prefixes = ("/assets/", "/files/", "/favicon", "/robots", "/b/", "/c/")
    if path.startswith(public_prefixes):
        return False
    if path.startswith(("/app", "/crm", "/crm-form", "/desk", "/analytics")):
        return True
    if path.startswith("/api/"):
        return frappe.session.user != "Guest"
    return False


def _doctype_plan_gate(entitlements, doctype, path, write=False):
    """Apply plan gates to a DocType reached by resource or generic API routes."""
    if not doctype:
        return
    if doctype.startswith(CRM_DOCTYPE_PREFIX) or doctype in CRM_EXTRA_DOCTYPES:
        _require_feature(entitlements, "crm_access", path)
    if doctype in ANALYTICS_DOCTYPES:
        _require_feature(entitlements, "analytics", path)
    if doctype in IMPORT_EXPORT_DOCTYPES:
        _require_feature(entitlements, "import_export", path)
    if write and doctype in ADVANCED_ADMIN_DOCTYPES:
        _require_feature(entitlements, "advanced_admin", path)


def _require_feature(entitlements, feature_key, path):
    if has_feature(feature_key):
        return
    label, required_plan = FEATURE_MESSAGES[feature_key]
    message = _(
        "{0} is available on the {1} plan and above.{2}"
    ).format(label, required_plan, _upgrade_link(entitlements))
    _deny(feature_key, message, path)


# ---------------------------------------------------------------------------
# before_request hook
# ---------------------------------------------------------------------------

def enforce_plan_gates():
    """Frappe ``before_request`` hook. Raise PermissionError to block a request."""
    if getattr(frappe.flags, "in_install", False) or getattr(frappe.flags, "in_migrate", False):
        return

    path = _path()
    method = _method_name(path)
    ent = get_entitlements()

    # Subscription status — never applied to the public website.
    if not ent.get("accessible") and _private_surface(path):
        status = ent.get("status") or "Inactive"
        _deny(
            "site_access",
            _("This site is currently {0}. Please contact your plan administrator.").format(status),
            path,
        )

    # External CRM kill switch: block both the whitelisted generator and direct
    # writes to User.api_key / User.api_secret on every plan.
    if not ent.get("external_crm_enabled"):
        is_token_method = method == API_TOKEN_METHOD
        is_user_write = (
            path.startswith("/api/resource/User")
            and _request_method() in WRITE_METHODS
            and _payload_has_api_key_fields()
        )
        if is_token_method or is_user_write:
            _deny(
                "external_crm_disabled",
                _("API key and token generation is disabled on this site.") + _upgrade_link(ent),
                path,
            )

    is_write = _request_method() in WRITE_METHODS

    # CRM (Business and above)
    if (
        path in CRM_PAGES
        or path.startswith(CRM_PAGE_PREFIXES + CRM_DESK_PREFIXES)
        or method.startswith(CRM_METHOD_PREFIX)
    ):
        _require_feature(ent, "crm_access", path)

    # Analytics (Business and above)
    if path.startswith(ANALYTICS_PAGES) or method in ANALYTICS_METHODS:
        _require_feature(ent, "analytics", path)

    # Import / Export (Business and above)
    import_export = (
        path.startswith(IMPORT_EXPORT_PAGES)
        or (
            method.startswith(DATA_IMPORT_METHOD_PREFIX)
            and method[len(DATA_IMPORT_METHOD_PREFIX):] in DATA_IMPORT_METHODS
        )
        or (
            method.startswith(GRID_IMPORT_METHOD_PREFIX)
            and method[len(GRID_IMPORT_METHOD_PREFIX):] in GRID_IMPORT_METHODS
        )
    )
    if import_export:
        _require_feature(ent, "import_export", path)

    # DocType-level gates for direct resource access and generic client methods.
    resource_type = _resource_doctype(path)
    _doctype_plan_gate(ent, resource_type, path, write=is_write)
    if method in GENERIC_DOCTYPE_METHODS:
        _doctype_plan_gate(
            ent,
            _target_doctype(path),
            path,
            write=is_write or method in GENERIC_WRITE_METHODS,
        )

    # Advanced Administration (Enterprise only)
    advanced_target = (
        _target_doctype(path) if method in GENERIC_DOCTYPE_METHODS else resource_type
    )
    if (
        method in ADVANCED_ADMIN_METHODS
        or path.startswith(ADVANCED_ADMIN_DESK_PREFIXES)
    ):
        _require_feature(ent, "advanced_admin", path)
    elif advanced_target in ADVANCED_ADMIN_DOCTYPES and is_write:
        _require_feature(ent, "advanced_admin", path)


# ---------------------------------------------------------------------------
# Defence in depth — DocType hooks (Frappe v16: returning None means DENY)
# ---------------------------------------------------------------------------

def has_permission_for_doctype(doc, user=None, ptype=None):
    """Return True for 'no OSDuo objection', False to deny.

    Never returns None: Frappe v16's has_controller_permissions does
    ``return bool(controller_permission)`` for a falsy value, so None denies.
    """
    if getattr(frappe.flags, "in_install", False) or getattr(frappe.flags, "in_migrate", False):
        return True

    doctype = getattr(doc, "doctype", None)
    if not doctype:
        return True

    if doctype in IMPORT_EXPORT_DOCTYPES and not has_feature("import_export"):
        return False

    if doctype in ADVANCED_ADMIN_DOCTYPES and ptype in ("write", "create", "delete"):
        if not has_feature("advanced_admin"):
            return False

    if doctype == "User" and ptype in ("write", "create"):
        ent = get_entitlements()
        if not ent.get("external_crm_enabled") and _doc_changes_api_fields(doc):
            return False

    return True


def _doc_changes_api_fields(doc):
    for field in API_TOKEN_FIELDS:
        new_value = doc.get(field)
        if not new_value:
            continue
        name = getattr(doc, "name", None)
        old_value = frappe.db.get_value("User", name, field) if name else None
        if new_value != old_value:
            return True
    return False


def import_export_query_conditions(user=None):
    # Table-agnostic: the same helper is registered for several DocTypes.
    return "" if has_feature("import_export") else "1=0"


def advanced_admin_query_conditions(user=None):
    return "" if has_feature("advanced_admin") else "1=0"
