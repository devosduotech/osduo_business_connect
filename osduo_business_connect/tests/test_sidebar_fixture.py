# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Offline checks for the standard Business Connect Desk sidebar fixture.

Frappe v16 imports ``<app>/<module>/sidebar/<name>/<name>.json`` as a standard
Sidebar document during install/migrate, so this file is what every new customer
site receives. Keeping the contract here prevents a developer-mode export from
silently reintroducing Desk routes that business customers must not see.
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
FIXTURE = os.path.join(
    APP_DIR, "business", "sidebar", "business_connect", "business_connect.json"
)

EXPECTED_LINKS = (
    ("Home", "Workspace", "Business Connect", None),
    ("Business", "DocType", "Business", None),
    ("Member", "DocType", "Business Member", None),
    ("Digital Card", "DocType", "Digital Card", None),
    ("Product", "DocType", "Showcase Product", None),
    ("Service", "DocType", "Showcase Service", None),
    ("Categories", "DocType", "Product Category", None),
    ("Enquiry", "DocType", "Enquiry", None),
    ("Theme", "DocType", "BC Theme", None),
    ("Card Event", "DocType", "Engagement Event", None),
    ("Team", "URL", None, "/portal/team"),
)


class TestBusinessConnectSidebarFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FIXTURE) as handle:
            cls.sidebar = json.load(handle)

    def test_fixture_is_a_standard_module_sidebar(self):
        self.assertEqual(self.sidebar["doctype"], "Sidebar")
        self.assertEqual(self.sidebar["standard"], 1)
        self.assertEqual(self.sidebar["app"], "osduo_business_connect")
        self.assertEqual(self.sidebar["module"], "Business")
        self.assertEqual(self.sidebar["name"], "Business Connect")
        self.assertEqual(self.sidebar["title"], "Business Connect")
        self.assertEqual(self.sidebar["header_icon"], "briefcase-business")

    def test_sidebar_items_are_the_standard_list_in_order(self):
        actual = tuple(
            (item["label"], item["link_type"], item.get("link_to"), item.get("url"))
            for item in self.sidebar["items"]
        )
        self.assertEqual(actual, EXPECTED_LINKS)

    def test_all_items_are_visible_links(self):
        for item in self.sidebar["items"]:
            self.assertEqual(item["type"], "Link")
            self.assertEqual(item["hidden"], 0)
            self.assertEqual(item["open_in_new_tab"], 1)

    def test_no_native_desk_or_admin_links(self):
        blocked_routes = {"/app", "/desk", "/desk/build"}
        blocked_doctypes = {"User", "Role", "Role Profile", "Invitation"}
        for item in self.sidebar["items"]:
            self.assertNotIn(item.get("url"), blocked_routes)
            self.assertNotIn(item.get("link_to"), blocked_doctypes)


if __name__ == "__main__":
    unittest.main()
