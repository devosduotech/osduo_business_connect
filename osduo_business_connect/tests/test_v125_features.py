# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
v1.2.5 structural tests.

These are intentionally offline checks: the suite runs without a Frappe bench,
so it verifies wiring, schema and source-level contracts rather than DB writes.
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(os.path.dirname(__file__), "..")


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return f.read()


def load_json(*parts):
    with open(os.path.join(APP_DIR, *parts)) as f:
        return json.load(f)


class TestShareBar(unittest.TestCase):
    """The reusable share bar must cover every channel and default to ref tokens."""

    def setUp(self):
        self.template = read("templates", "pages", "parts", "share_bar.html")

    def test_all_channels_present(self):
        for channel in ("wa.me", "sms:", "mailto:", "bc-card-share-link", "data-bc-native-share"):
            self.assertIn(channel, self.template)

    def test_ref_tokens_are_emitted(self):
        for ref in ("share_whatsapp", "share_sms", "share_email", "share_copy"):
            self.assertIn(ref, self.template)

    def test_share_by_slug_is_encoded(self):
        self.assertIn("share_by | urlencode", self.template)

    def test_included_by_all_public_templates(self):
        include = "osduo_business_connect/templates/pages/parts/share_bar.html"
        for page in ("business/business.html", "product/product.html",
                     "service/service.html", "card/card.html"):
            self.assertIn(include, read("templates", "pages", *page.split("/")), page)

    def test_controllers_publish_share_context(self):
        for page in ("business/business.py", "product/product.py",
                     "service/service.py", "card/card.py"):
            source = read("templates", "pages", *page.split("/"))
            for key in ("context.share_url", "context.share_by",
                        "context.share_title", "context.share_ref"):
                self.assertIn(key, source, f"{page} missing {key}")


class TestMyCard(unittest.TestCase):
    def test_files_exist(self):
        for rel in (("card", "my_card.py"), ("templates", "pages", "my_card.py"),
                    ("templates", "pages", "my-card.html"),
                    ("templates", "pages", "parts", "my_card_chip.html")):
            self.assertTrue(os.path.exists(os.path.join(APP_DIR, *rel)), os.path.join(*rel))

    def test_get_my_cards_is_whitelisted_and_guest_safe(self):
        source = read("card", "my_card.py")
        self.assertIn("@frappe.whitelist()", source)
        self.assertIn("def get_my_cards", source)
        self.assertIn('== "Guest"', source)
        self.assertIn("return []", source)
        self.assertIn("get_card_public_url", source)

    def test_only_cards_with_public_business_are_returned(self):
        source = read("card", "my_card.py")
        self.assertIn('"status": "Published"', source)
        self.assertIn('"public_profile_enabled": 1', source)
        self.assertIn("if not card.slug or not business:", source)

    def test_page_requires_login_and_disables_cache(self):
        source = read("templates", "pages", "my_card.py")
        self.assertIn("no_cache = 1", source)
        self.assertIn("Login required", source)
        self.assertIn("get_my_cards_for_user", source)

    def test_mycard_ref_is_used(self):
        self.assertIn("ref=mycard", read("templates", "pages", "my-card.html"))

    def test_entry_points_exist(self):
        self.assertIn("/my-card", read("public", "js", "branding.js"))
        self.assertIn("/my-card", read("templates", "pages", "analytics.html"))


class TestContactExchange(unittest.TestCase):
    def setUp(self):
        self.doctype = load_json("card", "doctype", "contact_exchange", "contact_exchange.json")
        self.controller = read("card", "doctype", "contact_exchange", "contact_exchange.py")
        self.api = read("card", "contact_exchange_api.py")

    def test_doctype_schema(self):
        self.assertEqual(self.doctype["module"], "Card")
        fieldnames = [f["fieldname"] for f in self.doctype["fields"]]
        for req in ("business", "card", "product", "service", "recipient_name",
                    "recipient_phone", "recipient_email", "channel",
                    "event_name", "exchanged_at", "user", "member", "status",
                    "linked_enquiry"):
            self.assertIn(req, fieldnames, req)
        # The CRM Lead lives on the Enquiry, not duplicated on the exchange.
        self.assertNotIn("crm_lead", fieldnames)

    def test_channel_options(self):
        channel = next(f for f in self.doctype["fields"] if f["fieldname"] == "channel")
        self.assertEqual(set(channel["options"].split("\n")),
                         {"WhatsApp", "SMS", "Email", "In-person"})

    def test_has_role_permissions(self):
        roles = {p["role"] for p in self.doctype["permissions"]}
        for role in ("BC Business Owner", "BC Business Manager",
                     "BC Business Member", "BC System Manager"):
            self.assertIn(role, roles)

    def test_permission_hooks_are_wired(self):
        for rel in (("permissions", "__init__.py"), ("hooks.py",)):
            source = read(*rel)
            self.assertIn("Contact Exchange", source, os.path.join(*rel))

    def test_controller_guards_and_normalization(self):
        for token in ("get_permission_query_conditions", "has_permission",
                      "normalize_phone", "validate_contact", "is_system_manager"):
            self.assertIn(token, self.controller, token)

    def test_api_is_login_only(self):
        self.assertIn("_require_login", self.api)
        self.assertIn("frappe.PermissionError", self.api)
        self.assertIn("record_contact_exchange", self.api)
        self.assertIn("get_contact_exchanges", self.api)
        self.assertIn("get_user_role_in_business", self.api)

    def test_exchange_creates_enquiry_with_valid_sources(self):
        """A shared contact is an Enquiry, created through the public service."""
        self.assertIn(
            "from osduo_business_connect.enquiry.enquiry_service import create_enquiry",
            self.api,
        )
        self.assertIn("def create_enquiry_from_exchange", self.api)
        self.assertIn("create_enquiry=1", self.api)
        self.assertIn('exchange.db_set("linked_enquiry"', self.api)

        enquiry_fields = {f["fieldname"]: f for f in
                          load_json("enquiry", "doctype", "enquiry", "enquiry.json")["fields"]}
        sources = set(enquiry_fields["source"]["options"].split("\n"))
        mapping = self.api.split("ENQUIRY_SOURCES = {", 1)[1].split("}", 1)[0]
        mapping += self.api.split("DEFAULT_ENQUIRY_SOURCE = ", 1)[1].split("\n", 1)[0]
        for value in ("Digital Card", "Product", "Service", "Business Profile"):
            self.assertIn(value, mapping, value)
            self.assertIn(value, sources, f"{value} is not an Enquiry.source option")

    def test_enquiry_failures_never_lose_the_exchange(self):
        source = self.api.split("def create_enquiry_from_exchange", 1)[1]
        self.assertIn("except Exception", source)
        self.assertIn("frappe.log_error", source)
        self.assertIn("del frappe.local.message_log[message_count:]", source)

    def test_by_prefers_the_sharers_own_card(self):
        self.assertIn("get_user_card_slug", self.api)
        self.assertIn("sharer or business_row.slug", self.api)
        self.assertIn("def get_user_card_slug", read("card", "my_card.py"))

    def test_api_uses_canonical_urls_and_refs(self):
        self.assertIn("get_card_public_url", self.api)
        self.assertIn("get_business_public_url", self.api)
        for ref in ("share_whatsapp", "share_sms", "share_email"):
            self.assertIn(ref, self.api)

    def test_share_targets_must_be_publicly_reachable(self):
        self.assertIn("def _require_shareable", self.api)
        self.assertIn("has no public link yet", self.api)
        self.assertIn("is not published yet", self.api)
        self.assertIn("is not publicly visible", self.api)
        for field in ("status", "public_profile_enabled"):
            self.assertIn(field, self.api)

    def test_contact_exchange_logs_analytics_event(self):
        self.assertIn('"contact_exchanged"', self.api)

    def test_form_is_login_gated(self):
        form = read("templates", "pages", "parts", "contact_exchange_form.html")
        self.assertIn("{% if show_my_card %}", form)
        self.assertIn("record_contact_exchange", form)

    def test_form_offers_the_enquiry_option(self):
        form = read("templates", "pages", "parts", "contact_exchange_form.html")
        self.assertIn('name="create_enquiry" value="1" checked', form)
        self.assertIn("create_enquiry: data.get(\"create_enquiry\") ? 1 : 0", form)
        self.assertNotIn("create_lead", form)
        self.assertIn("result.message.enquiry", form)


class TestShareAttribution(unittest.TestCase):
    def setUp(self):
        self.source = read("utils", "share.py")

    def test_whitelist_values(self):
        for ref in ("share_whatsapp", "share_sms", "share_email", "share_copy", "mycard"):
            self.assertIn(ref, self.source)

    def test_unknown_refs_are_dropped(self):
        self.assertIn("return ref if ref in SHARE_REFS else None", self.source)

    def test_shared_link_open_is_logged(self):
        for page in ("business/business.py", "product/product.py",
                     "service/service.py", "card/card.py"):
            source = read("templates", "pages", *page.split("/"))
            self.assertIn('"shared_link_open"', source, page)
            self.assertIn("get_share_ref", source, page)
            self.assertIn("get_share_by", source, page)
            self.assertIn("shared_by=share_by", source, page)


class TestVisitorClassification(unittest.TestCase):
    def setUp(self):
        self.tracking = read("analytics", "tracking.py")
        self.event_json = load_json("analytics", "doctype", "engagement_event", "engagement_event.json")
        self.event_py = read("analytics", "doctype", "engagement_event", "engagement_event.py")
        self.service = read("analytics", "analytics_service.py")

    def test_classify_visitor_labels(self):
        self.assertIn("def classify_visitor", self.tracking)
        for label in ("Guest", "Owner", "Member", "Other User", "Unknown"):
            self.assertIn(f'"{label}"', self.tracking)

    def test_visitor_fields_on_event(self):
        fields = {f["fieldname"]: f for f in self.event_json["fields"]}
        self.assertIn("visitor_type", fields)
        self.assertIn("visitor_user", fields)
        self.assertIn("shared_by", fields)
        self.assertEqual(fields["visitor_type"]["options"].split("\n"),
                         ["Guest", "Owner", "Member", "Other User", "Unknown"])
        self.assertEqual(fields["visitor_user"].get("hidden"), 1)
        self.assertEqual(fields["shared_by"].get("hidden"), 1)

    def test_background_job_receives_classification(self):
        self.assertIn('kwargs.get("visitor_type")', self.service)
        self.assertIn('kwargs.get("visitor_user")', self.service)
        self.assertIn('kwargs.get("shared_by")', self.service)

    def test_no_internal_filter_keeps_legacy_rows(self):
        self.assertIn("COALESCE(", self.service)
        self.assertIn("NOT IN ('Owner', 'Member')", self.service)
        self.assertIn("exclude_internal", self.service)
        self.assertIn("events_by_visitor", self.service)

    def test_new_event_types_allowed(self):
        options = next(f for f in self.event_json["fields"]
                       if f["fieldname"] == "event_type")["options"].split("\n")
        self.assertIn("shared_link_open", options)
        self.assertIn("contact_exchanged", options)
        self.assertIn('"shared_link_open"', self.event_py)
        self.assertIn('"contact_exchanged"', self.event_py)

    def test_attribution_events_are_server_only(self):
        client_types = self.service.split("CLIENT_EVENT_TYPES = {", 1)[1].split("}", 1)[0]
        self.assertNotIn("shared_link_open", client_types)
        self.assertNotIn("contact_exchanged", client_types)


if __name__ == "__main__":
    unittest.main()
