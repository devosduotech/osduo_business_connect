import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")

# Brand files that must ship inside the app (never be copied into a site's
# public/files directory).
BUNDLED_IMAGES = (
    "logo-512.png",
    "logo-dark-512.png",
    "logo-mark-512.png",
    "logo-mark-128.png",
    "favicon-256.png",
    "login-panel.jpg",
    "logo.png",
    "logo-dark.png",
    "logo-mark.png",
    "favicon.png",
    "og-image.png",
)


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


class TestBundledBranding(unittest.TestCase):
    """Brand assets and the login/desk logo must come from the app package."""

    def test_brand_assets_are_bundled(self):
        for image in BUNDLED_IMAGES:
            path = os.path.join(APP_DIR, "public", "images", image)
            self.assertTrue(os.path.exists(path), f"Missing bundled asset {image}")

    def test_hooks_point_at_app_assets(self):
        hooks = read("hooks.py")
        for key in ("logo", "logo_dark", "favicon", "logo_mark", "logo_mark_small", "login_panel"):
            self.assertIn(f'"{key}"', hooks)
        # Brand URLs must be served from the app, not the site's files dir.
        self.assertNotIn('"/files/', hooks)
        self.assertIn("/assets/osduo_business_connect/images/", hooks)

    def test_login_layout_uses_bundled_logo(self):
        js = read("public", "js", "login-layout.js")
        self.assertIn("/assets/osduo_business_connect/images/logo-mark-128.png", js)
        self.assertNotIn('src="/files/', js)
        self.assertNotIn("/files/logo_mark", js)

    def test_login_css_uses_bundled_panel(self):
        css = read("public", "css", "login.css")
        self.assertIn(
            'url("/assets/osduo_business_connect/images/login-panel.jpg")', css
        )
        self.assertNotIn("/files/", css)

    def test_no_site_files_brand_references(self):
        for rel in (
            ("public", "js", "branding.js"),
            ("templates", "bc_base.html"),
            ("templates", "login.html"),
        ):
            content = read(*rel)
            self.assertNotIn("/files/", content, f"{'/'.join(rel)} still uses /files/")

    def test_branding_applied_on_install_and_migrate(self):
        install = read("install.py")
        self.assertIn("def apply_branding_settings", install)
        # Both hooks must apply branding so existing sites migrate automatically.
        self.assertGreaterEqual(install.count("apply_branding_settings()"), 2)

    def test_branding_module_replaces_legacy_copies(self):
        branding = read("branding.py")
        self.assertIn("def apply_branding_settings", branding)
        self.assertIn("def _is_legacy_brand_copy", branding)
        self.assertIn("logo_mark_512x512", branding)

    def test_pwa_icon_accepts_bundled_assets(self):
        pwa = read("pwa.py")
        self.assertIn("APP_ASSET_PREFIX", pwa)
        self.assertIn("/assets/osduo_business_connect/", pwa)
        self.assertIn("OSDUO_BRANDING[\"logo_mark\"]", pwa)


if __name__ == "__main__":
    unittest.main()
