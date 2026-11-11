import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from osduo_business_connect.seo.robots import (
    DEFAULT_ROBOTS_RULES,
    _drop_sitemap_lines,
    compose_robots_txt,
)

BASE = "https://beadazzled.connect.osduotech.com"


class TestDropSitemapLines(unittest.TestCase):
    def test_removes_single_declaration(self):
        body = "User-agent: *\nSitemap: http://beadazzled.connect/sitemap.xml\n"
        self.assertNotIn("Sitemap", _drop_sitemap_lines(body))
        self.assertIn("User-agent: *", _drop_sitemap_lines(body))

    def test_is_case_insensitive(self):
        self.assertEqual(_drop_sitemap_lines("sitemap: https://x/sitemap.xml"), "")

    def test_removes_multiple_declarations(self):
        body = "Sitemap: https://a/sitemap.xml\nAllow: /\nSITEMAP: https://b/sitemap.xml"
        self.assertEqual(_drop_sitemap_lines(body), "Allow: /")

    def test_keeps_unrelated_lines(self):
        self.assertEqual(_drop_sitemap_lines("Disallow: /api/"), "Disallow: /api/")


class TestComposeRobotsTxt(unittest.TestCase):
    def test_empty_body_uses_bundled_defaults(self):
        text = compose_robots_txt("", BASE)
        self.assertIn(DEFAULT_ROBOTS_RULES[0], text)
        self.assertIn("Disallow: /api/", text)

    def test_stale_sitemap_is_replaced_with_the_current_host(self):
        body = "User-agent: *\nDisallow: /app\nSitemap: http://beadazzled.connect/sitemap.xml\n"
        text = compose_robots_txt(body, BASE)
        self.assertNotIn("http://beadazzled.connect", text)
        self.assertIn(f"Sitemap: {BASE}/sitemap.xml", text)
        # Admin rules are otherwise preserved.
        self.assertIn("Disallow: /app", text)

    def test_exactly_one_sitemap_line(self):
        body = "Sitemap: https://old.test/sitemap.xml\nAllow: /"
        text = compose_robots_txt(body, BASE)
        self.assertEqual(text.count("Sitemap:"), 1)

    def test_sitemap_line_points_at_the_index(self):
        self.assertIn(f"Sitemap: {BASE}/sitemap.xml", compose_robots_txt("", BASE))


class TestRenderEntriesIsHostIndependent(unittest.TestCase):
    """The sitemap cache stores relative paths; the host is added per request."""

    def _read(self, *parts):
        app_dir = os.path.join(os.path.dirname(__file__), "..")
        with open(os.path.join(app_dir, *parts)) as f:
            return f.read()

    def test_cache_stores_paths_not_absolute_urls(self):
        src = self._read("seo", "sitemap.py")
        # Entries are built as relative paths; the old absolute-URL helper is gone.
        self.assertIn('"path": _path(', src)
        self.assertNotIn("def _loc(", src)
        self.assertIn("def _absolute(", src)
        self.assertIn("def get_render_entries", src)
        self.assertIn("get_sitemap_base_url", src)

    def test_every_controller_renders_per_request(self):
        for name in ("sitemap", "sitemap_businesses", "sitemap_products", "sitemap_services", "sitemap_cards"):
            self.assertIn("get_render_entries", self._read("www", f"{name}.py"), f"www/{name}.py")


if __name__ == "__main__":
    unittest.main()
