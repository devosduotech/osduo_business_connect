import ast
import importlib.util
import json
import os
import sys
import types
import unittest

# Structure/constant tests only: do not import frappe (see tests/test_app.py).
APP_DIR = os.path.join(os.path.dirname(__file__), "..")
SUB_DIR = os.path.join(APP_DIR, "subscription")


class TestSubscriptionModuleStructure(unittest.TestCase):
    """Verify the phase-1 module layout and DocType definitions."""

    def test_core_modules_exist(self):
        for filename in (
            "__init__.py",
            "constants.py",
            "entitlements.py",
            "seed.py",
            "provision.py",
        ):
            path = os.path.join(SUB_DIR, filename)
            self.assertTrue(os.path.exists(path), "Missing: subscription/%s" % filename)

    def test_doctypes_exist(self):
        expected = (
            "saas_plan",
            "add_on_master",
            "add_on_applicable_plan",
            "subscription",
            "domain_mapping",
            "subscription_audit_log",
            "add_on_order",
            "plan_restriction_log",
        )
        for name in expected:
            base = os.path.join(SUB_DIR, "doctype", name)
            self.assertTrue(os.path.isdir(base), "Missing doctype dir: %s" % name)
            self.assertTrue(
                os.path.exists(os.path.join(base, "%s.json" % name)),
                "Missing JSON: %s" % name,
            )
            self.assertTrue(
                os.path.exists(os.path.join(base, "%s.py" % name)),
                "Missing controller: %s" % name,
            )

    def test_all_doctype_json_is_valid(self):
        doctype_dir = os.path.join(SUB_DIR, "doctype")
        for name in os.listdir(doctype_dir):
            json_path = os.path.join(doctype_dir, name, "%s.json" % name)
            if not os.path.exists(json_path):
                continue
            with open(json_path) as handle:
                data = json.load(handle)
            self.assertEqual(data["module"], "Subscription")
            # Frappe's scrub() maps both spaces and hyphens to underscores.
            scrubbed = data["name"].replace(" ", "_").replace("-", "_").lower()
            self.assertEqual(scrubbed, name)

    def test_controller_class_names_match_frappe_convention(self):
        # Frappe v16 derives the controller class as
        # doctype.replace(" ", "").replace("-", ""). "Add-on Master" must
        # therefore be AddonMaster, not AddOnMaster.
        doctype_dir = os.path.join(SUB_DIR, "doctype")
        for name in os.listdir(doctype_dir):
            json_path = os.path.join(doctype_dir, name, "%s.json" % name)
            py_path = os.path.join(doctype_dir, name, "%s.py" % name)
            if not (os.path.exists(json_path) and os.path.exists(py_path)):
                continue
            with open(json_path) as handle:
                doctype_name = json.load(handle)["name"]
            expected = doctype_name.replace(" ", "").replace("-", "")
            with open(py_path) as handle:
                tree = ast.parse(handle.read(), filename=py_path)
            classes = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
            self.assertIn(
                expected,
                classes,
                "%s controller must define class %s (found %s)"
                % (doctype_name, expected, sorted(classes)),
            )

    def test_subscription_is_single(self):
        path = os.path.join(SUB_DIR, "doctype", "subscription", "subscription.json")
        with open(path) as handle:
            data = json.load(handle)
        self.assertEqual(data["issingle"], 1)

    def test_role_and_patch_registered(self):
        self.assertTrue(
            os.path.exists(os.path.join(APP_DIR, "roles", "bc_subscription_manager.json"))
        )
        patches = open(os.path.join(APP_DIR, "patches.txt")).read()
        self.assertIn("seed_subscription_existing_sites", patches)
        modules = open(os.path.join(APP_DIR, "modules.txt")).read()
        self.assertIn("Subscription", modules)

    def test_provision_script_exists(self):
        path = os.path.join(APP_DIR, "..", "scripts", "provision_customer_site.py")
        self.assertTrue(os.path.exists(path))

    def test_provision_script_uses_sites_as_working_directory(self):
        # Frappe's logger writes to ../logs relative to cwd. A plain
        # `python script.py` from the bench root must enter sites/ first or it
        # tries to write to $HOME/logs and crashes on connect().
        path = os.path.join(APP_DIR, "..", "scripts", "provision_customer_site.py")
        with open(path) as handle:
            source = handle.read()
        self.assertIn("os.chdir(sites_path)", source)
        self.assertIn('frappe.init(site=args.site, sites_path=".")', source)


class TestPlanConstants(unittest.TestCase):
    """Validate the locked plan matrix without a database."""

    @classmethod
    def setUpClass(cls):
        # constants.py has no frappe import, so it is safe to load by path.
        spec = importlib.util.spec_from_file_location(
            "bc_subscription_constants", os.path.join(SUB_DIR, "constants.py")
        )
        cls.constants = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.constants)

    def test_prices_and_minimums(self):
        plans = self.constants.PLAN_SEEDS
        self.assertEqual(plans["PROFESSIONAL"]["price_per_seat_per_year"], 595)
        self.assertEqual(plans["PROFESSIONAL"]["min_seats"], 1)
        self.assertEqual(plans["BUSINESS"]["price_per_seat_per_year"], 895)
        self.assertEqual(plans["BUSINESS"]["min_seats"], 5)
        self.assertEqual(plans["ENTERPRISE"]["price_per_seat_per_year"], 1295)
        self.assertEqual(plans["ENTERPRISE"]["min_seats"], 10)

    def test_business_caps(self):
        plans = self.constants.PLAN_SEEDS
        self.assertEqual(plans["PROFESSIONAL"]["max_businesses"], 1)
        self.assertEqual(plans["BUSINESS"]["max_businesses"], 3)
        self.assertEqual(plans["ENTERPRISE"]["max_businesses"], 5)

    def test_domain_entitlements(self):
        plans = self.constants.PLAN_SEEDS
        self.assertEqual(plans["PROFESSIONAL"]["included_domain_mappings"], 0)
        self.assertEqual(plans["BUSINESS"]["included_domain_mappings"], 0)
        self.assertEqual(plans["ENTERPRISE"]["included_domain_mappings"], 1)
        self.assertEqual(self.constants.DOMAIN_MAPPING_PRICE, 5999)

    def test_feature_gating_matrix(self):
        features = self.constants.PLAN_SEEDS
        for code in ("PROFESSIONAL", "BUSINESS", "ENTERPRISE"):
            snapshot = self.constants.feature_defaults(code)
            for key in self.constants.BASE_FEATURES:
                self.assertTrue(snapshot[key], "%s missing base feature %s" % (code, key))

        prof = self.constants.feature_defaults("PROFESSIONAL")
        for key in (
            "multiple_business_profiles",
            "team_management",
            "crm_access",
            "analytics",
            "import_export",
            "crm_full_control",
            "email_configuration",
            "whatsapp_configuration",
            "advanced_admin",
        ):
            self.assertFalse(prof[key], "Professional must not include %s" % key)

        biz = self.constants.feature_defaults("BUSINESS")
        self.assertTrue(biz["crm_access"])
        self.assertTrue(biz["analytics"])
        self.assertTrue(biz["import_export"])
        self.assertFalse(biz["advanced_admin"])
        self.assertFalse(biz["crm_full_control"])

        ent = self.constants.feature_defaults("ENTERPRISE")
        for key in self.constants.EXTRA_FEATURES:
            self.assertTrue(ent[key], "Enterprise missing %s" % key)

    def test_snapshot_defaults_fail_closed(self):
        unknown = self.constants.snapshot_defaults("NOT_A_PLAN")
        self.assertEqual(unknown["plan_code"], "NOT_A_PLAN")
        self.assertFalse(unknown["features"]["analytics"])
        self.assertEqual(unknown["limits"]["max_businesses"], 1)


class TestSubscriptionPermissionHook(unittest.TestCase):
    """Frappe v16 treats None as deny; subscription hooks must return True."""

    @classmethod
    def setUpClass(cls):
        stub = types.ModuleType("frappe")
        stub.session = types.SimpleNamespace(user="provider@example.com")
        previous = sys.modules.get("frappe")
        sys.modules["frappe"] = stub
        try:
            path = os.path.join(APP_DIR, "permissions", "__init__.py")
            spec = importlib.util.spec_from_file_location("bc_permissions_under_test", path)
            cls.permissions = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.permissions)
        finally:
            if previous is None:
                del sys.modules["frappe"]
            else:
                sys.modules["frappe"] = previous

    def test_subscription_doctypes_are_not_blocked_by_hook(self):
        for doctype in (
            "SaaS Plan",
            "Add-on Master",
            "Subscription",
            "Add-on Order",
            "Plan Restriction Log",
        ):
            doc = types.SimpleNamespace(doctype=doctype)
            result = self.permissions.has_permission(
                doc, user="provider@example.com", ptype="read"
            )
            self.assertIs(
                result,
                True,
                "%s must return True so DocPerms apply (got %r)" % (doctype, result),
            )


if __name__ == "__main__":
    unittest.main()
