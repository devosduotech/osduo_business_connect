__version__ = "1.0.1"
app_name = "osduo_business_connect"

# Apply website route fix for Frappe v16 bug
# (evaluate_dynamic_routes prepends "/" to path that already has one)
from osduo_business_connect.patches.website_route_fix import apply_patch
apply_patch()
