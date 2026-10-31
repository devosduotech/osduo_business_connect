import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


class TestPWAWiring(unittest.TestCase):
    """Structural checks for the PWA layer (manifest, service worker, icons)."""

    def test_www_route_files_exist(self):
        for rel in (
            ("www", "manifest.py"),
            ("www", "manifest.json"),
            ("www", "sw.py"),
            ("www", "sw.js"),
            ("www", "offline.py"),
            ("www", "offline.html"),
            ("pwa.py",),
            ("utils", "urls.py"),
            ("public", "js", "pwa.js"),
        ):
            path = os.path.join(APP_DIR, *rel)
            self.assertTrue(os.path.exists(path), f"Missing {os.path.join(*rel)}")

    def test_raw_template_mechanism(self):
        # Same pattern as Frappe's www/website_script and www/sitemap controllers
        manifest = read("www", "manifest.py")
        self.assertIn('base_template_path = "www/manifest.json"', manifest)
        sw = read("www", "sw.py")
        self.assertIn('base_template_path = "www/sw.js"', sw)
        self.assertIn("no_cache", sw)

    def test_manifest_required_fields(self):
        manifest = read("www", "manifest.json")
        for key in ('"name"', '"start_url"', '"scope"', '"display"', '"icons"', '"theme_color"'):
            self.assertIn(key, manifest, f"manifest.json missing {key}")
        self.assertIn("standalone", manifest)

    def test_service_worker_caches_never_touch_api(self):
        sw = read("www", "sw.js")
        self.assertIn("skipWaiting", sw)
        self.assertIn("clients.claim", sw)
        self.assertIn("/offline", sw)
        # Strategy guard: API/private/desk paths must be excluded from caching
        self.assertIn('"/api/"', sw)
        self.assertIn('"/private/"', sw)

    def test_pwa_js_registered_in_hooks(self):
        hooks = read("hooks.py")
        self.assertIn("/assets/osduo_business_connect/js/pwa.js", hooks)

    def test_icon_endpoint_whitelisted_for_guest(self):
        pwa = read("pwa.py")
        self.assertIn("@frappe.whitelist(allow_guest=True)", pwa)
        self.assertIn("def get_app_icon", pwa)
        # raw inline response (v16 "download" type) so <img>/manifest can use it
        self.assertIn('"type"] = "download"', pwa)
        self.assertIn('"display_content_as"] = "inline"', pwa)

    def test_canonical_urls_ignore_request_host(self):
        urls = read("utils", "urls.py")
        self.assertIn("allow_header_override=False", urls)

    def test_public_url_auto_derived(self):
        card = read("card", "doctype", "digital_card", "digital_card.py")
        self.assertIn("get_card_public_url", card)
        self.assertIn("def set_public_url", card)
        self.assertIn("def ensure_qr_image", card)
        business = read("business", "core.py")
        self.assertIn("get_business_public_url", business)
        self.assertIn("def set_public_url", business)

    def test_backfill_runs_on_migrate(self):
        install = read("install.py")
        self.assertIn("def backfill_public_urls", install)
        self.assertIn("backfill_public_urls()", install)


if __name__ == "__main__":
    unittest.main()
