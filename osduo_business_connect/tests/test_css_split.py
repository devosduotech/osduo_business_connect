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


class TestSharedHeroComponents(unittest.TestCase):
    """The bc-prof-* hero components are shared by every template, not just Professional.

    Their structural rules (logo tile, flex band, nav) must stay in the base CSS
    bundle or every non-Professional theme renders an unstyled, full-size logo.
    """

    def test_shared_selectors_are_not_classified_as_one_theme(self):
        for selector in (
            ".bc-prof-band",
            ".bc-prof-band-inner",
            ".bc-prof-logo",
            ".bc-prof-logo img",
            ".bc-prof-band-info",
            ".bc-prof-nav",
            ".bc-prof-nav-inner",
        ):
            self.assertIsNone(split_css.classify(selector), selector)

    def test_theme_specific_logo_variant_is_still_classified(self):
        self.assertEqual(
            split_css.classify(".bc-prof-band.bc-hero-modern .bc-prof-logo"),
            "modern",
        )

    def test_logo_sizing_lives_in_base(self):
        base = rules_in(read_css("business_connect.css"))
        logo = [decls for sel, decls in base if sel == ".bc-prof-logo" and "width: 80px" in decls]
        self.assertTrue(logo, "base CSS must contain the shared 80px logo tile rule")
        self.assertIn("height: 80px", logo[0])
        self.assertIn("overflow: hidden", logo[0])
        img = [decls for sel, decls in base if sel == ".bc-prof-logo img"]
        self.assertTrue(img, "base CSS must constrain the logo image")
        self.assertIn("object-fit: cover", img[0])

    def test_logo_mobile_override_lives_in_base(self):
        base = rules_in(read_css("business_connect.css"))
        mobile = [decls for sel, decls in base if sel == ".bc-prof-logo" and "width: 64px" in decls]
        self.assertTrue(mobile, "the mobile 64px logo override must apply to every theme")
        self.assertIn("height: 64px", mobile[0])

    def test_no_theme_file_carries_the_shared_logo_rule(self):
        for theme in THEMES:
            rules = rules_in(read_css(f"theme-{theme}.css"))
            bare = [sel for sel, _ in rules if sel in (".bc-prof-logo", ".bc-prof-logo img")]
            self.assertFalse(bare, f"theme-{theme}.css must not own the shared logo rule: {bare}")

    def test_logo_background_uses_the_exact_selected_colour(self):
        base = read_css("business_connect.css")
        tile = re.search(r"\.bc-prof-logo \{[^}]*\}", base)
        self.assertIsNotNone(tile)
        self.assertIn("background: var(--bc-primary);", tile.group(0))
        self.assertNotIn("primary-fill", tile.group(0))

    def test_no_logo_variant_hardcodes_a_background(self):
        for theme in THEMES:
            for selector, decls in rules_in(read_css(f"theme-{theme}.css")):
                if not selector.endswith(".bc-prof-logo"):
                    continue
                for declaration in decls:
                    if declaration.startswith("background:"):
                        self.assertIn("var(--bc-primary)", declaration, (theme, selector))
                        self.assertNotIn("#C9A227", declaration, (theme, selector))
                        self.assertNotIn("transparent", declaration, (theme, selector))

    def test_every_business_hero_uses_the_shared_logo_class(self):
        parts_dir = os.path.join(APP_DIR, "templates", "pages", "business", "parts")
        heroes = [name for name in os.listdir(parts_dir) if name.startswith("hero_") and name.endswith(".html")]
        self.assertEqual(len(heroes), 6, heroes)
        for name in heroes:
            with open(os.path.join(parts_dir, name)) as f:
                self.assertIn('class="bc-prof-logo"', f.read(), name)


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
