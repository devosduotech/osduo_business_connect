#!/usr/bin/env python3
# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Operator CLI for manual plan provisioning.

Run from the bench root with Frappe on the Python path::

    python3 scripts/provision_customer_site.py --site mysite.local provision \
        --plan BUSINESS --seats 5

    python3 scripts/provision_customer_site.py --site mysite.local status \
        "Past Due" --grace-until 2027-01-15

No payment, invoice or order is created here. The plan/seat state must already
have been agreed with the customer in Aasriva.
"""

import argparse
import json
import sys


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", required=True, help="Frappe site name")
    parser.add_argument(
        "--sites-path",
        default="sites",
        help="Path to the bench sites directory (default: sites)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    provision = sub.add_parser("provision", help="Create/refresh the site's Subscription")
    provision.add_argument(
        "--plan", required=True, choices=["PROFESSIONAL", "BUSINESS", "ENTERPRISE"]
    )
    provision.add_argument("--seats", type=int, help="Defaults to the plan minimum")
    provision.add_argument("--status", default="Active")
    provision.add_argument("--external-crm", action="store_true", default=False)
    provision.add_argument("--hostname", help="Optional host_name to set (additive domain policy)")
    provision.add_argument("--start-date", help="YYYY-MM-DD; defaults to today")
    provision.add_argument("--external-ref", help="Reserved for Aasriva reference")
    provision.add_argument("--notes")
    provision.add_argument("--dry-run", action="store_true")
    provision.add_argument("--force", action="store_true")

    status = sub.add_parser("status", help="Apply a provider-controlled status change")
    status.add_argument("status")
    status.add_argument("--grace-until", help="YYYY-MM-DD, used with Past Due")
    status.add_argument("--note")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    try:
        import frappe
    except ImportError:
        print(
            "Frappe is not importable. Run this script from the bench root with "
            "the bench Python environment.",
            file=sys.stderr,
        )
        return 2

    frappe.init(site=args.site, sites_path=args.sites_path)
    frappe.connect()
    try:
        from osduo_business_connect.subscription.provision import (
            provision_site,
            set_status,
        )

        if args.command == "provision":
            result = provision_site(
                plan_code=args.plan,
                seats=args.seats,
                status=args.status,
                external_crm=args.external_crm,
                hostname=args.hostname,
                start_date=args.start_date,
                external_ref=args.external_ref,
                notes=args.notes,
                provisioned_by="Administrator",
                dry_run=args.dry_run,
                force=args.force,
            )
        else:
            result = set_status(
                args.status,
                grace_until=args.grace_until,
                note=args.note,
                user="Administrator",
            )

        print(json.dumps(result, indent=2, default=str))
        return 0
    finally:
        frappe.destroy()


if __name__ == "__main__":
    sys.exit(main())
