# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""JSON-LD (schema.org) builders for the public pages.

Each builder takes records the page controllers have already fetched (plain
dicts) and returns a schema.org node as a ``dict``. Nothing here imports
``frappe`` or touches the database, so the whole module is exercised by the
offline test suite; the controllers own data fetching and assemble the node
list into ``build_seo(..., blocks=[...])``.

Every URL is resolved through :func:`osduo_business_connect.utils.seo.absolute_url`
(the canonical, ``host_name``-first origin) so structured data never points at
a per-request host. Serialisation into the ``<script type="application/ld+json">``
element happens in ``templates/bc_base.html`` through the ``jsonld`` Jinja filter,
which escapes ``<`` so user-entered text cannot break out of the script block.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from osduo_business_connect.hooks import OSDUO_BRANDING
from osduo_business_connect.utils.seo import absolute_url, clean_text

CONTEXT = "https://schema.org"

# ``price_display_mode`` values that publicly expose a price and so can back a
# schema.org ``Offer``. ``Hidden`` and ``Contact`` cannot.
_PRICED_MODES = ("Fixed", "Start From")

# ``availability`` we surface for a listed price — the catalogue is treated as
# in stock (there is no inventory model).
_INSTOCK = f"{CONTEXT}/InStock"

_TIME_AMPM_RE = re.compile(r"^(\d{1,2}):(\d{2})\s*([APap])\.?[Mm]\.?$")
_TIME_24_RE = re.compile(r"^(\d{1,2}):(\d{2})")


def _num(value):
    """Coerce a price to a JSON-serialisable ``float`` (or ``None``).

    Currency fields arrive as ``Decimal``/``str`` on some paths, which
    ``json.dumps`` cannot serialise, so every price is normalised here.
    """
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _hhmm(value):
    """Normalise a time field to the 24-hour ``HH:MM`` schema.org expects.

    Accepts ``timedelta`` / ``time`` (Frappe ``Time`` storage), an ``HH:MM[:SS]``
    string, or a display string such as ``9:00 AM``. Returns ``None`` when the
    value cannot be interpreted.
    """
    if not value:
        return None
    if isinstance(value, timedelta):
        value = (datetime.min + value).time()
    if hasattr(value, "strftime"):
        return value.strftime("%H:%M")
    text = str(value).strip()
    match = _TIME_AMPM_RE.match(text)
    if match:
        hour = int(match.group(1)) % 12
        if match.group(3).lower() == "p":
            hour += 12
        return f"{hour:02d}:{match.group(2)}"
    match = _TIME_24_RE.match(text)
    if match:
        return f"{int(match.group(1)):02d}:{match.group(2)}"
    return None


def _is_http(url):
    return bool(url) and str(url).strip().lower().startswith(("http://", "https://"))


def _same_as(rows, url_key="url"):
    """Ordered, de-duplicated list of absolute profile URLs from link rows."""
    seen = set()
    out = []
    for row in rows or []:
        url = (row.get(url_key) or "").strip() if isinstance(row, dict) else ""
        if _is_http(url) and url not in seen:
            seen.add(url)
            out.append(url)
    return out


def _business_ref(business):
    """Compact Organization reference for a business (publisher/provider/…)."""
    name = business.get("business_name") or business.get("name")
    ref = {"@type": "Organization", "name": name}
    if business.get("slug"):
        ref["url"] = absolute_url(f"/b/{business['slug']}")
    return ref


# --------------------------------------------------------------------------- #
# Sitewide vendor identity — Organization + Brand (every public page).
# --------------------------------------------------------------------------- #

def vendor_org_ref():
    """Inline ``Organization`` reference for the vendor (OSDuo Tech LLP)."""
    return {
        "@type": "Organization",
        "name": OSDUO_BRANDING["vendor_name"],
        "url": OSDUO_BRANDING["vendor_url"],
    }


def vendor_blocks():
    """The two attribution nodes emitted on every public page.

    ``Brand.url`` resolves to the product page once it is live and to the vendor
    site while ``product_url_live`` is False — the product URL is never emitted
    before it exists.
    """
    brand_url = (
        OSDUO_BRANDING["product_url"]
        if OSDUO_BRANDING.get("product_url_live")
        else OSDUO_BRANDING["vendor_url"]
    )
    organization = {
        "@context": CONTEXT,
        "@type": "Organization",
        "name": OSDUO_BRANDING["vendor_name"],
        "url": OSDUO_BRANDING["vendor_url"],
        "logo": absolute_url(OSDUO_BRANDING["logo"]),
    }
    brand = {
        "@context": CONTEXT,
        "@type": "Brand",
        "name": OSDUO_BRANDING["product_name"],
        "url": brand_url,
    }
    return [organization, brand]


def website_node():
    """``WebSite`` — business pages only (decision 10; the de-facto hub)."""
    return {
        "@context": CONTEXT,
        "@type": "WebSite",
        "name": OSDUO_BRANDING["product_name"],
        "url": absolute_url(""),
        "publisher": vendor_org_ref(),
    }


# --------------------------------------------------------------------------- #
# Business — LocalBusiness (address, hours, socials).
# --------------------------------------------------------------------------- #

def _postal_address(business):
    parts = {}
    street = clean_text(business.get("address") or "", limit=0)
    if street:
        parts["streetAddress"] = street
    for field, key in (
        ("city", "addressLocality"),
        ("state", "addressRegion"),
        ("postal_code", "postalCode"),
        ("country", "addressCountry"),
    ):
        if business.get(field):
            parts[key] = business[field]
    return {"@type": "PostalAddress", **parts} if parts else None


def _opening_hours(hours):
    specs = {}
    for row in hours or []:
        if not isinstance(row, dict) or not row.get("day"):
            continue
        # ``enabled`` is not selected by the controller query (rows are
        # pre-filtered to enabled=1), so default to enabled when absent.
        if not row.get("enabled", 1):
            continue
        if row.get("is_24_hours"):
            opens, closes = "00:00", "23:59"
        else:
            opens = _hhmm(row.get("open_time") or row.get("open_time_24"))
            closes = _hhmm(row.get("close_time") or row.get("close_time_24"))
            if not opens or not closes:
                continue
        specs.setdefault(
            row["day"],
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": row["day"],
                "opens": opens,
                "closes": closes,
            },
        )
    return list(specs.values())


def local_business_node(business, hours=None, socials=None):
    """``LocalBusiness`` for a public business profile."""
    node = {
        "@context": CONTEXT,
        "@type": "LocalBusiness",
        "name": business.get("business_name") or business.get("name"),
        "url": absolute_url(f"/b/{business.get('slug')}"),
    }
    image = business.get("cover_image") or business.get("logo")
    if image:
        node["image"] = absolute_url(image)
    if business.get("logo"):
        node["logo"] = absolute_url(business["logo"])
    description = clean_text(business.get("seo_description") or business.get("description") or "", limit=0)
    if description:
        node["description"] = description
    if business.get("phone"):
        node["telephone"] = business["phone"]
    if business.get("email"):
        node["email"] = business["email"]
    address = _postal_address(business)
    if address:
        node["address"] = address
    hours_spec = _opening_hours(hours)
    if hours_spec:
        node["openingHoursSpecification"] = hours_spec
    same_as = _same_as(socials)
    if same_as:
        node["sameAs"] = same_as
    return node


# --------------------------------------------------------------------------- #
# Product / Service (+ Offer only when a price is publicly displayed).
# --------------------------------------------------------------------------- #

def has_public_price(item):
    """True when ``item`` displays a real price (Fixed / Start From, priced, currency set)."""
    return bool(
        item
        and item.get("price_display_mode") in _PRICED_MODES
        and _num(item.get("price"))
        and item.get("currency")
    )


def _offer(item, url):
    return {
        "@type": "Offer",
        "price": _num(item.get("price")),
        "priceCurrency": item.get("currency"),
        "availability": _INSTOCK,
        "url": url,
    }


def product_node(business, product):
    """``Product`` + ``Offer`` for a priced product.

    Returns ``None`` when the product is unpriced (``Hidden`` / ``Contact`` or no
    value): an ``Product`` without ``offers`` draws a Rich Results warning, so the
    caller emits ``WebPage`` + ``BreadcrumbList`` instead (SEO_PLAN §G).
    """
    if not has_public_price(product):
        return None
    url = absolute_url(f"/b/{business.get('slug')}/products/{product.get('slug')}")
    node = {
        "@context": CONTEXT,
        "@type": "Product",
        "name": product.get("product_name") or product.get("name"),
        "url": url,
    }
    description = clean_text(product.get("short_description") or product.get("description") or "", limit=0)
    if description:
        node["description"] = description
    if product.get("image"):
        node["image"] = absolute_url(product["image"])
    brand_name = business.get("business_name") or business.get("name")
    if brand_name:
        node["brand"] = {"@type": "Brand", "name": brand_name}
    node["offers"] = _offer(product, url)
    return node


def service_node(business, service):
    """``Service`` for a public service page.

    The ``Service`` node is always emitted; an ``Offer`` is attached only when the
    price is publicly displayed (services carry the same price fields as products).
    """
    url = absolute_url(f"/b/{business.get('slug')}/services/{service.get('slug')}")
    node = {
        "@context": CONTEXT,
        "@type": "Service",
        "name": service.get("service_name") or service.get("name"),
        "url": url,
    }
    description = clean_text(service.get("short_description") or service.get("description") or "", limit=0)
    if description:
        node["description"] = description
    if service.get("image"):
        node["image"] = absolute_url(service["image"])
    provider = _business_ref(business)
    if provider.get("name"):
        node["provider"] = provider
    if business.get("city"):
        node["areaServed"] = {"@type": "City", "name": business["city"]}
    if has_public_price(service):
        node["offers"] = _offer(service, url)
    return node


def webpage_node(name, description, path, image=None):
    """Generic ``WebPage`` used when a product/service carries no rich entity."""
    node = {
        "@context": CONTEXT,
        "@type": "WebPage",
        "name": name,
        "url": absolute_url(path),
    }
    description = clean_text(description or "", limit=0)
    if description:
        node["description"] = description
    if image:
        node["image"] = absolute_url(image)
    return node


# --------------------------------------------------------------------------- #
# Card — Person wrapped in ProfilePage.
# --------------------------------------------------------------------------- #

def profile_page_node(card, business=None, links=None):
    """``ProfilePage`` with the cardholder as ``mainEntity`` (``Person``)."""
    url = absolute_url(f"/c/{card.get('slug')}")
    person = {
        "@type": "Person",
        "name": card.get("display_name") or card.get("name"),
        "url": url,
    }
    if card.get("designation"):
        person["jobTitle"] = card["designation"]
    if card.get("profile_image"):
        person["image"] = absolute_url(card["profile_image"])
    bio = clean_text(card.get("bio") or "", limit=0)
    if bio:
        person["description"] = bio
    if card.get("email"):
        person["email"] = card["email"]
    if card.get("phone"):
        person["telephone"] = card["phone"]
    if business and (business.get("business_name") or business.get("name")):
        person["worksFor"] = _business_ref(business)
    same_as = _same_as(links)
    if _is_http(card.get("website")):
        if card["website"] not in same_as:
            same_as.append(card["website"])
    if same_as:
        person["sameAs"] = same_as
    return {
        "@context": CONTEXT,
        "@type": "ProfilePage",
        "url": url,
        "mainEntity": person,
    }


# --------------------------------------------------------------------------- #
# Breadcrumbs — Business → Item (no fake home page; the root is a login screen).
# --------------------------------------------------------------------------- #

def breadcrumb_node(crumb_list):
    """``BreadcrumbList`` from ``[(name, relative_path), …]``, last = the page."""
    items = []
    for position, (name, path) in enumerate(crumb_list, start=1):
        items.append(
            {
                "@type": "ListItem",
                "position": position,
                "name": name,
                "item": absolute_url(path),
            }
        )
    return {"@context": CONTEXT, "@type": "BreadcrumbList", "itemListElement": items}
