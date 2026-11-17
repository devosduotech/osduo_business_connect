# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Phase D follow-up — theme-split CSS (unused-CSS reduction).

The monolithic stylesheet is split into a base file (loaded on every page) plus
one file per theme (loaded only when that theme is active). These offline checks
prove the committed split is complete, isolated, and correctly wired into the
head — the guarantee that replaces the browser verification we cannot run here.
"""

import importlib.util
import os
import re
import unittest

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
CSS_DIR = os.path.join(APP_DIR, "public", "css")
SRC = os.path.join(APP_DIR, "..", "styles", "business_connect.src.css")
SPLIT = os.path.join(APP_DIR, "..", "scripts", "split_css.py")

_spec = importlib.util.spec_from_file_location("split_css_under_test", SPLIT)
split_css = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(split_css)

THEMES = list(split_css.THEMES)


def read_css(name):
    with open(os.path.join(CSS_DIR, name)) as f:
        return f.read()


def rules_in(text):
    return {split_css._norm(s, b) for s, b in split_css._leaf_rules(split_css.parse(text))}


class TestSplitFiles(unittest.TestCase):
    def test_all_files_exist(self):
        self.assertTrue(os.path.exists(os.path.join(CSS_DIR, "business_connect.css")))
        for t in THEMES:
            self.assertTrue(os.path.exists(os.path.join(CSS_DIR, f"theme-{t}.css")), t)

    def test_generated_header(self):
        for name in ["business_connect.css"] + [f"theme-{t}.css" for t in THEMES]:
            self.assertIn("GENERATED", read_css(name), name)

    def test_full_coverage_no_loss(self):
        base = rules_in(read_css("business_connect.css"))
        union = set(base)
        for t in THEMES:
            union |= rules_in(read_css(f"theme-{t}.css"))
        with open(SRC) as f:
            src = rules_in(f.read())
        self.assertEqual(union, src, "split lost or added rules vs the source")
        # and they partition: a rule lives in exactly one file
        total = len(base) + sum(len(rules_in(read_css(f"theme-{t}.css"))) for t in THEMES)
        self.assertEqual(total, len(src))

    def test_theme_files_are_isolated(self):
        for t in THEMES:
            text = read_css(f"theme-{t}.css")
            for other in THEMES:
                if other == t:
                    continue
                for tok in split_css.THEMES[other]:
                    pattern = rf"\b{re.escape(tok)}\b"
                    self.assertIsNone(re.search(pattern, text), f"theme-{t}.css should not reference {tok}")

    def test_shared_footer_and_icon_stay_in_base(self):
        base = read_css("business_connect.css")
        for shared in (".bc-vendor-footer", ".bc-icon", ".bc-share-widget", ".bc-btn", ".bc-page"):
            self.assertIn(shared, base, shared)

    def test_footer_clears_mobile_action_bar(self):
        # The fixed .bc-action-bar overlays the body-level footer on mobile; the
        # footer must reserve bottom clearance so the credit stays visible.
        base = read_css("business_connect.css")
        self.assertRegex(
            base,
            r"@media \(max-width: 768px\)[^}]*\{[^}]*\.bc-vendor-footer \{[^}]*padding-bottom",
            "vendor footer needs mobile padding-bottom to clear the fixed action bar",
        )


class TestHeadWiring(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(APP_DIR, "templates", "bc_base.html")) as f:
            self.head = f.read()

    def test_base_always_linked(self):
        self.assertIn("/assets/osduo_business_connect/css/business_connect.css", self.head)

    def test_theme_link_is_guarded_and_ordered_after_base(self):
        self.assertIn("theme-{{ _theme_css }}.css", self.head)
        self.assertIn("_theme_css in ('modern', 'professional', 'minimal', 'classic', 'luxury', 'creative')", self.head)
        base_pos = self.head.index("css/business_connect.css")
        theme_pos = self.head.index("theme-{{ _theme_css }}.css")
        self.assertLess(base_pos, theme_pos, "theme CSS must load after base")

    def test_only_matching_theme_file_is_linked(self):
        from jinja2 import Environment

        env = Environment(autoescape=False)
        tmpl = env.from_string(
            '{%- set _theme_css = ((template_type or "") | lower | replace(" ", "-")) -%}'
            "{%- if _theme_css in ('modern','professional','minimal','classic','luxury','creative') -%}"
            '<link href="theme-{{ _theme_css }}.css">{%- endif -%}'
        )
        self.assertIn("theme-professional.css", tmpl.render(template_type="Professional"))
        self.assertIn("theme-modern.css", tmpl.render(template_type="Modern"))
        self.assertEqual(tmpl.render(template_type=""), "")
        self.assertEqual(tmpl.render(), "")  # undefined -> no theme css
        self.assertEqual(tmpl.render(template_type="Unknown"), "")


if __name__ == "__main__":
    unittest.main()
