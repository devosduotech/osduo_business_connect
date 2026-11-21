"""Behavioural tests for the subscription foundation using a minimal Frappe stub.

These run without a bench (the local test suite is pure Python) and cover the
regressions found in review: Single-DocType existence, Guest exclusion,
purchased seat caps, fresh-install fail-closed, and domain expiry syncing.
Frappe integration tests are added in phase 5 on a real bench.
"""

import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
SUB_DIR = os.path.join(APP_DIR, "subscription")


class FakeDB:
    def __init__(self):
        self.single = {}
        self.counts = {}
        self.count_calls = []
        self.created = []
        self.values = {}

    def exists(self, dt, dn=None):
        # Frappe v16 short-circuits dt == dn for Singles: they always "exist".
        if dt == "DocType":
            return True
        if dt == "Subscription":
            return True
        return False

    def get_single_value(self, dt, field):
        return self.single.get((dt, field))

    def count(self, dt, filters=None):
        self.count_calls.append((dt, filters))
        return self.counts.get(dt, 0)

    def get_value(self, dt, dn, field):
        return self.values.get((dt, dn, field))

    def sql(self, *args, **kwargs):
        return [(0,)]

    def commit(self):
        pass


class FakeDocument:
    def __init__(self, *args, **kwargs):
        data = args[0] if args and isinstance(args[0], dict) else dict(kwargs)
        self._data = dict(data)
        for key, value in data.items():
            setattr(self, key, value)
        self._new = not bool(data.get("name"))

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        if not key.startswith("_") and hasattr(self, "_data"):
            self._data[key] = value

    def __getattr__(self, key):
        # Real Frappe Documents return None for unset fields.
        return self._data.get(key)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        setattr(self, key, value)

    def append(self, key, value):
        # Frappe child rows are Documents, not plain dicts.
        if isinstance(value, dict) and not isinstance(value, FakeDocument):
            value = FakeDocument(value)
        self._data.setdefault(key, []).append(value)
        setattr(self, key, self._data[key])

    def is_new(self):
        return self._new

    def insert(self, **kwargs):
        self._inserted = True
        return self

    def save(self, **kwargs):
        self._saved = True
        return self


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class StubEnvironment:
    """Install a fake frappe package tree and load the real subscription modules."""

    def __enter__(self):
        self.original = dict(sys.modules)
        self.tmpdir = tempfile.mkdtemp(prefix="bc-subscription-test-")

        frappe = types.ModuleType("frappe")
        frappe.local = types.SimpleNamespace(site="test.local")
        frappe.flags = types.SimpleNamespace(in_test=True)
        frappe.conf = {
            "bc_upgrade_url": "https://example.com/upgrade",
            "bc_external_crm_enabled": 0,
        }
        frappe.db = FakeDB()
        frappe.session = types.SimpleNamespace(user="provider@example.com")
        cache_values = {}

        def cache_get(key):
            return cache_values.get(key)

        def cache_set(key, value, expires_in_sec=None):
            cache_values[key] = value

        frappe.cache = types.SimpleNamespace(
            get_value=cache_get, set_value=cache_set
        )
        frappe.form_dict = {}
        frappe.local.request = types.SimpleNamespace(
            path="/", method="GET", get_json=lambda silent=True: {}
        )
        frappe.ValidationError = type("ValidationError", (Exception,), {})
        frappe.PermissionError = type("PermissionError", (Exception,), {"http_status_code": 403})
        frappe.throw = lambda msg: (_ for _ in ()).throw(frappe.ValidationError(msg))
        frappe._ = lambda value: value
        frappe.get_doc = lambda *a, **k: FakeDocument(*a, **k)
        frappe.logger = lambda name=None: types.SimpleNamespace(
            info=lambda *a, **k: None
        )
        frappe.get_site_path = lambda *parts: os.path.join(self.tmpdir, *parts)

        utils = types.ModuleType("frappe.utils")
        utils.cint = lambda value: int(value or 0)
        utils.getdate = lambda value: value
        utils.today = lambda: "2026-01-01"
        utils.add_days = lambda start, days: "2027-01-01"
        utils.now_datetime = lambda: "2026-01-01 00:00:00"

        model = types.ModuleType("frappe.model")
        document = types.ModuleType("frappe.model.document")
        document.Document = FakeDocument
        model.document = document

        for name, module in (
            ("frappe", frappe),
            ("frappe.utils", utils),
            ("frappe.model", model),
            ("frappe.model.document", document),
        ):
            sys.modules[name] = module

        packages = {
            "osduo_business_connect": APP_DIR,
            "osduo_business_connect.subscription": SUB_DIR,
            "osduo_business_connect.patches": os.path.join(APP_DIR, "patches"),
            "osduo_business_connect.patches.v1_4": os.path.join(APP_DIR, "patches", "v1_4"),
            "osduo_business_connect.subscription.doctype": os.path.join(SUB_DIR, "doctype"),
            "osduo_business_connect.subscription.doctype.subscription": os.path.join(
                SUB_DIR, "doctype", "subscription"
            ),
        }
        for name, path in packages.items():
            package = types.ModuleType(name)
            package.__path__ = [path]
            sys.modules[name] = package

        self.constants = _load(
            "osduo_business_connect.subscription.constants",
            os.path.join(SUB_DIR, "constants.py"),
        )
        self.entitlements = _load(
            "osduo_business_connect.subscription.entitlements",
            os.path.join(SUB_DIR, "entitlements.py"),
        )
        self.provision = _load(
            "osduo_business_connect.subscription.provision",
            os.path.join(SUB_DIR, "provision.py"),
        )
        self.seed = _load(
            "osduo_business_connect.subscription.seed",
            os.path.join(SUB_DIR, "seed.py"),
        )
        self.patch = _load(
            "osduo_business_connect.patches.v1_4.seed_subscription_existing_sites",
            os.path.join(APP_DIR, "patches", "v1_4", "seed_subscription_existing_sites.py"),
        )
        self.controller = _load(
            "osduo_business_connect.subscription.doctype.subscription.subscription",
            os.path.join(SUB_DIR, "doctype", "subscription", "subscription.py"),
        )
        self.plan_gates = _load(
            "osduo_business_connect.subscription.plan_gates",
            os.path.join(SUB_DIR, "plan_gates.py"),
        )
        self.frappe = frappe
        return self

    def set_plan(self, plan_code):
        self.frappe.flags.in_test = True
        self.frappe.flags.bc_plan_override = plan_code
        self.entitlements.clear_entitlement_cache()

    def set_request(self, path, method="GET", payload=None, form=None):
        self.frappe.local.request = types.SimpleNamespace(
            path=path,
            method=method,
            get_json=lambda silent=True: payload or {},
        )
        self.frappe.form_dict = dict(form or {})
        self.entitlements.clear_entitlement_cache()

    def __exit__(self, *exc):
        sys.modules.clear()
        sys.modules.update(self.original)


class TestSingleDocTypeDetection(unittest.TestCase):
    def test_unprovisioned_site_fails_closed(self):
        with StubEnvironment() as env:
            ent = env.entitlements.get_entitlements()
            self.assertIsNone(env.entitlements.get_subscription())
            self.assertEqual(ent["plan_code"], "PROFESSIONAL")
            self.assertEqual(ent["source"], "fail_closed_default")
            self.assertFalse(ent["features"]["analytics"])

    def test_provisioned_site_uses_single_value_check(self):
        with StubEnvironment() as env:
            env.frappe.db.single[("Subscription", "plan")] = "BUSINESS"
            self.assertIsNotNone(env.entitlements.get_subscription())

    def test_purchased_seat_cap_overrides_plan_default(self):
        with StubEnvironment() as env:
            snapshot = env.constants.snapshot_defaults("BUSINESS")
            snapshot["captured_at"] = "2026-01-01"
            subscription = FakeDocument({
                "plan": "BUSINESS",
                "status": "Active",
                "seats_cap": 20,
                "entitlement_snapshot": json.dumps(snapshot),
            })
            env.frappe.db.single[("Subscription", "plan")] = "BUSINESS"
            original_get_doc = env.frappe.get_doc

            def get_doc(*args, **kwargs):
                if args == ("Subscription",):
                    return subscription
                return original_get_doc(*args, **kwargs)

            env.frappe.get_doc = get_doc
            env.entitlements.get_subscription.__globals__["frappe"].get_doc = get_doc

            ent = env.entitlements.get_entitlements()
            self.assertEqual(ent["limits"]["seat_cap"], 20)

    def test_plan_override_ignored_outside_tests(self):
        with StubEnvironment() as env:
            env.frappe.flags.in_test = False
            env.frappe.flags.bc_plan_override = "ENTERPRISE"
            ent = env.entitlements.get_entitlements()
            self.assertEqual(ent["plan_code"], "PROFESSIONAL")


class TestMigrationPatch(unittest.TestCase):
    def test_fresh_site_is_not_migrated(self):
        with StubEnvironment() as env:
            created = []
            original_get_doc = env.frappe.get_doc

            def get_doc(*args, **kwargs):
                doc = original_get_doc(*args, **kwargs)
                created.append(doc)
                return doc

            env.frappe.get_doc = get_doc
            env.patch.execute()
            subscriptions = [
                doc for doc in created if doc.get("doctype") == "Subscription"
            ]
            self.assertEqual(subscriptions, [])

    def test_guest_is_excluded_from_existing_user_check(self):
        with StubEnvironment() as env:
            env.frappe.db.counts = {"Business": 2, "User": 0}
            env.patch.execute()
            user_calls = [f for dt, f in env.frappe.db.count_calls if dt == "User"]
            self.assertTrue(user_calls)
            self.assertIn("not in", str(user_calls[0]["name"]))
            self.assertIn("Guest", str(user_calls[0]["name"][1]))

    def test_existing_site_gets_business_subscription(self):
        with StubEnvironment() as env:
            env.frappe.db.counts = {"Business": 2, "User": 0}
            created = []
            original_get_doc = env.frappe.get_doc

            def get_doc(*args, **kwargs):
                doc = original_get_doc(*args, **kwargs)
                created.append(doc)
                return doc

            env.frappe.get_doc = get_doc
            env.patch._write_site_config = lambda updates: updates
            env.patch.clear_entitlement_cache = lambda: None
            env.patch.execute()

            subscriptions = [
                doc for doc in created if doc.get("doctype") == "Subscription"
            ]
            self.assertEqual(len(subscriptions), 1)
            self.assertEqual(subscriptions[0].get("plan"), "BUSINESS")
            self.assertEqual(subscriptions[0].get("migrated"), 1)
            self.assertTrue(hasattr(subscriptions[0], "_inserted"))


class TestDomainExpiry(unittest.TestCase):
    def test_domain_expiry_follows_period_end(self):
        with StubEnvironment() as env:
            doc = env.controller.Subscription({
                "current_period_end": "2027-11-21",
                "seats_ordered": 5,
                "min_billed_seats": 5,
                "domain_mappings": [
                    FakeDocument({"hostname": "a.example.com", "status": "Active"}),
                    FakeDocument({"hostname": "b.example.com", "status": "Verified"}),
                    FakeDocument({"hostname": "c.example.com", "status": "Cancelled"}),
                ],
            })
            doc.validate()
            rows = doc.get("domain_mappings")
            self.assertEqual(rows[0].get("expires_on"), "2027-11-21")
            self.assertEqual(rows[1].get("expires_on"), "2027-11-21")
            self.assertIsNone(rows[2].get("expires_on"))


class TestPlanGates(unittest.TestCase):
    def suspend_site(self, env):
        snapshot = env.constants.snapshot_defaults("PROFESSIONAL")
        subscription = FakeDocument({
            "plan": "PROFESSIONAL",
            "status": "Suspended",
            "seats_cap": 1,
            "entitlement_snapshot": json.dumps(snapshot),
        })
        env.frappe.db.single[("Subscription", "plan")] = "PROFESSIONAL"
        original_get_doc = env.frappe.get_doc

        def get_doc(*args, **kwargs):
            if args == ("Subscription",):
                return subscription
            return original_get_doc(*args, **kwargs)

        env.frappe.get_doc = get_doc
        env.entitlements.clear_entitlement_cache()

    def assert_blocked(self, env, path, **kwargs):
        env.set_request(path, **kwargs)
        with self.assertRaises(env.frappe.PermissionError) as ctx:
            env.plan_gates.enforce_plan_gates()
        return str(ctx.exception)

    def assert_allowed(self, env, path, **kwargs):
        env.set_request(path, **kwargs)
        env.plan_gates.enforce_plan_gates()

    def test_professional_blocks_all_gated_surfaces(self):
        with StubEnvironment() as env:
            env.set_plan("PROFESSIONAL")
            for path in (
                "/crm",
                "/crm-form/crm-lead",
                "/api/method/crm.api.doc.get_data",
                "/analytics",
                "/api/method/osduo_business_connect.pages.analytics.get_analytics",
                "/app/data-import",
                "/app/data-export",
                "/api/resource/Data Export",
                "/api/method/frappe.core.doctype.data_import.data_import.form_start_import",
                "/api/method/frappe.desk.form.grid_import.parse_file",
                "/api/method/crm.api.settings.create_email_account",
                "/api/resource/CRM Lead",
                "/api/resource/Engagement Event",
                "/app/crm-lead",
                "/app/engagement-event",
                "/app/email-account",
            ):
                with self.subTest(path=path):
                    self.assert_blocked(env, path)

    def test_generic_client_methods_cannot_bypass_doctype_gates(self):
        with StubEnvironment() as env:
            env.set_plan("PROFESSIONAL")
            self.assert_blocked(
                env,
                "/api/method/frappe.client.get_list",
                form={"doctype": "CRM Deal"},
            )
            self.assert_blocked(
                env,
                "/api/method/frappe.client.get_list",
                payload={"doctype": "Engagement Event"},
            )
            self.assert_allowed(
                env,
                "/api/method/frappe.client.get_list",
                form={"doctype": "Business"},
            )

    def test_business_allows_crm_but_not_advanced_admin(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            for path in (
                "/crm",
                "/analytics",
                "/app/data-import",
                "/api/method/frappe.core.doctype.data_import.data_import.get_import_logs",
                "/api/resource/CRM Lead",
                "/api/resource/Engagement Event",
            ):
                self.assert_allowed(env, path)
            self.assert_blocked(env, "/api/method/crm.api.settings.create_email_account")
            self.assert_blocked(
                env,
                "/api/resource/Email Account",
                method="POST",
                payload={"email_id": "x@example.com"},
            )

    def test_enterprise_allows_everything(self):
        with StubEnvironment() as env:
            env.set_plan("ENTERPRISE")
            for path in (
                "/crm",
                "/analytics",
                "/app/data-import",
                "/api/method/crm.api.settings.create_email_account",
                "/api/resource/Email Account",
            ):
                self.assert_allowed(env, path, method="POST", payload={})

    def test_denial_message_carries_upgrade_url(self):
        with StubEnvironment() as env:
            env.set_plan("PROFESSIONAL")
            message = self.assert_blocked(env, "/crm")
            self.assertIn("https://example.com/upgrade", message)
            self.assertIn("Business", message)

    def test_api_key_generation_blocked_when_external_crm_off(self):
        with StubEnvironment() as env:
            env.set_plan("ENTERPRISE")
            self.assert_blocked(
                env, "/api/method/frappe.core.doctype.user.user.generate_keys"
            )
            env.frappe.conf["bc_external_crm_enabled"] = 1
            env.entitlements.clear_entitlement_cache()
            self.assert_allowed(
                env, "/api/method/frappe.core.doctype.user.user.generate_keys"
            )

    def test_direct_api_key_field_write_blocked(self):
        with StubEnvironment() as env:
            env.set_plan("ENTERPRISE")
            self.assert_blocked(
                env,
                "/api/resource/User/admin@example.com",
                method="PUT",
                payload={"api_secret": "leaked"},
            )
            self.assert_allowed(
                env,
                "/api/resource/User/admin@example.com",
                method="PUT",
                payload={"full_name": "Admin"},
            )

    def test_suspended_site_keeps_public_pages_live(self):
        with StubEnvironment() as env:
            self.suspend_site(env)
            self.assert_allowed(env, "/b/acme")
            self.assert_allowed(env, "/")
            self.assert_blocked(env, "/app/business")

    def test_suspended_site_blocks_token_style_api_requests(self):
        with StubEnvironment() as env:
            self.suspend_site(env)
            # before_request runs before token auth, so session.user may still
            # be Guest even for a request carrying a valid API key.
            env.frappe.session.user = "Guest"
            self.assert_allowed(env,
                "/api/method/osduo_business_connect.enquiry.public_enquiry_api.submit_enquiry"
            )
            self.assert_blocked(
                env, "/api/method/frappe.client.get_list", form={"doctype": "Business"}
            )
            self.assert_blocked(env, "/api/v2/document/Business")

    def test_rpc_cmd_cannot_smuggle_a_gated_method(self):
        with StubEnvironment() as env:
            env.set_plan("PROFESSIONAL")
            self.assert_blocked(
                env, "/api/method/frappe.ping", form={"cmd": "crm.api.doc.get_data"}
            )
            env.set_plan("ENTERPRISE")
            self.assert_blocked(
                env,
                "/api/method/frappe.ping",
                form={"cmd": "frappe.core.doctype.user.user.generate_keys"},
            )
            self.assert_allowed(env, "/api/method/frappe.ping", form={"cmd": "frappe.ping"})

    def test_versioned_api_routes_are_gated(self):
        with StubEnvironment() as env:
            env.set_plan("PROFESSIONAL")
            for path in (
                "/api/v1/method/crm.api.doc.get_data",
                "/api/v2/method/crm.api.doc.get_data",
                "/api/v1/resource/CRM Lead",
                "/api/v2/document/Engagement Event",
                "/api/v2/doctype/Data Import/meta",
                "/api/v2/document/Facebook Page",
            ):
                with self.subTest(path=path):
                    self.assert_blocked(env, path)

            env.set_plan("BUSINESS")
            for path in (
                "/api/v2/document/Email Account",
                "/api/v2/method/FCRM Settings/restore_defaults",
                "/api/v2/document/FCRM Settings/FCRM Settings/method/restore_defaults/",
                "/api/v2/mcp",
            ):
                with self.subTest(path=path):
                    self.assert_blocked(env, path)

            env.set_plan("ENTERPRISE")
            self.assert_allowed(env, "/api/v2/mcp")

    def test_desk_save_runner_carries_doctype_into_gate(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            self.assert_blocked(
                env,
                "/api/method/frappe.desk.form.save.savedocs",
                method="POST",
                payload={"doc": json.dumps({"doctype": "Email Account", "email_id": "x"})},
            )
            self.assert_allowed(
                env,
                "/api/method/frappe.desk.form.save.savedocs",
                method="POST",
                payload={"doc": json.dumps({"doctype": "Business", "business_name": "Acme"})},
            )

    def test_indirect_api_key_writes_are_blocked(self):
        with StubEnvironment() as env:
            env.set_plan("ENTERPRISE")
            self.assert_blocked(
                env,
                "/api/method/frappe.client.set_value",
                form={
                    "doctype": "User",
                    "name": "admin@example.com",
                    "fieldname": "api_secret",
                    "value": "leaked",
                },
            )
            self.assert_blocked(
                env,
                "/api/method/frappe.client.insert",
                payload={"doc": json.dumps({"doctype": "User", "api_key": "leaked"})},
            )

            # A Desk save that only echoes the existing credential is allowed.
            env.frappe.db.values[("User", "admin@example.com", "api_key")] = "existing"
            self.assert_allowed(
                env,
                "/api/method/frappe.desk.form.save.savedocs",
                method="POST",
                payload={
                    "doc": json.dumps({
                        "doctype": "User",
                        "name": "admin@example.com",
                        "api_key": "existing",
                    })
                },
            )

    def test_upgrade_url_html_is_escaped(self):
        with StubEnvironment() as env:
            env.frappe.conf["bc_upgrade_url"] = "https://example.com/up?a=1&b=2"
            env.entitlements.clear_entitlement_cache()
            env.set_plan("PROFESSIONAL")
            message = self.assert_blocked(env, "/crm")
            self.assertIn("View plans", message)
            self.assertIn("&amp;", message)

    def test_doctype_hook_never_returns_none(self):
        with StubEnvironment() as env:
            env.set_plan("PROFESSIONAL")
            gate = env.plan_gates.has_permission_for_doctype
            self.assertIs(
                gate(FakeDocument({"doctype": "Data Import"}), user="x", ptype="read"),
                False,
            )
            self.assertIs(
                gate(FakeDocument({"doctype": "Email Account"}), user="x", ptype="write"),
                False,
            )
            self.assertIs(
                gate(FakeDocument({"doctype": "Email Account"}), user="x", ptype="read"),
                False,
            )
            self.assertIs(
                gate(FakeDocument({"doctype": "CRM Fields Layout"}), user="x", ptype="read"),
                True,
            )
            self.assertEqual(env.plan_gates.import_export_query_conditions("x"), "1=0")
            self.assertEqual(env.plan_gates.advanced_admin_query_conditions("x"), "1=0")


if __name__ == "__main__":
    unittest.main()
