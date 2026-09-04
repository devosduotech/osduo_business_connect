# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Website branding context injection.

Injects branding variables into all web templates so they can
use {{ bc_app_name }}, {{ bc_logo }}, etc. without hardcoding.
"""

import frappe

from osduo_business_connect.hooks import OSDUO_BRANDING


def get_branding_context(context):
    """
    Add branding variables to website context.

    Called via update_website_context hook in hooks.py.
    Available in all web templates as {{ bc_app_name }}, {{ bc_logo }}, etc.
    """
    context.update({
        "bc_app_name": OSDUO_BRANDING["app_name"],
        "bc_app_short_name": OSDUO_BRANDING["app_short_name"],
        "bc_tagline": OSDUO_BRANDING["tagline"],
        "bc_logo": OSDUO_BRANDING["logo"],
        "bc_logo_white": OSDUO_BRANDING["logo_white"],
        "bc_favicon": OSDUO_BRANDING["favicon"],
        "bc_logo_mark": OSDUO_BRANDING["logo_mark"],
        "bc_primary_color": OSDUO_BRANDING["primary_color"],
        "bc_secondary_color": OSDUO_BRANDING["secondary_color"],
        "bc_accent_color": OSDUO_BRANDING["accent_color"],
        "bc_background_color": OSDUO_BRANDING["background_color"],
        "bc_text_color": OSDUO_BRANDING["text_color"],
    })
