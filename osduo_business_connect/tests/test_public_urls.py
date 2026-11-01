# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Structural checks for canonical public URLs.

The origin is derived from ``host_name`` only (``allow_header_override=False``),
because public URLs are printed into QR codes and NFC tags. These tests guard the
wiring that keeps generated URLs and QR images in sync after a domain change.
"""

import os
import unittest

APP_DIR = os.path.join(os.path.dirname(__file__), "..")


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


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


if __name__ == "__main__":
    unittest.main()
