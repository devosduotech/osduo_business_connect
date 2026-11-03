# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Canonical URL helpers.

Public URLs (card and business) are frozen into printed QR codes and NFC
taps, so they must be derived from the site's canonical base URL — never from
the host of the current request. Otherwise saving a card through a custom
domain would silently change the URL encoded on already-printed material.

The canonical base is controlled, in order of precedence:

1. ``host_name`` in ``site_config.json`` (recommended for production/BYOD)
2. SSL/wildcard configuration + the site name (bench default)
3. ``Website Settings → Subdomain`` as a last resort

``host_name`` may be written with or without a scheme. Written without one it
is treated as ``https://`` — except for loopback/private hosts, which are
almost always a bench served over plain HTTP.

``frappe.utils.get_url`` is deliberately not used when ``host_name`` exists:
that helper appends the bench's dev webserver port whenever ``developer_mode``
is on, which would bake ``:8000`` into a real production domain.

See docs/PWA.md for setup notes.
"""

import ipaddress
import re

import frappe

LOCAL_NAME_RE = re.compile(r"^(localhost|.*\.local|.*\.localhost)$")
SCHEME_RE = re.compile(r"^(https?)://(.*)$", re.I)


def _is_local_host(host):
    """True for loopback, private-network and ``.local``-style dev hosts."""
    host = (host or "").strip().lower().strip("[]")
    if not host:
        return False
    if LOCAL_NAME_RE.match(host):
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return bool(ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved)


def _normalize_host(value):
    """Turn a configured host into a full ``scheme://host[:port]`` base URL."""
    value = (value or "").strip().rstrip("/")
    if not value:
        return None

    match = SCHEME_RE.match(value)
    if match:
        return f"{match.group(1).lower()}://{match.group(2)}"

    # Written without a scheme: a public host is https, a dev host is http.
    scheme = "http" if _is_local_host(value.split(":")[0]) else "https"
    return f"{scheme}://{value}"


def _with_dev_port(base, conf):
    """Append the bench webserver port, but only to local dev hosts."""
    if not base or ":" in base.split("://", 1)[-1].split("/", 1)[0]:
        return base
    if not conf.get("developer_mode"):
        return base
    port = conf.get("webserver_port")
    if not port or not _is_local_host(_hostname(base)):
        return base
    return f"{base}:{port}"


def _hostname(base):
    """Return the bare hostname of a ``scheme://host[:port]`` value."""
    host = (base or "").split("://", 1)[-1].split("/", 1)[0]
    return host.rsplit(":", 1)[0] if ":" in host else host


def get_canonical_base_url():
    """Return the site's canonical base URL without a trailing slash."""
    conf = frappe.local.conf or {}
    for key in ("host_name", "hostname"):
        base = _normalize_host(conf.get(key))
        if base:
            return _with_dev_port(base, conf)

    # Nothing configured: let Frappe resolve the site name / subdomain.
    url = frappe.utils.get_url(allow_header_override=False) or ""
    return url.rstrip("/")


def get_canonical_base_url_source():
    """Which configuration produced the canonical base (for diagnostics)."""
    conf = frappe.local.conf or {}
    for key in ("host_name", "hostname"):
        if (conf.get(key) or "").strip():
            return f"site_config.json -> {key}"
    return "frappe.utils.get_url() (no host_name configured)"


def describe_canonical_url():
    """Show what the app will print into links and QR codes.

    ``bench --site <site> execute
    osduo_business_connect.utils.urls.describe_canonical_url``
    """
    conf = frappe.local.conf or {}
    return {
        "canonical_base_url": get_canonical_base_url(),
        "source": get_canonical_base_url_source(),
        "host_name": conf.get("host_name") or conf.get("hostname"),
        "developer_mode": conf.get("developer_mode"),
        "webserver_port": conf.get("webserver_port"),
    }


def get_business_public_url(slug):
    if not slug:
        return None
    return f"{get_canonical_base_url()}/b/{slug}"


def get_card_public_url(slug):
    if not slug:
        return None
    return f"{get_canonical_base_url()}/c/{slug}"
