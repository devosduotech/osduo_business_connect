import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from osduo_business_connect.utils.money import format_money

APP_DIR = os.path.join(os.path.dirname(__file__), "..")
PARTS_DIR = os.path.join(APP_DIR, "templates", "pages", "product", "parts")
CARD_TEMPLATE = os.path.join(APP_DIR, "templates", "pages", "card", "card.html")

HERO_TEMPLATES = [
    "hero_modern.html",
    "hero_classic.html",
    "hero_professional.html",
    "hero_minimal.html",
    "hero_luxury.html",
    "hero_creative.html",
]


def read(path):
    with open(path) as f:
        return f.read()


class TestFormatMoney(unittest.TestCase):
    """Formatting rules for the public price display."""

    def test_thousands_separator(self):
        self.assertEqual(format_money(12000, "INR"), "INR 12,000")
        self.assertEqual(format_money(140000, "INR"), "INR 140,000")
        self.assertEqual(format_money(1000000, "INR"), "INR 1,000,000")

    def test_small_amount_has_no_separator(self):
        self.assertEqual(format_money(999, "INR"), "INR 999")

    def test_whole_amount_drops_decimals(self):
        self.assertEqual(format_money(12000.0, "INR"), "INR 12,000")

    def test_fractional_amount_keeps_two_decimals(self):
        self.assertEqual(format_money(12000.5, "INR"), "INR 12,000.50")

    def test_rounds_before_dropping_decimals(self):
        self.assertEqual(format_money(12000.999, "INR"), "INR 12,001")

    def test_explicit_precision_is_respected(self):
        self.assertEqual(format_money(12000, "INR", 2), "INR 12,000.00")

    def test_currency_code_prefix(self):
        self.assertEqual(format_money(500, "USD"), "USD 500")

    def test_amount_without_currency(self):
        self.assertEqual(format_money(140000), "140,000")

    def test_missing_amount_returns_empty_string(self):
        self.assertEqual(format_money(None, "INR"), "")
        self.assertEqual(format_money("", "INR"), "")

    def test_non_numeric_amount_is_returned_as_text(self):
        self.assertEqual(format_money("on request", "INR"), "on request")


class TestPriceTemplatesUseFormatMoney(unittest.TestCase):
    """Guard against re-introducing raw, unformatted prices."""

    def test_hero_templates_format_price(self):
        for name in HERO_TEMPLATES:
            body = read(os.path.join(PARTS_DIR, name))
            self.assertIn("format_money", body, f"{name} must format prices")
            self.assertNotIn("{{ doc.price }}", body, f"{name} still renders raw price")
            self.assertNotIn("{{ doc.currency }}", body, f"{name} still renders raw currency")

    def test_card_template_formats_price(self):
        body = read(CARD_TEMPLATE)
        self.assertIn("product.price | format_money(product.currency)", body)
        self.assertIn("service.price | format_money(service.currency)", body)
        self.assertNotIn("{{ product.price }}", body)
        self.assertNotIn("{{ service.price }}", body)


class TestJinjaHookRegistersMoneyFilter(unittest.TestCase):
    """The money module must be wired into the Jinja filter hook."""

    def test_money_module_in_jinja_filters(self):
        body = read(os.path.join(APP_DIR, "hooks.py"))
        self.assertIn("osduo_business_connect.utils.money", body)


if __name__ == "__main__":
    unittest.main()
