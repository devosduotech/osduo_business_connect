# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Scheduler Module

Handles scheduled tasks for OSDuo Business Connect.
"""

import frappe
from frappe import _


def daily_tasks():
    """Run daily tasks."""
    # Retry failed CRM sync
    retry_pending_enquiries()
    # Expire custom-domain mappings at the subscription period end. This only
    # changes mapping/order status; public QR/NFC URLs stay stable.
    expire_subscription_domains()


def expire_subscription_domains():
    """Daily domain-expiry task (provider-controlled status stays untouched)."""
    try:
        from osduo_business_connect.subscription.domains import expire_domains

        expired = expire_domains()
        if expired:
            frappe.logger().info(f"Expired {expired} custom domain mapping(s)")
    except Exception as e:
        frappe.log_error(
            message=f"Failed to expire domains: {str(e)}",
            title="Domain Expiry Failed",
        )


def hourly_tasks():
    """Run hourly tasks."""
    # CRM Lead is authoritative when linked; conversions can bypass doc hooks,
    # so reconcile both Enquiry and Contact Exchange status on a bounded batch.
    reconcile_share_connect_statuses()
    # Recover Exchanges whose Enquiry creation failed. This is separate from
    # the daily CRM Lead retry handled by retry_pending_enquiries().
    retry_failed_enquiry_creation()


def reconcile_share_connect_statuses():
    """Hourly bounded status reconciliation for linked CRM Leads."""
    try:
        from osduo_business_connect.crm_integration.status_reconciliation import (
            reconcile_statuses,
        )
        updated = reconcile_statuses(limit=200)
        if updated:
            frappe.logger().info(
                f"Reconciled {updated} Share & Connect status record(s)"
            )
    except Exception as e:
        frappe.log_error(
            message=f"Failed to reconcile Share & Connect statuses: {str(e)}",
            title="Share & Connect Status Reconciliation Failed",
        )


def retry_failed_enquiry_creation():
    """Retry Enquiry creation for requested-but-failed Contact Exchanges."""
    try:
        from osduo_business_connect.card.enquiry_recovery import (
            retry_failed_enquiry_creation as retry,
        )
        recovered = retry(limit=100)
        if recovered:
            frappe.logger().info(
                f"Recovered {recovered} failed Share & Connect Enquiry creation(s)"
            )
    except Exception as e:
        frappe.log_error(
            message=f"Failed to recover pending Enquiries: {str(e)}",
            title="Share & Connect Enquiry Recovery Failed",
        )


def weekly_tasks():
    """Run weekly tasks."""
    pass


def retry_pending_enquiries():
    """
    Retry creating CRM Leads for enquiries that failed to sync.
    Called by scheduler (daily).
    """
    try:
        from osduo_business_connect.crm_integration.lead_mapper import retry_failed_enquiries
        synced_count = retry_failed_enquiries()
        if synced_count > 0:
            frappe.logger().info(f"Successfully synced {synced_count} enquiries to CRM")
    except Exception as e:
        frappe.log_error(
            message=f"Failed to retry CRM sync: {str(e)}",
            title="CRM Sync Retry Failed"
        )
