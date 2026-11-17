# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Structural + pure-Python checks for the SEO layer (Phase A / P1).

Runnable without a bench: the text/JSON helpers are exercised directly and the
canonical base is loaded against a stubbed ``frappe`` (same technique as
``test_public_urls``), while the ``<head>`` wiring is asserted on the template
and controller source.
"""

import contextlib
import importlib.util
import json
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from osduo_business_connect.seo import jsonld as jl
from osduo_business_connect.utils.seo import (
    DEFAULT_ROBOTS,
    NOINDEX,
    absolute_url,
    build_seo,
    clean_text,
    is_login_path,
    jsonld,
)

CANON = "https://connect.osduotech.com"

BUSINESS = {
    "name": "BIZ-0001",
    "business_name": "OSDuo Tech",
    "slug": "osduo",
    "logo": "/files/logo.png",
    "cover_image": "/files/cover.jpg",
    "description": "<p>We do <b>tech</b>.</p>",
    "phone": "+91 90000 00000",
    "email": "hi@osduo.com",
    "address": "1 MG Road",
    "city": "Chennai",
    "state": "TN",
    "postal_code": "600001",
    "country": "India",
}
PRODUCT = {
    "name": "PROD-1",
    "product_name": "Widget",
    "slug": "widget",
    "short_description": "A widget",
    "image": "/files/w.png",
    "price": "12000",
    "currency": "INR",
    "price_display_mode": "Fixed",
}
SERVICE = {
    "name": "SERV-1",
    "service_name": "Consulting",
    "slug": "consulting",
    "short_description": "expert advice",
    "price": "5000",
    "currency": "INR",
    "price_display_mode": "Start From",
}
CARD = {
    "name": "CARD-1",
    "display_name": "Karthic",
    "designation": "Managing Director",
    "slug": "karthic",
    "profile_image": "/files/k.png",
    "bio": "Leads the firm",
    "phone": "+91 90000 00000",
    "email": "k@osduo.com",
    "website": "https://karthic.dev",
}

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
URLS_PATH = os.path.join(APP_DIR, "utils", "urls.py")


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


@contextlib.contextmanager
def canonical_base(host_name="https://connect.osduotech.com"):
    """Install utils/urls.py under its package name against a stubbed frappe.

    ``utils.seo.absolute_url`` imports ``get_canonical_base_url`` lazily, so the
    stub only has to be present at call time — never at import time.
    """
    frappe_stub = types.ModuleType("frappe")
    utils_stub = types.ModuleType("frappe.utils")
    utils_stub.get_url = lambda *a, **k: "http://stub.example"
    frappe_stub.utils = utils_stub
    frappe_stub.local = types.SimpleNamespace(conf={"host_name": host_name}, request=None)

    spec = importlib.util.spec_from_file_location("osduo_business_connect.utils.urls", URLS_PATH)
    module = importlib.util.module_from_spec(spec)

    saved = {name: sys.modules.get(name) for name in ("frappe", "frappe.utils")}
    saved["osduo_business_connect.utils.urls"] = sys.modules.get("osduo_business_connect.utils.urls")
    sys.modules["frappe"] = frappe_stub
    sys.modules["frappe.utils"] = utils_stub
    sys.modules["osduo_business_connect.utils.urls"] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        for name, value in saved.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


class TestCleanText(unittest.TestCase):
    def test_strips_tags_and_entities(self):
        self.assertEqual(clean_text("<p>Tea &amp;&nbsp;Toast</p>"), "Tea & Toast")

    def test_removes_script_and_style_blocks(self):
        html = "<style>.x{}</style><p>Hello</p><script>alert(1)</script>"
        self.assertEqual(clean_text(html), "Hello")

    def test_does_not_run_words_together_across_block_tags(self):
        self.assertEqual(clean_text("<p>Red</p><p>Shoes</p>"), "Red Shoes")

    def test_collapses_whitespace(self):
        self.assertEqual(clean_text("  a\n\t b   c  "), "a b c")

    def test_none_is_empty(self):
        self.assertEqual(clean_text(None), "")

    def test_truncates_on_word_boundary(self):
        text = clean_text("word " * 100, limit=20)
        self.assertLessEqual(len(text), 20)
        self.assertNotIn(" ", text[-1:], "cut should not leave a trailing space")
        self.assertEqual(text, "word word word word")

    def test_limit_zero_disables_truncation(self):
        long = "x" * 500
        self.assertEqual(clean_text(long, limit=0), long)

    def test_short_text_is_unchanged(self):
        self.assertEqual(clean_text("Sneakers", limit=155), "Sneakers")


class TestJsonld(unittest.TestCase):
    def test_escapes_angle_brackets(self):
        payload = jsonld({"bio": "</script><script>alert(1)</script>"})
        self.assertNotIn("<", payload)
        self.assertIn("\\u003c", payload)

    def test_round_trips_to_the_same_object(self):
        obj = {"a": 1, "b": ["x", "y"], "c": {"nested": True}}
        self.assertEqual(json.loads(jsonld(obj)), obj)

    def test_non_ascii_is_escaped(self):
        self.assertIn("\\u00e9", jsonld({"name": "café"}))

    def test_compact_separators(self):
        self.assertEqual(jsonld({"a": 1, "b": 2}), '{"a":1,"b":2}')


class TestAbsoluteUrl(unittest.TestCase):
    def test_relative_path_uses_canonical_base(self):
        with canonical_base("https://connect.osduotech.com"):
            self.assertEqual(absolute_url("/b/osduo"), "https://connect.osduotech.com/b/osduo")

    def test_leading_slash_normalised(self):
        with canonical_base("https://connect.osduotech.com"):
            self.assertEqual(absolute_url("b/osduo"), "https://connect.osduotech.com/b/osduo")

    def test_already_absolute_is_kept(self):
        with canonical_base("https://connect.osduotech.com"):
            self.assertEqual(absolute_url("https://cdn.example/x.png"), "https://cdn.example/x.png")

    def test_empty_path_returns_base(self):
        with canonical_base("https://connect.osduotech.com"):
            self.assertEqual(absolute_url(""), "https://connect.osduotech.com")

    def test_never_uses_the_request_host(self):
        # Decision 11: canonical resolves host_name-first; the request host is ignored.
        with canonical_base("https://connect.osduotech.com"):
            self.assertEqual(absolute_url("/c/owner"), "https://connect.osduotech.com/c/owner")


class TestBuildSeo(unittest.TestCase):
    def test_defaults(self):
        with canonical_base("https://connect.osduotech.com"):
            result = build_seo("Acme Studio", "We make furniture.", "/b/acme")
        self.assertEqual(result["title"], "Acme Studio")
        self.assertEqual(result["description"], "We make furniture.")
        self.assertEqual(result["canonical"], "https://connect.osduotech.com/b/acme")
        self.assertEqual(result["og_url"], result["canonical"])
        self.assertEqual(result["robots"], DEFAULT_ROBOTS)
        self.assertEqual(result["og_type"], "website")
        self.assertEqual(result["og_site_name"], "OSDuo Business Connect")
        self.assertEqual(result["og_locale"], "en_IN")
        self.assertEqual(result["twitter_card"], "summary_large_image")

    def test_image_falls_back_to_bundled_og_image(self):
        with canonical_base("https://connect.osduotech.com"):
            result = build_seo("T", "D", "/b/acme")
        self.assertTrue(result["og_image"].endswith("/assets/osduo_business_connect/images/og-image.png"))
        self.assertTrue(result["og_image"].startswith("https://connect.osduotech.com/"))

    def test_provided_image_is_made_absolute(self):
        with canonical_base("https://connect.osduotech.com"):
            result = build_seo("T", "D", "/b/acme", image="/files/cover.jpg")
        self.assertEqual(result["og_image"], "https://connect.osduotech.com/files/cover.jpg")

    def test_description_is_cleaned_and_capped(self):
        html = "<p>" + ("lorem ipsum dolor sit amet " * 20) + "</p>"
        with canonical_base("https://connect.osduotech.com"):
            result = build_seo("T", html, "/b/acme")
        self.assertLessEqual(len(result["description"]), 155)
        self.assertNotIn("<", result["description"])

    def test_title_is_cleaned_but_not_truncated(self):
        long_title = "A very long business title that should be kept whole"
        with canonical_base("https://connect.osduotech.com"):
            result = build_seo(f"<b>{long_title}</b>", "D", "/b/acme")
        self.assertEqual(result["title"], long_title)

    def test_page_type_and_robots_are_overridable(self):
        with canonical_base("https://connect.osduotech.com"):
            result = build_seo("T", "D", "/b/acme", page_type="product", robots=NOINDEX)
        self.assertEqual(result["og_type"], "product")
        self.assertEqual(result["robots"], "noindex,nofollow")

    def test_jsonld_is_an_empty_list_in_phase_a(self):
        with canonical_base("https://connect.osduotech.com"):
            self.assertEqual(build_seo("T", "D", "/b/acme")["jsonld"], [])


class TestLoginPath(unittest.TestCase):
    def test_root_and_login_are_login_paths(self):
        for path in ("", "/", "/login", "/login/", "login", "/login?redirect=/app"):
            self.assertTrue(is_login_path(path), path)

    def test_public_pages_are_not(self):
        for path in ("/b/acme", "/c/owner", "/analytics", "/my-card", "b/acme"):
            self.assertFalse(is_login_path(path), path)


class TestHeadWiring(unittest.TestCase):
    """The rewritten ``<head>`` must render the real SEO context (finding 1)."""

    def setUp(self):
        self.head = read("templates", "bc_base.html")

    def test_dead_og_guards_removed(self):
        for token in ("og_title %}", "og_description %}", "{% if og_image %}"):
            self.assertNotIn(token, self.head)

    def test_renders_seo_fields(self):
        for token in (
            "<title>{{ seo_title | e }}</title>",
            'content="{{ seo_description | e }}"',
            'rel="canonical"',
            'name="robots"',
            'property="og:type"',
            'property="og:site_name"',
            'property="og:locale"',
            'property="og:title"',
            'property="og:description"',
            'property="og:url"',
            'property="og:image"',
            'property="og:image:alt"',
            'name="twitter:card"',
            'name="application-name"',
            'name="generator"',
            'name="theme-color"',
        ):
            self.assertIn(token, self.head, token)

    def test_attribute_values_are_escaped(self):
        # Jinja autoescape is off in Frappe, so text values must carry | e.
        self.assertIn("{{ seo_description | e }}", self.head)
        self.assertIn("{{ seo_title | e }}", self.head)
        # ...but the JSON-LD script block must stay raw.
        self.assertIn("{{ block | jsonld | safe }}", self.head)

    def test_jsonld_blocks_iterated(self):
        self.assertIn("application/ld+json", self.head)
        self.assertIn("jsonld | safe", self.head)

    def test_twitter_uses_large_image_card(self):
        self.assertIn("summary_large_image", self.head)

    def test_title_has_no_brand_suffix(self):
        # Decision 6: page-content-only title — no brand concatenation.
        self.assertIn("<title>{{ seo_title | e }}</title>", self.head)


class TestNoindex(unittest.TestCase):
    def test_login_uses_metatags(self):
        source = read("utils", "website.py")
        self.assertIn("is_login_path", source)
        self.assertIn('["robots"] = NOINDEX', source)

    def test_offline_page_has_noindex_meta(self):
        self.assertIn('<meta name="robots" content="noindex,nofollow">', read("www", "offline.html"))

    def test_analytics_and_my_card_set_seo(self):
        analytics = read("templates", "pages", "analytics.py")
        self.assertIn("robots=NOINDEX", analytics)
        self.assertIn('"/analytics"', analytics)
        my_card = read("templates", "pages", "my_card.py")
        self.assertIn("robots=NOINDEX", my_card)

    def test_dead_www_analytics_controller_removed(self):
        self.assertFalse(os.path.exists(os.path.join(APP_DIR, "www", "analytics.py")))


class TestSeoWiring(unittest.TestCase):
    def test_seo_module_registered_as_jinja_filter(self):
        self.assertIn("osduo_business_connect.utils.seo", read("hooks.py"))

    def test_filters_module_imports_without_frappe(self):
        # get_jinja_hooks only exposes functions defined in the module, so the
        # import-time guarantee is that utils/seo.py pulls in no frappe.
        self.assertNotIn("\nimport frappe", read("utils", "seo.py"))
        self.assertNotIn("\nfrom frappe", read("utils", "seo.py"))

    def test_every_public_controller_builds_seo(self):
        for rel in (
            ("templates", "pages", "business", "business.py"),
            ("templates", "pages", "product", "product.py"),
            ("templates", "pages", "service", "service.py"),
            ("templates", "pages", "card", "card.py"),
        ):
            source = read(*rel)
            self.assertIn("context.seo = build_seo(", source, "/".join(rel))
            self.assertIn("from ....utils.seo import build_seo", source, "/".join(rel))

    def test_business_canonical_path(self):
        self.assertIn('f"/b/{doc.slug}"', read("templates", "pages", "business", "business.py"))

    def test_product_and_service_canonical_paths(self):
        self.assertIn(
            'f"/b/{business.slug}/products/{doc.slug}"',
            read("templates", "pages", "product", "product.py"),
        )
        self.assertIn(
            'f"/b/{business.slug}/services/{doc.slug}"',
            read("templates", "pages", "service", "service.py"),
        )

    def test_card_landing_url_is_canonical(self):
        source = read("templates", "pages", "card", "card.py")
        self.assertIn("context.landing_url = context.card_url", source)
        self.assertNotIn("frappe.request.url", source)

    def test_card_business_fetch_includes_seo_fields(self):
        source = read("templates", "pages", "card", "card.py")
        self.assertIn("seo_description", source)
        self.assertIn("logo", source)


class TestVendorBlocks(unittest.TestCase):
    def test_organization_and_brand(self):
        with canonical_base(CANON):
            org, brand = jl.vendor_blocks()
        self.assertEqual(org["@type"], "Organization")
        self.assertEqual(org["name"], "OSDuo Tech LLP")
        self.assertEqual(org["url"], "https://www.osduotech.com")
        self.assertEqual(brand["@type"], "Brand")
        self.assertEqual(brand["name"], "OSDuo Business Connect")

    def test_product_url_not_emitted_while_unpublished(self):
        # product_url_live is False, so Brand.url must fall back to the vendor
        # site and the (not-yet-live) product URL must appear nowhere.
        with canonical_base(CANON):
            dumped = json.dumps(jl.vendor_blocks())
        self.assertIn("https://www.osduotech.com", dumped)
        self.assertNotIn("solutions/business-connect", dumped)

    def test_organization_logo_is_absolute(self):
        with canonical_base(CANON):
            org = jl.vendor_blocks()[0]
        self.assertTrue(org["logo"].startswith(CANON + "/assets/"))


class TestWebSiteNode(unittest.TestCase):
    def test_url_is_canonical_base_and_publisher_is_vendor(self):
        with canonical_base(CANON):
            node = jl.website_node()
        self.assertEqual(node["@type"], "WebSite")
        self.assertEqual(node["url"], CANON)
        self.assertEqual(node["publisher"]["@type"], "Organization")
        self.assertEqual(node["publisher"]["name"], "OSDuo Tech LLP")


class TestLocalBusinessNode(unittest.TestCase):
    def test_core_fields(self):
        with canonical_base(CANON):
            node = jl.local_business_node(BUSINESS)
        self.assertEqual(node["@type"], "LocalBusiness")
        self.assertEqual(node["name"], "OSDuo Tech")
        self.assertEqual(node["url"], CANON + "/b/osduo")
        self.assertEqual(node["telephone"], "+91 90000 00000")
        self.assertEqual(node["email"], "hi@osduo.com")
        self.assertEqual(node["description"], "We do tech.")  # cleaned of tags

    def test_postal_address(self):
        with canonical_base(CANON):
            addr = jl.local_business_node(BUSINESS)["address"]
        self.assertEqual(addr["@type"], "PostalAddress")
        self.assertEqual(addr["addressLocality"], "Chennai")
        self.assertEqual(addr["addressCountry"], "India")

    def test_opening_hours(self):
        hours = [
            {"day": "Monday", "open_time": "9:00 AM", "close_time": "6:00 PM", "is_24_hours": 0, "enabled": 1},
            {"day": "Sunday", "open_time": "", "close_time": "", "is_24_hours": 1, "enabled": 1},
            {"day": "Tuesday", "open_time": "9:00 AM", "close_time": "1:00 PM", "is_24_hours": 0, "enabled": 0},
        ]
        with canonical_base(CANON):
            spec = jl.local_business_node(BUSINESS, hours=hours)["openingHoursSpecification"]
        by_day = {s["dayOfWeek"]: s for s in spec}
        self.assertEqual(by_day["Monday"]["opens"], "09:00")
        self.assertEqual(by_day["Monday"]["closes"], "18:00")
        self.assertEqual(by_day["Sunday"]["opens"], "00:00")
        self.assertEqual(by_day["Sunday"]["closes"], "23:59")
        self.assertNotIn("Tuesday", by_day)  # disabled rows are dropped

    def test_same_as_filters_non_http(self):
        socials = [
            {"url": "https://linkedin.com/company/osduo"},
            {"url": "not-a-url"},
            {"url": ""},
        ]
        with canonical_base(CANON):
            same = jl.local_business_node(BUSINESS, socials=socials)["sameAs"]
        self.assertEqual(same, ["https://linkedin.com/company/osduo"])

    def test_image_prefers_cover_then_logo(self):
        with canonical_base(CANON):
            self.assertTrue(jl.local_business_node(BUSINESS)["image"].endswith("/cover.jpg"))
            no_cover = {k: v for k, v in BUSINESS.items() if k != "cover_image"}
            self.assertTrue(jl.local_business_node(no_cover)["image"].endswith("/logo.png"))


class TestProductNode(unittest.TestCase):
    def test_priced_product_has_offer(self):
        with canonical_base(CANON):
            node = jl.product_node(BUSINESS, PRODUCT)
        self.assertEqual(node["@type"], "Product")
        self.assertEqual(node["brand"], {"@type": "Brand", "name": "OSDuo Tech"})
        offer = node["offers"]
        self.assertEqual(offer["@type"], "Offer")
        self.assertEqual(offer["price"], 12000.0)  # coerced to float, JSON-safe
        self.assertEqual(offer["priceCurrency"], "INR")
        self.assertTrue(offer["availability"].endswith("/InStock"))
        self.assertEqual(offer["url"], CANON + "/b/osduo/products/widget")

    def test_start_from_is_priced(self):
        with canonical_base(CANON):
            self.assertIsNotNone(jl.product_node(BUSINESS, {**PRODUCT, "price_display_mode": "Start From"}))

    def test_unpriced_returns_none(self):
        with canonical_base(CANON):
            self.assertIsNone(jl.product_node(BUSINESS, {**PRODUCT, "price_display_mode": "Hidden"}))
            self.assertIsNone(jl.product_node(BUSINESS, {**PRODUCT, "price_display_mode": "Contact"}))
            self.assertIsNone(jl.product_node(BUSINESS, {**PRODUCT, "price": 0}))
            self.assertIsNone(jl.product_node(BUSINESS, {**PRODUCT, "currency": None}))


class TestServiceNode(unittest.TestCase):
    def test_service_always_emitted_with_area_and_offer(self):
        with canonical_base(CANON):
            node = jl.service_node(BUSINESS, SERVICE)
        self.assertEqual(node["@type"], "Service")
        self.assertEqual(node["provider"]["name"], "OSDuo Tech")
        self.assertEqual(node["areaServed"], {"@type": "City", "name": "Chennai"})
        self.assertEqual(node["offers"]["price"], 5000.0)

    def test_service_without_price_has_no_offer(self):
        with canonical_base(CANON):
            node = jl.service_node(BUSINESS, {**SERVICE, "price_display_mode": "Contact"})
        self.assertEqual(node["@type"], "Service")
        self.assertNotIn("offers", node)


class TestWebPageFallback(unittest.TestCase):
    def test_unpriced_uses_webpage_node(self):
        with canonical_base(CANON):
            node = jl.webpage_node("Widget", "desc", "/b/osduo/products/widget", image="/files/w.png")
        self.assertEqual(node["@type"], "WebPage")
        self.assertEqual(node["url"], CANON + "/b/osduo/products/widget")
        self.assertTrue(node["image"].endswith("/w.png"))


class TestProfilePageNode(unittest.TestCase):
    def test_person_wrapped_in_profile_page(self):
        links = [{"url": "https://linkedin.com/in/karthic"}]
        with canonical_base(CANON):
            node = jl.profile_page_node(CARD, BUSINESS, links)
        self.assertEqual(node["@type"], "ProfilePage")
        self.assertEqual(node["url"], CANON + "/c/karthic")
        person = node["mainEntity"]
        self.assertEqual(person["@type"], "Person")
        self.assertEqual(person["name"], "Karthic")
        self.assertEqual(person["jobTitle"], "Managing Director")
        self.assertEqual(person["worksFor"]["name"], "OSDuo Tech")
        self.assertTrue(person["image"].endswith("/k.png"))
        self.assertIn("https://karthic.dev", person["sameAs"])

    def test_card_without_business(self):
        with canonical_base(CANON):
            person = jl.profile_page_node(CARD, None, [])["mainEntity"]
        self.assertNotIn("worksFor", person)
        # the card's own website is still a legitimate sameAs
        self.assertEqual(person["sameAs"], ["https://karthic.dev"])


class TestBreadcrumbNode(unittest.TestCase):
    def test_positions_and_absolute_items(self):
        with canonical_base(CANON):
            node = jl.breadcrumb_node(
                [("OSDuo Tech", "/b/osduo"), ("Widget", "/b/osduo/products/widget")]
            )
        self.assertEqual(node["@type"], "BreadcrumbList")
        items = node["itemListElement"]
        self.assertEqual([i["position"] for i in items], [1, 2])
        self.assertEqual(items[0]["item"], CANON + "/b/osduo")
        self.assertEqual(items[1]["item"], CANON + "/b/osduo/products/widget")


class TestTimeNormalisation(unittest.TestCase):
    def test_formats(self):
        from datetime import time, timedelta

        self.assertEqual(jl._hhmm("9:00 AM"), "09:00")
        self.assertEqual(jl._hhmm("6:00 PM"), "18:00")
        self.assertEqual(jl._hhmm("12:00 AM"), "00:00")
        self.assertEqual(jl._hhmm("12:30 PM"), "12:30")
        self.assertEqual(jl._hhmm("13:45:00"), "13:45")
        self.assertEqual(jl._hhmm(time(9, 30)), "09:30")
        self.assertEqual(jl._hhmm(timedelta(hours=9, minutes=30)), "09:30")
        self.assertIsNone(jl._hhmm(""))
        self.assertIsNone(jl._hhmm(None))


class TestJsonldIntegration(unittest.TestCase):
    def test_product_output_has_no_bare_angle_bracket(self):
        with canonical_base(CANON):
            node = jl.product_node({**BUSINESS, "business_name": "A & <B>"}, PRODUCT)
        serialized = jsonld(node)
        self.assertNotIn("<", serialized)
        self.assertIn("\\u003c", serialized)

    def test_build_seo_threads_blocks_into_jsonld(self):
        with canonical_base(CANON):
            blocks = [*jl.vendor_blocks(), jl.website_node(), jl.local_business_node(BUSINESS)]
            result = build_seo("T", "D", "/b/osduo", blocks=blocks)
        self.assertEqual(len(result["jsonld"]), 4)


class TestControllerWiring(unittest.TestCase):
    """Each controller assembles the documented node set (SEO_PLAN §G)."""

    def test_business(self):
        src = read("templates", "pages", "business", "business.py")
        self.assertIn("from ....seo import jsonld", src)
        self.assertIn("jsonld.vendor_blocks()", src)
        self.assertIn("jsonld.website_node()", src)
        self.assertIn("jsonld.local_business_node(", src)

    def test_product(self):
        src = read("templates", "pages", "product", "product.py")
        self.assertIn("jsonld.vendor_blocks()", src)
        self.assertIn("jsonld.product_node(", src)
        self.assertIn("jsonld.webpage_node(", src)  # unpriced fallback
        self.assertIn("jsonld.breadcrumb_node(", src)

    def test_service(self):
        src = read("templates", "pages", "service", "service.py")
        self.assertIn("jsonld.vendor_blocks()", src)
        self.assertIn("jsonld.service_node(", src)
        self.assertIn("jsonld.breadcrumb_node(", src)

    def test_card(self):
        src = read("templates", "pages", "card", "card.py")
        self.assertIn("jsonld.vendor_blocks()", src)
        self.assertIn("jsonld.profile_page_node(", src)
        self.assertIn("jsonld.breadcrumb_node(", src)


if __name__ == "__main__":
    unittest.main()
