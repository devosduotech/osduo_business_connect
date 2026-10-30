# Installation Guide — OSDuo Business Connect

This guide provides step-by-step instructions to install and configure the **OSDuo Business Connect** application on a fresh Frappe/ERPNext server.

## 📋 Prerequisites

Before installing the application, ensure your server meets the following requirements:

- **Frappe Framework**: v14+ (installed and configured)
- **Bench CLI**: Installed and functional
- **Python**: 3.10+
- **MariaDB / PostgreSQL**: Installed and configured
- **Redis**: Installed and configured
- **Node.js & Yarn**: Installed for asset compilation

---

## 🚀 Installation Steps

### 1. Initialize the Bench
If you haven't already, create a new bench or use an existing one:
```bash
# Create a new bench
bench init frappe-bench --frappe-branch version-14
cd frappe-bench
```

### 2. Create a New Site
Create a site where the application will be hosted:
```bash
bench new-site business-connect.local
```

### 3. Install the Application
Clone the repository and install the app onto your site:
```bash
# Get the app from GitHub
bench get-app https://github.com/devosduotech/osduo_business_connect.git

# Install the app onto your site
bench --site business-connect.local install-app osduo_business_connect
```

### 4. Configure Site Settings
To ensure the public pages (Digital Cards, Business Profiles) are accessible:
1. Log in to the site as **Administrator**.
2. Navigate to **System Settings**.
3. Ensure that the site is configured for public access to the relevant DocTypes.
4. Set up the `bc_base.html` variables if any custom domain configuration is required.

### 5. Build Assets
Compile the CSS and JS assets to ensure the redesigned templates render correctly:
```bash
bench build
bench restart
```

---

## 🛠 Configuration & Troubleshooting

### Theme Setup
The application comes with a set of default themes. To create a new custom theme:
1. Go to **BC Theme** list.
2. Create a new theme and select a **Template** (Professional, Modern, Minimal, Classic, Luxury, or Creative).
3. Assign a **Color Scheme** (e.g., Blue, Gold, Violet).

### Common Issues

**Issue: Header/Footer not displaying correctly**
- **Fix**: Run `bench clear-cache` and `bench build` to ensure the latest CSS is being served.

**Issue: Public URLs showing 404**
- **Fix**: Ensure that the `Business` and `Showcase Product` records are marked as **Published** and that the `public_profile_enabled` checkbox is checked.

---

## 📦 Maintenance

### Updating the App
To update to the latest version of the redesign:
```bash
bench update --pull
```

### Backing up Data
```bash
bench backup --site business_connect.local
```
