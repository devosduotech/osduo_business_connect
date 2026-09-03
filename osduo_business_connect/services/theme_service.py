# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Theme Service

Handles theme resolution and CSS variable generation.
Static CSS is in public/css/business_connect.css.
Theme only supplies CSS custom properties.
"""

import frappe
from frappe import _


# Color scheme definitions
COLOR_SCHEMES = {
    "Violet": {"primary": "#7C3AED", "secondary": "#FFFFFF", "accent": "#A78BFA", "gradient_start": "#7C3AED", "gradient_end": "#A78BFA"},
    "Indigo": {"primary": "#4F46E5", "secondary": "#FFFFFF", "accent": "#818CF8", "gradient_start": "#4F46E5", "gradient_end": "#818CF8"},
    "Blue":   {"primary": "#2563EB", "secondary": "#FFFFFF", "accent": "#60A5FA", "gradient_start": "#2563EB", "gradient_end": "#60A5FA"},
    "Green":  {"primary": "#16A34A", "secondary": "#FFFFFF", "accent": "#4ADE80", "gradient_start": "#16A34A", "gradient_end": "#4ADE80"},
    "Yellow": {"primary": "#EAB308", "secondary": "#FFFFFF", "accent": "#FDE047", "gradient_start": "#EAB308", "gradient_end": "#FDE047"},
    "Orange": {"primary": "#EA580C", "secondary": "#FFFFFF", "accent": "#FB923C", "gradient_start": "#EA580C", "gradient_end": "#FB923C"},
    "Red":    {"primary": "#DC2626", "secondary": "#FFFFFF", "accent": "#F87171", "gradient_start": "#DC2626", "gradient_end": "#F87171"},
}


def get_business_theme(business_name):
    """
    Get the theme for a business.
    Uses Business.default_theme as authoritative source.

    Args:
        business_name: Business name

    Returns:
        dict: Theme data
    """
    default_theme = frappe.db.get_value("Business", business_name, "default_theme")
    if default_theme:
        return get_theme_data(default_theme)

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

    scheme = theme.color_scheme or "Blue"
    scheme_colors = COLOR_SCHEMES.get(scheme, COLOR_SCHEMES["Blue"])

    if scheme == "Custom":
        scheme_colors = {
            "primary": theme.primary_color or "#2563EB",
            "secondary": theme.secondary_color or "#FFFFFF",
            "accent": theme.accent_color or "#60A5FA",
            "gradient_start": theme.primary_color or "#2563EB",
            "gradient_end": theme.accent_color or "#60A5FA",
            "background": theme.background_color or "#F8FAFC",
            "font_color": theme.font_color or "#1E293B",
        }

    return {
        "name": theme.name,
        "theme_name": theme.theme_name or theme.name,
        "template": theme.template or "Modern",
        "color_scheme": scheme,
        "primary_color": scheme_colors["primary"],
        "secondary_color": scheme_colors["secondary"],
        "accent_color": scheme_colors["accent"],
        "gradient_start": scheme_colors["gradient_start"],
        "gradient_end": scheme_colors["gradient_end"],
        "background_color": scheme_colors.get("background", "#F8FAFC"),
        "font_color": scheme_colors.get("font_color", "#1E293B"),
        "button_style": theme.button_style or "Filled",
        "font_family": theme.font_family or "inherit",
    }


def get_default_theme():
    """
    Get default theme (Modern + Blue).

    Returns:
        dict: Default theme data
    """
    return {
        "name": None,
        "theme_name": "Default",
        "template": "Modern",
        "color_scheme": "Blue",
        "primary_color": "#2563EB",
        "secondary_color": "#FFFFFF",
        "accent_color": "#60A5FA",
        "gradient_start": "#2563EB",
        "gradient_end": "#60A5FA",
        "background_color": "#F8FAFC",
        "font_color": "#1E293B",
        "button_style": "Filled",
        "font_family": "inherit",
    }


def get_theme_variables(theme_data):
    """
    Generate CSS custom properties string from theme data.
    This is injected as inline style on .bc-page.

    Args:
        theme_data: Theme data dictionary

    Returns:
        str: CSS custom properties string
    """
    template = theme_data.get("template", "Modern")
    primary = theme_data.get("primary_color", "#2563EB")
    secondary = theme_data.get("secondary_color", "#FFFFFF")
    accent = theme_data.get("accent_color", "#60A5FA")
    gradient_start = theme_data.get("gradient_start", primary)
    gradient_end = theme_data.get("gradient_end", accent)
    button_style = theme_data.get("button_style", "Filled")
    font_family = theme_data.get("font_family") or "inherit"
    color_scheme = theme_data.get("color_scheme", "Blue")

    # Card elevation — derived from template
    card_elevation_map = {"Modern": "shadow", "Professional": "border", "Minimal": "none", "Classic": "shadow"}
    card_elevation = card_elevation_map.get(template, "shadow")
    shadow = "0 1px 3px rgba(0,0,0,0.1)" if card_elevation == "shadow" else "none"
    border = "1px solid #e2e8f0" if card_elevation == "border" else "none"

    # Border radius — derived from template
    radius_map = {"Modern": "8px", "Professional": "4px", "Minimal": "0px", "Classic": "12px"}
    card_radius = radius_map.get(template, "8px")

    # Button radius
    btn_radius_map = {"Filled": card_radius, "Outline": card_radius, "Rounded": "8px", "Pill": "999px"}
    btn_radius = btn_radius_map.get(button_style, card_radius)

    # Background — use custom if scheme is Custom, else template-based default
    if color_scheme == "Custom":
        background = theme_data.get("background_color", "#F8FAFC")
    else:
        background = "#f8fafc" if template != "Minimal" else "#ffffff"

    # Text color — use custom if scheme is Custom, else default
    text_color = theme_data.get("font_color", "#1E293B") if color_scheme == "Custom" else "#1e293b"

    # Header
    header_style_map = {
        "Modern": f"linear-gradient(135deg, {gradient_start}, {gradient_end})",
        "Professional": primary,
        "Minimal": secondary,
        "Classic": f"linear-gradient(180deg, {gradient_start}, {gradient_end})",
    }
    header_bg = header_style_map.get(template, header_style_map["Modern"])
    header_text = "white" if template != "Minimal" else primary

    # Section spacing
    spacing_map = {"Modern": "2rem 1.5rem", "Professional": "1.5rem 1.5rem", "Minimal": "1rem 1.5rem", "Classic": "2rem 1.5rem"}
    section_spacing = spacing_map.get(template, "2rem 1.5rem")

    vars_css = (
        f"--bc-primary: {primary};"
        f"--bc-secondary: {secondary};"
        f"--bc-accent: {accent};"
        f"--bc-background: {background};"
        f"--bc-text: {text_color};"
        f"--bc-card-radius: {card_radius};"
        f"--bc-btn-radius: {btn_radius};"
        f"--bc-font-family: {font_family};"
        f"--bc-header-bg: {header_bg};"
        f"--bc-header-text: {header_text};"
        f"--bc-section-spacing: {section_spacing};"
        f"--bc-card-shadow: {shadow};"
        f"--bc-card-border: {border};"
    )

    return vars_css
