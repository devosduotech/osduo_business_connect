# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Published public digital cards — served at ``/sitemap-cards.xml``."""

from osduo_business_connect.seo.sitemap import get_render_entries

no_cache = 1
base_template_path = "www/sitemap-cards.xml"


def get_context(context):
    context.urls = get_render_entries("cards")
    return context
