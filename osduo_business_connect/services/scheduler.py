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


def hourly_tasks():
    """Run hourly tasks."""
    pass


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
