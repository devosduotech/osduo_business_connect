# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Theme Service

This module handles theme-related operations for businesses.
Activation is handled by the Theme controller to ensure validation.
"""

import frappe
from frappe import _


def get_business_theme(business_name):
    """
    Get the active theme for a business.

    Args:
        business_name: Business name

    Returns:
        dict: Theme data or default theme
    """
    # Get active theme
    theme = frappe.get_all(
        "Theme",
        filters={
            "business": business_name,
            "active": 1,
        },
        fields=["name"],
        limit=1,
    )

    if theme:
        return get_theme_data(theme[0].name)

    # Return default theme
    return get_default_theme()


def get_theme_data(theme_name):
    """
    Get theme data by name.

    Args:
        theme_name: Theme name

    Returns:
        dict: Theme data
    """
    theme = frappe.get_doc("Theme", theme_name)

    return {
        "name": theme.name,
        "template": theme.template,
        "primary_color": theme.primary_color,
        "secondary_color": theme.secondary_color,
        "accent_color": theme.accent_color,
        "button_style": theme.button_style,
        "card_style": theme.card_style,
        "font_family": theme.font_family,
        "custom_settings": theme.custom_settings,
    }


def get_default_theme():
    """
    Get default theme settings.

    Returns:
        dict: Default theme data
    """
    return {
        "name": None,
        "template": "Modern",
        "primary_color": "#000000",
        "secondary_color": "#FFFFFF",
        "accent_color": "#007BFF",
        "button_style": "Filled",
        "card_style": "Modern",
        "font_family": None,
        "custom_settings": None,
    }


def activate_theme(theme_name):
    """
    Activate a theme and deactivate others for the same business.
    
    This delegates to the Theme controller which handles validation
    and deactivation of other themes.

    Args:
        theme_name: Theme name to activate

    Returns:
        bool: True if successful
    """
    theme = frappe.get_doc("Theme", theme_name)
    
    # Set active flag - the controller will handle deactivation of others
    theme.active = 1
    theme.save(ignore_permissions=True)
    
    return True


def get_theme_css(theme_data):
    """
    Generate CSS from theme data.

    Args:
        theme_data: Theme data dictionary

    Returns:
        str: CSS string
    """
    css = f"""
:root {{
    --primary-color: {theme_data.get('primary_color', '#000000')};
    --secondary-color: {theme_data.get('secondary_color', '#FFFFFF')};
    --accent-color: {theme_data.get('accent_color', '#007BFF')};
}}

body {{
    font-family: {theme_data.get('font_family', 'inherit')};
}}

.btn-primary {{
    background-color: var(--primary-color);
    border-color: var(--primary-color);
}}

.btn-secondary {{
    background-color: var(--secondary-color);
    border-color: var(--secondary-color);
}}

.card {{
    border-radius: {get_border_radius(theme_data.get('card_style', 'Modern'))};
}}
"""
    return css


def get_border_radius(style):
    """
    Get border radius based on card style.

    Args:
        style: Card style name

    Returns:
        str: Border radius value
    """
    styles = {
        "Modern": "8px",
        "Professional": "4px",
        "Minimal": "0px",
        "Classic": "12px",
    }
    return styles.get(style, "8px")
