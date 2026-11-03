# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Structural checks for canonical public URLs.

The origin is derived from ``host_name`` only (``allow_header_override=False``),
because public URLs are printed into QR codes and NFC tags. These tests guard the
wiring that keeps generated URLs and QR images in sync after a domain change,
plus the scheme/port rules the helper applies to a configured host.
"""

import contextlib
import importlib.util
import os
import sys
import types
import unittest

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
URLS_PATH = os.path.join(APP_DIR, "utils", "urls.py")


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


@contextlib.contextmanager
def loaded_urls_module(conf, fallback="http://fallback.example"):
    """Import utils/urls.py against a stubbed frappe, without leaking the stub."""
    frappe_stub = types.ModuleType("frappe")
    utils_stub = types.ModuleType("frappe.utils")
    utils_stub.get_url = lambda *args, **kwargs: fallback
    frappe_stub.utils = utils_stub
    frappe_stub.local = types.SimpleNamespace(conf=conf)

    saved = {name: sys.modules.get(name) for name in ("frappe", "frappe.utils")}
    sys.modules["frappe"] = frappe_stub
    sys.modules["frappe.utils"] = utils_stub
    try:
        spec = importlib.util.spec_from_file_location("bc_urls_under_test", URLS_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module
    finally:
        for name, value in saved.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


class TestCanonicalUrls(unittest.TestCase):
    def test_canonical_base_ignores_request_host(self):
        source = read("utils", "urls.py")
        self.assertIn("allow_header_override=False", source)

    def test_migrate_refreshes_qr_after_url_change(self):
        install = read("install.py")
        self.assertIn("def refresh_card_qr_codes", install)
        self.assertIn("refresh_card_qr_codes(stale_cards)", install)

    def test_qr_regeneration_reuses_existing_file_row(self):
        source = read("services", "qr_service.py")
        self.assertIn("existing_file", source)
        self.assertIn('"attached_to_doctype": "Digital Card"', source)


class TestHostRules(unittest.TestCase):
    """What the helper does with the value an operator typed in site_config.json."""

    def test_explicit_https_is_kept(self):
        with loaded_urls_module({"host_name": "https://connect.osduotech.com"}) as urls:
            self.assertEqual(urls.get_canonical_base_url(), "https://connect.osduotech.com")

    def test_scheme_less_public_host_becomes_https(self):
        with loaded_urls_module({"host_name": "connect.osduotech.com"}) as urls:
            self.assertEqual(urls.get_canonical_base_url(), "https://connect.osduotech.com")

    def test_public_host_never_gets_the_dev_port(self):
        conf = {
            "host_name": "https://connect.osduotech.com",
            "developer_mode": 1,
            "webserver_port": 8000,
        }
        with loaded_urls_module(conf) as urls:
            self.assertEqual(urls.get_canonical_base_url(), "https://connect.osduotech.com")

    def test_local_host_stays_http(self):
        with loaded_urls_module({"host_name": "localhost"}) as urls:
            self.assertEqual(urls.get_canonical_base_url(), "http://localhost")

    def test_private_network_host_stays_http(self):
        with loaded_urls_module({"host_name": "192.168.122.49:8000"}) as urls:
            self.assertEqual(urls.get_canonical_base_url(), "http://192.168.122.49:8000")

    def test_local_dev_host_gets_the_webserver_port(self):
        conf = {"host_name": "localhost", "developer_mode": 1, "webserver_port": 8000}
        with loaded_urls_module(conf) as urls:
            self.assertEqual(urls.get_canonical_base_url(), "http://localhost:8000")

    def test_explicit_http_is_respected(self):
        with loaded_urls_module({"host_name": "http://localhost:8000"}) as urls:
            self.assertEqual(urls.get_canonical_base_url(), "http://localhost:8000")

    def test_page_urls_are_built_on_the_canonical_base(self):
        with loaded_urls_module({"host_name": "https://connect.osduotech.com"}) as urls:
            self.assertEqual(urls.get_business_public_url("osduo"), "https://connect.osduotech.com/b/osduo")
            self.assertEqual(urls.get_card_public_url("owner"), "https://connect.osduotech.com/c/owner")
            self.assertIsNone(urls.get_business_public_url(None))

    def test_without_host_name_it_falls_back_to_frappe(self):
        with loaded_urls_module({}, fallback="http://osduo.connect:8000") as urls:
            self.assertEqual(urls.get_canonical_base_url(), "http://osduo.connect:8000")
            self.assertIn("no host_name", urls.get_canonical_base_url_source())

    def test_diagnostics_report_the_source(self):
        with loaded_urls_module({"host_name": "connect.osduotech.com"}) as urls:
            info = urls.describe_canonical_url()
            self.assertEqual(info["source"], "site_config.json -> host_name")
            self.assertEqual(info["canonical_base_url"], "https://connect.osduotech.com")


if __name__ == "__main__":
    unittest.main()
