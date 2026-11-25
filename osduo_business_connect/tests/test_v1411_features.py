# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Offline regression checks for Share & Connect (v1.4.11).

The suite has no Frappe bench, so these tests verify the source-level contracts
that protect the release: schema, API compatibility, idempotency, transaction
boundaries, cache-safe endpoints, status reconciliation and migration safety.
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from osduo_business_connect.utils.seo import json_for_script

APP_DIR = os.path.join(os.path.dirname(__file__), "..")


def read(*parts):
    with open(os.path.join(APP_DIR, *parts)) as handle:
        return handle.read()


def load_json(*parts):
    with open(os.path.join(APP_DIR, *parts)) as handle:
        return json.load(handle)


def fields(*parts):
    return {field["fieldname"]: field for field in load_json(*parts)["fields"]}


class TestSchemaChanges(unittest.TestCase):
    """Exactly 13 fields across the three approved DocTypes."""

    def test_contact_exchange_fields(self):
        exchange = fields("card", "doctype", "contact_exchange", "contact_exchange.json")
        self.assertEqual(
            set(exchange) & {
                "shared_content_type", "request_id", "idempotency_key",
                "enquiry_error", "enquiry_requested",
            },
            {
                "shared_content_type", "request_id", "idempotency_key",
                "enquiry_error", "enquiry_requested",
            },
        )
        self.assertEqual(exchange["shared_content_type"]["fieldtype"], "Select")
        self.assertEqual(
            exchange["shared_content_type"]["options"], "Card\nBusiness\nProduct\nService"
        )
        self.assertTrue(exchange["idempotency_key"].get("unique"))
        self.assertTrue(exchange["idempotency_key"].get("set_only_once"))
        self.assertTrue(exchange["request_id"].get("no_copy"))
        self.assertEqual(exchange["enquiry_error"]["fieldtype"], "Small Text")
        self.assertEqual(exchange["enquiry_requested"]["fieldtype"], "Check")
        self.assertEqual(exchange["enquiry_requested"].get("default"), 0)

    def test_enquiry_fields(self):
        enquiry = fields("enquiry", "doctype", "enquiry", "enquiry.json")
        self.assertEqual(enquiry["enquiry_origin"]["fieldtype"], "Select")
        self.assertEqual(
            enquiry["enquiry_origin"]["options"], "Website Form\nContact Exchange\nUnknown"
        )
        self.assertEqual(enquiry["contact_exchange"]["options"], "Contact Exchange")
        self.assertEqual(enquiry["shared_by"]["options"], "User")
        self.assertTrue(enquiry["contact_exchange"].get("read_only"))
        self.assertTrue(enquiry["shared_by"].get("read_only"))

    def test_crm_custom_fields_are_registered(self):
        install = read("install.py")
        for fieldname in (
            "osduo_shared_content_type", "osduo_shared_by", "osduo_share_channel",
            "osduo_share_event", "osduo_enquiry_origin",
        ):
            self.assertIn(f'"{fieldname}"', install, fieldname)
            self.assertIn(f'"fieldname": "{fieldname}"', install, fieldname)
        self.assertIn("osduo_attribution", install)
        self.assertIn("OSDUO_CRM_FIELDNAMES", install)

    def test_migration_patch_is_registered(self):
        patches = read("patches.txt")
        self.assertIn("contact_exchange_attribution_backfill", patches)
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    APP_DIR, "patches", "v1_4", "contact_exchange_attribution_backfill.py"
                )
            )
        )


class TestApiContract(unittest.TestCase):
    def setUp(self):
        self.api = read("card", "contact_exchange_api.py")

    def test_positional_signature_is_preserved(self):
        self.assertIn("def record_contact_exchange(", self.api)
        signature = self.api.split("def record_contact_exchange(", 1)[1].split("):", 1)[0]
        self.assertLess(signature.index("business=None"), signature.index("card=None"))
        self.assertLess(signature.index("service=None"), signature.index("recipient_name=None"))
        self.assertLess(signature.index("create_enquiry=1"), signature.index("shared_content_type=None"))
        self.assertLess(signature.index("shared_content_type=None"), signature.index("request_id=None"))
        self.assertTrue(signature.rstrip().endswith("request_id=None,"))

    def test_discriminator_and_legacy_precedence(self):
        self.assertIn("def _normalize_content_type", self.api)
        self.assertIn("def _resolve_content_type", self.api)
        self.assertIn("Invalid shared content type", self.api)
        self.assertIn("Selected content does not match the supplied document", self.api)
        self.assertIn("Business sharing cannot include a card, product or service reference", self.api)
        self.assertIn("# Legacy compatibility: infer from the single populated typed reference", self.api)

    def test_idempotent_legacy_result_resolves_content_type_by_keywords(self):
        # Legacy exchange rows have NULL shared_content_type; the idempotent
        # response builder must not shift card/product/service into the wrong
        # keyword arguments.
        self.assertIn(
            "_resolve_content_type(\n        None, exchange.card, exchange.product, exchange.service\n    )",
            self.api,
        )

    def test_idempotency_handles_race_and_conflict(self):
        self.assertIn("def _idempotency_key", self.api)
        self.assertIn('sha256(f"{user}:{request_id}"', self.api)
        self.assertIn("def _existing_exchange_by_key", self.api)
        self.assertIn("def _payload_matches", self.api)
        self.assertIn('["http_status_code"] = 409', self.api)
        self.assertIn("A concurrent request may have won the unique-key race", self.api)
        self.assertIn("return _result_from_exchange(existing, idempotent=True)", self.api)

    def test_transaction_boundary_keeps_exchange(self):
        self.assertIn("frappe.db.savepoint(savepoint)", self.api)
        self.assertIn("frappe.db.rollback(save_point=savepoint)", self.api)
        self.assertIn("frappe.db.release_savepoint(savepoint)", self.api)
        self.assertIn("frappe.db.commit()", self.api)
        self.assertIn("Exception:", self.api)
        self.assertIn("str(exc)[:500]", self.api)

    def test_no_enquiry_when_unchecked(self):
        self.assertIn("wants_enquiry = str(create_enquiry).lower()", self.api)
        self.assertIn("if wants_enquiry:", self.api)
        self.assertIn("if _has_field(exchange, \"enquiry_requested\")", self.api)
        self.assertIn("exchange.enquiry_requested = 1 if wants_enquiry else 0", self.api)

    def test_attribution_and_fixed_templates(self):
        self.assertIn('"enquiry_origin": "Contact Exchange"', self.api)
        self.assertIn('"contact_exchange": exchange.name', self.api)
        self.assertIn('"shared_by": exchange.user', self.api)
        self.assertIn("Please find my digital business card below.", self.api)
        self.assertIn("Please find our business profile, products and services", self.api)
        self.assertIn("Feel free to contact me for further information.", self.api)
        bodies = self.api.split("MESSAGE_BODIES = {", 1)[1].split("}\n", 1)[0]
        self.assertNotIn("As discussed", bodies)
        self.assertNotIn("Nice connecting", bodies)
        self.assertIn("Hi {recipient_name},\\n\\n", self.api)

    def test_targets_are_server_resolved_and_scoped(self):
        self.assertIn("def resolve_share_target", self.api)
        self.assertIn('{"name": card, "business": business}', self.api)
        self.assertIn('{"name": product, "business": business}', self.api)
        self.assertIn('{"name": service, "business": business}', self.api)
        self.assertIn("get_user_card_slug(business, user)", self.api)
        self.assertIn("def _require_shareable", self.api)

    def test_enquiry_service_supports_shared_commit_boundary(self):
        service = read("enquiry", "enquiry_service.py")
        self.assertIn("commit=True):", service)
        self.assertIn("if commit:\n        frappe.db.commit()", service)
        self.assertIn('references.get("enquiry_origin") or "Website Form"', service)
        self.assertIn('references.get("contact_exchange")', service)
        self.assertIn('references.get("shared_by")', service)

    def test_controller_mirrors_validation(self):
        controller = read("card", "doctype", "contact_exchange", "contact_exchange.py")
        self.assertIn("self.validate_shared_target()", controller)
        self.assertIn("def validate_shared_target", controller)
        self.assertIn("Shared content has no public link yet", controller)
        self.assertIn("Selected content does not match the shared reference", controller)


class TestRecoveryAndStatus(unittest.TestCase):
    def test_failed_enquiry_recovery_is_scoped(self):
        recovery = read("card", "enquiry_recovery.py")
        self.assertIn("enquiry_requested = 1", recovery)
        self.assertIn("linked_enquiry IS NULL OR linked_enquiry = ''", recovery)
        self.assertIn("_existing_enquiry_for_exchange", recovery)
        self.assertIn('{"contact_exchange": exchange_name}', recovery)
        self.assertIn("enquiry_error\", None", recovery)
        self.assertIn("FOR UPDATE", recovery)
        self.assertIn("recovered = retry(limit=100)", read("services", "scheduler.py"))

    def test_status_mapping_contract(self):
        status = read("crm_integration", "status_reconciliation.py")
        self.assertIn('"Nurture": "Contacted"', status)
        self.assertIn('"Unqualified": "Archived"', status)
        self.assertIn('"Junk": "Archived"', status)
        self.assertIn("if converted:\n        return \"Converted\", \"Converted\"", status)
        for name in (
            "map_crm_status", "sync_from_crm_lead",
            "sync_contact_exchange_from_enquiry", "reconcile_statuses",
        ):
            self.assertIn(f'"{name}"', status)

    def test_hourly_reconciliation_is_wired(self):
        scheduler = read("services", "scheduler.py")
        self.assertIn("def hourly_tasks", scheduler)
        self.assertIn("reconcile_share_connect_statuses()", scheduler)
        self.assertIn("retry_failed_enquiry_creation()", scheduler)
        self.assertIn("reconcile_statuses(limit=200)", scheduler)
        hooks = read("hooks.py")
        self.assertIn('"hourly": [', hooks)
        self.assertIn("services.scheduler.hourly_tasks", hooks)
        self.assertIn("crm_integration.crm_lead_hook.on_crm_lead_update", hooks)

    def test_enquiry_hook_syncs_exchange(self):
        core = read("enquiry", "core.py")
        self.assertIn("sync_contact_exchange_from_enquiry", core)
        self.assertIn("Contact Exchange Status Sync Failed", core)

    def test_lead_mapper_maps_all_five_fields(self):
        mapper = read("crm_integration", "lead_mapper.py")
        for fieldname in (
            "osduo_shared_content_type", "osduo_shared_by", "osduo_share_channel",
            "osduo_share_event", "osduo_enquiry_origin",
        ):
            self.assertIn(f'"{fieldname}"', mapper, fieldname)
        self.assertIn("Share & Connect enquiries belong to the sender", mapper)
        self.assertIn("_card_owner_user(enquiry_doc)", mapper)


class TestCacheSafeReadEndpoints(unittest.TestCase):
    def test_manifest_contract(self):
        manifest = read("card", "share_manifest_api.py")
        self.assertIn(
            "def get_share_manifest(business=None, page_type=None, document=None):", manifest
        )
        self.assertIn(
            "@frappe.whitelist(allow_guest=True, methods=[\"GET\"])", manifest
        )
        self.assertIn('"Cache-Control", "private, no-store, max-age=0"', manifest)
        self.assertIn('"Pragma", "no-cache"', manifest)
        self.assertIn('"Expires", "0"', manifest)
        self.assertIn('"can_record_exchange"', manifest)
        self.assertIn('"my_card_available"', manifest)
        self.assertIn('"default_key"', manifest)
        self.assertIn('"items"', manifest)
        self.assertIn('"csrf_token"', manifest)
        self.assertIn("csrf_token", manifest)
        self.assertIn("get_user_card_slug", manifest)
        # A stale or guest request must return a safe empty manifest, never a
        # 404 that hides the whole section and leaves no diagnostics.
        self.assertIn("def _business_key(value):", manifest)
        self.assertIn('{"slug": value.lower()}, "name"', manifest)
        # Callers may pass a Business slug; normalize to the canonical name
        # before membership, card and showcase lookups.
        self.assertIn("business = business_key", manifest)
        self.assertIn("def _empty_manifest():", manifest)
        self.assertIn("return _empty_manifest()", manifest)
        # Business has no child document ID, so it must not be skipped by the
        # shared target resolver guard.
        self.assertIn('if kind != "Business" and not document:', manifest)
        self.assertNotIn('frappe.throw(_("Business not found")', manifest)

    def test_share_ui_uses_theme_tokens(self):
        css = read("public", "css", "branding.css")
        section = css.split("9. SHARE & CONNECT", 1)[1]
        for token in (
            "--bc-font-family",
            "--bc-surface",
            "--bc-border-color",
            "--bc-text-strong",
            "--bc-primary-fill",
            "--bc-primary-text",
            "--bc-on-primary",
            "--bc-primary-soft",
            "--bc-radius-sm",
            "--bc-radius-md",
            "--bc-card-shadow",
        ):
            self.assertIn(token, section, token)
        # A filled primary button needs --bc-on-primary. --bc-primary-text is
        # designed for primary text on a surface and disappears on the fill.
        active = section.split('.bc-sc-type[aria-pressed="true"] {', 1)[1]
        active = active.split("}", 1)[0]
        self.assertIn("color: var(--bc-on-primary", active)
        self.assertNotIn("--bc-primary-text", active)
        chip = section.split(".bc-my-card-chip {", 1)[1].split("}", 1)[0]
        self.assertIn("color: var(--bc-on-primary", chip)
        self.assertNotIn("--bc-primary-text", chip)

        shell = read("templates", "pages", "parts", "share_connect.html")
        form = read("templates", "pages", "parts", "contact_exchange_form.html")
        self.assertIn("bc-sc-title bc-card-section-title", shell)
        self.assertIn("bc-ce-title bc-card-section-title", form)

    def test_qr_contract(self):
        qr = read("card", "qr_api.py")
        self.assertIn("def get_share_qr(doctype=None, name=None):", qr)
        self.assertIn(
            "@frappe.whitelist(allow_guest=True, methods=[\"GET\"])", qr
        )
        for doctype in ("Digital Card", "Business", "Showcase Product", "Showcase Service"):
            self.assertIn(f'"{doctype}"', qr, doctype)
        self.assertIn("f\"{doctype}|{name}|{url_hash}\"", qr)
        self.assertIn("sha256(url.encode", qr)
        self.assertIn("qr_enabled", qr)
        # Frappe v16 exposes frappe.cache as an object, not a callable.
        self.assertIn("def _get_cache():", qr)
        self.assertIn("return cache() if callable(cache) else cache", qr)
        self.assertNotIn("frappe.cache()", qr)
        # A public read endpoint must not create File rows or write to disk.
        self.assertNotIn('"File"', qr)
        self.assertNotIn("frappe.get_doc", qr)
        self.assertIn("data:image/png;base64,", qr)

    def test_endpoints_are_in_both_allowlists(self):
        gates = read("subscription", "plan_gates.py")
        for method in ("share_manifest_api.get_share_manifest", "qr_api.get_share_qr"):
            self.assertEqual(gates.count(method), 2, method)

    def test_cached_public_templates_are_stateless(self):
        parts = (
            "templates", "pages", "parts",
        )
        for name in ("share_connect.html", "contact_exchange_form.html", "my_card_chip.html"):
            source = read(*parts, name)
            self.assertNotIn("frappe.session", source, name)
            self.assertNotIn("data-token=", source, name)
            self.assertNotIn('{% if show_my_card %}', source, name)
        for name in ("card/card.html", "card/team_member.html",
                     "business/business.html", "product/product.html",
                     "service/service.html"):
            source = read("templates", "pages", *name.split("/"))
            self.assertNotIn("frappe.session", source, name)
            self.assertNotIn("bc-csrf-token", source, name)
            self.assertNotIn("data-token=", source, name)
        for name in ("card/card.py", "card/team_member.py", "business/business.py",
                     "product/product.py", "service/service.py"):
            source = read("templates", "pages", *name.split("/"))
            self.assertNotIn("frappe.session", source, name)

    def test_shell_defers_personalisation_to_the_manifest(self):
        shell = read("templates", "pages", "parts", "share_connect.html")
        for marker in ("data-bc-share-config", "json_for_script", "qrGeneration",
                       "bc:share-manifest", "can_record_exchange", "bindShareBar"):
            self.assertIn(marker, shell)
        self.assertIn("csrf_token: state.csrfToken", shell)
        self.assertNotIn("updateShareBar", shell)
        self.assertNotIn("getSelection", shell)
        share_bar = read("templates", "pages", "parts", "share_bar.html")
        self.assertNotIn("share_qr", share_bar)

    def test_contact_exchange_uses_manifest_csrf_token(self):
        form = read("templates", "pages", "parts", "contact_exchange_form.html")
        self.assertIn("detail.csrf_token", form)
        self.assertIn("csrfToken", form)
        self.assertIn("X-Frappe-CSRF-Token", form)
        # Read calls are GET-only; frappe.xcall would send POST and be rejected.
        shell = read("templates", "pages", "parts", "share_connect.html")
        self.assertNotIn("frappe.xcall", shell)
        self.assertIn("fetch(url", shell)
        self.assertIn('method: "GET"', shell)
        self.assertIn('credentials: "same-origin"', shell)
        self.assertIn("hidden>", form)
        self.assertIn("create_enquiry: wantsEnquiry", form)
        self.assertNotIn("enquiry_requested: wantsEnquiry", form)

    def test_contact_form_defaults_to_india_country_code(self):
        form = read("templates", "pages", "parts", "contact_exchange_form.html")
        self.assertIn('name="recipient_phone_code"', form)
        self.assertIn('<option value="+91" selected>IN +91</option>', form)
        self.assertIn('var phoneCode = (data.get("recipient_phone_code") || "+91").trim();', form)
        self.assertIn("phoneCode + phoneLocal", form)

    def test_workspace_has_default_share_and_connect_shortcuts(self):
        workspace = load_json(
            "business", "workspace", "business_connect", "business_connect.json"
        )
        labels = {item["label"] for item in workspace["shortcuts"]}
        self.assertIn("My Card", labels)
        self.assertIn("Contact Exchanges", labels)
        self.assertIn("My Card", workspace["content"])
        self.assertIn("Contact Exchanges", workspace["content"])
        self.assertGreater(workspace["modified"], "2026-11-25 00:00:00")

        my_card = load_json("business", "workspace", "my_card", "my_card.json")
        self.assertEqual(my_card["type"], "URL")
        self.assertEqual(my_card["external_link"], "/my-card")
        contact_exchanges = load_json(
            "business", "workspace", "contact_exchanges", "contact_exchanges.json"
        )
        self.assertEqual(contact_exchanges["type"], "Link")
        self.assertEqual(contact_exchanges["link_to"], "Contact Exchange")

        sidebar = load_json(
            "business", "sidebar", "business_connect", "business_connect.json"
        )
        sidebar_items = {item["label"]: item for item in sidebar["items"]}
        self.assertIn("My Card", sidebar_items)
        self.assertEqual(sidebar_items["My Card"]["link_type"], "URL")
        self.assertEqual(sidebar_items["My Card"]["url"], "/my-card")
        self.assertIn("Contact Exchanges", sidebar_items)
        self.assertEqual(sidebar_items["Contact Exchanges"]["link_type"], "DocType")
        self.assertEqual(sidebar_items["Contact Exchanges"]["link_to"], "Contact Exchange")
        self.assertGreater(sidebar["modified"], "2026-11-25 00:00:00")

        install = read("install.py")
        self.assertIn("def ensure_business_connect_workspace_shortcuts", install)
        self.assertIn("def ensure_business_connect_sidebar_links", install)
        self.assertIn("def ensure_business_connect_sidebar_items", install)
        self.assertIn("ensure_business_connect_workspace_shortcuts()", install)
        self.assertIn("ensure_business_connect_sidebar_links()", install)
        self.assertIn("ensure_business_connect_sidebar_items()", install)

    def test_serializer_neutralises_script_breakout(self):
        payload = {"title": "</script><script>alert(1)</script>\u2028&>"}
        encoded = json_for_script(payload)
        self.assertNotIn("<", encoded)
        self.assertNotIn(">", encoded)
        self.assertNotIn("&", encoded)
        self.assertNotIn("\u2028", encoded)
        self.assertIn("\\u003c", encoded)
        self.assertIn("\\u003e", encoded)
        self.assertIn("\\u0026", encoded)
        self.assertEqual(json.loads(encoded), payload)


class TestMigrationSafety(unittest.TestCase):
    def setUp(self):
        self.patch = read("patches", "v1_4", "contact_exchange_attribution_backfill.py")

    def test_classifies_only_unambiguous_rows(self):
        self.assertIn("if len(typed) > 1:", self.patch)
        self.assertIn("cannot be classified", self.patch)
        self.assertIn("typed[0]", self.patch)
        self.assertIn('"Business"', self.patch)

    def test_backfill_is_one_to_one_and_non_destructive(self):
        self.assertIn("if counts[exchange.linked_enquiry] == 1", self.patch)
        self.assertIn("if not enquiry.contact_exchange", self.patch)
        self.assertIn("if not enquiry.enquiry_origin", self.patch)
        self.assertIn('"Unknown"', self.patch)
        self.assertIn("update_modified=False", self.patch)

    def test_historical_crm_leads_are_untouched(self):
        self.assertNotIn('"CRM Lead"', self.patch)
        self.assertIn("CRM Leads are deliberately left alone", self.patch)


class TestVersionAndReleaseWiring(unittest.TestCase):
    def test_version_and_revisions_are_bumped(self):
        self.assertIn('__version__ = "1.4.12"', read("__init__.py"))
        self.assertIn('BC_ASSET_REVISION = "2026-11-24-share-connect-v1412"', read("hooks.py"))
        self.assertIn('"2026-11-24-share-connect-v1412"', read("www", "sw.py"))

    def test_docs_and_release_notes_are_updated(self):
        spec = read("..", "docs", "SHARE_AND_CONNECT_SPEC.md")
        self.assertIn("**Version:** 0.3.1", spec)
        self.assertIn("T44", spec)
        notes = read("..", "RELEASE_NOTES.md")
        self.assertIn("# Release Notes - business_connect (v1.4.12)", notes)
        self.assertIn("**Release:** v1.4.12.", notes)
        manual = read("..", "docs", "USER_MANUAL.md")
        self.assertIn("Save as an Enquiry (goes to CRM)", manual)


if __name__ == "__main__":
    unittest.main()
