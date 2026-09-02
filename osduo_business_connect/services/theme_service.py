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
    template = theme_data.get('template', 'Modern')
    config = get_template_config(template)
    
    css = f"""
:root {{
    --primary-color: {theme_data.get('primary_color', '#000000')};
    --secondary-color: {theme_data.get('secondary_color', '#FFFFFF')};
    --accent-color: {theme_data.get('accent_color', '#007BFF')};
    --border-radius: {get_border_radius(theme_data.get('card_style', 'Modern'))};
    --font-family: {theme_data.get('font_family', 'inherit')};
}}

body {{
    font-family: var(--font-family);
    background-color: #f8fafc;
    color: #1e293b;
    margin: 0;
    padding: 0;
}}

/* Header Styles */
.business-header {{
    background: linear-gradient(135deg, {config.get('gradient_start', theme_data.get('primary_color', '#000000'))}, {config.get('gradient_end', theme_data.get('accent_color', '#007BFF'))});
    color: white;
    padding: 3rem 1.5rem;
    text-align: center;
}}

.business-header h1 {{
    font-size: 2rem;
    margin: 0 0 0.5rem 0;
    font-weight: 700;
}}

.business-header .tagline {{
    font-size: 1.1rem;
    opacity: 0.9;
    margin: 0;
}}

/* Card Styles */
.card {{
    background: white;
    border-radius: var(--border-radius);
    box-shadow: {'0 1px 3px rgba(0,0,0,0.1)' if config.get('card_elevation') == 'shadow' else 'none'};
    border: {'1px solid #e2e8f0' if config.get('card_elevation') == 'border' else 'none'};
    padding: 1.5rem;
    margin-bottom: 1rem;
}}

/* Button Styles */
.btn {{
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border-radius: var(--border-radius);
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s;
    border: none;
    cursor: pointer;
}}

.btn-primary {{
    background-color: var(--primary-color);
    color: white;
}}

.btn-primary:hover {{
    opacity: 0.9;
    transform: translateY(-1px);
}}

.btn-secondary {{
    background-color: var(--secondary-color);
    color: var(--primary-color);
    border: 1px solid var(--primary-color);
}}

.btn-accent {{
    background-color: var(--accent-color);
    color: white;
}}

/* Action Bar */
.action-bar {{
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    padding: 0.75rem;
    display: flex;
    justify-content: space-around;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    z-index: 100;
}}

.action-bar .btn {{
    flex: 1;
    margin: 0 0.25rem;
    text-align: center;
}}

/* Section Styles */
.section {{
    padding: 2rem 1.5rem;
    max-width: 800px;
    margin: 0 auto;
}}

.section-title {{
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
    color: var(--primary-color);
}}

/* Product Grid */
.product-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
}}

.product-card {{
    text-align: center;
}}

.product-card img {{
    width: 100%;
    height: 150px;
    object-fit: cover;
    border-radius: var(--border-radius);
}}

/* Team Grid */
.team-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1.5rem;
    text-align: center;
}}

.team-member img {{
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
}}

/* Contact Info */
.contact-item {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}}

.contact-item .icon {{
    width: 20px;
    color: var(--primary-color);
}}

/* Footer */
.footer {{
    text-align: center;
    padding: 2rem;
    color: #64748b;
    font-size: 0.875rem;
}}

/* Responsive */
@media (max-width: 768px) {{
    .business-header {{
        padding: 2rem 1rem;
    }}
    
    .business-header h1 {{
        font-size: 1.5rem;
    }}
    
    .section {{
        padding: 1.5rem 1rem;
    }}
    
    .product-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
    
    .team-grid {{
        grid-template-columns: repeat(2, 1fr);
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
