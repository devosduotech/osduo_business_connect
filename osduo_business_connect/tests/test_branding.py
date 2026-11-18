import importlib
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")


def _load_branding():
    """Import ``branding.py`` without a Frappe install.

    The module only needs ``frappe`` at call time, so a bare stub is enough to
    exercise the pure helpers (the matcher and the dropdown sweeper).
    """
    if "frappe" not in sys.modules:
        try:
            import frappe
        except Exception:
            sys.modules["frappe"] = types.ModuleType("frappe")
    return importlib.import_module("osduo_business_connect.branding")


def _row_class():
    """A dict that also supports the ``row.field`` access the helpers use."""

    class Row(dict):
        def __getattr__(self, name):
            try:
                return self[name]
            except KeyError:
                raise AttributeError(name) from None

        def __setattr__(self, name, value):
            self[name] = value

    return Row


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


class TestDeskSupportMenu(unittest.TestCase):
    """Desk support links (avatar menu + header menu) and Frappe help removal."""

    def test_branding_exposes_support_destinations(self):
        hooks = read("hooks.py")
        self.assertIn(
            '"support_manual_url": "https://www.osduotech.com/business-connect-manual"',
            hooks,
        )
        self.assertIn('"support_email": "connect@osduotech.com"', hooks)
        self.assertIn(
            '"support_portal_url": "https://www.osduotech.com/contact"', hooks
        )

    def test_boot_session_hook_registered(self):
        hooks = read("hooks.py")
        self.assertIn(
            'boot_session = "osduo_business_connect.branding.boot_session"', hooks
        )

    def test_boot_session_publishes_avatar_rows(self):
        branding = read("branding.py")
        self.assertIn("def boot_session(bootinfo)", branding)
        self.assertIn("bootinfo.osduo_support", branding)
        self.assertIn("def support_menu_items", branding)
        # The boot payload must not try to rewrite navbar_settings: Frappe's
        # sessions.get() replaces it from the stored record after every
        # boot_session hook has run, so such a rewrite never reaches the desk.
        self.assertNotIn("bootinfo.navbar_settings =", branding)

    def test_navbar_support_hides_frappe_help_rows(self):
        branding = read("branding.py")
        self.assertIn("def apply_navbar_support", branding)
        self.assertIn("def _hide_frappe_help_rows", branding)
        self.assertIn('"Frappe Support"', branding)
        self.assertIn('"System Health"', branding)
        self.assertIn("frappe.ui.toolbar.show_about()", branding)
        # Both dropdown tables are swept: the header menu renders
        # settings_dropdown flat, so a stray help row there must be hidden too.
        self.assertIn(
            '_NAVBAR_DROPDOWN_FIELDS = ("help_dropdown", "settings_dropdown")',
            branding,
        )
        # Hidden in the stored record, not deleted: sync_standard_items
        # re-adds any missing standard row on every migrate.
        self.assertIn("row.hidden = 1", branding)

    def test_navbar_support_adds_osduo_header_rows(self):
        branding = read("branding.py")
        self.assertIn("settings_dropdown", branding)
        self.assertIn('"is_standard": 0', branding)
        self.assertIn("navbar.save(ignore_permissions=True)", branding)

    def test_branding_settings_applies_navbar_support(self):
        branding = read("branding.py")
        self.assertIn('"navbar_settings": False', branding)
        self.assertIn('changed["navbar_settings"] = apply_navbar_support()', branding)

    def test_support_menu_rows_open_correctly(self):
        branding = read("branding.py")
        # Email row opens the default mail client, not a new tab.
        self.assertIn("mailto:", branding)
        self.assertIn("support_email", branding)
        # The two web rows open a new tab; Frappe then adds rel="noopener".
        self.assertIn('"target": "_blank"', branding)

    def test_desk_js_reads_boot_config_without_hardcoding(self):
        js = read("public", "js", "branding.js")
        self.assertIn("frappe.boot.osduo_support", js)
        self.assertIn("user_menu_options", js)
        self.assertIn("target", js)
        # Destinations live in hooks.py, never in the JS.
        self.assertNotIn("osduotech.com", js)
        self.assertNotIn("connect@", js)

    def test_desk_css_hides_frappe_footer_links(self):
        css = read("public", "css", "branding.css")
        self.assertIn("display: none", css)
        self.assertNotIn("opacity: 0.5", css)


class TestFrappeHelpRowSweeper(unittest.TestCase):
    """Unit coverage for the row matcher and the two-table sweeper."""

    @classmethod
    def setUpClass(cls):
        cls.branding = _load_branding()
        cls.Row = _row_class()

    def test_matches_frappe_help_rows(self):
        matches = self.branding._is_frappe_help_item
        self.assertTrue(
            matches({"item_label": "Frappe Support", "route": "https://frappe.io/support"})
        )
        self.assertTrue(
            matches({"item_label": "System Health", "route": "/desk/system-health-report"})
        )
        self.assertTrue(
            matches({"item_label": "About", "action": "frappe.ui.toolbar.show_about()"})
        )
        # Route marker catches scheme/slash variants of Frappe's support link.
        self.assertTrue(matches({"item_label": "Help", "route": "http://frappecloud.com/support/"}))

    def test_ignores_osduo_and_other_rows(self):
        matches = self.branding._is_frappe_help_item
        self.assertFalse(
            matches(
                {
                    "item_label": "User Manual",
                    "route": "https://www.osduotech.com/business-connect-manual",
                }
            )
        )
        self.assertFalse(matches({"item_label": "Support Email", "route": "mailto:connect@osduotech.com"}))
        self.assertFalse(matches({"item_label": "Apps", "route": "/apps"}))

    def test_sweeps_both_dropdown_tables(self):
        row = lambda **kw: self.Row(**kw)  # noqa: E731
        navbar = types.SimpleNamespace(
            help_dropdown=[row(item_label="Frappe Support", route="https://frappe.io/support", hidden=0)],
            settings_dropdown=[
                row(item_label="Frappe Support", route="https://frappe.io/support", hidden=0),
                row(item_label="User Manual", route="https://www.osduotech.com/business-connect-manual", hidden=0),
            ],
        )
        self.assertTrue(self.branding._hide_frappe_help_rows(navbar))
        self.assertEqual(navbar.help_dropdown[0].hidden, 1)
        self.assertEqual(navbar.settings_dropdown[0].hidden, 1)
        # The OSDuo row is untouched.
        self.assertEqual(navbar.settings_dropdown[1].hidden, 0)
        # Idempotent: a second pass finds nothing to change.
        self.assertFalse(self.branding._hide_frappe_help_rows(navbar))


if __name__ == "__main__":
    unittest.main()
