# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

PLATFORM_ICONS = {
    "Facebook": "fa-brands fa-facebook",
    "Instagram": "fa-brands fa-instagram",
    "LinkedIn": "fa-brands fa-linkedin",
    "X": "fa-brands fa-x-twitter",
    "YouTube": "fa-brands fa-youtube",
    "Telegram": "fa-brands fa-telegram",
    "Website": "fa-solid fa-globe",
    "Portfolio": "fa-solid fa-briefcase",
    "Other": "fa-solid fa-link",
}


class BusinessSocialLink(Document):
    def before_save(self):
        if self.platform and not self.icon_class:
            self.icon_class = PLATFORM_ICONS.get(self.platform, "")
