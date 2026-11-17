# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Phase D (P5) — Core Web Vitals.

Offline checks that the third-party font/icon CDNs are gone, fonts are
self-hosted, icons render as inline SVG, images carry decode/lazy/priority
hints, and the Open Graph image was re-cut. No bench required.
"""

import glob
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from osduo_business_connect.utils import icons

APP_DIR = os.path.join(os.path.dirname(__file__), "..")

# Above-the-fold hero image classes (LCP candidates) across the themes.
_HERO_CLASSES = frozenset({
    "bc-prof-cover-img", "bc-cover-img", "bc-prof-gallery-img",
    "bc-hero-modern-avatar", "bc-hero-classic-avatar", "bc-hero-luxury-avatar",
    "bc-hero-minimal-avatar", "bc-hero-creative-avatar", "bc-hero-professional-avatar",
})


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


def read_path(full):
    with open(full) as f:
        return f.read()


def png_dims(path):
    with open(path, "rb") as f:
        head = f.read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")


class TestThirdPartyRemoved(unittest.TestCase):
    def test_no_font_or_icon_cdn_in_base(self):
        head = read("templates", "bc_base.html")
        for bad in ("fonts.googleapis.com", "fonts.gstatic.com", "cdnjs.cloudflare.com", "font-awesome"):
            self.assertNotIn(bad, head, bad)

    def test_no_icon_cdn_anywhere(self):
        for path in glob.glob(os.path.join(APP_DIR, "templates", "**", "*.html"), recursive=True):
            self.assertNotIn("cdnjs.cloudflare.com", read_path(path), path)
            self.assertNotIn("fonts.googleapis.com", read_path(path), path)

    def test_fonts_css_is_linked(self):
        self.assertIn("/assets/osduo_business_connect/css/fonts.css", read("templates", "bc_base.html"))


class TestSelfHostedFonts(unittest.TestCase):
    def test_fonts_css_present_and_references_woff2(self):
        css = read("public", "css", "fonts.css")
        self.assertIn("font-display: swap", css)
        self.assertIn("../fonts/", css)
        self.assertIn("Inter", css)

    def test_woff2_files_exist(self):
        files = glob.glob(os.path.join(APP_DIR, "public", "fonts", "*.woff2"))
        self.assertGreaterEqual(len(files), 30, "expected a woff2 per declared face")
        # every @font-face src points at a file we actually shipped
        css = read("public", "css", "fonts.css")
        names = set(re.findall(r"url\('\.\./fonts/([^']+)'\)", css))
        present = {os.path.basename(p) for p in files}
        self.assertTrue(names <= present, names - present)

    def test_licensed_provenance_note(self):
        self.assertIn("OFL", read("public", "css", "fonts.css"))


class TestInlineIcons(unittest.TestCase):
    def test_bc_icon_returns_inline_svg(self):
        svg = icons.bc_icon("fa-brands fa-facebook")
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn('viewBox="0 0 24 24"', svg)
        self.assertIn("bc-icon-facebook", svg)
        self.assertIn('fill="currentColor"', svg)  # brand style

    def test_solid_icons_use_stroke(self):
        svg = icons.bc_icon("fa-solid fa-globe", "Website")
        self.assertIn('stroke="currentColor"', svg)
        self.assertIn("bc-icon-globe", svg)

    def test_resolve_all_platform_icons(self):
        mapping = {
            "fa-brands fa-facebook": "facebook",
            "fa-brands fa-instagram": "instagram",
            "fa-brands fa-linkedin": "linkedin",
            "fa-brands fa-x-twitter": "x",
            "fa-brands fa-youtube": "youtube",
            "fa-brands fa-telegram": "telegram",
            "fa-solid fa-globe": "globe",
            "fa-solid fa-briefcase": "briefcase",
            "fa-solid fa-link": "link",
        }
        for icon_class, expected in mapping.items():
            self.assertEqual(icons.resolve_icon(icon_class), expected)

    def test_platform_only_and_fallback(self):
        self.assertEqual(icons.resolve_icon("", "Portfolio"), "briefcase")
        self.assertEqual(icons.resolve_icon("", "", "Other"), "link")
        self.assertEqual(icons.resolve_icon("nonsense"), "link")  # generic fallback

    def test_all_icon_names_render(self):
        for name, rec in icons._ICONS.items():
            svg = icons.bc_icon("", name)
            self.assertIn(f"bc-icon-{name}", svg)
            self.assertGreater(len(rec["svg"]), 40, name)

    def test_registered_as_jinja_filter(self):
        self.assertIn("osduo_business_connect.utils.icons", read("hooks.py"))


class TestTemplateIconWiring(unittest.TestCase):
    def test_no_fontawesome_i_tags_remain(self):
        for path in glob.glob(os.path.join(APP_DIR, "templates", "**", "*.html"), recursive=True):
            src = read_path(path)
            self.assertNotIn('<i class="{{ link.icon_class }}"', src, path)

    def test_templates_use_bc_icon(self):
        # business social row + every card hero resolve through the filter
        self.assertIn("bc_icon(link.platform)", read("templates", "pages", "business", "business.html"))
        for hero in glob.glob(os.path.join(APP_DIR, "templates", "pages", "card", "parts", "hero_*.html")):
            self.assertIn("bc_icon(link.link_type)", open(hero).read(), hero)


class TestImageAttributes(unittest.TestCase):
    TAG = re.compile(r"<img\b[^>]*>", re.S)

    def _all_imgs(self):
        for path in glob.glob(os.path.join(APP_DIR, "templates", "**", "*.html"), recursive=True):
            for m in self.TAG.finditer(read_path(path)):
                yield path, m.group(0)

    def test_every_img_decodes_async(self):
        for path, tag in self._all_imgs():
            self.assertIn("decoding=", tag, path)

    def test_hero_imgs_have_fetchpriority(self):
        for path, tag in self._all_imgs():
            cls = re.search(r'class="([^"]*)"', tag)
            if cls and any(h in cls.group(1) for h in _HERO_CLASSES):
                self.assertIn("fetchpriority=\"high\"", tag, path)

    def test_no_hero_is_lazy_loaded(self):
        for path, tag in self._all_imgs():
            cls = re.search(r'class="([^"]*)"', tag)
            if cls and any(h in cls.group(1) for h in _HERO_CLASSES):
                self.assertNotIn("loading=\"lazy\"", tag, path)

    def test_gallery_and_features_are_lazy(self):
        gallery = read("templates", "pages", "product", "parts", "gallery.html")
        for tag in self.TAG.findall(gallery):
            self.assertIn("loading=\"lazy\"", tag)


class TestOpenGraphImage(unittest.TestCase):
    def test_recut_to_1200x630_under_300kb(self):
        path = os.path.join(APP_DIR, "public", "images", "og-image.png")
        w, h = png_dims(path)
        self.assertEqual((w, h), (1200, 630))
        self.assertLess(os.path.getsize(path), 300_000)


if __name__ == "__main__":
    unittest.main()
