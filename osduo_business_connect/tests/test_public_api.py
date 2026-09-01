"""
Unit tests for Showcase Public API.

These tests verify:
- Public product API functionality
- Public service API functionality
- Serialization functions
"""

import os
import sys
import unittest

# Add parent directory to path for local testing
app_parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, app_parent_dir)


class TestPublicAPI(unittest.TestCase):
    """Tests for Public API."""

    def test_public_api_exists(self):
        """Test that public API file exists."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "public_api.py",
        )
        self.assertTrue(os.path.exists(api_path), "Public API not found")

    def test_public_api_has_get_public_product(self):
        """Test that public API has get_public_product function."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "public_api.py",
        )
        with open(api_path, "r") as f:
            content = f.read()
        self.assertIn("def get_public_product", content, "get_public_product function not found")

    def test_public_api_has_get_public_products(self):
        """Test that public API has get_public_products function."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "public_api.py",
        )
        with open(api_path, "r") as f:
            content = f.read()
        self.assertIn("def get_public_products", content, "get_public_products function not found")

    def test_public_api_has_get_public_service(self):
        """Test that public API has get_public_service function."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "public_api.py",
        )
        with open(api_path, "r") as f:
            content = f.read()
        self.assertIn("def get_public_service", content, "get_public_service function not found")

    def test_public_api_has_get_public_services(self):
        """Test that public API has get_public_services function."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "public_api.py",
        )
        with open(api_path, "r") as f:
            content = f.read()
        self.assertIn("def get_public_services", content, "get_public_services function not found")

    def test_public_api_has_serialize_product(self):
        """Test that public API has serialize_product function."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "public_api.py",
        )
        with open(api_path, "r") as f:
            content = f.read()
        self.assertIn("def serialize_product", content, "serialize_product function not found")

    def test_public_api_has_serialize_service(self):
        """Test that public API has serialize_service function."""
        api_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "public_api.py",
        )
        with open(api_path, "r") as f:
            content = f.read()
        self.assertIn("def serialize_service", content, "serialize_service function not found")


class TestPublicRoutes(unittest.TestCase):
    """Tests for Public Routes."""

    def test_product_route_exists(self):
        """Test that product route file exists."""
        route_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "product_route.py",
        )
        self.assertTrue(os.path.exists(route_path), "Product route not found")

    def test_product_route_has_get_context(self):
        """Test that product route has get_context function."""
        route_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "product_route.py",
        )
        with open(route_path, "r") as f:
            content = f.read()
        self.assertIn("def get_context", content, "get_context function not found")

    def test_service_route_exists(self):
        """Test that service route file exists."""
        route_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "service_route.py",
        )
        self.assertTrue(os.path.exists(route_path), "Service route not found")

    def test_service_route_has_get_context(self):
        """Test that service route has get_context function."""
        route_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "showcase",
            "showcase",
            "service_route.py",
        )
        with open(route_path, "r") as f:
            content = f.read()
        self.assertIn("def get_context", content, "get_context function not found")


if __name__ == "__main__":
    unittest.main()
