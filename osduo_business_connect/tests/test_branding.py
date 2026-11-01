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

    def test_default_website_theme_is_created_on_install(self):
        branding = read("branding.py")
        self.assertIn('WEBSITE_THEME_NAME = "OSDuo Business Connect"', branding)
        self.assertIn("def ensure_default_website_theme", branding)
        self.assertIn('"doctype": "Website Theme"', branding)
        self.assertIn('"theme": WEBSITE_THEME_NAME', branding)
        # Must be editable per site and compiled by Frappe.
        self.assertIn('"custom": 1', branding)

    def test_default_website_theme_only_fills_empty_slot(self):
        branding = read("branding.py")
        # A deliberate per-site theme choice (anything other than empty or
        # Standard) must win over the bundled default.
        self.assertIn("def _is_default_theme_slot", branding)
        self.assertIn('("", "Standard")', branding)
        self.assertIn("website_settings, \"website_theme\", WEBSITE_THEME_NAME", branding)

    def test_default_website_theme_uses_bundled_brand_colors(self):
        branding = read("branding.py")
        self.assertIn("--osduo-primary: #0B3D91", branding)
        self.assertIn("--osduo-secondary: #1677FF", branding)
        self.assertIn("--osduo-accent: #00C49A", branding)
        # No runtime font/network imports in the bundled theme.
        self.assertNotIn("@import url(", branding)

    def test_default_website_theme_reuses_color_records(self):
        branding = read("branding.py")
        self.assertIn("def _get_or_create_color", branding)
        self.assertIn('"doctype": "Color"', branding)
        self.assertIn('"__newname": name', branding)

    def test_pwa_icon_accepts_bundled_assets(self):
        pwa = read("pwa.py")
        self.assertIn("APP_ASSET_PREFIX", pwa)
        self.assertIn("/assets/osduo_business_connect/", pwa)
        self.assertIn("OSDUO_BRANDING[\"logo_mark\"]", pwa)


if __name__ == "__main__":
    unittest.main()
