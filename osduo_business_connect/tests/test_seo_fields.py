# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Phase C (P4) — Product/Service/Business SEO fields.

Offline structural checks that the editable-after-submit SEO fields exist on all
three submittable doctypes in their own section, that the controllers normalise
them, and that the shared tag-stripping helper behaves.
"""

import contextlib
import json
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from osduo_business_connect.utils.seo import (
    SEO_DESCRIPTION_LIMIT,
    SEO_TITLE_LIMIT,
    clean_seo_value,
    normalize_seo_fields,
)

APP_DIR = os.path.join(os.path.dirname(__file__), "..")

DOCTYPES = {
    "Business": os.path.join("business", "doctype", "business", "business.json"),
    "Showcase Product": os.path.join("showcase", "doctype", "showcase_product", "showcase_product.json"),
    "Showcase Service": os.path.join("showcase", "doctype", "showcase_service", "showcase_service.json"),
}


def load_doctype(rel):
    with open(os.path.join(APP_DIR, rel)) as f:
        return json.load(f)


def by_fieldname(doc):
    return {f.get("fieldname"): f for f in doc["fields"]}, [f.get("fieldname") for f in doc["fields"]]


class TestSeoDocFields(unittest.TestCase):
    def test_all_three_doctypes_have_seo_fields(self):
        for label, rel in DOCTYPES.items():
            fields, _ = by_fieldname(load_doctype(rel))
            with self.subTest(doctype=label):
                self.assertEqual(fields["seo_title"]["fieldtype"], "Data")
                self.assertEqual(fields["seo_description"]["fieldtype"], "Small Text")

    def test_own_seo_section(self):
        for label, rel in DOCTYPES.items():
            fields, order = by_fieldname(load_doctype(rel))
            with self.subTest(doctype=label):
                self.assertEqual(fields["section_seo"]["fieldtype"], "Section Break")
                self.assertEqual(fields["section_seo"]["label"], "SEO")
                # section precedes both fields
                self.assertLess(order.index("section_seo"), order.index("seo_title"))
                self.assertLess(order.index("seo_title"), order.index("seo_description"))

    def test_editable_after_submit(self):
        # Acceptance #7: seo text is adjustable on a submitted record without amend.
        for label, rel in DOCTYPES.items():
            fields, _ = by_fieldname(load_doctype(rel))
            with self.subTest(doctype=label):
                self.assertEqual(fields["seo_title"].get("allow_on_submit"), 1)
                self.assertEqual(fields["seo_description"].get("allow_on_submit"), 1)
                self.assertTrue(load_doctype(rel).get("is_submittable"))

    def test_author_guidance_in_help_text(self):
        for label, rel in DOCTYPES.items():
            fields, _ = by_fieldname(load_doctype(rel))
            with self.subTest(doctype=label):
                self.assertIn("50", fields["seo_title"]["description"])
                self.assertIn("150", fields["seo_description"]["description"])

    def test_branding_column_break_repurposed(self):
        # The Business SEO fields left "Branding & Theme" for the dedicated section.
        _, order = by_fieldname(load_doctype(DOCTYPES["Business"]))
        self.assertNotIn("column_break_branding", order)


class TestControllerWiring(unittest.TestCase):
    def test_controllers_normalise_seo_fields(self):
        sources = {
            "business": os.path.join("business", "core.py"),
            "product": os.path.join("showcase", "doctype", "showcase_product", "showcase_product.py"),
            "service": os.path.join("showcase", "doctype", "showcase_service", "showcase_service.py"),
        }
        for label, rel in sources.items():
            src = read(rel)
            with self.subTest(controller=label):
                self.assertIn("from osduo_business_connect.utils.seo import normalize_seo_fields", src)
                self.assertIn("normalize_seo_fields(self)", src)

    def test_page_controllers_prefer_the_seo_fields(self):
        for rel, key in (
            (os.path.join("templates", "pages", "business", "business.py"), "seo_title"),
            (os.path.join("templates", "pages", "product", "product.py"), "seo_title"),
            (os.path.join("templates", "pages", "service", "service.py"), "seo_title"),
        ):
            src = read(rel)
            with self.subTest(page=rel):
                self.assertIn(key, src)


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


class TestCleanSeoValue(unittest.TestCase):
    def test_strips_tags_and_decodes_entities(self):
        self.assertEqual(clean_seo_value("<b>Acme &amp; Sons</b>"), "Acme & Sons")

    def test_collapses_whitespace_without_truncating(self):
        long = "word " * 40
        self.assertEqual(clean_seo_value(long), "word " * 39 + "word")
        self.assertGreater(len(clean_seo_value(long)), SEO_DESCRIPTION_LIMIT)  # not capped

    def test_empty_and_none(self):
        self.assertEqual(clean_seo_value(""), "")
        self.assertEqual(clean_seo_value(None), "")


class _StubDoc:
    def __init__(self, data):
        self._data = dict(data)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value


@contextlib.contextmanager
def frappe_stub():
    """Install a minimal frappe module that records msgprint calls."""
    calls = []
    module = types.ModuleType("frappe")
    module.msgprint = lambda *a, **k: calls.append(k.get("indicator"))
    saved = sys.modules.get("frappe")
    sys.modules["frappe"] = module
    try:
        yield calls
    finally:
        if saved is None:
            sys.modules.pop("frappe", None)
        else:
            sys.modules["frappe"] = saved


class TestNormalizeSeoFields(unittest.TestCase):
    def test_strips_markup(self):
        with frappe_stub():
            doc = _StubDoc({"seo_title": "<b>Acme</b> &amp; Co", "seo_description": "<p>Hi</p>"})
            normalize_seo_fields(doc)
        self.assertEqual(doc.get("seo_title"), "Acme & Co")
        self.assertEqual(doc.get("seo_description"), "Hi")

    def test_warns_on_long_values_without_blocking(self):
        long = "x" * (SEO_TITLE_LIMIT + 30)
        with frappe_stub() as printed:
            doc = _StubDoc({"seo_title": long})
            normalize_seo_fields(doc)  # must not raise
        self.assertIn("orange", printed)

    def test_no_warning_within_limits(self):
        with frappe_stub() as printed:
            normalize_seo_fields(_StubDoc({"seo_title": "Short title", "seo_description": "Short body"}))
        self.assertEqual(printed, [])

    def test_limits_are_the_soft_ceilings(self):
        self.assertEqual(SEO_TITLE_LIMIT, 70)
        self.assertEqual(SEO_DESCRIPTION_LIMIT, 160)


if __name__ == "__main__":
    unittest.main()
