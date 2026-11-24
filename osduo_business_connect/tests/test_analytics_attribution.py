# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Offline wiring tests: one event per action, event/meeting as campaign.

The suite runs without a Frappe bench, so these check the source-level
contracts and the pure share-URL helper rather than database writes.
"""

import importlib.util
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


def load_share():
    path = os.path.join(APP_DIR, "utils", "share.py")
    spec = importlib.util.spec_from_file_location("bc_share_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSinglePageViewWriter(unittest.TestCase):
    """A card open creates exactly one card_view row."""

    def test_controller_does_not_write_card_view(self):
        source = read("templates", "pages", "card", "card.py")
        self.assertNotIn('"card_view"', source)
        self.assertIn('"shared_link_open"', source)

    def test_page_beacon_is_the_only_card_view_writer(self):
        html = read("templates", "pages", "card", "card.html")
        self.assertEqual(html.count("sendEvent('card_view')"), 1)
        self.assertIn("navigator.sendBeacon", html)

    def test_product_and_service_tiles_rely_on_destination_view(self):
        html = read("templates", "pages", "card", "card.html")
        self.assertNotIn('data-bc-event="product_view"', html)
        self.assertNotIn('data-bc-event="service_view"', html)

    def test_link_visits_exclude_funnel_events(self):
        source = read("analytics", "analytics_service.py")
        self.assertIn('page_views = ("card_view", "profile_view", "product_view", "service_view")', source)
        self.assertIn("AND event_type IN ({placeholders})", source)


class TestSingleEnquiryWriter(unittest.TestCase):
    """create_enquiry() records enquiry_submitted once for every path."""

    def test_card_page_no_longer_beacons_enquiry_submitted(self):
        html = read("templates", "pages", "card", "card.html")
        self.assertNotIn("sendEvent('enquiry_submitted')", html)
        self.assertIn("campaign: context.campaign", html)

    def test_enquiry_service_passes_the_stored_campaign(self):
        source = read("enquiry", "enquiry_service.py")
        self.assertIn("campaign=enquiry.campaign", source)
        self.assertIn("campaign=campaign or source", source)

    def test_client_endpoint_rejects_enquiry_submitted(self):
        source = read("analytics", "analytics_service.py")
        client_types = source.split("CLIENT_EVENT_TYPES = {", 1)[1].split("}", 1)[0]
        self.assertNotIn('"enquiry_submitted",', client_types)


class TestEventAsCampaign(unittest.TestCase):
    """Event / meeting from Share & Save Contact flows into Campaign."""

    def test_contact_exchange_campaign_and_share_link(self):
        source = read("card", "contact_exchange_api.py")
        self.assertIn("campaign=event_name or channel", source)
        self.assertIn("campaign=event_name or channel,", source)
        self.assertIn("def _attributed_url(url, channel, by_slug, campaign=None):", source)

    def test_view_events_read_inbound_campaign(self):
        for page in ("business/business.py", "product/product.py", "service/service.py"):
            source = read("templates", "pages", *page.split("/"))
            self.assertIn("get_share_campaign()", source, page)

    def test_build_share_url_emits_utm_campaign(self):
        share = load_share()
        url = share.build_share_url(
            "https://example.com/c/jane", "whatsapp", by="jane", campaign="Expo 2026"
        )
        self.assertIn("utm_source=whatsapp", url)
        self.assertIn("utm_medium=share", url)
        self.assertIn("by=jane", url)
        self.assertIn("utm_campaign=Expo+2026", url)

    def test_build_share_url_without_campaign_is_unchanged(self):
        share = load_share()
        url = share.build_share_url("https://example.com/c/jane", "sms", by="jane")
        self.assertNotIn("utm_campaign", url)


if __name__ == "__main__":
    unittest.main()
