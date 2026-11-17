# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Website branding context injection.

Injects branding variables into all web templates so they can
use {{ bc_app_name }}, {{ bc_logo }}, etc. without hardcoding.
"""

import re
from urllib.parse import parse_qs, urlparse

from osduo_business_connect.hooks import OSDUO_BRANDING
from osduo_business_connect.utils.seo import NOINDEX, is_login_path


def get_branding_context(context):
    """
    Add branding variables to website context.

    Called via update_website_context hook in hooks.py.
    Available in all web templates as {{ bc_app_name }}, {{ bc_logo }}, etc.

    Also marks the login screen (the site root, ``home_page = "login"``) as
    ``noindex`` so the private login page is never indexed. Runs after Frappe
    has populated ``context.metatags``, so mutating it here reaches the
    standard ``meta_block`` renderer.
    """
    context.update({
        "bc_app_name": OSDUO_BRANDING["app_name"],
        "bc_app_short_name": OSDUO_BRANDING["app_short_name"],
        "bc_tagline": OSDUO_BRANDING["tagline"],
        "bc_logo": OSDUO_BRANDING["logo"],
        "bc_logo_dark": OSDUO_BRANDING["logo_dark"],
        "bc_favicon": OSDUO_BRANDING["favicon"],
        "bc_logo_mark": OSDUO_BRANDING["logo_mark"],
        "bc_logo_mark_small": OSDUO_BRANDING["logo_mark_small"],
        "bc_login_panel": OSDUO_BRANDING["login_panel"],
        "bc_og_image": OSDUO_BRANDING["og_image"],
        "bc_primary_color": OSDUO_BRANDING["primary_color"],
        "bc_secondary_color": OSDUO_BRANDING["secondary_color"],
        "bc_accent_color": OSDUO_BRANDING["accent_color"],
        "bc_background_color": OSDUO_BRANDING["background_color"],
        "bc_text_color": OSDUO_BRANDING["text_color"],
        # Vendor attribution (Phase E footer). The credit links to the product
        # page only once it is live; until then it points at the vendor site, so
        # the not-yet-published product URL is never surfaced.
        "bc_show_vendor_credit": OSDUO_BRANDING["show_vendor_credit"],
        "bc_vendor_credit_text": OSDUO_BRANDING["vendor_credit_text"],
        "bc_credit_url": (
            OSDUO_BRANDING["product_url"]
            if OSDUO_BRANDING.get("product_url_live")
            else OSDUO_BRANDING["vendor_url"]
        ),
    })

    if is_login_path(context.get("path")):
        context.setdefault("metatags", {})["robots"] = NOINDEX


def safe_url(url):
    """Jinja filter: sanitize URL to prevent javascript: protocol injection.

    Returns empty string for dangerous protocols.
    """
    if not url:
        return ""
    url = str(url).strip()
    url_lower = url.lower()
    dangerous = ["javascript:", "data:", "vbscript:", "file:"]
    for proto in dangerous:
        if url_lower.startswith(proto):
            return ""
    return url


# Hosts a user is allowed to embed from, and the share/page hosts whose plain
# URLs are *not* frameable and must be rewritten to an embed URL.
# Provider hosts that render inside an <iframe> (directly or after rewriting to
# their /embed form in _to_embed_url).
_ALLOWED_VIDEO_DOMAINS = [
    "youtube.com", "www.youtube.com", "youtu.be",
    "youtube-nocookie.com", "www.youtube-nocookie.com",
    "vimeo.com", "www.vimeo.com",
    "player.vimeo.com",
    "dailymotion.com", "www.dailymotion.com",
    "wistia.com", "www.wistia.com",
    "loom.com", "www.loom.com",
    "streamable.com", "www.streamable.com",
    "facebook.com", "www.facebook.com",
    "drive.google.com",
]
_YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}
_YOUTUBE_SHORT_HOSTS = {"youtu.be", "www.youtu.be"}
_VIMEO_SHARE_HOSTS = {"vimeo.com", "www.vimeo.com"}
_DAILYMOTION_SHARE_HOSTS = {"dailymotion.com", "www.dailymotion.com"}

# YouTube ids are 11 chars in practice; allow a short lower bound for legacy /v/ ids.
_YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{6,11}$")


def _youtube_video_id(parsed):
    """Return the 11-char id for any YouTube URL shape, else ``None``."""
    host = (parsed.hostname or "").lower()
    parts = [p for p in (parsed.path or "").split("/") if p]

    if host in _YOUTUBE_SHORT_HOSTS:
        vid = parts[0] if parts else ""
        return vid if _YOUTUBE_ID_RE.match(vid) else None

    if host in _YOUTUBE_HOSTS:
        if parts and parts[0] in ("embed", "shorts", "live", "v") and len(parts) >= 2:
            vid = parts[1]
            return vid if _YOUTUBE_ID_RE.match(vid) else None
        if parts and parts[0] == "watch":
            vids = parse_qs(parsed.query or "").get("v") or []
            if vids and _YOUTUBE_ID_RE.match(vids[0]):
                return vids[0]

    return None


def _to_embed_url(parsed):
    """Rewrite a share/page URL to a provider URL that renders in an <iframe>.

    Only the common cases where the plain link is *not* embeddable are handled;
    anything already embeddable (or a provider we pass through) returns ``None``
    so the caller keeps the original, allow-listed URL.
    """
    host = (parsed.hostname or "").lower()

    # YouTube: watch / youtu.be / shorts / live  →  privacy-friendly nocookie embed.
    vid = _youtube_video_id(parsed)
    if vid:
        return f"https://www.youtube-nocookie.com/embed/{vid}"

    # Vimeo share page vimeo.com/ID → player.vimeo.com/video/ID.
    if host in _VIMEO_SHARE_HOSTS:
        parts = [p for p in (parsed.path or "").split("/") if p]
        if parts and parts[0].isdigit():
            return f"https://player.vimeo.com/video/{parts[0]}"

    # Google Drive /file/d/ID/view → /preview (the only frameable form).
    if host == "drive.google.com":
        parts = [p for p in (parsed.path or "").split("/") if p]
        if "d" in parts:
            idx = parts.index("d")
            if idx + 1 < len(parts) and parts[idx + 1]:
                return f"https://drive.google.com/file/d/{parts[idx + 1]}/preview"

    # Dailymotion /video/xID → /embed/video/xID.
    if host in _DAILYMOTION_SHARE_HOSTS:
        parts = [p for p in (parsed.path or "").split("/") if p]
        if len(parts) >= 2 and parts[0] == "video":
            return f"https://www.dailymotion.com/embed/video/{parts[1]}"

    return None


# Video-file extensions that can play directly in an HTML5 <video> element from
# any host (a self-hosted server, a CDN, an S3 bucket, …).
_VIDEO_FILE_EXTENSIONS = (".mp4", ".webm", ".ogg", ".ogv", ".m4v", ".mov")

# Nextcloud public share: https://host[/index.php]/s/<token>[/download|/video|/preview]
_NEXTCLOUD_SHARE_RE = re.compile(
    r"^(?P<pre>/index\.php)?/s/(?P<token>[A-Za-z0-9._-]+)(?:/(?P<action>download|video|preview))?/?$",
    re.I,
)


def _parse_safe_video(url):
    """Parse a user-entered video URL, or return ``None`` if it is not usable."""
    if not url:
        return None
    url = str(url).strip()
    url_lower = url.lower()

    # Block dangerous protocols.
    for proto in ("javascript:", "data:", "vbscript:", "file:"):
        if url_lower.startswith(proto):
            return None

    # Only allow https or http.
    if not url_lower.startswith("http://") and not url_lower.startswith("https://"):
        return None

    try:
        return urlparse(url)
    except Exception:
        return None


def _is_allowed_video_host(host):
    return bool(host) and any(host == d or host.endswith("." + d) for d in _ALLOWED_VIDEO_DOMAINS)


def _nextcloud_download_url(parsed):
    """Direct-download URL for a Nextcloud ``/s/<token>`` share page, else ``None``.

    The share page itself is not frameable, but the file can be played straight
    from ``…/s/<token>/download?inline=true`` in an HTML5 ``<video>`` element.
    """
    match = _NEXTCLOUD_SHARE_RE.match(parsed.path or "")
    if not match:
        return None
    prefix = match.group("pre") or ""
    token = match.group("token")
    return f"{parsed.scheme}://{parsed.netloc}{prefix}/s/{token}/download?inline=true"


def video_embed(url):
    """Jinja filter: resolve a pasted video link into a player spec.

    Returns ``{"kind": "iframe", "src": ...}`` for known embed providers
    (YouTube, Vimeo, Google Drive, Dailymotion, Loom, …), or
    ``{"kind": "file", "src": ...}`` for a direct video file or a **Nextcloud**
    public share on any host (played with an HTML5 ``<video>`` — self-hosted
    share pages are not iframable). Returns ``None`` when the URL is unsafe or
    unrecognised, so the template renders nothing instead of a broken/blank box.
    """
    parsed = _parse_safe_video(url)
    if parsed is None:
        return None
    url = str(url).strip()
    host = (parsed.hostname or "").lower()

    # Known providers → embeddable iframe.
    if _is_allowed_video_host(host):
        return {"kind": "iframe", "src": _to_embed_url(parsed) or url}

    # Direct video file on any https host → HTML5 <video>.
    if (parsed.path or "").lower().endswith(_VIDEO_FILE_EXTENSIONS):
        return {"kind": "file", "src": url}

    # Nextcloud (or similar) public share page → direct file in <video>.
    nc = _nextcloud_download_url(parsed)
    if nc:
        return {"kind": "file", "src": nc}

    return None


def safe_video_url(url):
    """Jinja filter (kept for compatibility): the iframe src for a known provider.

    Prefer :func:`video_embed`, which also supports direct files and Nextcloud
    shares. This returns an empty string for anything that is not an
    iframe-embeddable provider URL.
    """
    embed = video_embed(url)
    if embed and embed["kind"] == "iframe":
        return embed["src"]
    return ""
