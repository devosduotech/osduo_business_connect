import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


class TestSitemapWiring(unittest.TestCase):
    """Structural checks for the database-driven sitemap layer.

    The sitemaps are served through Frappe's raw-template mechanism
    (controller ``.py`` + ``.xml`` template), like Frappe's own
    ``www/sitemap``. These tests do not need a running bench.
    """

    SUB_SITEMAPS = (
        "sitemap-businesses",
        "sitemap-products",
        "sitemap-services",
        "sitemap-cards",
    )

    def test_generator_module_exists(self):
        self.assertTrue(os.path.exists(os.path.join(APP_DIR, "seo", "sitemap.py")))

    def test_index_route_files_exist(self):
        for rel in (("www", "sitemap.py"), ("www", "sitemap.xml")):
            self.assertTrue(os.path.exists(os.path.join(APP_DIR, *rel)), f"Missing {'/'.join(rel)}")

    def test_sub_sitemap_route_files_exist(self):
        for name in self.SUB_SITEMAPS:
            controller = os.path.join(APP_DIR, "www", f"{name.replace('-', '_')}.py")
            template = os.path.join(APP_DIR, "www", f"{name}.xml")
            self.assertTrue(os.path.exists(controller), f"Missing www/{name.replace('-', '_')}.py")
            self.assertTrue(os.path.exists(template), f"Missing www/{name}.xml")

    def test_controllers_use_raw_template_and_no_cache(self):
        # The index and each sub-sitemap must declare the raw-template path and
        # opt out of Frappe's 30-minute HTML page cache.
        index = read("www", "sitemap.py")
        self.assertIn('base_template_path = "www/sitemap.xml"', index)
        self.assertIn("no_cache = 1", index)

        for name in self.SUB_SITEMAPS:
            controller = read("www", f"{name.replace('-', '_')}.py")
            self.assertIn(f'base_template_path = "www/{name}.xml"', controller)
            self.assertIn("no_cache = 1", controller)

    def test_public_urls_are_generated_from_records(self):
        sitemap = read("seo", "sitemap.py")
        # URL shapes must match the public page controllers.
        self.assertIn('_loc("b", r.slug)', sitemap)
        self.assertIn('_loc("b", r.business_slug, segment, r.slug)', sitemap)
        self.assertIn('_loc("c", r.slug)', sitemap)
        self.assertIn('"products"', sitemap)
        self.assertIn('"services"', sitemap)

    def test_only_public_records_are_included(self):
        sitemap = read("seo", "sitemap.py")
        # Visibility rules mirror the page controllers.
        self.assertIn("status = 'Published'", sitemap)
        self.assertIn("public_profile_enabled = 1", sitemap)
        self.assertIn("docstatus < 2", sitemap)
        # Child URLs require the parent business to be public too.
        self.assertIn("INNER JOIN `tabBusiness` b", sitemap)

    def test_index_references_every_sub_sitemap(self):
        sitemap = read("seo", "sitemap.py")
        for name in self.SUB_SITEMAPS:
            self.assertIn(f'"{name}.xml"', sitemap)

    def test_sitemap_xml_namespaces(self):
        index = read("www", "sitemap.xml")
        self.assertIn("http://www.sitemaps.org/schemas/sitemap/0.9", index)
        self.assertIn("<sitemapindex", index)
        for name in self.SUB_SITEMAPS:
            body = read("www", f"{name}.xml")
            self.assertIn("http://www.sitemaps.org/schemas/sitemap/0.9", body)
            self.assertIn("<urlset", body)
            self.assertIn("<loc>", body)

    def test_scheduled_regeneration_registered(self):
        hooks = read("hooks.py")
        self.assertIn('"0 2 */3 * *"', hooks)
        self.assertIn("osduo_business_connect.seo.sitemap.generate_sitemaps", hooks)

    def test_publication_events_invalidate_cache(self):
        hooks = read("hooks.py")
        self.assertIn("invalidate_sitemap_cache", hooks)
        for doctype in ("Business", "Showcase Product", "Showcase Service", "Digital Card"):
            self.assertIn(f'"{doctype}"', hooks)
        for event in ("on_update", "on_submit", "on_cancel", "on_trash"):
            self.assertIn(f'"{event}"', hooks)

    def test_generator_caches_and_invalidates(self):
        sitemap = read("seo", "sitemap.py")
        self.assertIn("def get_cached_entries", sitemap)
        self.assertIn("def invalidate_sitemap_cache", sitemap)
        self.assertIn("def generate_sitemaps", sitemap)
        self.assertIn("frappe.cache.get_value", sitemap)
        self.assertIn("frappe.cache.set_value", sitemap)
        self.assertIn("expires_in_sec", sitemap)

    def test_robots_txt_points_at_sitemap(self):
        branding = read("branding.py")
        self.assertIn("def _default_robots_txt", branding)
        self.assertIn("/sitemap.xml", branding)
        # Must not clobber an administrator's custom robots.txt.
        self.assertIn("robots_txt", branding)

    def test_no_static_sitemap_files_are_written(self):
        # Dynamic, DB-driven sitemaps: nothing should be written to disk.
        sitemap = read("seo", "sitemap.py")
        self.assertNotIn("write_file", sitemap)
        self.assertNotIn("open(", sitemap)


if __name__ == "__main__":
    unittest.main()
