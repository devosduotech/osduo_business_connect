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
    Generate CSS from theme data. All classes prefixed with 'bc-' to avoid
    conflicts with Frappe/Bootstrap global styles.

    Args:
        theme_data: Theme data dictionary

    Returns:
        str: CSS string
    """
    template = theme_data.get('template', 'Modern')
    config = get_template_config(template)
    primary = theme_data.get('primary_color', '#000000')
    secondary = theme_data.get('secondary_color', '#FFFFFF')
    accent = theme_data.get('accent_color', '#007BFF')
    gradient_start = config.get('gradient_start', primary)
    gradient_end = config.get('gradient_end', accent)
    border_radius = get_border_radius(theme_data.get('card_style', 'Modern'))
    font_family = theme_data.get('font_family', 'inherit')
    card_elevation = config.get('card_elevation', 'shadow')

    shadow_css = '0 1px 3px rgba(0,0,0,0.1)' if card_elevation == 'shadow' else 'none'
    border_css = '1px solid #e2e8f0' if card_elevation == 'border' else 'none'

    css = f"""
/* ===== OSDuo Business Connect Theme ===== */
.bc-page {{
    font-family: {font_family};
    background: #f8fafc;
    color: #1e293b;
    margin: 0;
    padding: 0;
    line-height: 1.6;
}}

/* Header */
.bc-header {{
    background: linear-gradient(135deg, {gradient_start}, {gradient_end});
    color: white;
    padding: 3rem 1.5rem;
    text-align: center;
}}

.bc-header h1 {{
    font-size: 2rem;
    margin: 0 0 0.5rem 0;
    font-weight: 700;
    color: white;
}}

.bc-header .bc-tagline {{
    font-size: 1.1rem;
    opacity: 0.9;
    margin: 0;
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
    border-radius: {border_radius};
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s;
    border: none;
    cursor: pointer;
    text-align: center;
    font-size: 0.95rem;
}}

.bc-btn-primary {{
    background-color: {primary};
    color: white;
}}

.bc-btn-primary:hover {{
    opacity: 0.9;
    transform: translateY(-1px);
    color: white;
    text-decoration: none;
}}

.bc-btn-secondary {{
    background-color: {secondary};
    color: {primary};
    border: 1px solid {primary};
}}

.bc-btn-secondary:hover {{
    opacity: 0.9;
    color: {primary};
    text-decoration: none;
}}

.bc-btn-accent {{
    background-color: {accent};
    color: white;
}}

.bc-btn-accent:hover {{
    opacity: 0.9;
    color: white;
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
    padding: 2rem 1.5rem;
    max-width: 800px;
    margin: 0 auto;
}}

.bc-section-title {{
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
    color: {primary};
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
    border-radius: 50%;
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
        "Violet": "8px",
        "Indigo": "8px",
        "Blue": "8px",
        "Green": "8px",
        "Yellow": "8px",
        "Orange": "8px",
        "Red": "8px",
    }
    return styles.get(style, "8px")


def get_template_config(template):
    """
    Get template-specific configuration.

    Args:
        template: Template name

    Returns:
        dict: Template configuration
    """
    configs = {
        "Modern": {
            "header_style": "gradient",
            "section_spacing": "large",
            "card_elevation": "shadow",
        },
        "Professional": {
            "header_style": "solid",
            "section_spacing": "medium",
            "card_elevation": "border",
        },
        "Minimal": {
            "header_style": "clean",
            "section_spacing": "small",
            "card_elevation": "none",
        },
        "Classic": {
            "header_style": "ornate",
            "section_spacing": "large",
            "card_elevation": "shadow",
        },
        "Violet": {
            "header_style": "gradient",
            "section_spacing": "large",
            "card_elevation": "shadow",
            "gradient_start": "#7C3AED",
            "gradient_end": "#A78BFA",
        },
        "Indigo": {
            "header_style": "gradient",
            "section_spacing": "large",
            "card_elevation": "shadow",
            "gradient_start": "#4F46E5",
            "gradient_end": "#818CF8",
        },
        "Blue": {
            "header_style": "gradient",
            "section_spacing": "large",
            "card_elevation": "shadow",
            "gradient_start": "#2563EB",
            "gradient_end": "#60A5FA",
        },
        "Green": {
            "header_style": "gradient",
            "section_spacing": "large",
            "card_elevation": "shadow",
            "gradient_start": "#16A34A",
            "gradient_end": "#4ADE80",
        },
        "Yellow": {
            "header_style": "gradient",
            "section_spacing": "large",
            "card_elevation": "shadow",
            "gradient_start": "#EAB308",
            "gradient_end": "#FDE047",
        },
        "Orange": {
            "header_style": "gradient",
            "section_spacing": "large",
            "card_elevation": "shadow",
            "gradient_start": "#EA580C",
            "gradient_end": "#FB923C",
        },
        "Red": {
            "header_style": "gradient",
            "section_spacing": "large",
            "card_elevation": "shadow",
            "gradient_start": "#DC2626",
            "gradient_end": "#F87171",
        },
    }
    return configs.get(template, configs["Modern"])
