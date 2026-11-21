# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""Controller for the app's /login override.

Reuse Frappe's controller so social login, OTP, signup and redirect handling
stay identical to core. Only the template is overridden.
"""

from frappe.www.login import *  # noqa: F401,F403
