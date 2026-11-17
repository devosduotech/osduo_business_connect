# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""SEO helpers for the public pages.

Single source of truth for the ``<head>`` metadata rendered by
``templates/bc_base.html`` and for the JSON-LD blocks emitted on public pages.

``frappe`` is never imported at module level here (the canonical-URL helper is
imported lazily inside :func:`absolute_url`), so the structural test suite can
import and exercise this module without a bench.
"""

from __future__ import annotations

import html as _html
import json
import re

from osduo_business_connect.hooks import OSDUO_BRANDING

# Crawl directives.
DEFAULT_ROBOTS = "index,follow,max-image-preview:large"
NOINDEX = "noindex,nofollow"

OG_LOCALE = "en_IN"
OG_TYPE_DEFAULT = "website"
TWITTER_CARD = "summary_large_image"

# Paths that must never be indexed: the site root (``home_page = "login"``) and
# the login route itself. Other private pages set ``context.seo`` directly.
# Compared on the slash-stripped form, so both ``login`` and ``/login`` match.
_LOGIN_PATHS = ("", "login")

_SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1\s*>", re.IGNORECASE | re.DOTALL)
_BLOCK_TAG_RE = re.compile(
    r"</?(?:p|div|br|hr|li|ul|ol|tr|td|th|table|h[1-6]|section|article|header|footer|"
    r"blockquote|figure|figcaption|pre)\b[^>]*>",
    re.IGNORECASE,
)
_TAG_RE = re.compile(r"<[^>]*>")
_WS_RE = re.compile(r"\s+")
_TRIM_CHARS = " \t\r\n,;:.!?\u2013\u2014-"


def clean_text(value, limit=155):
    """Return a plain-text summary of ``value`` (which may contain HTML).

    Script/style blocks and tags are removed, HTML entities decoded, runs of
    whitespace collapsed, and the result cut on a word boundary when it is
    longer than ``limit`` characters. ``limit=0`` disables truncation.
    """
    if value is None:
        return ""
    text = str(value)
    text = _SCRIPT_STYLE_RE.sub(" ", text)
    text = _BLOCK_TAG_RE.sub(" ", text)
    text = _TAG_RE.sub("", text)
    text = _html.unescape(text)
    text = _WS_RE.sub(" ", text).strip()
    if limit and len(text) > limit:
        cut = text[:limit]
        space = cut.rfind(" ")
        if space > 0:
            cut = cut[:space]
        text = cut.rstrip(_TRIM_CHARS)
    return text


def absolute_url(path):
    """Make ``path`` absolute against the canonical base URL.

    Uses :func:`osduo_business_connect.utils.urls.get_canonical_base_url`
    (``host_name``-first) — never the host of the current request — so canonical
    and Open Graph URLs stay stable when a card is opened through another domain.
    """
    from osduo_business_connect.utils.urls import get_canonical_base_url

    base = (get_canonical_base_url() or "").rstrip("/")
    if not path:
        return base
    path = str(path)
    if path.startswith(("http://", "https://")):
        return path
    return f"{base}/{path.lstrip('/')}"


def jsonld(obj):
    """Serialise ``obj`` for a ``<script type="application/ld+json">`` block.

    Non-ASCII is escaped and ``<`` is written as ``\\u003c`` so user-entered text
    can never break out of the script element (``</script>``).
    """
    return json.dumps(obj, ensure_ascii=True, separators=(",", ":")).replace("<", "\\u003c")


def is_login_path(path):
    """True for the site root and ``/login`` (``home_page = "login"``).

    Frappe page paths may arrive with or without a leading slash (the router
    stores them as ``login``, the request carries ``/login``), so the comparison
    is made on the stripped form.
    """
    path = (path or "").split("?", 1)[0].split("#", 1)[0].strip("/")
    return path in _LOGIN_PATHS


def build_seo(
    title,
    description,
    path,
    image=None,
    page_type=OG_TYPE_DEFAULT,
    robots=DEFAULT_ROBOTS,
    business=None,
    blocks=None,
):
    """Assemble the ``seo`` context dict consumed by ``bc_base.html``.

    ``title`` and ``description`` are cleaned of markup (the title is not
    truncated, the description is cut to a 155-character search snippet).
    ``image`` may be a relative or absolute URL; when falsy the bundled Open
    Graph image is used. ``business`` is reserved for the JSON-LD builders
    (Phase B) and is not read here yet. ``blocks`` is the list of JSON-LD dicts
    to emit (empty until Phase B).
    """
    clean_title = clean_text(title, limit=0)
    clean_description = clean_text(description, limit=155)

    canonical = absolute_url(path)
    image_url = absolute_url(image) if image else absolute_url(OSDUO_BRANDING["og_image"])
    image_alt = clean_title or OSDUO_BRANDING["app_name"]

    return {
        "title": clean_title,
        "description": clean_description,
        "canonical": canonical,
        "robots": robots,
        "og_title": clean_title,
        "og_description": clean_description,
        "og_url": canonical,
        "og_image": image_url,
        "og_image_alt": image_alt,
        "og_type": page_type,
        "og_site_name": OSDUO_BRANDING["app_name"],
        "og_locale": OG_LOCALE,
        "twitter_card": TWITTER_CARD,
        "jsonld": list(blocks or []),
    }
