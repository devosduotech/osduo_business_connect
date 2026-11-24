"""Behavioural tests for the subscription foundation using a minimal Frappe stub.

These run without a bench (the local test suite is pure Python) and cover the
regressions found in review: Single-DocType existence, Guest exclusion,
purchased seat caps, fresh-install fail-closed, and domain expiry syncing.
Frappe integration tests are added in phase 5 on a real bench.
"""

import importlib.util
import json
import os
import re
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

    def set_value(self, dt, dn, field, value=None, **kwargs):
        updates = field if isinstance(field, dict) else {field: value}
        for key, item in updates.items():
            self.values[(dt, dn, key)] = item

    def set_single_value(self, dt, field, value, **kwargs):
        self.single[(dt, field)] = value

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
        self.roles_by_user = {}
        self.memberships = {}
        self.get_all_rows = {}

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
        def throw(msg, exc=None, **kwargs):
            raise (exc or frappe.ValidationError)(msg)

        frappe.throw = throw
        frappe._ = lambda value: value
        frappe.get_doc = lambda *a, **k: FakeDocument(*a, **k)
        frappe.whitelist = lambda *a, **k: (lambda fn: fn)

        def get_roles(user=None):
            user = user or frappe.session.user
            return list(self.roles_by_user.get(user, []))

        def get_all(doctype, filters=None, fields=None, **kwargs):
            return list(self.get_all_rows.get(doctype, []))

        frappe.get_roles = get_roles
        frappe.get_all = get_all
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

        # Minimal stand-in for business.core: invitation tests only need these
        # two scope helpers, and loading the real controller would pull in the
        # whole publishing/sanitisation stack.
        business_core = types.ModuleType("osduo_business_connect.business.core")

        def get_user_role_in_business(user, business):
            return self.memberships.get((user, business))

        def get_user_businesses(user):
            return [
                {"name": business, "role": role}
                for (member, business), role in self.memberships.items()
                if member == user
            ]

        business_core.get_user_role_in_business = get_user_role_in_business
        business_core.get_user_businesses = get_user_businesses
        sys.modules["osduo_business_connect.business.core"] = business_core

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
        self.limits = _load(
            "osduo_business_connect.subscription.limits",
            os.path.join(SUB_DIR, "limits.py"),
        )
        self.domains = _load(
            "osduo_business_connect.subscription.domains",
            os.path.join(SUB_DIR, "domains.py"),
        )
        self.subscription_page = _load(
            "osduo_business_connect.subscription.subscription_page",
            os.path.join(SUB_DIR, "subscription_page.py"),
        )
        self.team_invite = _load(
            "osduo_business_connect.subscription.team_invite",
            os.path.join(SUB_DIR, "team_invite.py"),
        )
        self.portal_nav = _load(
            "osduo_business_connect.subscription.portal_nav",
            os.path.join(SUB_DIR, "portal_nav.py"),
        )
        self.addon_order = _load(
            "osduo_business_connect.subscription.doctype.add_on_order.add_on_order",
            os.path.join(
                SUB_DIR, "doctype", "add_on_order", "add_on_order.py"
            ),
        )
        self.addon_master = _load(
            "osduo_business_connect.subscription.doctype.add_on_master.add_on_master",
            os.path.join(
                SUB_DIR, "doctype", "add_on_master", "add_on_master.py"
            ),
        )
        self.frappe = frappe
        return self

    def set_plan(self, plan_code):
        self.frappe.flags.in_test = True
        self.frappe.flags.bc_plan_override = plan_code
        self.entitlements.clear_entitlement_cache()

    def set_roles(self, *roles, user=None):
        self.roles_by_user[user or self.frappe.session.user] = list(roles)

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

    def test_v16_desk_routes_are_gated(self):
        # Frappe v16 serves the Desk at /desk/<slug>; /app/<slug> is only a
        # redirect. Both spellings must reach the same plan gates.
        with StubEnvironment() as env:
            env.set_plan("PROFESSIONAL")
            for path in (
                "/desk/crm",
                "/desk/crm-lead",
                "/desk/engagement-event",
                "/desk/data-import",
                "/desk/email-account",
                "/desk/facebook-page",
            ):
                with self.subTest(path=path):
                    self.assert_blocked(env, path)

            env.set_plan("BUSINESS")
            for path in (
                "/desk/crm",
                "/desk/crm-lead",
                "/desk/engagement-event",
                "/desk/data-import",
                "/desk/facebook-page",
            ):
                with self.subTest(path=path):
                    self.assert_allowed(env, path)
            self.assert_blocked(env, "/desk/email-account")

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

    def test_legacy_upgrade_url_is_normalised_to_pricing_anchor(self):
        with StubEnvironment() as env:
            env.frappe.conf.pop("bc_upgrade_url", None)
            env.entitlements.clear_entitlement_cache()
            default = env.entitlements.get_entitlements()["upgrade_url"]
            self.assertIn("#section_business-connect-pricing", default)

            env.frappe.conf["bc_upgrade_url"] = next(
                iter(env.constants.LEGACY_UPGRADE_URLS)
            )
            env.entitlements.clear_entitlement_cache()
            self.assertEqual(
                env.entitlements.get_entitlements()["upgrade_url"], default
            )

            env.frappe.conf["bc_upgrade_url"] = "https://example.com/custom-plans"
            env.entitlements.clear_entitlement_cache()
            self.assertEqual(
                env.entitlements.get_entitlements()["upgrade_url"],
                "https://example.com/custom-plans",
            )

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
            # set_value accepts fieldname as a JSON string or dict.
            self.assert_blocked(
                env,
                "/api/method/frappe.client.set_value",
                method="POST",
                payload={
                    "doctype": "User",
                    "name": "admin@example.com",
                    "fieldname": json.dumps({"api_key": "leaked"}),
                },
            )
            self.assert_blocked(
                env,
                "/api/method/frappe.client.set_value",
                method="POST",
                payload={
                    "doctype": "User",
                    "name": "admin@example.com",
                    "fieldname": {"api_secret": "leaked"},
                },
            )
            self.assert_blocked(
                env,
                "/api/method/frappe.client.bulk_update",
                method="POST",
                payload={"docs": [{"doctype": "User", "api_secret": "leaked"}]},
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

    def test_report_view_export_is_import_export(self):
        with StubEnvironment() as env:
            env.set_plan("PROFESSIONAL")
            self.assert_blocked(env, "/api/method/frappe.desk.reportview.export_query")

    def test_remaining_crm_config_methods_are_enterprise_only(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            for method in (
                "crm.fcrm.doctype.crm_view_settings.crm_view_settings.pin",
                "crm.fcrm.doctype.crm_view_settings.crm_view_settings.public",
                "crm.fcrm.doctype.crm_view_settings.crm_view_settings.fetch_and_update_kanban_columns",
                "crm.fcrm.doctype.erpnext_crm_settings.erpnext_crm_settings.dismiss_sync_issue",
            ):
                with self.subTest(method=method):
                    self.assert_blocked(env, "/api/method/" + method)

    def test_business_can_read_settings_needed_by_crm(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            self.assert_allowed(env, "/api/resource/ERPNext CRM Settings")
            self.assertNotIn(
                "ERPNext CRM Settings", env.constants.PLAN_GATE_QUERY_DOCTYPES
            )

    def test_pwa_icon_stays_public_on_suspended_site(self):
        with StubEnvironment() as env:
            self.suspend_site(env)
            env.frappe.session.user = "Guest"
            self.assert_allowed(
                env, "/api/method/osduo_business_connect.pwa.get_app_icon"
            )

    def test_html_403_shows_plan_message_and_upgrade_link(self):
        class FakeResponse:
            def __init__(self, status=403):
                self.status_code = status
                self.headers = {}
                self.data = ""

            def set_data(self, value):
                self.data = value

        with StubEnvironment() as env:
            env.set_plan("PROFESSIONAL")
            self.assert_blocked(env, "/desk/crm")

            response = FakeResponse()
            env.plan_gates.render_plan_gate_message(
                response=response,
                request=types.SimpleNamespace(path="/desk/crm"),
            )
            self.assertIn("available on the Business plan", response.data)
            self.assertIn("https://example.com/upgrade", response.data)
            self.assertIn("View plans", response.data)
            self.assertEqual(response.headers["Content-Type"], "text/html; charset=utf-8")

            # API errors already carry the message in their JSON body.
            api_response = FakeResponse()
            env.plan_gates.render_plan_gate_message(
                response=api_response,
                request=types.SimpleNamespace(path="/api/method/frappe.ping"),
            )
            self.assertEqual(api_response.data, "")


class TestPlanQuotas(unittest.TestCase):
    """Creation-time quota checks wired into the DocType controllers."""

    def setUp_env(self, plan, seats=0, businesses=0, existing_user=False):
        env = StubEnvironment().__enter__()
        self.addCleanup(env.__exit__, None, None, None)
        env.set_plan(plan)
        env.frappe.db.sql = lambda *args, **kwargs: [(seats,)]
        env.frappe.db.counts["Business"] = businesses
        env.frappe.db.exists = lambda dt, filters=None: (
            existing_user if dt == "Business Member" else False
        )
        return env

    def member(self, **kwargs):
        data = {
            "doctype": "Business Member",
            "business": "BIZ-1",
            "user": "new@example.com",
            "status": "Active",
        }
        data.update(kwargs)
        return FakeDocument(data)

    def test_professional_blocks_second_seat(self):
        env = self.setUp_env("PROFESSIONAL", seats=1)
        with self.assertRaises(env.entitlements.PlanRestrictionError) as ctx:
            env.limits.enforce_seat_limit(self.member())
        self.assertIn("Seats limit reached (1 of 1)", str(ctx.exception))
        self.assertIn("https://example.com/upgrade", str(ctx.exception))

    def test_professional_allows_first_seat_and_business_plan_more(self):
        env = self.setUp_env("PROFESSIONAL", seats=0)
        env.limits.enforce_seat_limit(self.member())

        env.set_plan("BUSINESS")
        env.frappe.db.sql = lambda *a, **k: [(4,)]
        env.limits.enforce_seat_limit(self.member())

    def test_user_with_existing_seat_does_not_consume_another(self):
        env = self.setUp_env("PROFESSIONAL", seats=1, existing_user=True)
        env.limits.enforce_seat_limit(self.member())

    def test_inactive_member_is_not_a_seat(self):
        env = self.setUp_env("PROFESSIONAL", seats=1)
        env.limits.enforce_seat_limit(self.member(status="Inactive"))

    def test_unchanged_active_member_can_be_edited_at_cap(self):
        env = self.setUp_env("PROFESSIONAL", seats=1)
        env.frappe.db.values[("Business Member", "BM-1", "status")] = "Active"
        env.frappe.db.values[("Business Member", "BM-1", "user")] = "new@example.com"
        env.limits.enforce_seat_limit(self.member(name="BM-1"))

    def test_reassigning_seat_to_another_user_stays_within_cap(self):
        env = self.setUp_env("PROFESSIONAL", seats=1)
        env.frappe.db.values[("Business Member", "BM-1", "status")] = "Active"
        env.frappe.db.values[("Business Member", "BM-1", "user")] = "old@example.com"
        env.limits.enforce_seat_limit(
            self.member(name="BM-1", user="new@example.com")
        )

    def test_one_digital_card_per_member(self):
        env = self.setUp_env("PROFESSIONAL")
        env.frappe.db.exists = lambda dt, filters=None: dt == "Digital Card"
        card = self.member(member="BM-1", display_name="A")
        with self.assertRaises(env.frappe.ValidationError) as ctx:
            env.limits.enforce_member_card_limit(card)
        self.assertIn("already has a Digital Card", str(ctx.exception))

        seen = []
        env.frappe.db.exists = lambda dt, filters=None: seen.append(filters) or False
        existing = self.member(name="CARD-1", member="BM-1", display_name="B")
        env.limits.enforce_member_card_limit(existing)
        self.assertEqual(seen[-1]["member"], "BM-1")
        self.assertEqual(seen[-1]["docstatus"], ["<", 2])
        self.assertEqual(seen[-1]["name"], ["!=", "CARD-1"])

    def test_quota_and_gate_errors_publish_message_to_client(self):
        # v16 API v2 only shows __server_messages from frappe.throw; a bare
        # `raise` leaves the user with a save that silently fails.
        env = self.setUp_env("PROFESSIONAL", seats=1)
        calls = []
        original = env.frappe.throw

        def capture(msg, exc=None, **kwargs):
            calls.append((msg, exc))
            return original(msg, exc=exc, **kwargs)

        env.frappe.throw = capture

        with self.assertRaises(env.entitlements.PlanRestrictionError):
            env.limits.enforce_seat_limit(self.member())
        self.assertEqual(calls[-1][1], env.entitlements.PlanRestrictionError)
        self.assertIn("Seats limit reached (1 of 1)", calls[-1][0])

        env.set_request("/crm")
        with self.assertRaises(env.frappe.PermissionError):
            env.plan_gates.enforce_plan_gates()
        self.assertEqual(calls[-1][1], env.frappe.PermissionError)
        self.assertIn("CRM is available on the Business plan", calls[-1][0])

    def test_controllers_wire_quota_checks(self):
        with open(os.path.join(APP_DIR, "business", "core.py")) as handle:
            business_controller = handle.read()
        self.assertIn("enforce_business_limit()", business_controller)

        member_path = os.path.join(
            APP_DIR, "business", "doctype", "business_member", "business_member.py"
        )
        with open(member_path) as handle:
            member_controller = handle.read()
        self.assertIn("enforce_seat_limit(self)", member_controller)

    def test_business_cap_counts_drafts_and_blocks_creation(self):
        env = self.setUp_env("PROFESSIONAL", businesses=1)
        with self.assertRaises(env.entitlements.PlanRestrictionError) as ctx:
            env.limits.enforce_business_limit()
        self.assertIn("Business profiles limit reached (1 of 1)", str(ctx.exception))

        env.set_plan("BUSINESS")
        env.frappe.db.counts["Business"] = 2
        env.limits.enforce_business_limit()

        # Cancelled records are excluded by the usage query, not by a filter
        # here; confirm the filter is the expected docstatus range.
        self.assertEqual(
            env.frappe.db.count_calls[-1],
            ("Business", {"docstatus": ["<", 2]}),
        )


class TestAddOnsAndDomains(unittest.TestCase):
    """Phase 3/4: add-on ordering, custom domains and expiry."""

    def setUp_env(self, plan="ENTERPRISE", period_end="2027-11-21"):
        env = StubEnvironment().__enter__()
        self.addCleanup(env.__exit__, None, None, None)
        env.set_plan(plan)
        env.frappe.db.single[("Subscription", "plan")] = plan
        subscription = FakeDocument({
            "doctype": "Subscription",
            "name": "Subscription",
            "plan": plan,
            "status": "Active",
            "current_period_end": period_end,
            "domain_mappings": [],
        })
        env.frappe.get_doc = lambda *a, **k: (
            subscription if a == ("Subscription",) else FakeDocument(*a, **k)
        )
        env.frappe.conf["host_name"] = "original.example.com"
        return env, subscription

    def test_enterprise_first_domain_is_included(self):
        env, subscription = self.setUp_env()
        row = env.domains.add_domain_mapping(" Cards.Example.com ")
        self.assertEqual(row["hostname"], "cards.example.com")
        self.assertEqual(row["mapping_type"], "Included")
        self.assertEqual(row["price"], 0)
        self.assertEqual(row["expires_on"], "2027-11-21")
        self.assertEqual(len(subscription.domain_mappings), 1)
        self.assertEqual(env.frappe.conf["host_name"], "original.example.com")

    def test_second_domain_is_paid_at_plan_price(self):
        env, _ = self.setUp_env()
        env.domains.add_domain_mapping("one.example.com")
        row = env.domains.add_domain_mapping("two.example.com")
        self.assertEqual(row["mapping_type"], "Paid Custom Domain")
        self.assertEqual(row["price"], 5999)
        self.assertEqual(row["expires_on"], "2027-11-21")

    def test_caller_cannot_mark_a_paid_domain_as_included(self):
        env, _ = self.setUp_env()
        env.domains.add_domain_mapping("one.example.com")
        row = env.domains.add_domain_mapping(
            "two.example.com", mapping_type="Included"
        )
        self.assertEqual(row["mapping_type"], "Paid Custom Domain")
        self.assertEqual(row["price"], 5999)

    def test_business_has_no_included_domain(self):
        env, _ = self.setUp_env("BUSINESS")
        row = env.domains.add_domain_mapping("cards.example.com")
        self.assertEqual(row["mapping_type"], "Paid Custom Domain")
        self.assertEqual(row["price"], 5999)

    def test_duplicate_open_hostname_is_rejected(self):
        env, _ = self.setUp_env()
        env.domains.add_domain_mapping("cards.example.com")
        with self.assertRaises(env.frappe.ValidationError) as ctx:
            env.domains.add_domain_mapping("cards.example.com")
        self.assertIn("already has an open domain mapping", str(ctx.exception))

    def test_expiry_marks_domain_and_order_without_touching_host_name(self):
        env, subscription = self.setUp_env(period_end="2025-01-01")
        env.domains.add_domain_mapping("old.example.com", add_on_order="ADDON-1")
        self.assertEqual(env.domains.expire_domains(), 1)
        self.assertEqual(subscription.domain_mappings[0].status, "Expired")
        self.assertEqual(
            env.frappe.db.values[("Add-on Order", "ADDON-1", "status")], "Expired"
        )
        self.assertEqual(env.frappe.conf["host_name"], "original.example.com")
        self.assertEqual(env.domains.expire_domains(), 0)

    def test_addon_order_status_workflow(self):
        env, _ = self.setUp_env()
        env.frappe.session.user = "Administrator"
        order = env.addon_order.AddonOrder({"name": "ADDON-1", "status": "Active"})
        order.get_doc_before_save = lambda: FakeDocument({"status": "Requested"})
        with self.assertRaises(env.frappe.ValidationError) as ctx:
            order.validate_status_transition()
        self.assertIn("Cannot change", str(ctx.exception))

        order.status = "Approved"
        order.validate_status_transition()  # Requested -> Approved is allowed

        order.get_doc_before_save = lambda: FakeDocument({"status": "Approved"})
        order.status = "Configured"
        env.frappe.session.user = "owner@example.com"
        with self.assertRaises(env.frappe.PermissionError):
            order.validate_status_transition()

        env.frappe.session.user = "subscription-manager@example.com"
        with self.assertRaises(env.frappe.PermissionError):
            order.validate_status_transition()

    def test_subscription_manager_role_can_advance_addon_order(self):
        env, _ = self.setUp_env()
        env.frappe.session.user = "provider@example.com"
        env.set_roles("BC Subscription Manager")
        order = env.addon_order.AddonOrder({"name": "ADDON-1", "status": "Approved"})
        order.get_doc_before_save = lambda: FakeDocument({"status": "Requested"})
        order.validate_status_transition()  # must not raise

    def test_addon_quote_requires_an_authenticated_user(self):
        with StubEnvironment() as env:
            env.frappe.session.user = "Guest"
            with self.assertRaises(env.frappe.PermissionError):
                env.addon_order.get_addon_quote("PRIORITY_SUPPORT")

    def test_subscription_page_is_read_only_and_has_upgrade_url(self):
        env, _ = self.setUp_env()
        data = env.subscription_page.get_my_subscription()
        self.assertEqual(data["plan_code"], "ENTERPRISE")
        self.assertEqual(data["billing_source"], "Aasriva")
        self.assertEqual(data["upgrade_url"], "https://example.com/upgrade")
        self.assertEqual(data["seats"], {"used": 0, "billed": 10})
        self.assertEqual(
            {key for key in data if "api_key" in key or "secret" in key or "snapshot" in key},
            set(),
        )
        for forbidden in ("checkout", "payment", "invoice"):
            self.assertNotIn(forbidden, str(data).lower())

        env.frappe.session.user = "Guest"
        with self.assertRaises(env.frappe.PermissionError):
            env.subscription_page.get_my_subscription()

    def test_expiry_is_wired_into_daily_scheduler(self):
        with open(os.path.join(APP_DIR, "services", "scheduler.py")) as handle:
            scheduler = handle.read()
        self.assertIn("expire_subscription_domains()", scheduler)

    def test_desk_page_files_exist_and_are_read_only(self):
        base = os.path.join(APP_DIR, "subscription", "page", "my_subscription")
        with open(os.path.join(base, "my_subscription.json")) as handle:
            page = json.load(handle)
        self.assertEqual(page["name"], "my-subscription")
        self.assertEqual(page["doctype"], "Page")
        with open(os.path.join(base, "my_subscription.js")) as handle:
            script = handle.read()
        self.assertIn("get_my_subscription", script)
        self.assertIn('frappe.new_doc("Add-on Order")', script)
        self.assertIn("upgrade_url", script)


class TestFinalHardening(unittest.TestCase):
    """Phase 4 regressions: direct-insert, route and snapshot bypasses."""

    def test_addon_order_insert_cannot_bypass_workflow(self):
        with StubEnvironment() as env:
            env.set_plan("ENTERPRISE")
            order = env.addon_order.AddonOrder({
                "status": "Active",
                "approved_by": "attacker@example.com",
                "external_ref": "fake-ref",
                "hostname": "cards.example.com",
            })
            order.before_insert()
            self.assertEqual(order.status, "Requested")
            self.assertIsNone(order.approved_by)
            self.assertIsNone(order.external_ref)

    def test_customer_cannot_choose_or_change_addon_order_status(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            env.frappe.session.user = "owner@example.com"
            add_on = FakeDocument({
                "name": "CUSTOM_DOMAIN_SERVICE",
                "add_on_name": "Custom Domain Service",
                "billing_type": "Annual",
                "price": 5999,
                "is_active": 1,
                "applies_to_all_plans": 1,
                "applicable_plans": [],
            })
            env.frappe.get_doc = lambda *a, **k: add_on
            order = env.addon_order.AddonOrder({
                "add_on": "CUSTOM_DOMAIN_SERVICE",
                "hostname": "cards.example.com",
            })
            order.before_insert()
            order.status = "Approved"
            with self.assertRaises(env.frappe.PermissionError) as ctx:
                order.validate()
            self.assertIn("Customers can only request add-ons", str(ctx.exception))

            order.status = "Requested"
            order.validate()
            self.assertEqual(order.status, "Requested")

    def test_administrator_can_create_an_advanced_status(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            env.frappe.session.user = "Administrator"
            add_on = FakeDocument({
                "name": "PRIORITY_SUPPORT",
                "add_on_name": "Priority Support",
                "billing_type": "Annual",
                "price": 12000,
                "is_active": 1,
                "applies_to_all_plans": 1,
                "applicable_plans": [],
            })
            env.frappe.get_doc = lambda *a, **k: add_on
            order = env.addon_order.AddonOrder({
                "add_on": "PRIORITY_SUPPORT",
                "status": "Approved",
            })
            order.before_insert()
            order.validate()
            self.assertEqual(order.status, "Approved")
            self.assertEqual(order.approved_by, "Administrator")

    def test_customer_cannot_attach_invoice(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            env.frappe.session.user = "owner@example.com"
            add_on = FakeDocument({
                "name": "PRIORITY_SUPPORT",
                "add_on_name": "Priority Support",
                "billing_type": "Annual",
                "price": 12000,
                "is_active": 1,
                "applies_to_all_plans": 1,
                "applicable_plans": [],
            })
            env.frappe.get_doc = lambda *a, **k: add_on
            order = env.addon_order.AddonOrder({
                "add_on": "PRIORITY_SUPPORT",
                "invoice": "/files/invoice.pdf",
            })
            with self.assertRaises(env.frappe.PermissionError) as ctx:
                order.validate()
            self.assertIn("Only the subscription provider can attach an Invoice", str(ctx.exception))

            env.frappe.session.user = "Administrator"
            order.validate()

    def test_new_order_notification_uses_configured_recipients(self):
        with StubEnvironment() as env:
            sent = {}
            env.frappe.sendmail = lambda **kwargs: sent.update(kwargs)
            env.frappe.conf[env.constants.ADDON_ORDER_NOTIFICATION_CONFIG_KEY] = (
                "ops@example.com; info@osduotech.com"
            )
            order = FakeDocument({
                "doctype": "Add-on Order",
                "name": "ADDON-2026-00001",
                "add_on": "ADDITIONAL_USER",
                "plan_snapshot": "BUSINESS",
                "amount": 895,
                "customer_email": "owner@example.com",
                "hostname": "",
            })
            env.addon_order.send_new_order_notification(order)
            self.assertEqual(
                sent["recipients"],
                ["ops@example.com", "info@osduotech.com"],
            )
            self.assertIn("ADDON-2026-00001", sent["subject"])
            self.assertIn("BUSINESS", sent["message"])
            self.assertEqual(sent["reference_doctype"], "Add-on Order")

    def test_addon_order_amount_and_plan_are_server_derived(self):
        with StubEnvironment() as env:
            env.set_plan("ENTERPRISE")
            env.frappe.db.single[("Subscription", "plan")] = "ENTERPRISE"
            add_on = FakeDocument({
                "name": "CUSTOM_DOMAIN_SERVICE",
                "billing_type": "Annual",
                "price": 5999,
                "is_active": 1,
                "applies_to_all_plans": 1,
                "applicable_plans": [],
                "add_on_name": "Custom Domain Service",
            })
            env.frappe.get_doc = lambda *a, **k: add_on
            order = env.addon_order.AddonOrder({
                "add_on": "CUSTOM_DOMAIN_SERVICE",
                "hostname": "cards.example.com",
                "plan_snapshot": "PROFESSIONAL",
                "amount": 0,
            })
            order.validate()
            self.assertEqual(order.plan_snapshot, "ENTERPRISE")
            self.assertEqual(order.amount, 0)  # first Enterprise mapping included
            self.assertEqual(order.mapping_type, "Included")

    def test_generic_annual_addon_uses_master_price_without_hostname(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            env.frappe.db.single[("Subscription", "plan")] = "BUSINESS"
            add_on = FakeDocument({
                "name": "PRIORITY_SUPPORT",
                "billing_type": "Annual",
                "price": 12000,
                "is_active": 1,
                "applies_to_all_plans": 0,
                "applicable_plans": [
                    {"plan": "BUSINESS"}, {"plan": "ENTERPRISE"}
                ],
                "add_on_name": "Priority Support",
            })
            original_get_doc = env.frappe.get_doc

            def get_doc(*args, **kwargs):
                if args and args[0] == "Add-on Master":
                    return add_on
                return original_get_doc(*args, **kwargs)

            env.frappe.get_doc = get_doc
            order = env.addon_order.AddonOrder({"add_on": "PRIORITY_SUPPORT"})
            order.validate()
            self.assertEqual(order.plan_snapshot, "BUSINESS")
            self.assertEqual(order.billing_type, "Annual")
            self.assertEqual(order.amount, 12000)
            self.assertFalse(order.expires_on)

    def test_plan_specific_addon_blocks_other_plans(self):
        with StubEnvironment() as env:
            env.set_plan("PROFESSIONAL")
            env.frappe.db.single[("Subscription", "plan")] = "PROFESSIONAL"
            add_on = FakeDocument({
                "name": "PRIORITY_SUPPORT",
                "billing_type": "Annual",
                "price": 12000,
                "is_active": 1,
                "applies_to_all_plans": 0,
                "applicable_plans": [{"plan": "ENTERPRISE"}],
                "add_on_name": "Priority Support",
            })
            original_get_doc = env.frappe.get_doc

            def get_doc(*args, **kwargs):
                if args and args[0] == "Add-on Master":
                    return add_on
                return original_get_doc(*args, **kwargs)

            env.frappe.get_doc = get_doc
            order = env.addon_order.AddonOrder({"add_on": "PRIORITY_SUPPORT"})
            with self.assertRaises(env.frappe.ValidationError) as ctx:
                order.validate()
            self.assertIn("not available on the PROFESSIONAL plan", str(ctx.exception))
            self.assertIn("https://example.com/upgrade", str(ctx.exception))

    def test_addon_quote_is_server_derived_and_type_specific(self):
        with StubEnvironment() as env:
            env.set_plan("ENTERPRISE")
            env.frappe.db.single[("Subscription", "plan")] = "ENTERPRISE"
            masters = {
                "CUSTOM_DOMAIN_SERVICE": FakeDocument({
                    "name": "CUSTOM_DOMAIN_SERVICE",
                    "add_on_name": "Custom Domain Service",
                    "billing_type": "Annual",
                    "price": 5999,
                    "is_active": 1,
                    "applies_to_all_plans": 1,
                    "applicable_plans": [],
                }),
                "PRIORITY_SUPPORT": FakeDocument({
                    "name": "PRIORITY_SUPPORT",
                    "add_on_name": "Priority Support",
                    "billing_type": "Annual",
                    "price": 12000,
                    "is_active": 1,
                    "applies_to_all_plans": 1,
                    "applicable_plans": [],
                }),
                "DOMAIN_REGISTRATION_RENEWAL": FakeDocument({
                    "name": "DOMAIN_REGISTRATION_RENEWAL",
                    "add_on_name": "Domain Registration / Renewal",
                    "billing_type": "Actual Cost",
                    "price": 0,
                    "is_active": 1,
                    "applies_to_all_plans": 1,
                    "applicable_plans": [],
                }),
            }
            original_get_doc = env.frappe.get_doc

            def get_doc(*args, **kwargs):
                if args and args[0] == "Add-on Master":
                    return masters.get(args[1])
                return original_get_doc(*args, **kwargs)

            env.frappe.get_doc = get_doc

            domain = env.addon_order.get_addon_quote("CUSTOM_DOMAIN_SERVICE")
            self.assertTrue(domain["requires_hostname"])
            self.assertTrue(domain["requires_mapping_type"])
            self.assertFalse(domain["requires_registration_details"])
            self.assertFalse(domain["requires_attachment"])
            self.assertEqual(domain["amount"], 0)
            self.assertEqual(domain["mapping_type"], "Included")
            self.assertEqual(domain["amount_label"], "Included in your plan")

            generic = env.addon_order.get_addon_quote("PRIORITY_SUPPORT")
            self.assertFalse(generic["requires_hostname"])
            self.assertFalse(generic["requires_mapping_type"])
            self.assertFalse(generic["requires_registration_details"])
            self.assertFalse(generic["requires_attachment"])
            self.assertEqual(generic["amount"], 12000)
            self.assertEqual(generic["amount_label"], "Estimated annual amount")

            actual = env.addon_order.get_addon_quote("DOMAIN_REGISTRATION_RENEWAL")
            self.assertTrue(actual["requires_hostname"])
            self.assertFalse(actual["requires_mapping_type"])
            self.assertTrue(actual["requires_registration_details"])
            self.assertTrue(actual["requires_documents"])
            self.assertTrue(actual["requires_attachment"])
            self.assertEqual(actual["amount"], 0)
            self.assertIn("Actual vendor cost", actual["amount_label"])

    def test_domain_addon_still_requires_hostname(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            add_on = FakeDocument({
                "name": "CUSTOM_DOMAIN_SERVICE",
                "billing_type": "Annual",
                "price": 5999,
                "is_active": 1,
                "applies_to_all_plans": 1,
                "applicable_plans": [],
                "add_on_name": "Custom Domain Service",
            })
            env.frappe.get_doc = lambda *a, **k: add_on
            order = env.addon_order.AddonOrder({"add_on": "CUSTOM_DOMAIN_SERVICE"})
            with self.assertRaises(env.frappe.ValidationError) as ctx:
                order.validate()
            self.assertIn("Hostname is required", str(ctx.exception))

    def test_professional_blocks_multi_business_and_team_surfaces(self):
        with StubEnvironment() as env:
            env.set_plan("PROFESSIONAL")
            for path in (
                "/app/business/new",
                "/desk/business/new",
                "/app/business/view/new",
                "/app/business-member",
                "/desk/business-member",
                "/api/resource/Business Member",
            ):
                with self.subTest(path=path):
                    env.set_request(path, method="POST")
                    with self.assertRaises(env.frappe.PermissionError):
                        env.plan_gates.enforce_plan_gates()

            env.set_request(
                "/api/method/frappe.client.insert",
                method="POST",
                form={"cmd": "frappe.client.insert", "doctype": "Business"},
            )
            with self.assertRaises(env.frappe.PermissionError):
                env.plan_gates.enforce_plan_gates()

            # Editing the single Business stays usable on Professional.
            env.set_request("/app/business/BUS-1", method="GET")
            env.plan_gates.enforce_plan_gates()
            env.set_request(
                "/api/resource/Business/BUS-1",
                method="PUT",
                form={"doctype": "Business", "name": "BUS-1"},
            )
            env.plan_gates.enforce_plan_gates()

    def test_business_plan_allows_profile_and_team_creation(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            for path in ("/app/business/new", "/app/business-member"):
                with self.subTest(path=path):
                    env.set_request(path, method="GET")
                    env.plan_gates.enforce_plan_gates()
            env.set_request("/api/resource/Business Member", method="POST")
            env.plan_gates.enforce_plan_gates()

    def test_v2_admin_method_shorthand_is_gated_for_business(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            for method in ("save_fields_layout", "set_as_default", "dismiss_sync_issue"):
                with self.subTest(method=method):
                    path = f"/api/v2/method/CRM%20Fields%20Layout/{method}"
                    env.set_request(path, method="GET")
                    with self.assertRaises(env.frappe.PermissionError):
                        env.plan_gates.enforce_plan_gates()
            # Ordinary layout reads stay available so the CRM UI renders.
            env.set_request(
                "/api/v2/method/CRM%20Fields%20Layout/get_fields_layout",
                method="GET",
            )
            env.plan_gates.enforce_plan_gates()

    def test_subscription_provider_fields_are_immutable(self):
        with StubEnvironment() as env:
            snapshot = json.dumps(env.constants.snapshot_defaults("PROFESSIONAL"))
            old = env.controller.Subscription({
                "name": "Subscription",
                "plan": "PROFESSIONAL",
                "status": "Active",
                "seats_ordered": 1,
                "min_billed_seats": 1,
                "seats_cap": 1,
                "entitlement_snapshot": snapshot,
            })
            new = env.controller.Subscription({
                "name": "Subscription",
                "plan": "ENTERPRISE",
                "status": "Active",
                "seats_ordered": 1,
                "min_billed_seats": 1,
                "seats_cap": 1,
                "entitlement_snapshot": snapshot,
            })
            new.get_doc_before_save = lambda: old
            with self.assertRaises(env.frappe.ValidationError) as ctx:
                new.validate()
            self.assertIn("managed by the subscription provider", str(ctx.exception))

            env.frappe.flags.bc_provisioning = True
            new.validate()  # CLI path is trusted

    def test_snapshot_plan_code_is_authoritative(self):
        with StubEnvironment() as env:
            business = env.constants.snapshot_defaults("BUSINESS")
            business["plan_code"] = "BUSINESS"
            subscription = env.controller.Subscription({
                "name": "Subscription",
                "plan": "ENTERPRISE",  # tampered field
                "status": "Active",
                "seats_cap": 5,
                "entitlement_snapshot": json.dumps(business),
            })
            env.frappe.db.single[("Subscription", "plan")] = "ENTERPRISE"
            env.frappe.get_doc = lambda *a, **k: (
                subscription if a == ("Subscription",) else FakeDocument(*a, **k)
            )
            env.entitlements.clear_entitlement_cache()
            ent = env.entitlements.get_entitlements()
            self.assertEqual(ent["plan_code"], "BUSINESS")
            self.assertFalse(ent["features"]["advanced_admin"])

    def test_legacy_website_theme_colours_are_repaired_before_migrate(self):
        with StubEnvironment() as env:
            install = _load(
                "osduo_business_connect.install",
                os.path.join(APP_DIR, "install.py"),
            )
            colors = {"#333333"}
            theme = FakeDocument({
                "name": "Legacy Theme",
                "primary_color": "Primary Color",
                "text_color": "#333333",
                "background_color": "Page Background Color",
            })

            def exists(dt, dn=None):
                if dt == "DocType":
                    return True
                if dt == "Color":
                    return dn in colors
                return False

            created = []

            def get_doc(*args, **kwargs):
                data = args[0] if args and isinstance(args[0], dict) else None
                if isinstance(data, dict) and data.get("doctype") == "Color":
                    created.append(data)
                    colors.add(data["__newname"])
                    return FakeDocument(data)
                if args == ("Website Theme", "Legacy Theme"):
                    return theme
                return FakeDocument(*args, **kwargs)

            env.frappe.get_all = lambda *a, **k: ["Legacy Theme"]
            env.frappe.db.exists = exists
            env.frappe.get_doc = get_doc

            self.assertEqual(install.repair_website_theme_colors(), 2)
            self.assertEqual(
                env.frappe.db.values[("Website Theme", "Legacy Theme", "primary_color")],
                "#0B3D91",
            )
            self.assertEqual(
                env.frappe.db.values[("Website Theme", "Legacy Theme", "background_color")],
                "#F4F6F8",
            )
            self.assertNotIn(
                ("Website Theme", "Legacy Theme", "text_color"),
                env.frappe.db.values,
            )
            self.assertEqual(len(created), 2)

    def test_addon_master_requires_plans_when_not_all_plans(self):
        with StubEnvironment() as env:
            master = env.addon_master.AddonMaster({
                "billing_type": "Annual",
                "applies_to_all_plans": 0,
                "applicable_plans": [],
                "price": 12000,
            })
            with self.assertRaises(env.frappe.ValidationError) as ctx:
                master.validate()
            self.assertIn("Select at least one Applicable Plan", str(ctx.exception))

            master.applicable_plans = [{"plan": "BUSINESS"}]
            with self.assertRaises(env.frappe.ValidationError) as price_ctx:
                master.validate()
            self.assertIn("Set an Annual Price for BUSINESS", str(price_ctx.exception))

            master.applicable_plans = [{"plan": "BUSINESS", "price": 12000}]
            master.validate()
            self.assertEqual(master.applicable_plans[0]["price"], 12000.0)

    def test_addon_master_all_plans_clears_applicable_rows(self):
        with StubEnvironment() as env:
            master = env.addon_master.AddonMaster({
                "billing_type": "Annual",
                "price": 12000,
                "applies_to_all_plans": 1,
                "applicable_plans": [{"plan": "BUSINESS"}],
            })
            master.validate()
            self.assertEqual(master.applicable_plans, [])

    def test_additional_user_uses_the_active_plan_price(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            env.frappe.db.single[("Subscription", "plan")] = "BUSINESS"
            add_on = FakeDocument({
                "name": "ADDITIONAL_USER",
                "add_on_name": "Additional User",
                "billing_type": "Annual",
                "price": 0,
                "is_active": 1,
                "applies_to_all_plans": 0,
                "applicable_plans": [
                    {"plan": "PROFESSIONAL", "price": 595},
                    {"plan": "BUSINESS", "price": 895},
                    {"plan": "ENTERPRISE", "price": 1295},
                ],
            })
            original_get_doc = env.frappe.get_doc

            def get_doc(*args, **kwargs):
                if args and args[0] == "Add-on Master":
                    return add_on
                return original_get_doc(*args, **kwargs)

            env.frappe.get_doc = get_doc
            quote = env.addon_order.get_addon_quote("ADDITIONAL_USER")
            self.assertEqual(quote["amount"], 895)
            self.assertEqual(
                quote["amount_label"],
                "Estimated annual price for one additional user",
            )

            order = env.addon_order.AddonOrder({"add_on": "ADDITIONAL_USER"})
            order.validate()
            self.assertEqual(order.plan_snapshot, "BUSINESS")
            self.assertEqual(order.amount, 895)

    def test_higher_plan_addons_require_an_external_plan_upgrade(self):
        with StubEnvironment() as env:
            masters = [
                {
                    "name": "ENTERPRISE_ONLY",
                    "add_on_name": "Enterprise Only",
                    "applies_to_all_plans": 0,
                    "is_active": 1,
                },
            ]
            children = [{"parent": "ENTERPRISE_ONLY", "plan": "ENTERPRISE"}]

            def get_all(doctype, filters=None, **kwargs):
                if doctype == "Add-on Master":
                    return [dict(row) for row in masters]
                if doctype == "Add-on Applicable Plan":
                    parents = set(((filters or {}).get("parent") or [None, []])[1])
                    return [dict(row) for row in children if row["parent"] in parents]
                return []

            env.frappe.get_all = get_all
            env.set_plan("BUSINESS")
            self.assertEqual(env.addon_master.get_orderable_addons(txt=""), [])
            # A client-supplied target plan must never bypass the frozen plan.
            self.assertEqual(
                env.addon_master.get_orderable_addons(
                    txt="", filters={"plan": "ENTERPRISE", "plan_snapshot": "ENTERPRISE"}
                ),
                [],
            )

            env.set_plan("ENTERPRISE")
            self.assertEqual(
                env.addon_master.get_orderable_addons(txt=""),
                [("ENTERPRISE_ONLY", "Enterprise Only")],
            )

    def test_seed_backfills_missing_plan_prices_without_overwriting(self):
        with StubEnvironment() as env:
            master = FakeDocument({
                "name": "PRIORITY_SUPPORT",
                "billing_type": "Annual",
                "price": 12000,
                "applies_to_all_plans": 0,
                "applicable_plans": [
                    {"plan": "BUSINESS"},
                    {"plan": "ENTERPRISE", "price": 15000},
                ],
            })
            saved = []

            def save(**kwargs):
                saved.append(True)
                return master

            master.save = save
            env.frappe.get_all = lambda *a, **k: ["PRIORITY_SUPPORT"]
            env.frappe.get_doc = lambda *a, **k: master

            self.assertEqual(env.seed.backfill_addon_plan_prices(), 1)
            self.assertEqual(master.applicable_plans[0]["price"], 12000)
            self.assertEqual(master.applicable_plans[1]["price"], 15000)
            self.assertEqual(len(saved), 1)

    def test_addon_link_query_returns_only_plan_eligible_masters(self):
        with StubEnvironment() as env:
            env.set_plan("BUSINESS")
            masters = [
                {
                    "name": "CUSTOM_DOMAIN_SERVICE",
                    "add_on_name": "Custom Domain Service",
                    "applies_to_all_plans": 1,
                    "is_active": 1,
                },
                {
                    "name": "PRIORITY_SUPPORT",
                    "add_on_name": "Priority Support",
                    "applies_to_all_plans": 0,
                    "is_active": 1,
                },
                {
                    "name": "ENTERPRISE_ONLY",
                    "add_on_name": "Enterprise Only",
                    "applies_to_all_plans": 0,
                    "is_active": 1,
                },
                {
                    "name": "INACTIVE_ADDON",
                    "add_on_name": "Inactive Add-on",
                    "applies_to_all_plans": 1,
                    "is_active": 0,
                },
            ]
            children = [
                {"parent": "PRIORITY_SUPPORT", "plan": "BUSINESS"},
                {"parent": "ENTERPRISE_ONLY", "plan": "ENTERPRISE"},
            ]

            def get_all(doctype, filters=None, **kwargs):
                if doctype == "Add-on Master":
                    return [
                        dict(row) for row in masters
                        if (filters or {}).get("is_active", 1) == row["is_active"]
                    ]
                if doctype == "Add-on Applicable Plan":
                    parents = set(((filters or {}).get("parent") or [None, []])[1])
                    return [dict(row) for row in children if row["parent"] in parents]
                return []

            env.frappe.get_all = get_all
            self.assertEqual(
                env.addon_master.get_orderable_addons(txt=""),
                [
                    ("CUSTOM_DOMAIN_SERVICE", "Custom Domain Service"),
                    ("PRIORITY_SUPPORT", "Priority Support"),
                ],
            )
            self.assertEqual(
                env.addon_master.get_orderable_addons(txt="priority"),
                [("PRIORITY_SUPPORT", "Priority Support")],
            )


class TestPortalTeamInvitations(unittest.TestCase):
    """Portal-only team onboarding and the customer Desk lockdown."""

    def setUp_env(self, plan="BUSINESS"):
        env = StubEnvironment().__enter__()
        self.addCleanup(env.__exit__, None, None, None)
        env.set_plan(plan)
        env.frappe.session.user = "owner@example.com"
        env.set_roles("BC Business Owner")
        env.memberships[("owner@example.com", "BIZ-1")] = "Owner"
        env.frappe.db.exists = lambda dt, dn=None: dt == "Business" and dn in (None, "BIZ-1")
        env.frappe.db.count = lambda dt, filters=None: (
            1 if dt == "Business" else 0
        )
        env.frappe.db.sql = lambda *a, **k: [(0,)]
        return env

    def fake_core_invite(self, env):
        calls = []
        core = types.ModuleType("frappe.core.api.user_invitation")

        def invite_by_email(**kwargs):
            calls.append(kwargs)
            return {"invited_emails": [kwargs["emails"]]}

        core.invite_by_email = invite_by_email
        sys.modules["frappe.core.api.user_invitation"] = core
        return calls

    def assert_blocked(self, env, path, **kwargs):
        env.set_request(path, **kwargs)
        with self.assertRaises(env.frappe.PermissionError):
            env.plan_gates.enforce_plan_gates()

    def assert_allowed(self, env, path, **kwargs):
        env.set_request(path, **kwargs)
        env.plan_gates.enforce_plan_gates()

    def test_customer_desk_lockdown_on_business_and_professional(self):
        for plan in ("PROFESSIONAL", "BUSINESS"):
            with self.subTest(plan=plan):
                env = self.setUp_env(plan)
                for path in (
                    "/app",
                    "/desk",
                    "/desk/build",
                    "/app/user",
                    "/desk/role",
                    "/app/my-subscription",
                    "/api/method/frappe.core.api.user_invitation.invite_by_email",
                    "/api/v2/method/User/invite_by_email",
                    "/api/resource/User",
                    "/api/resource/User%20Invitation",
                    "/api/resource/Role",
                ):
                    with self.subTest(path=path):
                        self.assert_blocked(env, path)

                self.assert_allowed(env, "/portal/subscription")

                if plan == "BUSINESS":
                    for path in (
                        "/app/business-connect",
                        "/desk/business-connect",
                        "/desk/business/business-connect",
                        "/crm",
                        "/crm-form/crm-lead",
                        "/analytics",
                        "/portal/team",
                        "/api/method/osduo_business_connect.subscription.team_invite.get_team_page_data",
                        "/api/method/crm.api.doc.get_data",
                    ):
                        with self.subTest(path=path):
                            self.assert_allowed(env, path)
                else:
                    for path in (
                        "/app/business-connect",
                        "/desk/business-connect",
                        "/desk/business/business-connect",
                        "/crm",
                        "/analytics",
                        "/portal/team",
                        "/api/method/osduo_business_connect.subscription.team_invite.get_team_page_data",
                        "/api/method/osduo_business_connect.subscription.team_invite.invite_team_member",
                    ):
                        with self.subTest(path=path):
                            self.assert_blocked(env, path)

    def test_all_business_customer_roles_can_open_bc_workspace(self):
        for role in (
            "BC Business Owner",
            "BC Business Manager",
            "BC Business Member",
            "BC CRM User",
            "BC Marketing Manager",
        ):
            with self.subTest(role=role):
                env = self.setUp_env("BUSINESS")
                env.set_roles(role)
                self.assert_allowed(env, "/app/business-connect")
                self.assert_allowed(env, "/desk/business-connect")
                # Frappe v16 can add the module shell to the URL; a refresh of
                # that address must not turn into a 403.
                self.assert_allowed(env, "/desk/business/business-connect")
                # Direct requests to generic Desk routes stay blocked.
                for blocked in ("/desk", "/desk/build", "/api/resource/User"):
                    with self.subTest(role=role, blocked=blocked):
                        self.assert_blocked(env, blocked)

    def test_bc_workspace_links_survive_a_hard_refresh(self):
        env = self.setUp_env("BUSINESS")
        # With no child Workspace Docs published, the shortcuts shipped in
        # business_connect.json still have to work. Frappe writes their DocType
        # routes under the workspace shell, and a refresh sends them through
        # before_request even though SPA navigation does not.
        env.get_all_rows["Workspace"] = []

        for path in (
            "/desk/business-connect/business",
            "/desk/business-connect/business-member",
            "/desk/business-connect/digital-card",
            "/desk/business-connect/showcase-product",
            "/desk/business-connect/my-subscription",
            "/desk/business-connect/business/",
            "/app/business-connect/member",
            "/desk/business/business-connect/business",
        ):
            with self.subTest(path=path):
                self.assert_allowed(env, path)

        # Published child Workspaces remain supported as well.
        env.get_all_rows["Workspace"] = ["Business", "Member"]
        self.assert_allowed(env, "/desk/business-connect/member")

        # Native admin and unknown children must still be blocked on refresh.
        for path in (
            "/desk/business-connect/user",
            "/desk/business-connect/build",
            "/desk/business-connect/business/user",
        ):
            with self.subTest(path=path):
                self.assert_blocked(env, path)

        env.set_plan("PROFESSIONAL")
        self.assert_blocked(env, "/desk/business-connect/business")

    def test_workspace_link_slugs_cover_shipped_shortcuts(self):
        workspace_path = os.path.join(
            APP_DIR,
            "business",
            "workspace",
            "business_connect",
            "business_connect.json",
        )
        with open(workspace_path) as handle:
            workspace = json.load(handle)

        from osduo_business_connect.subscription.constants import (
            CUSTOMER_WORKSPACE_LINK_SLUGS,
        )

        slugs = set(CUSTOMER_WORKSPACE_LINK_SLUGS)
        rows = list(workspace.get("links") or []) + list(workspace.get("shortcuts") or [])
        for row in rows:
            link_to = row.get("link_to")
            if not link_to:
                continue
            with self.subTest(link_to=link_to):
                self.assertIn(self._route_slug(link_to), slugs)

    @staticmethod
    def _route_slug(name):
        return re.sub(r"[^a-z0-9]+", "-", str(name or "").lower()).strip("-")

    def test_rpc_form_cannot_smuggle_core_invite(self):
        env = self.setUp_env()
        self.assert_blocked(
            env,
            "/api/method/frappe.ping",
            form={"cmd": "frappe.core.api.user_invitation.invite_by_email"},
        )
        self.assert_blocked(
            env,
            "/api/method/frappe.ping",
            form={"cmd": "frappe.client.insert", "doctype": "User"},
        )
        self.assert_blocked(
            env,
            "/api/method/osduo_business_connect.subscription.team_invite.invite_team_member",
            form={"cmd": "frappe.core.api.user_invitation.invite_by_email"},
        )

    def test_privileged_roles_and_enterprise_keep_desk(self):
        env = self.setUp_env()
        env.set_roles("BC Business Owner", "System Manager")
        self.assert_allowed(env, "/app/user")
        self.assert_allowed(env, "/api/resource/User")

        env.set_roles("BC Subscription Manager")
        self.assert_allowed(env, "/desk")

        env.set_plan("ENTERPRISE")
        env.set_roles("BC Business Owner")
        self.assert_allowed(env, "/app")
        self.assert_allowed(env, "/api/resource/User")

    def test_guest_invitation_acceptance_stays_public(self):
        env = self.setUp_env()
        env.frappe.flags.bc_plan_override = None
        TestPlanGates().suspend_site(env)
        env.frappe.session.user = "Guest"
        self.assert_allowed(
            env,
            "/api/method/frappe.core.api.user_invitation.accept_invitation?key=abc",
        )
        self.assert_blocked(env, "/portal/team")

    def test_doctype_hook_denies_native_user_admin_for_customers(self):
        env = self.setUp_env()
        gate = env.plan_gates.has_permission_for_doctype
        for doctype in ("User", "User Invitation", "Role", "Role Permission"):
            with self.subTest(doctype=doctype):
                self.assertIs(
                    gate(
                        FakeDocument({"doctype": doctype}),
                        user="owner@example.com",
                        ptype="read",
                    ),
                    False,
                )
        self.assertIs(
            gate(
                FakeDocument({"doctype": "Business Member"}),
                user="owner@example.com",
                ptype="write",
            ),
            True,
        )

    def test_wrapper_validates_then_delegates_to_frappe(self):
        env = self.setUp_env()
        calls = self.fake_core_invite(env)

        result = env.team_invite.invite_team_member(
            email="  Teammate@Example.com ",
            first_name="  Ada ",
            last_name="  Lovelace ",
            business="BIZ-1",
            invite_role="BC CRM User",
        )
        self.assertEqual(result, {"invited_emails": ["teammate@example.com"]})
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["emails"], "teammate@example.com")
        self.assertEqual(calls[0]["roles"], ["BC CRM User"])
        self.assertEqual(calls[0]["app_name"], "osduo_business_connect")
        self.assertEqual(calls[0]["bc_business"], "BIZ-1")
        self.assertEqual(calls[0]["bc_member_role"], "CRM User")
        self.assertEqual(calls[0]["bc_first_name"], "Ada")
        self.assertEqual(calls[0]["bc_last_name"], "Lovelace")
        self.assertEqual(calls[0]["redirect_to_path"], "/portal/team")

        with self.assertRaises(env.frappe.PermissionError):
            env.team_invite.invite_team_member(
                email="x@example.com",
                first_name="X",
                business="BIZ-1",
                invite_role="System Manager",
            )
        with self.assertRaises(env.frappe.ValidationError):
            env.team_invite.invite_team_member(
                email="not-an-email",
                first_name="X",
                business="BIZ-1",
                invite_role="BC Business Member",
            )
        with self.assertRaises(env.frappe.ValidationError):
            env.team_invite.invite_team_member(
                email="x@example.com",
                first_name="",
                business="BIZ-1",
                invite_role="BC Business Member",
            )
        self.assertEqual(len(calls), 1)

    def test_wrapper_rejects_non_owner_wrong_business_and_professional(self):
        env = self.setUp_env()
        self.fake_core_invite(env)
        env.memberships[("owner@example.com", "BIZ-1")] = "Manager"
        with self.assertRaises(env.frappe.PermissionError):
            env.team_invite.invite_team_member(
                email="x@example.com",
                first_name="X",
                business="BIZ-1",
                invite_role="BC Business Member",
            )

        env.memberships[("owner@example.com", "BIZ-1")] = "Owner"
        env.frappe.db.exists = lambda dt, dn=None: False
        with self.assertRaises(env.frappe.ValidationError):
            env.team_invite.invite_team_member(
                email="x@example.com",
                first_name="X",
                business="BIZ-2",
                invite_role="BC Business Member",
            )

        env.frappe.db.exists = lambda dt, dn=None: dt == "Business"
        env.set_plan("PROFESSIONAL")
        with self.assertRaises(env.entitlements.PlanRestrictionError):
            env.team_invite.invite_team_member(
                email="x@example.com",
                first_name="X",
                business="BIZ-1",
                invite_role="BC Business Member",
            )

    def test_invite_reserves_prospective_seat_including_pending_invites(self):
        env = self.setUp_env()
        self.fake_core_invite(env)
        env.frappe.db.sql = lambda *a, **k: [(4,)]
        env.frappe.db.count = lambda dt, filters=None: (
            1 if dt == "User Invitation" else 0
        )
        with self.assertRaises(env.entitlements.PlanRestrictionError) as ctx:
            env.team_invite.invite_team_member(
                email="x@example.com",
                first_name="X",
                business="BIZ-1",
                invite_role="BC Business Member",
            )
        self.assertIn("Seats limit reached (5 of 5)", str(ctx.exception))

        # The pending invite for the same email is de-duplicated by Frappe, so
        # the exclusion filter removes it and the prospective count stays
        # within the cap.
        env.frappe.db.count = lambda dt, filters=None: (
            0
            if dt == "User Invitation" and (filters or {}).get("email")
            else 1
            if dt == "User Invitation"
            else 0
        )
        env.team_invite.invite_team_member(
            email="x@example.com",
            first_name="X",
            business="BIZ-1",
            invite_role="BC Business Member",
        )

    def test_doc_hook_blocks_direct_core_invite_without_bc_context(self):
        env = self.setUp_env()
        doc = FakeDocument({
            "app_name": "osduo_business_connect",
            "email": "x@example.com",
            "status": "Pending",
            "roles": [FakeDocument({"role": "BC Business Member"})],
            "bc_business": "BIZ-1",
            "bc_member_role": "Member",
            "bc_first_name": "X",
            "bc_last_name": "",
        })
        env.team_invite.validate_invitation_context(doc)

        doc.bc_business = None
        with self.assertRaises(env.frappe.ValidationError):
            env.team_invite.validate_invitation_context(doc)

        doc.bc_business = "BIZ-1"
        doc.roles = [FakeDocument({"role": "Administrator"})]
        with self.assertRaises(env.frappe.PermissionError):
            env.team_invite.validate_invitation_context(doc)

    def test_after_accept_applies_names_and_creates_member(self):
        env = self.setUp_env()
        created = []

        def get_doc(*args, **kwargs):
            doc = FakeDocument(kwargs or (args[0] if args else {}))
            created.append(doc)
            return doc

        env.frappe.get_doc = get_doc
        invitation = FakeDocument({
            "app_name": "osduo_business_connect",
            "email": "ada@example.com",
            "bc_business": "BIZ-1",
            "bc_member_role": "CRM User",
            "bc_first_name": "Ada",
            "bc_last_name": "Lovelace",
        })
        user = FakeDocument({
            "name": "ada@example.com",
            "email": "ada@example.com",
            "first_name": "Ada",
            "last_name": "",
        })

        env.team_invite.after_accept_create_member(invitation, user)

        self.assertEqual(user.first_name, "Ada")
        self.assertEqual(user.last_name, "Lovelace")
        self.assertTrue(getattr(user, "_saved", False))
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0].role, "CRM User")
        self.assertEqual(created[0].person_name, "Ada Lovelace")
        self.assertEqual(created[0].business, "BIZ-1")
        self.assertTrue(getattr(created[0], "_inserted", False))

    def test_after_accept_rechecks_plan_and_seat_cap(self):
        env = self.setUp_env()
        invitation = FakeDocument({
            "app_name": "osduo_business_connect",
            "email": "ada@example.com",
            "bc_business": "BIZ-1",
            "bc_member_role": "Member",
            "bc_first_name": "Ada",
        })
        user = FakeDocument({
            "name": "ada@example.com",
            "email": "ada@example.com",
            "first_name": "Ada",
        })

        env.set_plan("PROFESSIONAL")
        with self.assertRaises(env.entitlements.PlanRestrictionError):
            env.team_invite.after_accept_create_member(invitation, user)

        env.set_plan("BUSINESS")
        env.frappe.db.sql = lambda *a, **k: [(5,)]
        with self.assertRaises(env.entitlements.PlanRestrictionError):
            env.team_invite.after_accept_create_member(invitation, user)

    def test_portal_payload_is_scoped_and_read_only(self):
        env = self.setUp_env()
        env.frappe.db.sql = lambda *a, **k: [(1,)]
        env.get_all_rows["Business Member"] = [
            types.SimpleNamespace(
                name="BM-1",
                business="BIZ-1",
                person_name="Ada Lovelace",
                email="ada@example.com",
                role="CRM User",
                status="Active",
            )
        ]
        data = env.team_invite.get_team_page_data()
        self.assertTrue(data["can_manage"])
        self.assertTrue(data["is_owner"])
        self.assertEqual(data["seats"], {"used": 1, "billed": 5})
        self.assertEqual(data["businesses"], [{"name": "BIZ-1", "role": "Owner"}])
        self.assertEqual(data["members"][0]["email"], "ada@example.com")
        self.assertEqual(
            {row["invite_role"] for row in data["roles"]},
            {
                "BC Business Member",
                "BC Business Manager",
                "BC CRM User",
                "BC Marketing Manager",
            },
        )
        self.assertNotIn("api_key", str(data).lower())

        env.frappe.session.user = "Guest"
        with self.assertRaises(env.frappe.PermissionError):
            env.team_invite.get_team_page_data()

    def test_shared_portal_sidebar_is_plan_aware_and_desk_free(self):
        env = self.setUp_env()
        scenarios = {
            "PROFESSIONAL": (False, False, False, False, False),
            "BUSINESS": (True, True, True, False, True),
            "ENTERPRISE": (True, True, True, True, False),
        }
        for plan, expected in scenarios.items():
            with self.subTest(plan=plan):
                env.set_plan(plan)
                env.set_roles("BC Business Owner")
                nav = env.portal_nav.get_portal_nav("team")
                self.assertEqual(nav["active"], "team")
                self.assertEqual(nav["plan_code"], plan)
                self.assertEqual(
                    (
                        nav["can_team"],
                        nav["can_analytics"],
                        nav["can_crm"],
                        nav["can_admin"],
                        nav["can_bc_workspace"],
                    ),
                    expected,
                )
                self.assertEqual(nav["upgrade_url"], env.frappe.conf["bc_upgrade_url"])

        env.set_plan("BUSINESS")
        for role in (
            "BC Business Owner",
            "BC Business Manager",
            "BC Business Member",
            "BC CRM User",
            "BC Marketing Manager",
        ):
            with self.subTest(role=role):
                env.set_roles(role)
                nav = env.portal_nav.get_portal_nav("card")
                self.assertTrue(nav["can_bc_workspace"])
                self.assertEqual(nav["workspace_url"], "/desk/business-connect")

        env.set_plan("PROFESSIONAL")
        env.set_roles("BC Business Owner", "System Manager")
        nav = env.portal_nav.get_portal_nav("card")
        self.assertFalse(nav["can_team"])
        self.assertTrue(nav["can_admin"])
        self.assertFalse(nav["can_bc_workspace"])

    def test_login_home_page_points_customers_to_private_area(self):
        for plan, expected in (
            ("PROFESSIONAL", "/my-card"),
            ("BUSINESS", "/desk/business-connect"),
        ):
            with self.subTest(plan=plan):
                env = self.setUp_env(plan)
                env.frappe.flags.home_page = None
                env.plan_gates.set_customer_login_home(
                    types.SimpleNamespace(user="owner@example.com")
                )
                self.assertEqual(env.frappe.flags.home_page, expected)

        # Frappe calls on_login before make_session(), so the session may still
        # be Guest; the login_manager's user must win.
        env = self.setUp_env("BUSINESS")
        env.frappe.session.user = "Guest"
        env.frappe.flags.home_page = None
        env.plan_gates.set_customer_login_home(
            types.SimpleNamespace(user="owner@example.com")
        )
        self.assertEqual(env.frappe.flags.home_page, "/desk/business-connect")

        # Provider roles and Enterprise keep their Desk home page.
        env = self.setUp_env("BUSINESS")
        env.set_roles("BC Business Owner", "System Manager")
        env.frappe.flags.home_page = None
        env.plan_gates.set_customer_login_home(
            types.SimpleNamespace(user="owner@example.com")
        )
        self.assertIsNone(env.frappe.flags.home_page)

        env = self.setUp_env("ENTERPRISE")
        env.frappe.flags.home_page = None
        env.plan_gates.set_customer_login_home(
            types.SimpleNamespace(user="owner@example.com")
        )
        self.assertIsNone(env.frappe.flags.home_page)

    def test_request_gate_sets_plan_home_flag(self):
        for plan, expected, private_page in (
            ("PROFESSIONAL", "/my-card", "/my-card"),
            ("BUSINESS", "/desk/business-connect", "/portal/team"),
        ):
            env = self.setUp_env(plan)
            for path in ("/", "/login", private_page):
                with self.subTest(plan=plan, path=path):
                    env.set_request(path)
                    env.frappe.flags.home_page = None
                    env.plan_gates.enforce_plan_gates()
                    self.assertEqual(env.frappe.flags.home_page, expected)

        env = self.setUp_env("BUSINESS")
        env.set_roles("BC Business Owner", "BC System Manager")
        env.frappe.flags.home_page = None
        env.plan_gates.enforce_plan_gates()
        self.assertIsNone(env.frappe.flags.home_page)

    def test_automatic_desk_redirect_is_rewritten_per_plan(self):
        class FakeResponse:
            def __init__(self, status, location=None):
                self.status_code = status
                self.headers = {"Location": location} if location else {}
                self.data = ""

            def set_data(self, value):
                self.data = value

        def rewritten(env, location, status=301):
            response = FakeResponse(status, location)
            env.plan_gates.rewrite_customer_desk_redirect(
                response=response,
                request=types.SimpleNamespace(path="/login"),
            )
            return response.headers["Location"]

        # Business customer roles keep the BC workspace, normalised to the v16
        # route; other Desk targets go to the same private landing page.
        env = self.setUp_env("BUSINESS")
        for location in (
            "/app/business-connect",
            "app/business-connect",
            "https://phase2.uat/app/business-connect",
            "/desk/business/business-connect",
        ):
            with self.subTest(location=location):
                self.assertEqual(rewritten(env, location), "/desk/business-connect")
        self.assertEqual(rewritten(env, "/desk/business-connect"), "/desk/business-connect")
        self.assertEqual(rewritten(env, "/desk/build"), "/desk/business-connect")

        # Professional stays portal-only; even a workspace alias lands there.
        env = self.setUp_env("PROFESSIONAL")
        for location in (
            "/app/business-connect",
            "/desk/business-connect",
            "/desk/business/business-connect",
            "/desk/build",
        ):
            with self.subTest(plan="PROFESSIONAL", location=location):
                self.assertEqual(rewritten(env, location), "/my-card")

        # Enterprise/provider redirects must be left alone.
        env = self.setUp_env("BUSINESS")
        env.set_roles("BC Business Owner", "System Manager")
        self.assertEqual(
            rewritten(env, "/app/business-connect"), "/app/business-connect"
        )

        # Non-redirect responses and non-Desk locations are untouched.
        env.set_roles("BC Business Owner")
        self.assertEqual(
            rewritten(env, "/app/business-connect", status=403),
            "/app/business-connect",
        )
        self.assertEqual(rewritten(env, "/portal/team"), "/portal/team")

    def test_403_page_links_back_to_private_area_for_customers(self):
        class FakeResponse:
            def __init__(self):
                self.status_code = 403
                self.headers = {}
                self.data = ""

            def set_data(self, value):
                self.data = value

        def rendered(env, path):
            self.assert_blocked(env, path)
            response = FakeResponse()
            env.plan_gates.render_plan_gate_message(
                response=response, request=types.SimpleNamespace(path=path)
            )
            return response.data

        business_page = rendered(self.setUp_env("BUSINESS"), "/app")
        self.assertIn('href="/desk/business-connect"', business_page)
        self.assertIn("Back to Business Connect", business_page)
        self.assertIn("Business Connect workspace or portal", business_page)

        professional_page = rendered(self.setUp_env("PROFESSIONAL"), "/app")
        self.assertIn('href="/my-card"', professional_page)
        self.assertIn("Back to portal", professional_page)
        self.assertIn("Business Connect portal", professional_page)

    def test_hooks_fields_and_portal_pages_are_wired(self):
        with open(os.path.join(APP_DIR, "hooks.py")) as handle:
            hooks = handle.read()
        self.assertIn("user_invitation = {", hooks)
        self.assertIn('"allowed_roles"', hooks)
        self.assertIn('"extra_invite_params"', hooks)
        self.assertIn("after_accept_create_member", hooks)
        self.assertIn("validate_invitation_context", hooks)
        self.assertIn("on_login = [", hooks)
        self.assertIn("set_customer_login_home", hooks)
        self.assertIn("rewrite_customer_desk_redirect", hooks)
        self.assertIn('"from_route": "/portal/team"', hooks)
        self.assertIn('"to_route": "portal/team"', hooks)
        self.assertIn('"from_route": "/portal/subscription"', hooks)

        invitation_block = hooks.split("user_invitation = {", 1)[1].split("\n}\n", 1)[0]
        invitable_block = hooks.split("_BC_INVITABLE_ROLES = [", 1)[1].split("]", 1)[0]
        for role in (
            "BC Business Member",
            "BC Business Manager",
            "BC CRM User",
            "BC Marketing Manager",
        ):
            self.assertIn('"%s"' % role, invitable_block)
        for forbidden in (
            "Administrator",
            "System Manager",
            "BC System Manager",
            "BC Subscription Manager",
            "BC Business Owner",
        ):
            self.assertNotIn('"%s"' % forbidden, invitable_block)
        for inviter in (
            "Administrator",
            "System Manager",
            "BC System Manager",
            "BC Subscription Manager",
            "BC Business Owner",
        ):
            self.assertIn('"%s":' % inviter, invitation_block)

        with open(os.path.join(APP_DIR, "install.py")) as handle:
            install = handle.read()
        self.assertIn("def create_user_invitation_custom_fields(", install)
        for fieldname in env_fieldnames():
            self.assertIn('"fieldname": "%s"' % fieldname, install)

        for name in ("team", "subscription"):
            base = os.path.join(APP_DIR, "templates", "pages", "portal")
            controller = os.path.join(base, "%s.py" % name)
            template = os.path.join(base, "%s.html" % name)
            self.assertTrue(os.path.exists(controller), controller)
            self.assertTrue(os.path.exists(template), template)
            with open(controller) as handle:
                source = handle.read()
            self.assertIn("Guest", source)

        with open(os.path.join(APP_DIR, "templates", "pages", "portal", "team.html")) as handle:
            template = handle.read()
        self.assertIn(
            "invite_team_member", template
        )
        self.assertIn("access to OSDuo Business Connect", template)
        self.assertNotIn("access to the Frappe Desk", template)
        self.assertNotIn('frappe.new_doc("User")', template)
        for native_admin_link in ('href="/app/user"', 'href="/desk/user"', "User Invitation", "Role Editor"):
            self.assertNotIn(native_admin_link, template)

        sidebar = os.path.join(
            APP_DIR, "templates", "pages", "parts", "portal_sidebar.html"
        )
        self.assertTrue(os.path.exists(sidebar), sidebar)
        for controller_path in (
            os.path.join(APP_DIR, "templates", "pages", "portal", "team.py"),
            os.path.join(APP_DIR, "templates", "pages", "portal", "subscription.py"),
            os.path.join(APP_DIR, "templates", "pages", "my_card.py"),
            os.path.join(APP_DIR, "templates", "pages", "analytics.py"),
        ):
            with open(controller_path) as handle:
                source = handle.read()
            self.assertIn("get_portal_nav", source)
        for template_path in (
            os.path.join(APP_DIR, "templates", "pages", "portal", "team.html"),
            os.path.join(APP_DIR, "templates", "pages", "portal", "subscription.html"),
            os.path.join(APP_DIR, "templates", "pages", "my-card.html"),
            os.path.join(APP_DIR, "templates", "pages", "analytics.html"),
        ):
            with open(template_path) as handle:
                source = handle.read()
            self.assertIn("portal_sidebar.html", source)
            self.assertIn('class="bc-portal-shell"', source)

        with open(sidebar) as handle:
            sidebar_source = handle.read()
        self.assertIn("{% if nav.can_admin %}", sidebar_source)
        self.assertIn(
            "{% if nav.can_bc_workspace %}{{ nav_link(nav.workspace_url or "
            "'/desk/business-connect', 'workspace', 'Business Connect', '◆') "
            "}}{% endif %}",
            sidebar_source,
        )
        # The legacy URL is reserved for provider advanced admin, not customers.
        self.assertIn(
            "{{ nav_link('/app/business-connect', 'admin', 'Advanced admin', '⚙') }}",
            sidebar_source,
        )
        # The portal rail must stay viewport-height and sticky while long
        # content (for example /analytics) scrolls in the main column.
        self.assertIn("height: 100vh", sidebar_source)
        self.assertIn("position: sticky", sidebar_source)
        self.assertIn("top: 0", sidebar_source)
        self.assertIn("overflow-y: auto", sidebar_source)
        self.assertIn("align-self: flex-start", sidebar_source)
        self.assertIn("height: auto; position: static", sidebar_source)
        self.assertNotIn('href="/app/workspace"', sidebar_source)
        self.assertNotIn('href="/app/business"', sidebar_source)
        self.assertNotIn('href="/desk/build"', sidebar_source)

        with open(os.path.join(APP_DIR, "public", "css", "branding.css")) as handle:
            desk_css = handle.read()
        self.assertIn("body.bc-customer-workspace", desk_css)
        self.assertIn("html.bc-customer-workspace", desk_css)
        self.assertIn("#f4f6f8", desk_css)
        self.assertIn("border-radius: 12px", desk_css)
        self.assertIn("frappe.boot.osduo_branding", desk_css)
        # v16 workspace blocks must be themed, not just the legacy section classes.
        self.assertIn(".widget.links-widget-box", desk_css)
        self.assertIn(".widget.shortcut-widget-box", desk_css)
        self.assertIn(".body-sidebar", desk_css)
        self.assertIn("--bg-color", desk_css)
        self.assertIn("--navbar-bg", desk_css)

        with open(os.path.join(APP_DIR, "public", "js", "branding.js")) as handle:
            desk_js = handle.read()
        self.assertIn("bc-customer-workspace", desk_js)
        self.assertIn("/desk/business/business-connect", desk_js)
        self.assertIn("frappe.boot.osduo_branding", desk_js)
        self.assertIn("frappe.boot.bc_workspace_theme", desk_js)
        self.assertIn("frappe.router.current_route", desk_js)
        self.assertIn("function is_bc_workspace_path", desk_js)
        self.assertIn("/(?:[^/]+\\/)?business-connect(?:\\/[^/]+)?$/i", desk_js)
        self.assertIn("bc_roles_ready", desk_js)
        self.assertIn("Array.isArray(frappe.user_roles)", desk_js)
        self.assertIn("apply_patch_with_polling(apply_bc_workspace_theme)", desk_js)
        self.assertIn('if (typeof frappe !== "undefined" && frappe.ui && frappe.ui.form)', desk_js)
        self.assertIn("BC workspace theme patch failed", desk_js)
        self.assertNotIn("var payload = boot.workspaces", desk_js)
        self.assertNotIn("payload.pages", desk_js)
        self.assertIn('frappe.router.on("change"', desk_js)
        self.assertIn("document.documentElement.classList.toggle", desk_js)
        self.assertIn("--desk-sidebar-bg", desk_js)
        self.assertIn("setProperty", desk_js)
        self.assertIn("removeProperty", desk_js)
        for role in (
            "BC Business Owner",
            "BC Business Manager",
            "BC Business Member",
            "BC CRM User",
            "BC Marketing Manager",
        ):
            self.assertIn(role, desk_js)
        self.assertIn("/desk/business-connect", desk_js)

        with open(os.path.join(APP_DIR, "__init__.py")) as handle:
            version = handle.read()
        self.assertIn('__version__ = "1.4.6"', version)


def env_fieldnames():
    return (
        "bc_business",
        "bc_member_role",
        "bc_first_name",
        "bc_last_name",
    )


if __name__ == "__main__":
    unittest.main()
