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

    Only allows safe characters: hex colors, px, rem, em, %, rgba, gradients, etc.
    Strips anything that could inject CSS (semicolons, braces) or break HTML attributes.
    Preserves parentheses (needed for linear-gradient, rgba, etc.) and quotes
    (needed for multi-word font names like 'Playfair Display').
    """
    if not value:
        return fallback
    value = str(value).strip()
    # Remove dangerous patterns (but preserve parens for CSS functions)
    value = re.sub(r'[;{}]\s*', '', value)
    value = re.sub(r'url\s*\(', '', value, flags=re.IGNORECASE)
    value = re.sub(r'expression\s*\(', '', value, flags=re.IGNORECASE)
    value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
    # Limit length to prevent abuse
    if len(value) > 200:
        value = value[:200]
    return value or fallback


# Color scheme definitions
# primary_dark  -> header gradient end / hover states
# on_primary    -> readable text colour on a primary surface
# gradient_*    -> banner gradients (primary -> accent, per colour-schemes design)
COLOR_SCHEMES = {
    "Violet": {"primary": "#7C3AED", "primary_dark": "#6D28D9", "on_primary": "#FFFFFF", "secondary": "#FFFFFF", "accent": "#A78BFA", "gradient_start": "#7C3AED", "gradient_end": "#A78BFA"},
    "Indigo": {"primary": "#4F46E5", "primary_dark": "#4338CA", "on_primary": "#FFFFFF", "secondary": "#FFFFFF", "accent": "#818CF8", "gradient_start": "#4F46E5", "gradient_end": "#818CF8"},
    "Blue":   {"primary": "#2563EB", "primary_dark": "#1E40AF", "on_primary": "#FFFFFF", "secondary": "#FFFFFF", "accent": "#60A5FA", "gradient_start": "#2563EB", "gradient_end": "#60A5FA"},
    "Green":  {"primary": "#16A34A", "primary_dark": "#15803D", "on_primary": "#FFFFFF", "secondary": "#FFFFFF", "accent": "#4ADE80", "gradient_start": "#16A34A", "gradient_end": "#4ADE80"},
    "Yellow": {"primary": "#EAB308", "primary_dark": "#CA8A04", "on_primary": "#1E293B", "secondary": "#FFFFFF", "accent": "#FDE047", "gradient_start": "#EAB308", "gradient_end": "#FDE047"},
    "Orange": {"primary": "#EA580C", "primary_dark": "#C2410C", "on_primary": "#FFFFFF", "secondary": "#FFFFFF", "accent": "#FB923C", "gradient_start": "#EA580C", "gradient_end": "#FB923C"},
    "Red":    {"primary": "#DC2626", "primary_dark": "#B91C1C", "on_primary": "#FFFFFF", "secondary": "#FFFFFF", "accent": "#F87171", "gradient_start": "#DC2626", "gradient_end": "#F87171"},
    "Gold":   {"primary": "#D4AF37", "primary_dark": "#B8860B", "on_primary": "#1A1A2E", "secondary": "#1A1A2E", "accent": "#F5D060", "gradient_start": "#D4AF37", "gradient_end": "#F5D060"},
}


def _parse_hex(value, fallback="#2563EB"):
    """Return (r, g, b) for a #rrggbb value, falling back when invalid."""
    value = (value or fallback).strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6:
        value = fallback.lstrip("#")
    try:
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return _parse_hex(fallback, fallback)


def _rgb_to_hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def darken(hex_color, amount=0.12, fallback="#2563EB"):
    """Darken a hex colour by `amount` (0..1)."""
    r, g, b = _parse_hex(hex_color, fallback)
    return _rgb_to_hex((r * (1 - amount), g * (1 - amount), b * (1 - amount)))


def mix_with_white(hex_color, amount=0.9, fallback="#2563EB"):
    """Mix a hex colour with white. amount=0.9 -> 10% colour, 90% white."""
    r, g, b = _parse_hex(hex_color, fallback)
    return _rgb_to_hex((
        r + (255 - r) * amount,
        g + (255 - g) * amount,
        b + (255 - b) * amount,
    ))


def _relative_luminance(hex_color):
    r, g, b = (c / 255 for c in _parse_hex(hex_color))
    channels = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def on_color(hex_color):
    """Return a readable text colour for the given background."""
    return "#1E293B" if _relative_luminance(hex_color) > 0.45 else "#FFFFFF"


def on_color_auto(hex_color):
    """Pick the text colour (dark or white) with the higher contrast."""
    dark, light = "#1E293B", "#FFFFFF"
    return dark if contrast_ratio(dark, hex_color) >= contrast_ratio(light, hex_color) else light


def contrast_ratio(color_a, color_b):
    """WCAG contrast ratio between two hex colours."""
    l_a = _relative_luminance(color_a)
    l_b = _relative_luminance(color_b)
    lighter, darker = max(l_a, l_b), min(l_a, l_b)
    return (lighter + 0.05) / (darker + 0.05)


def fill_for(base_color, text_color, min_ratio=4.5):
    """Return a fill colour that gives text_color at least min_ratio contrast.

    Keeps the brand colour when it already works; otherwise darkens (for light
    text) or lightens (for dark text) just enough to pass.
    """
    if contrast_ratio(text_color, base_color) >= min_ratio:
        return base_color
    color = base_color
    if _relative_luminance(text_color) >= 0.5:
        # Light text -> darken the fill.
        for _ in range(24):
            color = darken(color, 0.06, base_color)
            if contrast_ratio(text_color, color) >= min_ratio:
                return color
    else:
        # Dark text -> lighten the fill.
        for step in range(1, 25):
            color = mix_with_white(base_color, step * 0.04, base_color)
            if contrast_ratio(text_color, color) >= min_ratio:
                return color
    return base_color


def readable_on(base_color, background, min_ratio=4.5):
    """Adjust base_color until it has at least min_ratio contrast on background."""
    color = base_color
    if contrast_ratio(color, background) >= min_ratio:
        return color
    # Light background -> darken; dark background -> lighten.
    if _relative_luminance(background) >= 0.5:
        for _ in range(20):
            color = darken(color, 0.06, base_color)
            if contrast_ratio(color, background) >= min_ratio:
                return color
    else:
        for step in range(1, 21):
            color = mix_with_white(base_color, step * 0.05, base_color)
            if contrast_ratio(color, background) >= min_ratio:
                return color
    return on_color(background)

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
        primary = theme_data.primary_color or "#2563EB"
        accent = theme_data.accent_color or "#60A5FA"
        scheme_colors = {
            "primary": primary,
            "primary_dark": darken(primary, 0.12, "#2563EB"),
            "on_primary": on_color(primary),
            "secondary": theme_data.secondary_color or "#FFFFFF",
            "accent": accent,
            "gradient_start": primary,
            "gradient_end": accent,
            "background": theme_data.background_color or "#F8FAFC",
            "font_color": theme_data.font_color or "#1E293B",
        }

    return {
        "name": theme_name,
        "theme_name": theme_data.theme_name or theme_name,
        "template": template,
        "color_scheme": scheme,
        "primary_color": scheme_colors["primary"],
        "primary_dark": scheme_colors.get("primary_dark") or darken(scheme_colors["primary"]),
        "on_primary": scheme_colors.get("on_primary") or on_color(scheme_colors["primary"]),
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
        "primary_dark": "#1E40AF",
        "on_primary": "#FFFFFF",
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
    primary_dark = theme_data.get("primary_dark") or darken(primary)
    on_primary = theme_data.get("on_primary") or on_color(primary)
    secondary = theme_data.get("secondary_color", "#FFFFFF")
    accent = theme_data.get("accent_color", "#60A5FA")
    gradient_start = theme_data.get("gradient_start", primary)
    gradient_end = theme_data.get("gradient_end", accent)
    primary_soft = mix_with_white(primary, 0.90)
    primary_tint = mix_with_white(primary, 0.78)
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

    # Supporting text colours
    if dark_mode:
        text_muted, text_faint = "#cbd5e1", "#94a3b8"
    else:
        text_muted, text_faint = "#475569", "#94a3b8"

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
        header_text = on_primary

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

    primary_text = readable_on(primary, surface)
    primary_fill = fill_for(primary, on_primary)
    on_accent = on_color_auto(accent)
    accent_fill = fill_for(accent, on_accent)

    vars_css = (
        f"--bc-primary: {sanitize_css_value(primary)};"
        f"--bc-primary-dark: {sanitize_css_value(primary_dark)};"
        f"--bc-primary-soft: {sanitize_css_value(primary_soft)};"
        f"--bc-primary-tint: {sanitize_css_value(primary_tint)};"
        f"--bc-on-primary: {sanitize_css_value(on_primary)};"
        f"--bc-on-accent: {sanitize_css_value(on_accent)};"
        f"--bc-primary-text: {sanitize_css_value(primary_text)};"
        f"--bc-primary-fill: {sanitize_css_value(primary_fill)};"
        f"--bc-accent-fill: {sanitize_css_value(accent_fill)};"
        f"--bc-secondary: {sanitize_css_value(secondary)};"
        f"--bc-accent: {sanitize_css_value(accent)};"
        f"--bc-background: {sanitize_css_value(background)};"
        f"--bc-text: {sanitize_css_value(text_color)};"
        f"--bc-text-strong: {sanitize_css_value(text_color)};"
        f"--bc-text-muted: {sanitize_css_value(text_muted)};"
        f"--bc-text-faint: {sanitize_css_value(text_faint)};"
        f"--bc-surface: {sanitize_css_value(surface)};"
        f"--bc-border-color: {sanitize_css_value(border_color)};"
        f"--bc-card-radius: {sanitize_css_value(card_radius)};"
        f"--bc-radius-sm: 8px;"
        f"--bc-radius-md: {sanitize_css_value(card_radius)};"
        f"--bc-radius-lg: {sanitize_css_value('12px' if template == 'Professional' else card_radius)};"
        f"--bc-btn-radius: {sanitize_css_value(btn_radius)};"
        f"--bc-font-family: {sanitize_css_value(font_family)};"
        f"--bc-display-font: {sanitize_css_value(display_font)};"
        f"--bc-font-size: {sanitize_css_value(font_size)};"
        f"--bc-header-bg: {sanitize_css_value(header_bg)};"
        f"--bc-header-text: {sanitize_css_value(header_text)};"
        f"--bc-section-spacing: {sanitize_css_value(section_spacing)};"
        f"--bc-card-shadow: {sanitize_css_value('0 1px 3px rgba(0,0,0,0.1)' if card_elevation == 'shadow' else 'none')};"
        f"--bc-card-shadow-md: {sanitize_css_value('0 4px 24px rgba(0,0,0,0.06)' if template == 'Professional' else ('0 4px 16px rgba(0,0,0,0.08)' if card_elevation == 'shadow' else 'none'))};"
        f"--bc-card-border: {sanitize_css_value(border)};"
        f"--bc-success: #16A34A;"
        f"--bc-danger: #DC2626;"
    )

    return vars_css
