# Installation Guide — OSDuo Business Connect

Step-by-step instructions to install, operate, and update **OSDuo Business Connect**
— from a single-site demo to a multi-tenant SaaS bench serving many customer domains.

Current release: **v1.4.1** (see [RELEASE_NOTES.md](../RELEASE_NOTES.md)).

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
- Website theme **`OSDuo Business Connect`** (set as the site default) plus
  favicon, app logo and app name — no manual Desk setup required

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

Behind a proxy that terminates TLS (Nginx Proxy Manager, Caddy, Cloudflare, …) the
bench itself sees plain HTTP, so Frappe cannot guess `https` — without `host_name`
every generated URL and QR code will say `http://`. The scheme in `host_name` is
the only thing that decides this.

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
address printed codes were generated from. The custom domain is *additive*: both
hostnames serve the same site, so keep the hosted subdomain serving and already-printed
cards keep resolving. Switching `host_name` to the custom domain **re-derives `public_url`
and regenerates the QR images**, so only do it deliberately (then `bench migrate`) and
only while the previously-printed subdomain stays served — otherwise earlier codes break.

> **Two URLs, one setting.** `host_name` feeds **both** the printed QR/NFC URLs and the
> canonical/OG/sitemap origin, so "permanent printed URL" and "preferred SEO domain" are
> the *same* value here. Choose the origin you want indexed and printed, and keep every
> host already printed for still serving.

---

## 🧾 Site Provisioning SOP (new customer site)

One site = one customer = one Subscription = one plan. Plan selection is manual:
there is no checkout/payment/webhook in this platform. Billing happens in Aasriva;
the CLI below only mirrors the agreed sale locally.

### Which path applies?

| Site state | What to do |
|---|---|
| **New site** (just created, never provisioned) | Follow Steps 1–4 below and run `provision` **without** `--force`. |
| **Existing site upgraded to v1.4.x** | Run `bench migrate` first. The migration seeds `BUSINESS` only when the site already has Business or User data. Verify at `/portal/subscription` or with the console. |
| **Existing site with no plan after upgrade** | Run the same `provision` command **without** `--force`. |
| **Existing site that already has a Subscription** | Re-run `provision` with `--force` to change or refresh the plan. See [Plan setup on an existing site](#plan-setup-on-an-existing-site). |

`--force` overwrites the Subscription and frozen entitlement snapshot in place;
it never purges CRM, public or user data. Keep `--hostname` unset unless you are
intentionally changing the public origin, because changing it re-derives printed
QR/NFC URLs.

### Plans and minimums

| Plan | Price / user / year | Minimum billed seats | Business profiles | Included custom domains |
|---|---:|---:|---:|---:|
| Professional | ₹595 | 1 | 1 | 0 |
| Business | ₹895 | 5 | 3 | 0 |
| Enterprise | ₹1,295 | 10 | 5 | 1 |

`seats_cap = max(minimum, seats_ordered)`. A seat is a distinct enabled
`Business Member.user` (owner included). Minimum seats are always billed. The
`entitlement_snapshot` is frozen at provisioning; later plan-master edits do not
change an existing site.

### Step 1 — create the site

```bash
cd ~/frappe-bench
bench new-site customer.example.com \
  --mariadb-root-password '<db-root-password>' \
  --admin-password '<administrator-password>'

bench --site customer.example.com install-app crm osduo_business_connect
bench --site customer.example.com pip install "qrcode[pil]"
```

`crm` must be installed before Business Connect. Do **not** provision yet: a
fresh site intentionally fails closed to Professional until step 3.

### Step 2 — set the canonical hostname (before any cards are printed)

Edit `sites/customer.example.com/site_config.json`:

```json
{
  "host_name": "https://customer.example.com"
}
```

Include the scheme, no trailing slash, no port. This is the origin used for
every public URL, QR code and NFC tag. Alternatively pass `--hostname` to the
provision command in step 3 (only accepted when the value is unset or identical;
`--force` is required to change an existing value and re-derives printed URLs).

### Step 2b — configure outgoing email / SMTP

Outgoing mail is **per site**. Frappe v16 can read SMTP settings directly from
`sites/<site>/site_config.json`, which is convenient when creating many sites
from the same template. Add these keys:

```json
{
  "mail_server": "smtp.example.com",
  "mail_port": 587,
  "mail_login": "no-reply@example.com",
  "mail_password": "app-password",
  "use_tls": 1,
  "use_ssl": 0,
  "auto_email_id": "no-reply@example.com",
  "email_sender_name": "OSDuo Business Connect"
}
```

- `mail_server` is the key that enables the site-config fallback. Without it,
  Frappe will not build an outgoing account from these values.
- Use `use_tls: 1` with port `587`, or `use_ssl: 1` with port `465` — not both.
- `auto_email_id` is the From address; it falls back to `mail_login` and then
  `notifications@example.com`. `email_sender_name` defaults to `Frappe`.
- An **Email Account** record in the site database with `Enable Outgoing = 1`
  and `Default Outgoing = 1` takes precedence over site config. Site config is
  the fallback used when no such record exists.
- Keep `site_config.json` permissions tight: the SMTP password is stored in
  plain text.

Restart after changing site config:

```bash
bench restart
```

Verify delivery from the bench:

```bash
bench --site customer.example.com execute frappe.email.sendmail \
  --kwargs "{'recipients':['you@example.com'],'subject':'SMTP test','message':'SMTP test'}"
```

Frappe queues outgoing mail, so the scheduler/worker must be running. A failed
`frappe.sendmail()` call is logged by Business Connect and never rolls back an
Add-on Order.

### Step 3 — provision the plan (new or never-provisioned site)

Run from the bench root, using the bench Python environment. This is the path
for a fresh site or an existing site that has no Subscription yet. If the site
already has a plan, use [Plan setup on an existing site](#plan-setup-on-an-existing-site)
instead.

```bash
# Preview first
env/bin/python apps/osduo_business_connect/scripts/provision_customer_site.py \
  --site customer.example.com provision \
  --plan BUSINESS --seats 5 --dry-run

# Apply
env/bin/python apps/osduo_business_connect/scripts/provision_customer_site.py \
  --site customer.example.com provision \
  --plan BUSINESS --seats 5 \
  --external-ref AASRIVA-ORDER-12345 \
  --notes "Annual plan, paid through Aasriva"
```

Options:

- `--plan PROFESSIONAL|BUSINESS|ENTERPRISE` (required).
- `--seats N` — defaults to the plan minimum; values below the minimum are rejected.
- `--status Active` (default) or `--status Trial`.
- `--hostname https://…` — optional; sets `host_name` at provisioning time.
- `--start-date YYYY-MM-DD` — defaults to today; period end is start + 365 days.
- `--external-ref` — reserved Aasriva reference (no payment data stored).
- `--notes` — operator note.
- `--dry-run` — preview without writing.
- `--force` — required only when reprovisioning a site that already has a
  Subscription. It overwrites in place and never purges data.

Leave `--external-crm` **unset** — external CRM applications are off for every
plan at present. Provisioning writes `bc_plan_code`, `bc_seats`,
`bc_external_crm_enabled` and the frozen snapshot to the site.

### Step 4 — finish and verify

```bash
bench --site customer.example.com migrate
bench --site customer.example.com clear-cache
bench --site customer.example.com clear-website-cache
```

Open **My Subscription** at `/portal/subscription` and confirm the plan, billed
seats, business cap and period end. Provider/Enterprise Desk users can still
use the legacy `/desk/my-subscription` page (`/app/my-subscription` on v15). Or
from the console:

```bash
bench --site customer.example.com console
>>> from osduo_business_connect.subscription.entitlements import get_entitlements
>>> get_entitlements()["plan_code"], get_entitlements()["limits"]["seat_cap"]
```

Then create the first **Business** from its native Desk form as the provider.
The owner's **Business Member** row is created automatically. Create one
**Digital Card** per member (extra cards with a different display name are
blocked). Professional and Business customers do this through the portal from
then on; they never need the Desk for team setup.

### Step 5 — access setup

- Do **not** grant customers permissions on the native `User`, `User
  Invitation`, `Role` or `Role Profile` DocTypes. The request gate blocks all
  of those surfaces for Professional/Business customer roles.
- Give each user a `BC *` role **and** an active Business Member row for the business.
  Frappe creates the User only when the teammate accepts the invitation from
  `/portal/team`; the `after_accept` hook then creates the Business Member row.
- Outgoing SMTP must be configured (see Step 2b), otherwise invitation emails
  cannot be delivered. `bench migrate` creates the hidden `bc_business`,
  `bc_member_role`, `bc_first_name` and `bc_last_name` fields on **User
  Invitation**; they are intentionally not globally mandatory so Frappe core
  invitations still work.
- Only the per-business Owner (plus provider roles) may invite. The portal
  offers only `BC Business Member`, `BC Business Manager`, `BC CRM User` and
  `BC Marketing Manager`; Administrator, System Manager, BC System Manager,
  BC Subscription Manager and the Owner role are never offered.
- Frappe CRM users additionally need a standard CRM role (`Sales User`,
  `Sales Manager` or `System Manager`) and access via `/crm` — BC roles alone
  are not enough.
- Professional has no Desk, team management, CRM, Analytics or import/export
  for customers. Business customer roles may open the BC workspace spellings
  (`/desk/business-connect`, `/desk/business/business-connect`, the legacy
  `/app/business-connect`, and public child workspace routes such as
  `/desk/business-connect/business`), themed like the portal. Direct requests to
  the generic Desk, `/desk/build`, DocType paths under the workspace prefix and
  native User/Role administration stay blocked.
  Business also adds the portal Team page,
  `/crm`, `/crm-form/*` and `/analytics`, up to 3 businesses and team
  invitations. Enterprise keeps its existing Desk-based advanced administration,
  Email/WhatsApp configuration, up to 5 businesses and one included custom
  domain.
- All plan/upgrade links must stay on
  `https://www.osduotech.com/solutions/business-connect#section_business-connect-pricing`.

### Verify portal team invitations

1. Sign in as the Business Owner on a Business-plan site and open `/portal/team`.
2. Confirm only the four allowed BC roles appear and the Owner role does not.
3. Invite a new email and confirm the seat counter increases immediately.
4. Open the emailed link as the invitee, set a password and confirm an active
   **Business Member** row is created for the selected business and role.
5. Try `/app`, `/desk/build` and
   `/api/method/frappe.core.api.user_invitation.invite_by_email` as the Owner:
   all must return 403. The guest acceptance URL must still work.
6. Open `/my-card`, `/portal/subscription`, `/analytics` and
   `/desk/business-connect`. All must show the OSDuo theme; the portal pages
   share the same sidebar with a **Business Connect** entry, and no native
   User/Role administration links appear for the Business Owner. The themed
   workspace rail should load; final visual parity of the selected sidebar/menu
   item text colour with `/portal/team` is still pending.
7. Sign out and back in. A Business customer must land on
   `/desk/business-connect`; opening `/login` or `/` while signed in must not
   produce a 403. A Professional customer must land on `/my-card` instead.
8. Sign out completely. `/` must forward a guest to `/login`, and `/login` must
   show the OSDuo split-screen branded page (dark image panel plus the stock
   Frappe sign-in form), not the unbranded Frappe login.

### Plan setup on an existing site

The provision CLI is the only supported way to add or change a site's plan. It
uses the `Administrator` session internally, so no Desk role is needed.

#### 1. Site upgraded from a pre-subscription version

Run the normal upgrade first. The v1.4 patch seeds `BUSINESS` for in-use sites so
existing CRM/Analytics users are not locked out. Fresh or empty sites are left
unprovisioned on purpose and fail closed to Professional.

```bash
cd ~/frappe-bench/apps/osduo_business_connect
git pull

cd ~/frappe-bench
bench build --app osduo_business_connect
bench --site customer.example.com migrate
bench --site customer.example.com clear-cache
bench --site customer.example.com clear-website-cache
bench restart
```

Verify the result at `/portal/subscription`, or from the console:

```bash
bench --site customer.example.com console
>>> from osduo_business_connect.subscription.entitlements import get_entitlements
>>> get_entitlements()["plan_code"], get_entitlements()["limits"]["seat_cap"]
```

If the site is in use and no plan was seeded, add one with the Step 3 command
**without** `--force`. Only use `--force` when a plan already exists.

#### 2. Site already has a Subscription

Preview the change, then re-run `provision` with `--force`. It updates the
Subscription and frozen entitlement snapshot in place and never purges data.

```bash
# Preview first
env/bin/python apps/osduo_business_connect/scripts/provision_customer_site.py \
  --site customer.example.com provision \
  --plan ENTERPRISE --seats 10 \
  --external-ref AASRIVA-UPGRADE-12345 \
  --notes "Upgraded from Business" \
  --dry-run

# Apply
env/bin/python apps/osduo_business_connect/scripts/provision_customer_site.py \
  --site customer.example.com provision \
  --plan ENTERPRISE --seats 10 \
  --external-ref AASRIVA-UPGRADE-12345 \
  --notes "Upgraded from Business" \
  --force

bench --site customer.example.com clear-cache
```

For a downgrade, use the lower plan code and its minimum seat count:

```bash
env/bin/python apps/osduo_business_connect/scripts/provision_customer_site.py \
  --site customer.example.com provision \
  --plan PROFESSIONAL --seats 1 \
  --force
```

No CRM/public data is deleted. Existing access is immediately gated by the new
snapshot; CRM/public records remain intact for a later upgrade. Changing both
plan and canonical `host_name` in one forced run re-derives printed QR/NFC URLs,
so confirm the printed-media policy before doing that.

### Status changes (provider only)

```bash
# Billing missed: public pages stay live, Desk/API blocked after grace
env/bin/python apps/osduo_business_connect/scripts/provision_customer_site.py \
  --site customer.example.com status "Past Due" --grace-until 2027-01-15

# Full suspension: public pages and guest-safe APIs stay live
env/bin/python apps/osduo_business_connect/scripts/provision_customer_site.py \
  --site customer.example.com status Suspended

# Reactivation
env/bin/python apps/osduo_business_connect/scripts/provision_customer_site.py \
  --site customer.example.com status Active
```

Allowed transitions: `Trial → Active/Past Due/Suspended/Cancelled`,
`Active → Past Due/Suspended/Cancelled`, `Past Due → Active/Suspended/Cancelled`,
`Suspended → Active/Cancelled`. `Cancelled` is terminal. The scheduler only
enforces a provider-set status; it never changes status by itself.

### Add-ons and custom domains

Business owner/manager creates an **Add-on Order** from its native Desk form:

- **Custom Domain Service** — ₹5,999/year; the first Enterprise mapping is
  included at ₹0, every other mapping is paid. Mapping status flows
  `Requested → Approved → Configured → Verified → Active`; only the site
  `Administrator` advances it. An Active order creates the domain mapping on
  the Subscription.
- **Domain Registration / Renewal** — actual vendor cost; attach a quote or
  invoice. No payment is collected in this platform.
- Mapping and order expiry follow `Subscription.current_period_end`. Adding a
  domain never changes `host_name` or printed QR/NFC URLs.
- A hostname is required only for the two domain add-ons. Other add-ons are
  billing/fulfilment records and do not need one.

#### Create an Add-on Master (provider)

Every site has its own database, so create the master on each customer site where
it should be orderable. Use `Administrator` only. The `SaaS Plan`, `Add-on Master`
and `Subscription` DocTypes have no DocPerms for other roles, so non-Administrators
cannot create, change or even list subscription masters. The Add-on Order link field
uses a restricted custom query; it does not expose the master list.

1. Desk → **Subscription** → **Add-on Master** → **Add Add-on Master**.
2. Fill:
   - **Code** — unique machine code, e.g. `PRIORITY_SUPPORT`. It cannot be renamed
     later.
   - **Add-on Name** — customer-facing label.
   - **Billing Type**:
     - `Annual` — fixed price. Use **List Price** when it applies to every plan;
       for selected plans, enter the price in each **Applicable Plans** row.
     - `Actual Cost` — set price to `0`; the customer must attach a quote/invoice
       and the order amount records `0` because payment is handled in Aasriva.
   - **Active** — keep checked to allow ordering.
3. Choose applicability:
   - For every plan: leave **Applies to All Plans** checked. The **Applicable
     Plans** table is read-only and any rows are cleared automatically.
   - For selected plans: **uncheck** it. The table becomes editable; add one row
     per allowed plan using the SaaS Plan names `PROFESSIONAL`, `BUSINESS`,
     `ENTERPRISE`, and enter that plan's **Annual Price**. Saving with an empty
     table or a missing price is blocked.
4. Save. Existing sites pick it up immediately; no reprovision is required.

`SaaS Plan` and the seeded add-ons are created by install/migrate. Seeding is
idempotent: it only creates missing records, backfills missing plan prices from
the master List Price, and never overwrites a provider-entered price.

#### Additional User add-on

Use **one** `ADDITIONAL_USER` master, not one master per plan. It is seeded
automatically with the annual per-user price for each plan:

| Plan | Annual Price |
|---|---:|
| Professional | ₹595 |
| Business | ₹895 |
| Enterprise | ₹1,295 |

These defaults follow the plan seed prices. Change a row in **Applicable Plans**
if your agreed price differs. One Add-on Order represents one additional user;
after the provider confirms payment in Aasriva, increase the site's seats with
the provisioning CLI (`--seats <new total> --force`). The order itself records
the request and price; it does not silently change the frozen Subscription.

Console equivalent for a selected-plan add-on:

```bash
bench --site customer.example.com console
>>> import frappe
>>> frappe.get_doc({
...   "doctype": "Add-on Master",
...   "code": "PRIORITY_SUPPORT",
...   "add_on_name": "Priority Support",
...   "billing_type": "Annual",
...   "price": 12000,
...   "is_active": 1,
...   "applies_to_all_plans": 0,
...   "applicable_plans": [
...     {"doctype": "Add-on Applicable Plan", "plan": "BUSINESS", "price": 12000},
...     {"doctype": "Add-on Applicable Plan", "plan": "ENTERPRISE", "price": 15000},
...   ],
...   "description": "Annual priority support add-on",
... }).insert()
>>> frappe.db.commit()
```

#### How customers order it

A `BC Business Owner` or `BC Business Manager` creates an **Add-on Order**. The
Add-on dropdown shows only active masters allowed by the site's frozen, active
plan, so the Add-on Master list stays Administrator-only. A plan-specific add-on
for a higher plan stays hidden; the customer must upgrade through Aasriva and the
provider must reprovision the site first. After the upgrade, the new plan's
add-ons appear automatically. The controller always sets `plan_snapshot` from
the frozen subscription entitlements — a client-supplied plan is ignored — and
re-derives `billing_type`/`amount` from the matching **Applicable Plans** row.
Customers can only create or keep an order in **Requested**. The status field is
read-only for customer roles, and the server rejects any other value from a
non-Administrator. The `Administrator` may select any workflow status when
creating an order and can advance existing orders:

```text
Requested → Approved → Configured → Verified → Active
```

#### Customer-facing form behaviour

The Add-on Order form adapts to the selected add-on:

| Add-on type | Hostname | Mapping Type | Registration Details | Supporting Documents | Quote / Vendor Invoice |
|---|---|---|---|---|---|
| Custom Domain Service | Shown, required | Shown, derived/read-only | Hidden | Hidden | Hidden unless Actual Cost |
| Domain Registration / Renewal | Shown, required | Hidden | Shown | Shown, optional | Shown, required |
| Generic annual add-on | Hidden | Hidden | Hidden | Hidden | Hidden |
| Generic actual-cost add-on | Hidden | Hidden | Hidden | Hidden | Shown, required |

`Invoice` is a separate field on every Add-on Order and is visible/editable only
to `Administrator`. A customer who bypasses the UI and submits an `invoice` value
is rejected by the controller. Hidden fields are also cleared when the add-on is
changed, and the controller re-derives the same values on save, so hiding a field
in the browser is not a security boundary.

**Yes, show the price to the customer.** The form calls a server-only quote
method when an add-on is selected and fills the read-only **Estimated Amount**:

- `Annual` add-ons show the **Annual Price** from the matching **Applicable
  Plans** row, or the master **List Price** for all-plan add-ons.
- `Additional User` shows `Estimated annual price for one additional user`.
- The first Enterprise custom-domain mapping shows `Included in your plan` and
  amount `0`; later mappings show the plan's domain price.
- `Actual Cost` add-ons show `Actual vendor cost. Attach a quote…` and amount
  `0`; the final amount is confirmed by the provider in Aasriva.

The customer cannot edit the amount. No payment is collected in this app.

#### New-order email notification

Every new Add-on Order sends an email to `info@osduotech.com` by default. To use
a different inbox or several recipients, set the site config key (comma- or
semicolon-separated):

```bash
bench --site customer.example.com set-config bc_addon_order_notification_email "ops@example.com,info@osduotech.com"
```

The site must have outgoing email configured (Email Account/SMTP); see
**Step 2b — configure outgoing email / SMTP** earlier in this SOP for the
per-site `site_config.json` keys. Mail failures are logged but never roll back
the customer's Requested order. The email includes the order number, add-on,
frozen plan, estimated amount, customer email and hostname.

**Plan links:** all “View plans”/upgrade links use
`https://www.osduotech.com/solutions/business-connect#section_business-connect-pricing`.
A legacy `bc_upgrade_url` pointing at the old unanchored product URL is
normalised to this pricing link automatically.

Only `Active` custom-domain orders create/update a Domain Mapping on the
Subscription. Changing an Add-on Master does not remove or alter existing
Subscriptions, mappings, printed QR codes or NFC URLs; existing orders are
revalidated only when saved.

### Troubleshooting

- `Permission Error: Insufficient Permission for Add-on Master` — pull the
  latest `develop` and run `bench --site <site> migrate`. Customer roles no longer
  need read access to Add-on Master; the Add-on Order form uses a restricted
  custom query instead.
- Add-on dropdown is empty — as Administrator, confirm the master is **Active**
  and that the site's plan is listed under **Applicable Plans** when
  **Applies to All Plans** is unchecked.
- `X is not available on the Y plan` — the master has **Applies to All Plans**
  unchecked and the site's plan is missing from **Applicable Plans**. Add the
  correct plan, or reprovision the site with the correct plan if the sale was
  recorded incorrectly.
- `LinkValidationError: Could not find Primary Color / Text Color / Page
  Background Color` during migrate — pull latest `develop`; the `before_migrate`
  hook repairs legacy Website Theme colour links.
- `This site already has a Subscription` — re-run `provision` with `--force`.
- Public URLs still `http://` behind a TLS proxy — set `host_name` with the
  `https://` scheme and migrate.

---

## ⬆️ Updating an Existing Deployment

```bash
cd ~/frappe-bench/apps/osduo_business_connect
git fetch && git pull origin main        # release branch; or develop on staging/VMs

# migrate is REQUIRED whenever DocType JSON changed (v1.2.0 and v1.2.8 included such changes; v1.2.8 also removes legacy Customize Form records for the BC doctypes)
bench --site all migrate
bench --site all clear-cache
bench build --app osduo_business_connect   # only if assets/JS changed & not dev mode
bench restart
```

Notes:
- v1.2.8 ships the standard **desk form layouts** (field order, hidden
  `naming_series`, About Us label on Business, merged **Enquiry and Purchase
  Link** section) directly in the DocType JSON. `bench migrate` applies the
  layout and removes any legacy Customize Form records — legacy **Custom
  Fields / Property Setters** for these seven doctypes are deleted on every
  migrate, so there is **no manual Customize Form work**. If you made your own
  layout tweaks on a site, migrate will overwrite them with the standard form.
- v1.2.2 creates and selects the bundled **Website Theme** `OSDuo Business
  Connect` on install/migrate, alongside the favicon/app logo/app name.
- v1.2.1 bundles the logo/favicon/login panel in the app and applies them on
  `migrate` (see **Branding & logo** below). Never copy brand images into
  `sites/<site>/public/files`.
- v1.2.0+'s service worker cache names are stamped with the app `__version__`, so
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
| Website Theme (site-wide web pages) | Website Settings → Theme (defaults to `OSDuo Business Connect`) |
| Theme (public card/profile pages) | Business → Default Theme (BC Theme: template + colors + layout) |
| Public visibility | Business/Card/Product/Service: Status = Published + Public Profile + submitted (not cancelled) |
| Team access | Business Member rows (Owner created automatically with the Business) |

Users typically need one of the `BC *` roles **plus** a Business Member row for the
specific business — role grants desk access to the doctypes, membership scopes the data.

### Branding & logo (bundled in the app)

All brand assets ship inside the app package and are served from
`/assets/osduo_business_connect/images/` — **never copy them into
`sites/<site>/public/files/`**:

| Asset | Bundled path | Used by |
|---|---|---|
| Horizontal logo | `logo-512.png` (full-res: `logo.png`) | Login card / branding context |
| App mark | `logo-mark-512.png` (+ `logo-mark-128.png`) | Login panel, app screen, PWA icons |
| Favicon | `favicon-256.png` | Browser tab, Website Settings |
| Login left panel | `login-panel.jpg` | Login split-screen background |

`bench migrate` / install automatically fills **Website Settings → App Logo + Favicon +
App Name** and **System Settings → App Name** from these bundled assets
(`osduo_business_connect.branding.apply_branding_settings`). It also creates the
**Website Theme `OSDuo Business Connect`** from the same brand palette and makes
it the default. Rules:

- Empty, generic (`Frappe`) or legacy hand-copied brand files (`/files/logo*.png`,
  `/files/logo_mark_512x512.png`, …) are replaced with the bundled assets.
- A genuine per-site custom logo/name is left untouched, so white-labelling still
  works by simply uploading a replacement in Website Settings.
- The theme is only **created when missing** and only **selected when Website
  Settings → Theme is empty or `Standard`**. An existing `OSDuo Business Connect`
  theme is never rewritten, so per-site SCSS edits survive migrations. A site
  that deliberately chose another theme keeps it.
- Website Theme SCSS is compiled by Frappe with Node; keep `node` available on
  the bench. If compilation fails the error is logged and the site keeps its
  current theme — the migration still succeeds.
- To re-apply the defaults after changing an asset:
  `bench --site <site> execute osduo_business_connect.branding.apply_branding_settings`
  then `bench --site <site> clear-cache`.

### SEO, sitemap & cache (v1.3.0)

Public pages emit canonical + Open Graph + Twitter meta, structured data
(JSON-LD), a page-specific OG image, and are listed in a per-host sitemap.
Nothing is pushed to Google — discovery happens through `robots.txt`.

| Concern | How it works |
|---|---|
| Canonical / OG origin | Always from `site_config.json → host_name` (see above), **never** the request host. BYOD customers: set `host_name` to the custom domain so canonical / OG / sitemap all follow it — but note `host_name` also feeds printed QR/NFC URLs, so keep the previously-printed host serving (see the BYOD printed-media policy above). Private pages (login/root, `/offline`, `/analytics`, `/my-card`) are `noindex,nofollow`. |
| Sitemap | `/sitemap.xml` is an index of four per-type sitemaps (`/sitemap-businesses.xml`, `/sitemap-products.xml`, `/sitemap-services.xml`, `/sitemap-cards.xml`), built from published records with `lastmod`. |
| robots.txt | `/robots.txt` is served by the app and rebuilt per request; the `Sitemap:` line always matches the host the crawler reached. Admin-set rules in Website Settings are respected (only the `Sitemap:` line is managed). |
| Search Console (optional) | You may submit `/sitemap.xml` once, but it is not required — Google discovers it via the `Sitemap:` line and recrawls on its own schedule. The app never pushes. |
| SEO edits show immediately | `utils/cache.py` clears the cached page for the record and its related pages on publish/edit, so title/description/JSON-LD changes appear on the next request (no waiting for the ~30-minute page cache). |
| Vendor / product link | The footer + JSON-LD Brand link `OSDUO_BRANDING["product_url"]` while `product_url_live` is `True` (current), else the vendor site. The credit is shown when `show_vendor_credit` is `True` — set it `False` to white-label the footer off with no code change. |

**Deploy note:** the fonts and split CSS in `public/` are served from the asset
bundle, so after `git pull` run `bench --site <site> build --app
osduo_business_connect` (then `clear-website-cache`). Schema (SEO fields) needs
`bench migrate`.

---

## 🔧 Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| Public page 404 — “Business not found” | Record must be submitted (`docstatus < 2`), **Status = Published**, **Public Profile Enabled**, and the URL slug must exactly match **Public Slug**. A submitted record can change Status directly (no amendment needed). Then `bench clear-website-cache` |
| QR missing on card | `pip install "qrcode[pil]"` in the bench env; open+save card (or migrate) to trigger generation |
| Card URL wrong domain | Set `host_name`, then `bench migrate` (re-backfills `public_url`) |
| Public URL says `http://` but the site is on HTTPS (TLS terminated by Nginx Proxy Manager, Caddy, Cloudflare…) | `host_name` is missing or lacks the scheme. Frappe only infers `https` from `ssl_certificate`/`wildcard` in `site_config.json`, so a proxy that terminates TLS must set `"host_name": "https://your.domain"`. Then `bench --site <site> migrate` to re-backfill `public_url` and regenerate QR codes |
| Want to know which origin the app will print into links and QR codes | `bench --site <site> execute osduo_business_connect.utils.urls.describe_canonical_url` — shows the resolved base, the config key it came from, and whether developer mode is on. A scheme-less `host_name` on a public domain is now read as `https://`; loopback/private hosts stay `http://` |
| Sitemap or `robots.txt` lists `http://<bare-site-name>` instead of the public domain | Only affects **QR/public URLs** if `host_name` is unset — set `"host_name": "https://your.domain"` and migrate. The **sitemap and robots.txt no longer freeze a host**: `/sitemap*.xml` and `/robots.txt` resolve the origin from `host_name` or, failing that, the request host (`X-Forwarded-Proto` aware), so a new tenant subdomain is correct out of the box. After deploying, `bench --site <site> clear-cache && bench --site <site> clear-website-cache` |
| OSDuo fields not visible on the CRM Lead page (they exist in Customize Form) | Frappe CRM renders the Lead form from its own saved layout. `bench --site <site> migrate` runs `ensure_crm_fields_layout()`, which appends the "OSDuo Attribution" section to `CRM Lead-Side Panel` (idempotent). If a layout builder was used by hand, re-run migrate after any layout change that removed them |
| Login page unstyled / giant icons after Frappe upgrade | Stale Website Theme CSS — re-save the theme in Desk, `bench build`, hard-refresh |
| Logo/favicon missing after upgrade | `bench migrate` (applies bundled branding), then `bench clear-cache`; do **not** upload logo files to `public/files` |
| PWA not installable | Needs HTTPS (or `localhost`); check `/manifest.json` & `/sw.js` return 200; DevTools → Application → Manifest errors |
| `migrate` fails on CRM custom fields | Ensure the `crm` app is installed on the same site before Business Connect |
| `migrate` fails with `LinkValidationError: Could not find Primary Color / Text Color / Page Background Color` | An older Website Theme still links to legacy `Color` labels after a Frappe upgrade. Business Connect repairs broken theme colour links in a `before_migrate` hook; pull the latest `develop` and re-run `bench --site <site> migrate`. Valid custom colours are untouched |
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

- [User Manual](USER_MANUAL.md) · [Release Notes](../RELEASE_NOTES.md)
