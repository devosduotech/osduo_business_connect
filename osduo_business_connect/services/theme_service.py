# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Theme Service

Handles theme resolution and CSS variable generation.
Static CSS is in public/css/business_connect.css.
Theme only supplies CSS custom properties.
"""

import re
import frappe
from frappe import _


def sanitize_css_value(value, fallback=""):
    """Sanitize a value for safe CSS interpolation.

    Only allows safe characters: hex colors, px, rem, em, %, rgba, etc.
    Strips anything that could inject CSS (semicolons, braces, url(), etc.).
    """
    if not value:
        return fallback
    value = str(value).strip()
    # Remove dangerous patterns
    value = re.sub(r'[;{}()]\s*', '', value)
    value = re.sub(r'url\s*\(', '', value, flags=re.IGNORECASE)
    value = re.sub(r'expression\s*\(', '', value, flags=re.IGNORECASE)
    value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
    # Limit length to prevent abuse
    if len(value) > 200:
        value = value[:200]
    return value or fallback


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

# Font family mapping — Select label → CSS font-family
FONT_FAMILY_MAP = {
    "System Default": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif",
    "Inter": "'Inter', sans-serif",
    "Roboto": "'Roboto', sans-serif",
    "Open Sans": "'Open Sans', sans-serif",
    "Lato": "'Lato', sans-serif",
    "Poppins": "'Poppins', sans-serif",
    "Montserrat": "'Montserrat', sans-serif",
    "Nunito": "'Nunito', sans-serif",
    "Source Sans 3": "'Source Sans 3', sans-serif",
    "Raleway": "'Raleway', sans-serif",
}

# Font size presets — label → CSS font-size
FONT_SIZE_MAP = {
    "Small": "14px",
    "Default": "16px",
    "Large": "18px",
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
    theme_data = frappe.db.get_value(
        "BC Theme", theme_name,
        ["theme_name", "template", "color_scheme", "primary_color", "secondary_color",
         "accent_color", "background_color", "font_color", "button_style",
         "font_family", "font_size"],
        as_dict=True,
    )
    if not theme_data:
        return get_default_theme()

    scheme = theme_data.color_scheme or "Blue"
    scheme_colors = COLOR_SCHEMES.get(scheme, COLOR_SCHEMES["Blue"])

    if scheme == "Custom":
        scheme_colors = {
            "primary": theme_data.primary_color or "#2563EB",
            "secondary": theme_data.secondary_color or "#FFFFFF",
            "accent": theme_data.accent_color or "#60A5FA",
            "gradient_start": theme_data.primary_color or "#2563EB",
            "gradient_end": theme_data.accent_color or "#60A5FA",
            "background": theme_data.background_color or "#F8FAFC",
            "font_color": theme_data.font_color or "#1E293B",
        }

    return {
        "name": theme_name,
        "theme_name": theme_data.theme_name or theme_name,
        "template": theme_data.template or "Modern",
        "color_scheme": scheme,
        "primary_color": scheme_colors["primary"],
        "secondary_color": scheme_colors["secondary"],
        "accent_color": scheme_colors["accent"],
        "gradient_start": scheme_colors["gradient_start"],
        "gradient_end": scheme_colors["gradient_end"],
        "background_color": scheme_colors.get("background", "#F8FAFC"),
        "font_color": scheme_colors.get("font_color", "#1E293B"),
        "button_style": theme_data.button_style or "Filled",
        "font_family": theme_data.font_family or "System Default",
        "font_size": theme_data.font_size or "Default",
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
        "font_family": "System Default",
        "font_size": "Default",
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
    font_family_raw = theme_data.get("font_family") or "System Default"
    font_family = FONT_FAMILY_MAP.get(font_family_raw, FONT_FAMILY_MAP["System Default"])
    font_size_raw = theme_data.get("font_size") or "Default"
    font_size = FONT_SIZE_MAP.get(font_size_raw, FONT_SIZE_MAP["Default"])
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
        f"--bc-primary: {sanitize_css_value(primary)};"
        f"--bc-secondary: {sanitize_css_value(secondary)};"
        f"--bc-accent: {sanitize_css_value(accent)};"
        f"--bc-background: {sanitize_css_value(background)};"
        f"--bc-text: {sanitize_css_value(text_color)};"
        f"--bc-card-radius: {sanitize_css_value(card_radius)};"
        f"--bc-btn-radius: {sanitize_css_value(btn_radius)};"
        f"--bc-font-family: {sanitize_css_value(font_family)};"
        f"--bc-font-size: {sanitize_css_value(font_size)};"
        f"--bc-header-bg: {sanitize_css_value(header_bg)};"
        f"--bc-header-text: {sanitize_css_value(header_text)};"
        f"--bc-section-spacing: {sanitize_css_value(section_spacing)};"
        f"--bc-card-shadow: {sanitize_css_value(shadow)};"
        f"--bc-card-border: {sanitize_css_value(border)};"
    )

    return vars_css
