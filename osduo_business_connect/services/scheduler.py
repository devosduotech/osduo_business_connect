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
    retry_failed_crm_sync()


def hourly_tasks():
    """Run hourly tasks."""
    pass


def weekly_tasks():
    """Run weekly tasks."""
    pass


def retry_failed_crm_sync():
    """
    Retry failed CRM sync for all pending enquiries.
    
    This is a safe background operation that doesn't require user interaction.
    """
    try:
        from osduo_business_connect.enquiry.enquiry_service import retry_failed_sync
        
        synced_count = retry_failed_sync()
        if synced_count > 0:
            frappe.logger().info(f"Successfully synced {synced_count} enquiries to CRM")
            
    except Exception as e:
        frappe.log_error(
            message=f"Failed to retry CRM sync: {str(e)}",
            title="CRM Sync Retry Failed"
        )
