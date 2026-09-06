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
    Strips anything that could inject CSS (semicolons, braces, url(), etc.)
    or break out of an HTML style attribute (quotes).
    """
    if not value:
        return fallback
    value = str(value).strip()
    # Remove dangerous patterns
    value = re.sub(r'[;{}()]\s*', '', value)
    value = re.sub(r'url\s*\(', '', value, flags=re.IGNORECASE)
    value = re.sub(r'expression\s*\(', '', value, flags=re.IGNORECASE)
    value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
    # Strip quotes to prevent style attribute breakout
    value = value.replace("'", '').replace('"', '')
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
    "Gold":   {"primary": "#D4AF37", "secondary": "#1A1A2E", "accent": "#F5D060", "gradient_start": "#D4AF37", "gradient_end": "#F5D060"},
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
    "Playfair Display": "'Playfair Display', serif",
    "Merriweather": "'Merriweather', serif",
    "Space Grotesk": "'Space Grotesk', sans-serif",
}

# Font size presets — label → CSS font-size
FONT_SIZE_MAP = {
    "Small": "14px",
    "Default": "16px",
    "Large": "18px",
}

# Template → default layout mode
LAYOUT_MAP = {
    "Modern": "Centered",
    "Professional": "Wide",
    "Minimal": "Centered",
    "Classic": "Centered",
    "Luxury": "Editorial",
    "Creative": "Editorial",
}

# Template → default font category (kept for reference, field removed from DocType)

# Template → default dark mode
DARK_MODE_MAP = {
    "Modern": False,
    "Professional": False,
    "Minimal": False,
    "Classic": False,
    "Luxury": True,
    "Creative": False,
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
         "font_family", "font_size", "layout_mode", "dark_mode"],
        as_dict=True,
    )
    if not theme_data:
        return get_default_theme()

    template = theme_data.template or "Modern"
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
        "template": template,
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
        "layout_mode": theme_data.layout_mode or LAYOUT_MAP.get(template, "Centered"),
        "dark_mode": theme_data.dark_mode if theme_data.dark_mode is not None else DARK_MODE_MAP.get(template, False),
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
        "layout_mode": "Centered",
        "dark_mode": False,
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
    layout_mode = theme_data.get("layout_mode") or LAYOUT_MAP.get(template, "Centered")
    dark_mode = theme_data.get("dark_mode", False)

    # Card elevation — derived from template
    card_elevation_map = {
        "Modern": "shadow", "Professional": "border", "Minimal": "none",
        "Classic": "shadow", "Luxury": "none", "Creative": "shadow",
    }
    card_elevation = card_elevation_map.get(template, "shadow")
    shadow = "0 1px 3px rgba(0,0,0,0.1)" if card_elevation == "shadow" else "none"
    border = "1px solid #e2e8f0" if card_elevation == "border" else "none"

    # Border radius — derived from template
    radius_map = {
        "Modern": "8px", "Professional": "4px", "Minimal": "0px",
        "Classic": "12px", "Luxury": "2px", "Creative": "8px",
    }
    card_radius = radius_map.get(template, "8px")

    # Button radius
    btn_radius_map = {"Filled": card_radius, "Outline": card_radius, "Rounded": "8px", "Pill": "999px"}
    btn_radius = btn_radius_map.get(button_style, card_radius)

    # Background — dark mode or template-based
    if dark_mode:
        background = "#0f172a"
    elif color_scheme == "Custom":
        background = theme_data.get("background_color", "#F8FAFC")
    else:
        bg_map = {"Minimal": "#ffffff", "Luxury": "#0f172a", "Creative": "#fafafa"}
        background = bg_map.get(template, "#f8fafc")

    # Text color
    if dark_mode:
        text_color = "#e2e8f0"
    elif color_scheme == "Custom":
        text_color = theme_data.get("font_color", "#1E293B")
    else:
        text_color = "#0f172a" if template == "Luxury" else "#1e293b"

    # Surface color (cards, sections)
    surface = "#1e293b" if dark_mode else "#ffffff"

    # Border color
    border_color = "#334155" if dark_mode else "#e2e8f0"

    # Header
    if template == "Luxury":
        header_bg = "transparent"
    elif template == "Creative":
        header_bg = f"linear-gradient(135deg, {gradient_start}, {gradient_end})"
    elif template == "Modern":
        header_bg = f"linear-gradient(135deg, {gradient_start}, {gradient_end})"
    elif template == "Professional":
        header_bg = primary
    elif template == "Minimal":
        header_bg = "transparent"
    elif template == "Classic":
        header_bg = f"linear-gradient(180deg, {gradient_start}, {gradient_end})"
    else:
        header_bg = f"linear-gradient(135deg, {gradient_start}, {gradient_end})"

    if template == "Minimal":
        header_text = primary
    elif template == "Luxury":
        header_text = "#e2e8f0" if dark_mode else "#ffffff"
    else:
        header_text = "white"

    # Section spacing
    spacing_map = {
        "Modern": "2rem 1.5rem", "Professional": "1.5rem 1.5rem",
        "Minimal": "1rem 1.5rem", "Classic": "2rem 1.5rem",
        "Luxury": "3rem 2rem", "Creative": "2.5rem 1.5rem",
    }
    section_spacing = spacing_map.get(template, "2rem 1.5rem")

    # Display font (for hero/title text)
    display_font_map = {
        "Modern": font_family,
        "Professional": font_family,
        "Minimal": font_family,
        "Classic": font_family,
        "Luxury": "'Playfair Display', serif",
        "Creative": "'Space Grotesk', sans-serif",
    }
    display_font = display_font_map.get(template, font_family)

    vars_css = (
        f"--bc-primary: {sanitize_css_value(primary)};"
        f"--bc-secondary: {sanitize_css_value(secondary)};"
        f"--bc-accent: {sanitize_css_value(accent)};"
        f"--bc-background: {sanitize_css_value(background)};"
        f"--bc-text: {sanitize_css_value(text_color)};"
        f"--bc-surface: {sanitize_css_value(surface)};"
        f"--bc-border-color: {sanitize_css_value(border_color)};"
        f"--bc-card-radius: {sanitize_css_value(card_radius)};"
        f"--bc-btn-radius: {sanitize_css_value(btn_radius)};"
        f"--bc-font-family: {sanitize_css_value(font_family)};"
        f"--bc-display-font: {sanitize_css_value(display_font)};"
        f"--bc-font-size: {sanitize_css_value(font_size)};"
        f"--bc-header-bg: {sanitize_css_value(header_bg)};"
        f"--bc-header-text: {sanitize_css_value(header_text)};"
        f"--bc-section-spacing: {sanitize_css_value(section_spacing)};"
        f"--bc-card-shadow: {sanitize_css_value(shadow)};"
        f"--bc-card-border: {sanitize_css_value(border)};"
    )

    return vars_css
