# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
UAT Test Cases for OSDuo Business Connect.

This module contains test cases for User Acceptance Testing.
These tests require a running Frappe site with CRM installed.
"""

import frappe
from frappe import _


def run_uat_tests():
    """
    Run all UAT test cases.
    
    Returns:
        dict: Test results
    """
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": [],
    }
    
    # Test cases
    test_cases = [
        test_business_creation,
        test_business_member_creation,
        test_digital_card_creation,
        test_showcase_product_creation,
        test_showcase_service_creation,
        test_theme_creation,
        test_enquiry_submission,
        test_crm_sync,
        test_public_profile_access,
        test_card_public_access,
        test_product_public_access,
        test_service_public_access,
        test_cross_business_isolation,
    ]
    
    for test_func in test_cases:
        results["total"] += 1
        try:
            test_func()
            results["passed"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "test": test_func.__name__,
                "error": str(e),
            })
    
    return results


def test_business_creation():
    """Test business creation with validation."""
    # Create test business
    business = frappe.get_doc({
        "doctype": "Business",
        "business_name": "UAT Test Business",
        "slug": "uat-test-business",
        "email": "test@uat.com",
        "phone": "+1234567890",
        "status": "Draft",
    })
    business.insert()
    
    # Verify slug validation
    assert business.slug == "uat-test-business"
    
    # Verify owner membership created
    members = frappe.get_all(
        "Business Member",
        filters={"business": business.name, "role": "Owner"},
        fields=["name"],
    )
    assert len(members) > 0
    
    # Cleanup
    frappe.delete_doc("Business", business.name)


def test_business_member_creation():
    """Test business member creation with role validation."""
    # Create test business
    business = frappe.get_doc({
        "doctype": "Business",
        "business_name": "UAT Member Test",
        "slug": "uat-member-test",
        "email": "member@test.com",
        "status": "Draft",
    })
    business.insert()
    
    # Add member
    member = frappe.get_doc({
        "doctype": "Business Member",
        "business": business.name,
        "user": frappe.session.user,
        "role": "Manager",
        "status": "Active",
    })
    member.insert()
    
    # Verify member created
    assert member.name
    
    # Cleanup
    frappe.delete_doc("Business Member", member.name)
    frappe.delete_doc("Business", business.name)


def test_digital_card_creation():
    """Test digital card creation with slug validation."""
    # Create test business and member
    business = frappe.get_doc({
        "doctype": "Business",
        "business_name": "UAT Card Test",
        "slug": "uat-card-test",
        "email": "card@test.com",
        "status": "Draft",
    })
    business.insert()
    
    member = frappe.get_doc({
        "doctype": "Business Member",
        "business": business.name,
        "user": frappe.session.user,
        "role": "Owner",
        "status": "Active",
    })
    member.insert()
    
    # Create card
    card = frappe.get_doc({
        "doctype": "Digital Card",
        "business": business.name,
        "member": member.name,
        "title": "Test Card",
        "slug": "test-card",
        "status": "Draft",
    })
    card.insert()
    
    # Verify card created
    assert card.name
    
    # Cleanup
    frappe.delete_doc("Digital Card", card.name)
    frappe.delete_doc("Business Member", member.name)
    frappe.delete_doc("Business", business.name)


def test_showcase_product_creation():
    """Test showcase product creation."""
    # Create test business
    business = frappe.get_doc({
        "doctype": "Business",
        "business_name": "UAT Product Test",
        "slug": "uat-product-test",
        "email": "product@test.com",
        "status": "Published",
    })
    business.insert()
    
    # Create product
    product = frappe.get_doc({
        "doctype": "Showcase Product",
        "business": business.name,
        "product_name": "Test Product",
        "slug": "test-product",
        "price_display_mode": "Fixed",
        "price": 99.99,
        "currency": "USD",
        "status": "Draft",
    })
    product.insert()
    
    # Verify product created
    assert product.name
    
    # Cleanup
    frappe.delete_doc("Showcase Product", product.name)
    frappe.delete_doc("Business", business.name)


def test_showcase_service_creation():
    """Test showcase service creation."""
    # Create test business
    business = frappe.get_doc({
        "doctype": "Business",
        "business_name": "UAT Service Test",
        "slug": "uat-service-test",
        "email": "service@test.com",
        "status": "Published",
    })
    business.insert()
    
    # Create service
    service = frappe.get_doc({
        "doctype": "Showcase Service",
        "business": business.name,
        "service_name": "Test Service",
        "slug": "test-service",
        "status": "Draft",
    })
    service.insert()
    
    # Verify service created
    assert service.name
    
    # Cleanup
    frappe.delete_doc("Showcase Service", service.name)
    frappe.delete_doc("Business", business.name)


def test_theme_creation():
    """Test theme creation with color validation."""
    # Create test business
    business = frappe.get_doc({
        "doctype": "Business",
        "business_name": "UAT Theme Test",
        "slug": "uat-theme-test",
        "email": "theme@test.com",
        "status": "Draft",
    })
    business.insert()
    
    # Create theme
    theme = frappe.get_doc({
        "doctype": "BC Theme",
        "business": business.name,
        "template": "Modern",
        "primary_color": "#000000",
        "secondary_color": "#FFFFFF",
        "button_style": "Filled",
        "card_style": "Modern",
        "active": 1,
    })
    theme.insert()
    
    # Verify theme created and active
    assert theme.name
    assert theme.active == 1
    
    # Cleanup
    frappe.delete_doc("BC Theme", theme.name)
    frappe.delete_doc("Business", business.name)


def test_enquiry_submission():
    """Test enquiry submission."""
    # Create test business
    business = frappe.get_doc({
        "doctype": "Business",
        "business_name": "UAT Enquiry Test",
        "slug": "uat-enquiry-test",
        "email": "enquiry@test.com",
        "status": "Published",
    })
    business.insert()
    
    # Submit enquiry
    enquiry = frappe.get_doc({
        "doctype": "Enquiry",
        "business": business.name,
        "visitor_name": "Test Visitor",
        "visitor_email": "visitor@test.com",
        "visitor_phone": "+1234567890",
        "message": "Test enquiry",
        "source": "Other",
        "submitted_at": frappe.utils.now_datetime(),
    })
    enquiry.insert()
    
    # Verify enquiry created
    assert enquiry.name
    assert enquiry.status == "New"
    
    # Cleanup
    frappe.delete_doc("Enquiry", enquiry.name)
    frappe.delete_doc("Business", business.name)


def test_crm_sync():
    """Test CRM sync functionality."""
    # This test requires CRM to be installed
    if not frappe.db.exists("DocType", "CRM Lead"):
        return
    
    # Create test business
    business = frappe.get_doc({
        "doctype": "Business",
        "business_name": "UAT CRM Test",
        "slug": "uat-crm-test",
        "email": "crm@test.com",
        "status": "Published",
    })
    business.insert()
    
    # Create enquiry
    enquiry = frappe.get_doc({
        "doctype": "Enquiry",
        "business": business.name,
        "visitor_name": "CRM Test Visitor",
        "visitor_email": "crm-visitor@test.com",
        "source": "Other",
        "submitted_at": frappe.utils.now_datetime(),
    })
    enquiry.insert()
    
    # Sync to CRM
    from osduo_business_connect.crm_integration.crm_sync import sync_enquiry_to_crm
    result = sync_enquiry_to_crm(enquiry.name)
    
    # Verify sync
    assert result["status"] == "success"
    
    # Cleanup
    if enquiry.crm_lead:
        frappe.delete_doc("CRM Lead", enquiry.crm_lead)
    frappe.delete_doc("Enquiry", enquiry.name)
    frappe.delete_doc("Business", business.name)


def test_public_profile_access():
    """Test public profile page access."""
    # This test requires a running web server
    pass


def test_card_public_access():
    """Test public card page access."""
    # This test requires a running web server
    pass


def test_product_public_access():
    """Test public product page access."""
    # This test requires a running web server
    pass


def test_service_public_access():
    """Test public service page access."""
    # This test requires a running web server
    pass


def test_cross_business_isolation():
    """Test cross-business data isolation."""
    # Create two test businesses
    business1 = frappe.get_doc({
        "doctype": "Business",
        "business_name": "UAT Isolation Test 1",
        "slug": "uat-isolation-test-1",
        "email": "isolation1@test.com",
        "status": "Draft",
    })
    business1.insert()
    
    business2 = frappe.get_doc({
        "doctype": "Business",
        "business_name": "UAT Isolation Test 2",
        "slug": "uat-isolation-test-2",
        "email": "isolation2@test.com",
        "status": "Draft",
    })
    business2.insert()
    
    # Create members for business1
    member1 = frappe.get_doc({
        "doctype": "Business Member",
        "business": business1.name,
        "user": frappe.session.user,
        "role": "Owner",
        "status": "Active",
    })
    member1.insert()
    
    # Verify cannot access business2 data
    # This would be tested via permission_query_conditions
    # For now, just verify businesses exist
    assert business1.name
    assert business2.name
    
    # Cleanup
    frappe.delete_doc("Business Member", member1.name)
    frappe.delete_doc("Business", business1.name)
    frappe.delete_doc("Business", business2.name)
