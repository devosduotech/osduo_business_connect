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

    def test_v16_login_override_is_wired(self):
        # Frappe v16 serves /login from www/login.html. The app override must
        # re-use the core controller and extend the repo template, which in
        # turn extends Frappe's v16 login template so stock forms/2FA survive.
        self.assertEqual(
            read("www", "login.html").strip(),
            '{%- extends "osduo_business_connect/templates/login.html" -%}',
        )
        controller = read("www", "login.py")
        self.assertIn("from frappe.www.login import *", controller)

        template = read("templates", "login.html")
        self.assertIn('extends "frappe/www/login.html"', template)
        self.assertIn("{% block page_content %}", template)
        self.assertIn("{{ super() }}", template)
        self.assertIn("bc-login-layout", template)
        self.assertIn("bc-brand-panel", template)
        self.assertIn("bc-login-forms", template)

    def test_login_layout_fallback_and_root_forward(self):
        js = read("public", "js", "login-layout.js")
        # Guests landing on / must be forwarded to the canonical /login route.
        self.assertIn('path === ""', js)
        self.assertIn('getAttribute("frappe-session-status") === "logged-out"', js)
        self.assertIn('window.location.replace("/login")', js)
        # insertBefore needs a real sibling: the card is nested in v16.
        self.assertNotIn("section.insertBefore(panel, card)", js)
        self.assertIn("card.closest(\".page_content\")", js)
        self.assertIn("container.insertBefore(panel, forms)", js)
        self.assertIn("document.querySelector(\".bc-brand-panel\")", js)

    def test_login_css_targets_template_and_fallback_layout(self):
        css = read("public", "css", "login.css")
        self.assertIn("body[data-path=\"login\"] .bc-login-layout {", css)
        self.assertIn("> .bc-login-forms", css)
        self.assertNotIn("section.for-login.bc-login-layout", css)

    def test_assets_are_cache_busted(self):
        # Firefox can have no service worker (plain HTTP / privacy settings), so
        # its plain disk cache would otherwise keep serving the old desk JS/CSS.
        # Every app asset URL must carry the shared revision query string.
        hooks = read("hooks.py")
        self.assertIn('BC_ASSET_REVISION = "2026-11-24-share-connect-v1412"', hooks)
        for asset in (
            "css/login.css",
            "js/login-layout.js",
            "js/pwa.js",
            "css/branding.css",
            "js/branding.js",
        ):
            self.assertIn(
                f"/assets/osduo_business_connect/{asset}?v={{BC_ASSET_REVISION}}",
                hooks,
            )
        self.assertEqual(
            read("www", "sw.py").count('"2026-11-24-share-connect-v1412"'), 1
        )

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

    def test_boot_session_publishes_avatar_rows_and_theme_colors(self):
        branding = read("branding.py")
        self.assertIn("def boot_session(bootinfo)", branding)
        self.assertIn("bootinfo.osduo_support", branding)
        self.assertIn("bootinfo.osduo_branding", branding)
        self.assertIn('"primary_color": OSDUO_BRANDING["primary_color"]', branding)
        self.assertIn('"secondary_color": OSDUO_BRANDING["secondary_color"]', branding)
        self.assertIn('"background_color": OSDUO_BRANDING["background_color"]', branding)
        self.assertIn('"text_color": OSDUO_BRANDING["text_color"]', branding)
        self.assertIn("bootinfo.bc_workspace_theme", branding)
        self.assertIn('"roles": sorted(CUSTOMER_ROLES)', branding)
        self.assertIn('"privileged_roles": sorted(PRIVILEGED_ROLES)', branding)
        self.assertIn('"paths": sorted(CUSTOMER_WORKSPACE_PATHS)', branding)
        self.assertIn("def support_menu_items", branding)
        # The boot payload must not try to rewrite navbar_settings: Frappe's
        # sessions.get() replaces it from the stored record after every
        # boot_session hook has run, so such a rewrite never reaches the desk.
        self.assertNotIn("bootinfo.navbar_settings =", branding)

    def test_boot_session_publishes_current_brand_palette(self):
        branding = _load_branding()
        bootinfo = types.SimpleNamespace()
        branding.boot_session(bootinfo)
        for key in ("primary_color", "secondary_color", "background_color", "text_color"):
            with self.subTest(key=key):
                self.assertEqual(
                    bootinfo.osduo_branding[key], branding.OSDUO_BRANDING[key]
                )

    def test_boot_session_publishes_workspace_theme_policy(self):
        from osduo_business_connect.subscription.constants import (
            CUSTOMER_ROLES,
            CUSTOMER_WORKSPACE_PATHS,
            PRIVILEGED_ROLES,
        )

        branding = _load_branding()
        bootinfo = types.SimpleNamespace()
        branding.boot_session(bootinfo)

        config = bootinfo.bc_workspace_theme
        self.assertEqual(config["roles"], sorted(CUSTOMER_ROLES))
        self.assertEqual(config["privileged_roles"], sorted(PRIVILEGED_ROLES))
        self.assertEqual(config["paths"], sorted(CUSTOMER_WORKSPACE_PATHS))
        self.assertIn("/desk/business-connect", config["paths"])
        self.assertIn("/desk/business/business-connect", config["paths"])

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

    def test_desk_js_patches_desktop_workspace_avatar_menu(self):
        js = read("public", "js", "branding.js")
        # Desktop/Workspace has a second, hard-coded avatar dropdown outside
        # Navbar Settings. Scope the patch to its .desktop-avatar trigger.
        self.assertIn('DESKTOP_AVATAR_SELECTOR = ".desktop-avatar"', js)
        self.assertIn("frappe.ui.Dropdown", js)
        self.assertIn("proto.open", js)
        self.assertIn("is_desktop_avatar_dropdown(this)", js)
        # All Frappe help rows are removed, and our rows go above Logout.
        self.assertIn('"About", "System Health", "Frappe Support"', js)
        self.assertIn('translated("Logout")', js)
        self.assertIn("rewrite_desktop_avatar_options", js)
        self.assertIn("support_menu_rows()", js)
        # Reuse the shared boot rows: href/target come from hooks.py.
        self.assertIn("href: item.url", js)
        self.assertIn("if (item.target) row.target = item.target;", js)
        self.assertIn("apply_patch_with_polling(patch_user_menu)", js)
        self.assertIn(
            "apply_patch_with_polling(patch_desktop_avatar_menu)", js
        )

    def test_desk_css_hides_frappe_footer_links(self):
        css = read("public", "css", "branding.css")
        self.assertIn("display: none", css)
        self.assertNotIn("opacity: 0.5", css)

    def test_desk_sidebar_selected_and_hover_use_dark_text_on_white(self):
        css = read("public", "css", "branding.css")
        js = read("public", "js", "branding.js")

        # The selected row is a white chip. Its text must be the dark portal
        # colour: white-on-white made the current item unreadable.
        row_selector = (
            "body.bc-customer-workspace .body-sidebar "
            ".standard-sidebar-item.active-sidebar .item-anchor,"
        )
        self.assertIn(row_selector, css)
        row_block = css.split(row_selector, 1)[1].split("}", 1)[0]
        self.assertIn("background-color: #ffffff !important;", row_block)
        self.assertIn("color: var(--bc-portal-text) !important;", row_block)
        self.assertNotIn("color: #fff !important;", row_block)

        # v16 keeps the visible text in a nested span. The muted !important
        # rule above would otherwise keep the label grey, so set it explicitly
        # along with the portal's semibold weight.
        active_selector = (
            "body.bc-customer-workspace .body-sidebar "
            ".standard-sidebar-item.active-sidebar .sidebar-item-label {"
        )
        self.assertIn(active_selector, css)
        active_block = css.split(active_selector, 1)[1].split("}", 1)[0]
        self.assertIn("color: var(--bc-portal-text) !important;", active_block)
        self.assertIn("font-weight: 600 !important;", active_block)
        self.assertNotIn("color: #fff !important;", active_block)

        # Hover has the same nested-label inheritance trap.
        hover_selector = (
            "body.bc-customer-workspace .body-sidebar .item-anchor:hover .sidebar-item-label"
        )
        self.assertIn(hover_selector, css)
        hover_block = css.split(hover_selector, 1)[1].split("}", 1)[0]
        self.assertIn("color: var(--bc-portal-text) !important;", hover_block)

        hover_row_selector = (
            "body.bc-customer-workspace .body-sidebar .item-anchor:hover,"
        )
        self.assertIn(hover_row_selector, css)
        hover_row_block = css.split(hover_row_selector, 1)[1].split("}", 1)[0]
        self.assertIn("background-color: #ffffff !important;", hover_row_block)
        self.assertIn("color: var(--bc-portal-text) !important;", hover_row_block)

        # Keep Frappe's own active-state background consistent with the chip.
        self.assertIn("--sidebar-select-color: #ffffff;", css)
        self.assertIn('"--sidebar-select-color", "#ffffff"', js)
        self.assertIn("--bc-portal-text: #1e293b;", css)

    def test_desk_mobile_collapsed_sidebar_is_transparent(self):
        css = read("public", "css", "branding.css")
        # Frappe v16 fades the collapsed phone drawer by making it transparent.
        # Our dark rail is !important, so it needs an explicit mobile override;
        # otherwise a blank slate slab covers two thirds of a phone screen.
        self.assertIn("@media (max-width: 767px)", css)
        selector = (
            "body.bc-customer-workspace .body-sidebar-container:not(.expanded) "
            ".body-sidebar"
        )
        self.assertIn(selector, css)
        block = css.split(selector, 1)[1].split("}", 1)[0]
        self.assertIn("background-color: transparent !important;", block)
        self.assertIn("border-right-color: transparent !important;", block)
        self.assertIn("pointer-events: none;", block)

    def test_desk_hover_chip_is_pointer_only(self):
        css = read("public", "css", "branding.css")
        # Touch browsers keep :hover on the last tapped row. If the white chip
        # is painted there too, Card Event looks permanently selected. Keep the
        # focus style universal, but gate hover on a real pointing device.
        media = "@media (hover: hover)"
        self.assertIn(media, css)
        focus_selector = (
            "body.bc-customer-workspace .body-sidebar "
            ".item-anchor:focus-visible .sidebar-item-label"
        )
        hover_selector = (
            "body.bc-customer-workspace .body-sidebar "
            ".item-anchor:hover .sidebar-item-label"
        )
        self.assertIn(focus_selector, css)
        self.assertIn(hover_selector, css)
        self.assertLess(css.index(focus_selector), css.index(media))
        self.assertLess(css.index(media), css.index(hover_selector))


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
