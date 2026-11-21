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

Request normalisation deliberately fails closed:

* ``frappe.form_dict.cmd`` is what Frappe actually executes, so it is evaluated
  alongside (not instead of) the method in the URL.
* Unversioned, v1 and v2 API routes all map to the same method/DocType checks.
* Any API request that is not on the explicit guest-safe allowlist is private
  for the subscription-status check. Token authentication happens *after*
  ``before_request``, so ``frappe.session.user`` alone cannot classify it.

Public pages (/, /b/*, /c/*) and the explicit guest-safe APIs stay reachable on
a Suspended site so printed QR/NFC links and lead capture keep working.
"""

import json
import re
from urllib.parse import unquote, urlparse
from xml.sax.saxutils import quoteattr

import frappe
from frappe import _

from osduo_business_connect.subscription.constants import (
    ADVANCED_ADMIN_DOCTYPES,
    ADVANCED_ADMIN_READ_DOCTYPES,
    ANALYTICS_DOCTYPES,
    CRM_EXTRA_DOCTYPES,
    CUSTOMER_DESK_LOCKDOWN_PLANS,
    CUSTOMER_ROLES,
    CUSTOMER_USER_ADMIN_DOCTYPES,
    IMPORT_EXPORT_DOCTYPES,
    MULTI_BUSINESS_DOCTYPES,
    PRIVILEGED_ROLES,
    TEAM_MANAGEMENT_DOCTYPES,
)
from osduo_business_connect.subscription.entitlements import (
    get_entitlements,
    has_feature,
)

# ---------------------------------------------------------------------------
# Route / method inventory (verified against Frappe v16 and Frappe CRM)
# ---------------------------------------------------------------------------

# Frappe v16 serves the Desk at /desk/<slug> (v15 used /app/<slug>, still
# redirected). Gate both spellings: an ungated Desk route would otherwise
# bypass the request-level plan check on the exact URL a v16 user visits.
def _desk_routes(*slugs):
    return tuple(f"/{prefix}/{slug}" for prefix in ("app", "desk") for slug in slugs)


CRM_PAGE_PREFIXES = ("/crm/", "/crm-form/")
CRM_PAGES = frozenset({"/crm", "/app/crm", "/desk/crm"})
CRM_DESK_PREFIXES = _desk_routes(
    "crm-",
    "fcrm-note",
    "lead-sync-",
    "failed-lead-sync-log",
    "facebook-page",
    "facebook-lead-form",
)
CRM_METHOD_PREFIX = "crm."
CRM_DOCTYPE_PREFIX = "CRM "

# Professional keeps one Business and its owner member, but cannot create
# additional profiles or manage a team. Edit routes for the single Business
# remain available.
MULTI_BUSINESS_CREATE_PAGES = frozenset(
    path + "/new"
    for path in _desk_routes("business")
) | frozenset(
    f"{base}/{slug}/new"
    for base in _desk_routes("business")
    for slug in ("view", "form")
)
TEAM_MANAGEMENT_PAGES = _desk_routes("business-member") + ("/portal/team",)
TEAM_MANAGEMENT_METHODS = frozenset({
    "osduo_business_connect.subscription.team_invite.get_team_page_data",
    "osduo_business_connect.subscription.team_invite.invite_team_member",
})

ANALYTICS_PAGES = ("/analytics",) + _desk_routes("analytics", "engagement-event")
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
IMPORT_EXPORT_PAGES = _desk_routes("data-import", "data-export")
# Report View can export any DocType to CSV/XLSX outside the Data Export form.
IMPORT_EXPORT_METHODS = frozenset({"frappe.desk.reportview.export_query"})

ADVANCED_ADMIN_DESK_PREFIXES = _desk_routes(
    "email-account",
    "email-domain",
    "whatsapp-",
    "fcrm-settings",
    "crm-global-settings",
    "crm-fields-layout",
    "crm-form-script",
    "crm-view-settings",
    "crm-sales-hierarchy",
    "crm-notification",
    "crm-telephony-agent",
    "crm-twilio-settings",
    "crm-exotel-settings",
    "crm-enrichment-settings",
    "erpnext-crm-settings",
)
# MCP is an integration/admin surface with an open-ended tool inventory; fail
# closed to Enterprise rather than trying to enumerate every tool.
ADVANCED_ADMIN_PATH_PREFIXES = ADVANCED_ADMIN_DESK_PREFIXES + ("/api/v2/mcp",)

# ERP / Enterprise-only configuration surfaces. The list is intentionally
# broader than the Desk routes: v1/v2 REST and RPC calls are normalised to the
# same method names before being checked.
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
    "crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.save_fields_layout",
    "crm.fcrm.doctype.crm_view_settings.crm_view_settings.create",
    "crm.fcrm.doctype.crm_view_settings.crm_view_settings.update",
    "crm.fcrm.doctype.crm_view_settings.crm_view_settings.delete",
    "crm.fcrm.doctype.crm_view_settings.crm_view_settings.set_as_default",
    "crm.fcrm.doctype.crm_view_settings.crm_view_settings.create_or_update_standard_view",
    "crm.fcrm.doctype.crm_view_settings.crm_view_settings.pin",
    "crm.fcrm.doctype.crm_view_settings.crm_view_settings.public",
    "crm.fcrm.doctype.crm_view_settings.crm_view_settings.fetch_and_update_kanban_columns",
    "crm.fcrm.doctype.erpnext_crm_settings.erpnext_crm_settings.dismiss_sync_issue",
    "crm.fcrm.doctype.fcrm_settings.fcrm_settings.restore_defaults",
    "crm.fcrm.doctype.fcrm_settings.fcrm_settings.restore_demo_data",
    "crm.fcrm.doctype.erpnext_crm_settings.erpnext_crm_settings.reset_erpnext_form_script",
    "crm.fcrm.doctype.erpnext_crm_settings.erpnext_crm_settings.run_product_sync",
})

# Short names used by v2's /method/<doctype>/<method> shorthand. These are all
# Enterprise-only writes; the full controller paths above are still checked.
ADVANCED_ADMIN_METHOD_SHORT_NAMES = frozenset({
    "create_email_account",
    "add_existing_users",
    "update_user_role",
    "remove_crm_roles_from_user",
    "duplicate_assignment_rule",
    "save_form",
    "set_published",
    "delete_form",
    "grant_guest_link_access",
    "reset_to_default",
    "save_fields_layout",
    "create",
    "update",
    "delete",
    "set_as_default",
    "create_or_update_standard_view",
    "pin",
    "public",
    "fetch_and_update_kanban_columns",
    "dismiss_sync_issue",
    "restore_defaults",
    "restore_demo_data",
    "reset_erpnext_form_script",
    "run_product_sync",
})

API_TOKEN_METHOD = "frappe.core.doctype.user.user.generate_keys"
API_TOKEN_FIELDS = frozenset({"api_key", "api_secret"})

# Desk save runners and doc-method runners carry a doctype in their payload.
# They must be treated as writes even when the HTTP verb is GET.
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
    "frappe.desk.form.save.savedocs",
    "frappe.desk.form.save.cancel",
    "frappe.desk.form.save.discard",
    "frappe.desk.form.run_method.run_doc_method",
    "frappe.handler.run_doc_method",
    "frappe.handler.runserverobj",
    "frappe.api.v2.run_doc_method",
    "frappe.api.v2.execute_doc_method",
    # v2 RPC route shorthands (handle_rpc_call expands these to the module path)
    "run_doc_method",
    "execute_doc_method",
    "savedocs",
})
GENERIC_DOCTYPE_METHODS = GENERIC_WRITE_METHODS | frozenset({
    "frappe.client.get_list",
    "frappe.client.get_count",
    "frappe.client.get",
    "frappe.client.get_value",
    "frappe.client.has_permission",
    "frappe.client.get_doc_permissions",
    "frappe.desk.form.load.getdoc",
    "frappe.desk.form.load.get_docinfo",
    "frappe.desk.reportview.get",
})

# APIs deliberately reachable while a site is inaccessible. Keep this list
# short: everything else under /api/ fails closed for the status gate.
PUBLIC_API_METHODS = frozenset({
    "login",
    "logout",
    "ping",
    "frappe.ping",
    "frappe.auth.login",
    "frappe.api.v2.login",
    "frappe.api.v2.logout",
    "osduo_business_connect.enquiry.public_enquiry_api.submit_enquiry",
    "osduo_business_connect.card.public_api.get_public_card",
    "osduo_business_connect.card.public_api.download_vcard",
    "osduo_business_connect.analytics.analytics_service.log_event",
    "osduo_business_connect.pwa.get_app_icon",
    # The invitation link is emailed to a guest; acceptance must stay reachable
    # even while a site is Suspended so pending invites can be completed.
    "frappe.core.api.user_invitation.accept_invitation",
})

# Customer-safe pages and APIs. These are the only surfaces a Professional or
# Business customer needs outside the CRM product UI and the analytics page.
CUSTOMER_PORTAL_PAGES = frozenset({"/portal/team", "/portal/subscription"})

# Business-plan customer roles may open the BC workspace itself, but never the
# generic Desk or native User administration. Professional stays portal-only.
# Frappe v16 serves the workspace at /desk/business-connect and still accepts
# the older /app/business-connect alias; both are normalised below.
CUSTOMER_PORTAL_HOME = "/my-card"
CUSTOMER_WORKSPACE_HOME = "/desk/business-connect"
CUSTOMER_WORKSPACE_PATHS = frozenset({"/app/business-connect", "/desk/business-connect"})
DESK_PATHS = frozenset({"/app", "/desk"})


def _customer_landing(entitlements):
    """Private landing page for a locked-down customer on this plan."""
    if entitlements.get("plan_code") == "BUSINESS":
        return CUSTOMER_WORKSPACE_HOME
    return CUSTOMER_PORTAL_HOME


CUSTOMER_PORTAL_API_METHODS = frozenset({
    "osduo_business_connect.subscription.team_invite.get_team_page_data",
    "osduo_business_connect.subscription.team_invite.invite_team_member",
    "osduo_business_connect.subscription.subscription_page.get_my_subscription",
    "osduo_business_connect.card.my_card.get_my_cards",
    "osduo_business_connect.card.contact_exchange_api.record_contact_exchange",
    "osduo_business_connect.card.contact_exchange_api.get_contact_exchanges",
    "osduo_business_connect.subscription.doctype.add_on_order.add_on_order.get_addon_quote",
    "osduo_business_connect.subscription.doctype.add_on_master.add_on_master.get_orderable_addons",
})

# Direct calls to these bypass BC's owner/business/plan/seat validation. The
# BC wrapper is the only invitation entry point allowed for customers; the
# guest acceptance endpoint remains available for the emailed link.
CUSTOMER_BLOCKED_INVITE_METHODS = frozenset({
    "frappe.core.api.user_invitation.invite_by_email",
    "frappe.core.api.user_invitation.cancel_invitation",
    "frappe.core.api.user_invitation.resend_invitation",
    "frappe.core.api.user_invitation.get_pending_invitations",
    "frappe.core.doctype.user_invitation.user_invitation.cancel_invite",
    "frappe.core.doctype.user_invitation.user_invitation.expire",
})
CUSTOMER_ALLOWED_INVITE_METHODS = frozenset({
    "frappe.core.api.user_invitation.accept_invitation",
})
CUSTOMER_BLOCKED_METHOD_PREFIXES = (
    "frappe.core.api.user_invitation.",
    "frappe.core.doctype.user_invitation.user_invitation.",
    "frappe.core.doctype.user.user.",
    "frappe.core.doctype.role.",
    "frappe.desk.doctype.role_",
)
# v2's /method/<doctype>/<method> shorthand reduces controller methods to a
# short name, so block those too. User-admin DocType routes are caught by the
# DocType set below even when the short name is not listed here.
CUSTOMER_BLOCKED_METHOD_SHORT_NAMES = frozenset({
    "invite_by_email",
    "cancel_invitation",
    "resend_invitation",
    "get_pending_invitations",
    "cancel_invite",
    "expire",
    "generate_keys",
})

FEATURE_MESSAGES = {
    "crm_access": ("CRM", "Business"),
    "analytics": ("Analytics", "Business"),
    "import_export": ("Import and export", "Business"),
    "multiple_business_profiles": ("Multiple business profiles", "Business"),
    "team_management": ("Team management", "Business"),
    "advanced_admin": ("Advanced administration", "Enterprise"),
}

WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
API_PREFIXES = ("/api/method/", "/api/v1/method/", "/api/v2/method/")
RESOURCE_PREFIXES = (
    "/api/resource/",
    "/api/v1/resource/",
    "/api/v2/document/",
    "/api/v2/doctype/",
    "/api/v2/discovery/doctype/",
)
V2_METHOD_ROUTE = re.compile(r"^/api/v\d+/method/([^/]+)/([^/]+)$")
RESOURCE_COLLECTION_ROUTE = re.compile(
    r"^/api/(?:v\d+/)?(?:resource|document)/([^/]+)/?$"
)
DOC_METHOD_ROUTE = re.compile(
    r"^/api/(?:v\d+/)?(?:resource|document)/([^/]+)/[^/]+/(?:method|copy)/(.*)$"
)


# ---------------------------------------------------------------------------
# Request normalisation helpers
# ---------------------------------------------------------------------------

def _path():
    request = getattr(frappe.local, "request", None)
    return (getattr(request, "path", "") or "").split("?", 1)[0].rstrip("/") or "/"


def _request_method():
    request = getattr(frappe.local, "request", None)
    return str(getattr(request, "method", "GET") or "GET").upper()


def _request_sources():
    """Return every request parameter source Frappe may read from."""
    sources = []
    try:
        sources.append(dict(frappe.form_dict or {}))
    except Exception:
        pass
    request = getattr(frappe.local, "request", None)
    if request is not None:
        try:
            payload = request.get_json(silent=True)
        except Exception:
            payload = None
        if isinstance(payload, dict):
            sources.append(payload)
    return sources


def _parse_json(value):
    if not isinstance(value, str) or len(value) > 200_000:
        return value
    try:
        parser = getattr(frappe, "parse_json", json.loads)
        return parser(value)
    except Exception:
        return value


def _walk_payload(value, depth=0):
    """Yield dicts from form values, JSON strings and nested doc structures."""
    if depth > 8:
        return
    if isinstance(value, str):
        parsed = _parse_json(value)
        if parsed is not value and isinstance(parsed, (dict, list)):
            yield from _walk_payload(parsed, depth + 1)
        return
    if isinstance(value, dict):
        yield value
        for key, nested in value.items():
            if key in (
                "doc", "docs", "data", "args", "fields", "fieldname", "value", "kwargs"
            ):
                yield from _walk_payload(nested, depth + 1)
        return
    if isinstance(value, (list, tuple)):
        for nested in value[:200]:
            yield from _walk_payload(nested, depth + 1)


def _request_methods(path):
    """All method names that could execute for this request.

    Frappe's handler executes ``form_dict.cmd`` before it looks at the URL, so
    evaluating only the URL would let a harmless path smuggle a gated cmd.
    """
    methods = set()
    for source in _request_sources():
        for key in ("cmd", "method", "run_method"):
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                methods.add(value.strip())

    for prefix in API_PREFIXES:
        if path.startswith(prefix):
            methods.add(unquote(path[len(prefix):]).replace("/", "."))

    match = V2_METHOD_ROUTE.match(path)
    if match:
        # v2 also supports /method/<doctype>/<method>, which is expanded by
        # handle_rpc_call before dispatch. Expand it here too: checking only
        # the short method name misses controller writes such as
        # /method/CRM%20Fields%20Layout/save_fields_layout.
        first, second = (unquote(group) for group in match.groups())
        methods.update({second, f"{first}.{second}"})
        try:
            from frappe.modules.utils import load_doctype_module

            methods.add(f"{load_doctype_module(first).__name__}.{second}")
        except Exception:
            # During install/migrate or in isolated tests the module may not
            # be importable; the short-name fallback below still applies.
            pass

    match = DOC_METHOD_ROUTE.match(path)
    if match:
        methods.update({"execute_doc_method", "frappe.api.v2.execute_doc_method"})
        tail = unquote(match.group(2)).strip("/")
        if tail.startswith("method/"):
            methods.add(tail[len("method/"):])

    return methods


def _request_doctypes(path):
    """All DocTypes this request can address, from route and payload."""
    doctypes = set()
    for prefix in RESOURCE_PREFIXES:
        if path.startswith(prefix):
            value = unquote(path[len(prefix):]).split("/", 1)[0].strip()
            if value:
                doctypes.add(value)

    match = DOC_METHOD_ROUTE.match(path)
    if match:
        doctypes.add(unquote(match.group(1)).strip())

    match = V2_METHOD_ROUTE.match(path)
    if match:
        doctypes.add(unquote(match.group(1)).strip())

    for source in _request_sources():
        for payload in _walk_payload(source):
            value = payload.get("doctype")
            if isinstance(value, str) and value.strip():
                doctypes.add(value.strip())
    return doctypes


def _created_doctypes(path, methods, is_write):
    """DocTypes this request creates (as opposed to edits an existing row)."""
    if not is_write:
        return set()
    created = set()
    if methods & {"frappe.client.insert", "frappe.client.insert_many"}:
        for source in _request_sources():
            for payload in _walk_payload(source):
                value = payload.get("doctype")
                if isinstance(value, str) and value.strip():
                    created.add(value.strip())

    match = RESOURCE_COLLECTION_ROUTE.match(path)
    if match:
        created.add(unquote(match.group(1)).strip())

    for source in _request_sources():
        for payload in _walk_payload(source):
            value = payload.get("doctype")
            if isinstance(value, str) and value.strip() and (
                payload.get("is_new") or payload.get("__islocal")
            ):
                created.add(value.strip())
    return created


def _method_matches(methods, prefix, names):
    return any(
        method.startswith(prefix) and method[len(prefix):] in names
        for method in methods
    )


def _session_roles(user=None):
    if not user:
        user = getattr(frappe.session, "user", None) or "Guest"
    getter = getattr(frappe, "get_roles", None)
    if not callable(getter):
        return set()
    try:
        return set(getter(user) or [])
    except Exception:
        return set()


def _is_locked_down_customer(entitlements, user=None):
    """Professional/Business customers without a provider role lose the Desk."""
    if entitlements.get("plan_code") not in CUSTOMER_DESK_LOCKDOWN_PLANS:
        return False
    roles = _session_roles(user)
    if roles & PRIVILEGED_ROLES:
        return False
    return bool(roles & CUSTOMER_ROLES)


def set_customer_login_home(login_manager=None):
    """Frappe ``on_login`` hook: send customer logins to their private area.

    ``LoginManager.set_user_info`` runs after this hook and reads
    ``frappe.local.flags.home_page`` before Role, Website Settings or the
    user's default workspace. Setting it here changes the ``home_page`` in the
    login API response, which Frappe's login JavaScript navigates to. Keeping
    the session check in ``_is_locked_down_customer`` means provider logins and
    Enterprise are unaffected.
    """
    try:
        user = getattr(login_manager, "user", None) or getattr(frappe.session, "user", None)
        ent = get_entitlements()
        if _is_locked_down_customer(ent, user):
            frappe.flags.home_page = _customer_landing(ent)
    except Exception:
        # A failed nav preference lookup must never fail the login itself. The
        # request-level gate remains the authoritative security boundary.
        pass


def _customer_user_admin_attempt(path, methods, doctypes, entitlements=None):
    """Return True for any native User/Role/User Invitation surface.

    The allowlist is checked before this helper so the BC wrapper and the
    emailed guest-acceptance link are not caught by the broad prefixes.
    """
    if "/portal/" in path or path in CUSTOMER_PORTAL_PAGES:
        return False
    # Explicit BC portal APIs are safe, but only when no other command is being
    # smuggled in the same request (form_dict.cmd wins at dispatch time).
    if methods and methods <= (CUSTOMER_PORTAL_API_METHODS | CUSTOMER_ALLOWED_INVITE_METHODS):
        return False
    workspace_allowed = bool(
        entitlements and entitlements.get("plan_code") == "BUSINESS"
    )
    is_desk_path = path in ("/app", "/desk") or path.startswith(("/app/", "/desk/"))
    if is_desk_path and not (
        workspace_allowed and path in CUSTOMER_WORKSPACE_PATHS
    ):
        return True
    if doctypes & CUSTOMER_USER_ADMIN_DOCTYPES:
        return True

    for method in methods:
        if method in CUSTOMER_ALLOWED_INVITE_METHODS:
            continue
        if method in CUSTOMER_BLOCKED_INVITE_METHODS:
            return True
        if method.startswith(CUSTOMER_BLOCKED_METHOD_PREFIXES):
            return True
        if method in CUSTOMER_BLOCKED_METHOD_SHORT_NAMES:
            return True
    return False


def _path_user_name(path):
    for prefix in (
        "/api/resource/User/",
        "/api/v1/resource/User/",
        "/api/v2/document/User/",
    ):
        if path.startswith(prefix):
            return unquote(path[len(prefix):]).split("/", 1)[0]
    return None


def _unchanged_user_token(name, field, value):
    """True when a payload only echoes an already-stored API credential."""
    if not name:
        return False
    try:
        old = frappe.db.get_value("User", name, field)
    except Exception:
        return False
    return bool(old) and str(old) == str(value)


def _fieldname_targets_token(raw_fieldname):
    """fieldname may be a plain field, a JSON string or a dict of fields."""
    if str(raw_fieldname) in API_TOKEN_FIELDS:
        return True
    return any(
        ({str(key) for key in item} & API_TOKEN_FIELDS)
        for item in _walk_payload(raw_fieldname)
    )


def _api_token_attempt(path, methods, doctypes, write=False):
    """Detect direct or indirect writes to User.api_key / api_secret."""
    if API_TOKEN_METHOD in methods:
        return True
    if not write or "User" not in doctypes:
        return False

    path_user = _path_user_name(path)
    for source in _request_sources():
        for payload in _walk_payload(source):
            keys = {str(key) for key in payload}

            # frappe.client.set_value accepts fieldname as a field, JSON string
            # or dict; all three forms are an explicit write attempt.
            raw_fieldname = payload.get("fieldname")
            if raw_fieldname and _fieldname_targets_token(raw_fieldname):
                return True

            fields = payload.get("fields")
            if isinstance(fields, dict) and (
                {str(key) for key in fields} & API_TOKEN_FIELDS
            ):
                return True
            if isinstance(fields, (list, tuple)) and any(
                str(field) in API_TOKEN_FIELDS for field in fields
            ):
                return True

            for field in keys & API_TOKEN_FIELDS:
                value = payload.get(field)
                if not value:
                    continue
                if _unchanged_user_token(
                    payload.get("name") or path_user, field, value
                ):
                    continue
                return True
    return False


def _upgrade_link(entitlements):
    url = entitlements.get("upgrade_url") or ""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ""
    return f" <a href={quoteattr(url)}>View plans</a>"


def _deny(feature_key, message, path):
    """Log and raise a 403. Never let logging mask the real denial."""
    _log_restriction(feature_key, path, message)
    # Frappe v16 hardcodes a generic message on HTML 403 pages and drops the
    # PermissionError text. Stash ours so the after_request hook can render it.
    # API responses already carry the exception message as JSON.
    frappe.flags.bc_plan_gate_message = str(message)
    frappe.throw(message, exc=frappe.PermissionError)


def _log_restriction(feature_key, path, message):
    if getattr(frappe.flags, "in_install", False) or getattr(frappe.flags, "in_migrate", False):
        return
    user = getattr(frappe.session, "user", "Guest")
    if user == "Guest":
        return

    # Do not let repeated automated requests grow the log without bound.
    cache_key = f"bc:plan-gate-log:{frappe.local.site}:{user}:{feature_key}:{path[:80]}"
    try:
        cache = frappe.cache
        count = int(cache.get_value(cache_key) or 0)
        if count >= 20:
            return
        cache.set_value(cache_key, count + 1, expires_in_sec=3600)
    except Exception:
        pass

    try:
        frappe.get_doc({
            "doctype": "Plan Restriction Log",
            "timestamp": frappe.utils.now_datetime(),
            "site": frappe.local.site,
            "user": user,
            "feature_key": feature_key,
            "attempted_route": path[:140],
            "message": str(message)[:300],
        }).insert(ignore_permissions=True)
    except Exception:
        pass


def _private_surface(path, methods):
    """Surfaces that must not be usable while the subscription is inaccessible."""
    public_prefixes = ("/assets/", "/files/", "/favicon", "/robots", "/b/", "/c/")
    if path.startswith(public_prefixes):
        return False
    if path.startswith(
        ("/app", "/crm", "/crm-form", "/desk", "/analytics", "/portal")
    ):
        return True
    if path.startswith("/api/"):
        # Token auth runs after before_request, so session.user is unreliable
        # here. Only the explicit guest-safe allowlist stays public.
        return not methods or any(method not in PUBLIC_API_METHODS for method in methods)
    return False


def _doctype_plan_gate(entitlements, doctypes, path, write=False):
    """Apply plan gates to every DocType this request can address."""
    created = _created_doctypes(path, _request_methods(path), write)
    for doctype in doctypes:
        if doctype.startswith(CRM_DOCTYPE_PREFIX) or doctype in CRM_EXTRA_DOCTYPES:
            _require_feature(entitlements, "crm_access", path)
        if doctype in ANALYTICS_DOCTYPES:
            _require_feature(entitlements, "analytics", path)
        if doctype in IMPORT_EXPORT_DOCTYPES:
            _require_feature(entitlements, "import_export", path)
        if doctype in MULTI_BUSINESS_DOCTYPES and doctype in created:
            _require_feature(entitlements, "multiple_business_profiles", path)
        if doctype in TEAM_MANAGEMENT_DOCTYPES and write:
            _require_feature(entitlements, "team_management", path)
        if doctype in ADVANCED_ADMIN_DOCTYPES and (
            write or doctype in ADVANCED_ADMIN_READ_DOCTYPES
        ):
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
    methods = _request_methods(path)
    doctypes = _request_doctypes(path)
    ent = get_entitlements()

    # Highest-priority home page in Frappe v16. Covers any get_home_page()
    # caller in this request (boot data, error pages, website routing) so a
    # customer never picks up a Desk default workspace.
    if _is_locked_down_customer(ent):
        frappe.flags.home_page = _customer_landing(ent)

    # Subscription status — never applied to public website/guest-safe APIs.
    if not ent.get("accessible") and _private_surface(path, methods):
        status = ent.get("status") or "Inactive"
        _deny(
            "site_access",
            _("This site is currently {0}. Please contact your plan administrator.").format(status),
            path,
        )

    # Customer Desk policy. Professional stays portal-only. Business customer
    # roles may open only the BC workspace; the generic Desk, framework routes
    # and native User/Role administration stay blocked. Enterprise keeps its
    # existing Desk-based advanced administration.
    if _is_locked_down_customer(ent) and _customer_user_admin_attempt(
        path, methods, doctypes, ent
    ):
        plan_name = ent.get("plan_name") or ent.get("plan_code") or "current"
        destination = (
            _("Business Connect workspace or portal")
            if ent.get("plan_code") == "BUSINESS"
            else _("Business Connect portal")
        )
        _deny(
            "desk_lockdown",
            _(
                "The Frappe Desk and native User administration are not available "
                "on the {0} plan. Use the {1} instead."
            ).format(plan_name, destination),
            path,
        )

    is_write = _request_method() in WRITE_METHODS or bool(
        methods & (GENERIC_WRITE_METHODS | {"execute_doc_method", "frappe.api.v2.execute_doc_method"})
    )

    # External CRM kill switch: block the generator and every way of writing
    # User.api_key / User.api_secret, including nested doc/payload structures.
    if not ent.get("external_crm_enabled") and _api_token_attempt(
        path, methods, doctypes, write=is_write
    ):
        _deny(
            "external_crm_disabled",
            _("API key and token generation is disabled on this site.") + _upgrade_link(ent),
            path,
        )

    # CRM (Business and above)
    if (
        path in CRM_PAGES
        or path.startswith(CRM_PAGE_PREFIXES + CRM_DESK_PREFIXES)
        or any(method.startswith(CRM_METHOD_PREFIX) for method in methods)
    ):
        _require_feature(ent, "crm_access", path)

    # Multiple Business profiles and Team management (Business and above).
    if path in MULTI_BUSINESS_CREATE_PAGES:
        _require_feature(ent, "multiple_business_profiles", path)
    if path.startswith(TEAM_MANAGEMENT_PAGES) or bool(methods & TEAM_MANAGEMENT_METHODS):
        _require_feature(ent, "team_management", path)

    # Analytics (Business and above)
    if (
        path.startswith(ANALYTICS_PAGES)
        or bool(methods & ANALYTICS_METHODS)
    ):
        _require_feature(ent, "analytics", path)

    # Import / Export (Business and above)
    if (
        path.startswith(IMPORT_EXPORT_PAGES)
        or bool(methods & IMPORT_EXPORT_METHODS)
        or _method_matches(methods, DATA_IMPORT_METHOD_PREFIX, DATA_IMPORT_METHODS)
        or _method_matches(methods, GRID_IMPORT_METHOD_PREFIX, GRID_IMPORT_METHODS)
    ):
        _require_feature(ent, "import_export", path)

    # DocType-level gates for resource routes, versioned routes and generic
    # client/Desk methods carrying a doctype in their payload.
    _doctype_plan_gate(ent, doctypes, path, write=is_write)

    # Advanced Administration (Enterprise only). v2's
    # /method/<doctype>/<method> shorthand is expanded above, and short admin
    # write names are checked explicitly so a failed module import cannot
    # turn an Enterprise-only write into a Business-plan GET.
    v2_match = V2_METHOD_ROUTE.match(path)
    v2_admin_write = bool(
        v2_match
        and unquote(v2_match.group(1)).strip() in ADVANCED_ADMIN_DOCTYPES
        and unquote(v2_match.group(2)).strip() in ADVANCED_ADMIN_METHOD_SHORT_NAMES
    )
    if (
        bool(methods & ADVANCED_ADMIN_METHODS)
        or path.startswith(ADVANCED_ADMIN_PATH_PREFIXES)
        or v2_admin_write
    ):
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

    # Defence in depth: a customer must never get through a DocType hook to a
    # native User, Role or User Invitation record. The request gate above is
    # authoritative because Administrator bypasses these hooks entirely.
    if (
        doctype in CUSTOMER_USER_ADMIN_DOCTYPES
        and _is_locked_down_customer(get_entitlements(), user)
    ):
        return False

    if doctype in IMPORT_EXPORT_DOCTYPES and not has_feature("import_export"):
        return False

    if doctype in MULTI_BUSINESS_DOCTYPES and ptype in ("create", "delete"):
        if not has_feature("multiple_business_profiles"):
            return False

    if doctype in TEAM_MANAGEMENT_DOCTYPES and ptype in ("write", "create", "delete"):
        flags = getattr(doc, "flags", None)
        if getattr(flags, "bc_bootstrap_owner", False):
            return True  # automatic owner row created with the first Business
        if not has_feature("team_management"):
            return False

    if doctype in ADVANCED_ADMIN_DOCTYPES and (
        doctype in ADVANCED_ADMIN_READ_DOCTYPES or ptype in ("write", "create", "delete")
    ):
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


# ---------------------------------------------------------------------------
# after_request hooks — landing redirects and actionable 403 pages
# ---------------------------------------------------------------------------
def _redirect_path(location):
    """Normalised path from a redirect target, including absolute same-site URLs."""
    try:
        path = (urlparse(location).path or "").rstrip("/") or "/"
    except Exception:
        return ""
    return path if path.startswith("/") else "/" + path


def _is_desk_path(location):
    """True for a Desk URL, including an absolute same-site redirect."""
    path = _redirect_path(location)
    if not path:
        return False
    if path in DESK_PATHS:
        return True
    return any(path.startswith(prefix + "/") for prefix in DESK_PATHS)


def rewrite_customer_desk_redirect(response=None, request=None):
    """Keep automatic logins off generic Desk routes for customers.

    Frappe v16 redirects an already-signed-in System User from ``/login`` to
    ``get_default_path()``. Our single ``add_to_apps_screen`` entry makes that
    ``/app/business-connect``. Business customer roles are allowed to use the
    BC workspace, so that target is normalised to the v16 route instead of
    being bounced to the portal; every other Desk target is rewritten to the
    plan's private landing page. Direct Desk requests still get their 403.
    """
    if response is None or getattr(response, "status_code", None) not in (301, 302, 303, 307, 308):
        return
    headers = getattr(response, "headers", None)
    if headers is None:
        return
    location = headers.get("Location") or ""
    if not location:
        return
    try:
        ent = get_entitlements()
    except Exception:
        return
    if not _is_locked_down_customer(ent):
        return

    target_path = _redirect_path(location)
    if target_path in CUSTOMER_WORKSPACE_PATHS and ent.get("plan_code") == "BUSINESS":
        target = CUSTOMER_WORKSPACE_HOME
    elif _is_desk_path(location):
        target = _customer_landing(ent)
    else:
        return

    if location != target:
        headers["Location"] = target
        frappe.flags.redirect_location = target


def render_plan_gate_message(response=None, request=None):
    """Replace Frappe's generic 403 page with the actual plan restriction.

    Frappe v16's ``handle_exception`` passes a fixed message to ErrorPage for
    HTTP 403, so the PermissionError text (plan name and upgrade link) is lost
    on page requests. API errors are unaffected: they already return the
    exception message as JSON, so this hook deliberately skips /api/.
    """
    message = getattr(frappe.flags, "bc_plan_gate_message", None)
    if not message or getattr(response, "status_code", None) != 403:
        return
    if request is not None and (getattr(request, "path", "") or "").startswith("/api/"):
        return

    back_label = "Back to login"
    back_url = "/login"
    try:
        ent = get_entitlements()
        if _is_locked_down_customer(ent):
            back_url = _customer_landing(ent)
            back_label = (
                "Back to Business Connect"
                if ent.get("plan_code") == "BUSINESS"
                else "Back to portal"
            )
    except Exception:
        pass

    html = (
        '<!doctype html><html><head><meta charset="utf-8">'
        "<title>Not Permitted</title></head>"
        '<body style="font-family:system-ui,sans-serif;max-width:640px;'
        'margin:10vh auto;padding:24px;line-height:1.6">'
        "<h1>Not Permitted</h1>"
        f"<p>{message}</p>"
        f'<p><a href="{back_url}">{back_label}</a></p>'
        "</body></html>"
    )
    try:
        response.set_data(html)
        response.headers["Content-Type"] = "text/html; charset=utf-8"
    except Exception:
        pass
