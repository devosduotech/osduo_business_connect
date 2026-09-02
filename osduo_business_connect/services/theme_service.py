# Copyright (c) 2026, OSDuo and contributors
# For license information, please see license.txt

"""
Theme Service

Handles theme resolution and CSS generation for Business Connect.
Template = layout structure (Modern, Professional, Minimal, Classic)
Color Scheme = color palette (Violet, Indigo, Blue, etc.)
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
    # Check Business.default_theme first (authoritative)
    default_theme = frappe.db.get_value("Business", business_name, "default_theme")
    if default_theme:
        return get_theme_data(default_theme)

    # Fall back to default
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

    # Get color scheme colors
    scheme = theme.color_scheme or "Blue"
    scheme_colors = COLOR_SCHEMES.get(scheme, COLOR_SCHEMES["Blue"])

    # Use custom colors if scheme is Custom
    if scheme == "Custom":
        scheme_colors = {
            "primary": theme.primary_color or "#2563EB",
            "secondary": theme.secondary_color or "#FFFFFF",
            "accent": theme.accent_color or "#60A5FA",
            "gradient_start": theme.primary_color or "#2563EB",
            "gradient_end": theme.accent_color or "#60A5FA",
        }

    return {
        "name": theme.name,
        "template": theme.template or "Modern",
        "color_scheme": scheme,
        "primary_color": scheme_colors["primary"],
        "secondary_color": scheme_colors["secondary"],
        "accent_color": scheme_colors["accent"],
        "gradient_start": scheme_colors["gradient_start"],
        "gradient_end": scheme_colors["gradient_end"],
        "button_style": theme.button_style or "Filled",
        "card_style": theme.card_style or "Modern",
        "font_family": theme.font_family,
    }


def get_default_theme():
    """
    Get default theme (Modern + Blue).

    Returns:
        dict: Default theme data
    """
    return {
        "name": None,
        "template": "Modern",
        "color_scheme": "Blue",
        "primary_color": "#2563EB",
        "secondary_color": "#FFFFFF",
        "accent_color": "#60A5FA",
        "gradient_start": "#2563EB",
        "gradient_end": "#60A5FA",
        "button_style": "Filled",
        "card_style": "Modern",
        "font_family": None,
    }


def get_theme_css(theme_data):
    """
    Generate CSS from theme data.

    Args:
        theme_data: Theme data dictionary

    Returns:
        str: CSS string
    """
    template = theme_data.get("template", "Modern")
    primary = theme_data.get("primary_color", "#2563EB")
    secondary = theme_data.get("secondary_color", "#FFFFFF")
    accent = theme_data.get("accent_color", "#60A5FA")
    gradient_start = theme_data.get("gradient_start", primary)
    gradient_end = theme_data.get("gradient_end", accent)
    button_style = theme_data.get("button_style", "Filled")
    card_style = theme_data.get("card_style", "Modern")
    font_family = theme_data.get("font_family", "inherit")

    # Card elevation from card_style
    card_elevation_map = {"Modern": "shadow", "Professional": "border", "Minimal": "none", "Classic": "shadow"}
    card_elevation = card_elevation_map.get(card_style, "shadow")
    shadow_css = "0 1px 3px rgba(0,0,0,0.1)" if card_elevation == "shadow" else "none"
    border_css = "1px solid #e2e8f0" if card_elevation == "border" else "none"

    # Border radius from card_style
    radius_map = {"Modern": "8px", "Professional": "4px", "Minimal": "0px", "Classic": "12px"}
    border_radius = radius_map.get(card_style, "8px")

    # Button border radius from button_style
    btn_radius_map = {"Filled": border_radius, "Outline": border_radius, "Rounded": "8px", "Pill": "999px"}
    btn_radius = btn_radius_map.get(button_style, border_radius)

    # Button style (filled vs outline)
    btn_filled = button_style in ("Filled", "Rounded", "Pill")

    # Section spacing from template
    spacing_map = {"Modern": "2rem 1.5rem", "Professional": "1.5rem 1.5rem", "Minimal": "1rem 1.5rem", "Classic": "2rem 1.5rem"}
    section_spacing = spacing_map.get(template, "2rem 1.5rem")

    # Header style from template
    header_style_map = {
        "Modern": f"background: linear-gradient(135deg, {gradient_start}, {gradient_end});",
        "Professional": f"background: {primary};",
        "Minimal": f"background: {secondary}; color: {primary}; border-bottom: 2px solid {primary};",
        "Classic": f"background: linear-gradient(180deg, {gradient_start}, {gradient_end});",
    }
    header_css = header_style_map.get(template, header_style_map["Modern"])

    # Header text color
    header_text_color = "white" if template != "Minimal" else primary

    css = f"""
/* ===== OSDuo Business Connect — {template} + {theme_data.get('color_scheme', 'Blue')} ===== */
.bc-page {{
    font-family: {font_family};
    background: {'#f8fafc' if template != 'Minimal' else '#ffffff'};
    color: #1e293b;
    margin: 0;
    padding: 0;
    line-height: 1.6;
}}

/* Header */
.bc-header {{
    {header_css}
    color: {header_text_color};
    padding: {'3rem 1.5rem' if template in ('Modern', 'Classic') else '2rem 1.5rem'};
    text-align: {'center' if template in ('Modern', 'Minimal') else 'left'};
}}

.bc-header h1 {{
    font-size: {'2rem' if template == 'Modern' else '1.75rem'};
    margin: 0 0 0.5rem 0;
    font-weight: 700;
    color: {header_text_color};
}}

.bc-header .bc-tagline {{
    font-size: 1.1rem;
    opacity: 0.9;
    margin: 0;
    color: {header_text_color};
}}

/* Cards */
.bc-card {{
    background: white;
    border-radius: {border_radius};
    box-shadow: {shadow_css};
    border: {border_css};
    padding: 1.5rem;
    margin-bottom: 1rem;
    text-decoration: none;
    color: inherit;
    display: block;
}}

/* Buttons */
.bc-btn {{
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border-radius: {btn_radius};
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s;
    border: none;
    cursor: pointer;
    text-align: center;
    font-size: 0.95rem;
}}

.bc-btn-primary {{
    background-color: {primary if btn_filled else 'transparent'};
    color: {'white' if btn_filled else primary};
    {'border: 2px solid ' + primary if not btn_filled else ''}
}}

.bc-btn-primary:hover {{
    opacity: 0.9;
    color: {'white' if btn_filled else primary};
    text-decoration: none;
}}

.bc-btn-secondary {{
    background-color: {secondary if btn_filled else 'transparent'};
    color: {primary};
    border: 1px solid {primary};
}}

.bc-btn-secondary:hover {{
    opacity: 0.9;
    color: {primary};
    text-decoration: none;
}}

.bc-btn-accent {{
    background-color: {accent if btn_filled else 'transparent'};
    color: {'white' if btn_filled else accent};
    {'border: 2px solid ' + accent if not btn_filled else ''}
}}

.bc-btn-accent:hover {{
    opacity: 0.9;
    color: {'white' if btn_filled else accent};
    text-decoration: none;
}}

/* Sticky Action Bar */
.bc-action-bar {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    padding: 0.75rem;
    display: flex;
    justify-content: space-around;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    z-index: 1000;
    gap: 0.5rem;
}}

.bc-action-bar .bc-btn {{
    flex: 1;
    margin: 0;
    font-size: 0.85rem;
    padding: 0.6rem 0.5rem;
}}

/* Sections */
.bc-section {{
    padding: {section_spacing};
    max-width: 800px;
    margin: 0 auto;
}}

.bc-section-title {{
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
    color: {primary};
    {'border-bottom: 2px solid ' + accent + '; padding-bottom: 0.5rem;' if template == 'Professional' else ''}
    {'text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.875rem; color: ' + accent if template == 'Minimal' else ''}
}}

/* Product Grid */
.bc-product-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
}}

.bc-product-card {{
    text-align: center;
}}

.bc-product-card img {{
    width: 100%;
    height: 150px;
    object-fit: cover;
    border-radius: {border_radius};
}}

/* Team Grid */
.bc-team-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1.5rem;
    text-align: center;
}}

.bc-team-grid img {{
    width: 100px;
    height: 100px;
    border-radius: {'50%' if template != 'Minimal' else '4px'};
    object-fit: cover;
}}

/* Contact */
.bc-contact-item {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}}

/* Back Link */
.bc-back-link {{
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    color: {primary};
    text-decoration: none;
    margin-bottom: 1.5rem;
    font-size: 0.9rem;
}}

.bc-back-link:hover {{
    text-decoration: underline;
    color: {primary};
}}

/* Footer */
.bc-footer {{
    text-align: center;
    padding: 2rem;
    color: #64748b;
    font-size: 0.875rem;
    {'border-top: 1px solid #e2e8f0;' if template == 'Professional' else ''}
}}

/* Responsive */
@media (max-width: 768px) {{
    .bc-header {{
        padding: 2rem 1rem;
    }}

    .bc-header h1 {{
        font-size: 1.5rem;
    }}

    .bc-section {{
        padding: 1.5rem 1rem;
    }}

    .bc-product-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}

    .bc-team-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}

    .bc-action-bar {{
        display: flex !important;
    }}
}}
"""
    return css
