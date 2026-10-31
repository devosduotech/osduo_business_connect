# Installation Guide — OSDuo Business Connect

Step-by-step instructions to install, operate, and update **OSDuo Business Connect**
— from a single-site demo to a multi-tenant SaaS bench serving many customer domains.

Current release: **v1.2.0** (see [RELEASE_NOTES.md](../RELEASE_NOTES.md)).

---

## 📋 Prerequisites

| Requirement | Version / Notes |
|---|---|
| Frappe Framework | **v16** (`>=16.0.0,<17.0.0` — enforced by `pyproject.toml`) |
| Frappe CRM | Required app (`required_apps = ["crm"]`) |
| Python | 3.10+ |
| Node.js + Yarn | For asset building |
| MariaDB + Redis | Standard Frappe stack |
| `qrcode[pil]` | QR generation: `bench pip install "qrcode[pil]"` |
| Pillow | Pulled in by Frappe; used for PWA icon rendering |
| HTTPS | Mandatory in production — the PWA (service worker + install) requires a secure context |

---

## 🚀 Fresh Install (single site)

```bash
# 1. Bench on Frappe v16
bench init frappe-bench --frappe-branch version-16
cd frappe-bench

# 2. Create the site
bench new-site mysite.local

# 3. Install CRM + Business Connect
bench get-app https://github.com/frappe/crm.git --branch version-15    # or matching branch
bench get-app https://github.com/devosduotech/osduo_business_connect.git
bench --site mysite.local install-app crm osduo_business_connect

# 4. QR support
bench --site mysite.local pip install "qrcode[pil]"   # or: bench pip install "qrcode[pil]"

# 5. Migrate (also runs after_install hooks: roles, built-in themes, CRM custom fields)
bench --site mysite.local migrate
```

On install the app automatically creates:
- Roles: `BC Business Owner`, `BC Business Manager`, `BC Business Member`,
  `BC Marketing Manager`, `BC CRM User`, `BC System Manager`
- Built-in themes: `Default Blue`, `Default Violet`, … (template Modern + color scheme)
- CRM custom fields (`osduo_business`, `osduo_enquiry`, …) on the Lead doctype

### Set the canonical domain (do this early!)

`host_name` is the origin used to generate **every public URL** (`/b/<slug>`,
`/c/<slug>`) — including the QR codes and NFC tags that get physically printed.
Set it in `sites/<sitename>/site_config.json` **before** creating cards:

```json
{
  "db_name": "...",
  "host_name": "https://mysite.example.com"
}
```

Rules: include the scheme, no trailing slash, no port. After changing it, run
`bench --site <site> migrate` — the `public_url` backfill re-syncs all Business and
Digital Card records to the new canonical origin.

### Post-install verification

```bash
bench --site mysite.local clear-cache && bench restart

# Public/PWA endpoints
curl -sI https://mysite.example.com/manifest.json      # 200 application/json
curl -sI https://mysite.example.com/sw.js              # 200 text/javascript
curl -sI https://mysite.example.com/offline            # 200 text/html
curl -sI "https://mysite.example.com/api/method/osduo_business_connect.pwa.get_app_icon?size=192"   # 200 image/png
```

---

## 🏢 Multi-Tenant SaaS Setup

One bench serves many customers. Each customer is a **separate site**
(Frappe routes requests by the `Host` header) and automatically gets its own
branded installable PWA, its own storage, and hard data isolation between tenants.

### A. Hosted subdomains — `customer.connect.yourdomain.com`

One-time per root domain:

1. **Wildcard DNS**: `*.connect.yourdomain.com` → bench IP (A record)
2. **Wildcard TLS**: `certbot certonly --dns-<provider> -d '*.connect.yourdomain.com'`
   (DNS-01 challenge — requires DNS API credentials for auto-renewal)
3. **Nginx**: either per-site server blocks via `bench setup nginx`, or one wildcard
   `server` block listening on 443 with the wildcard cert, `proxy_pass` to the bench.
   Frappe resolves the site from the `Host` header either way.

Per customer (≈ 1 minute):

```bash
bench new-site karthic.connect.yourdomain.com --mariadb-root-password '...' --admin-password '...'
bench --site karthic.connect.yourdomain.com install-app crm osduo_business_connect

# canonical domain for generated URLs / printed cards
nano sites/karthic.connect.yourdomain.com/site_config.json
#   "host_name": "https://karthic.connect.yourdomain.com"

bench --site karthic.connect.yourdomain.com migrate
bench --site karthic.connect.yourdomain.com clear-cache
```

### B. Bring-your-own domains (BYOD) — e.g. `connect.customer-own-domain.in`

1. The customer points DNS at you:
   `CNAME connect.customer-own-domain.in → karthic.connect.yourdomain.com`
   (CNAME follows you if the bench IP changes; require subdomains — apex domains need
   ANAME/ALIAS-capable DNS)
2. Add a **Domain** document on their site:
   Desk → *Domain* → New → `https://connect.customer-own-domain.in` → linked to the site
   (or `bench --site karthic... add-domain "connect.customer-own-domain.in"`)
3. Certificate (HTTP-01 works once their DNS points at you):
   `bench setup lets-encrypt connect.customer-own-domain.in` (or add to the
   front-proxy / Caddy `on_demand_tls` config if you automate many BYOD domains)
4. `bench setup nginx && sudo service nginx reload`

**Policy for printed media:** keep `host_name` on the hosted subdomain — it is the
permanent NFC/QR anchor. The custom domain is *additive*: both hostnames serve the same
site, so already-printed cards keep working forever. Only switch `host_name` to the
custom domain deliberately (then re-migrate) when you accept that QR codes printed
earlier still resolve via the retained subdomain.

---

## ⬆️ Updating an Existing Deployment

```bash
cd ~/frappe-bench/apps/osduo_business_connect
git fetch && git pull origin main        # release branch; or develop on staging/VMs

# migrate is REQUIRED whenever DocType JSON changed (v1.2.0 included such changes)
bench --site all migrate
bench --site all clear-cache
bench build --app osduo_business_connect   # only if assets/JS changed & not dev mode
bench restart
```

Notes:
- v1.2.0's service worker cache names are stamped with the app `__version__`, so
  installed PWAs roll themselves forward on the next visit after a version bump.
- `bench migrate` also re-runs `backfill_public_urls()` — after a `host_name` change,
  one migrate is all that's needed to re-stamp `public_url` everywhere.
- If the site uses a custom **Website Theme**, re-save it (Desk → Website Theme → Save)
  or simply migrate after a Frappe upgrade so its compiled CSS is regenerated.

---

## 🛠 Configuration

| What | Where |
|---|---|
| PWA app name / logo per customer | Website Settings → App Name / App Logo (falls back to System Settings → app defaults) |
| Canonical URL origin | `site_config.json → host_name` per site |
| Theme | Business → Default Theme (BC Theme: template + colors + layout) |
| Public visibility | Business/Card/Product/Service: Status = Published + Public Profile + submitted (not cancelled) |
| Team access | Business Member rows (Owner created automatically with the Business) |

Users typically need one of the `BC *` roles **plus** a Business Member row for the
specific business — role grants desk access to the doctypes, membership scopes the data.

---

## 🔧 Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| QR missing on card | `pip install "qrcode[pil]"` in the bench env; open+save card (or migrate) to trigger generation |
| Public page 404 | Record must be Published **and submitted** (`docstatus < 2`) with Public Profile on; `bench clear-website-cache` |
| Card URL wrong domain | Set `host_name`, then `bench migrate` (re-backfills `public_url`) |
| Login page unstyled / giant icons after Frappe upgrade | Stale Website Theme CSS — re-save the theme in Desk, `bench build`, hard-refresh |
| PWA not installable | Needs HTTPS (or `localhost`); check `/manifest.json` & `/sw.js` return 200; DevTools → Application → Manifest errors |
| `migrate` fails on CRM custom fields | Ensure the `crm` app is installed on the same site before Business Connect |
| Permission oddities (submit/cancel greyed out) | User needs the role bit **and** an active Business Member row (Owner/Manager/Marketing for submit; Owner for cancel/amend) |

---

## 📦 Maintenance

```bash
bench --site <site> backup                     # scheduled via bench config backup
bench --site <site> show-config                # verify host_name etc.
bench doctor                                   # workers/redis health
```

---

## Related Docs

- [User Manual](USER_MANUAL.md) · [PWA Architecture & Runbook](PWA.md) ·
  [SaaS Implementation Plan](SAAS_IMPLEMENTATION_PLAN.md) ·
  [Release Notes](../RELEASE_NOTES.md)
